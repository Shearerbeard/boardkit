"""Generate a per-card, PR-style review packet from its commit range.

Ported from terminalbench-aura's scripts/card_review_packet.py. Reads
the card's `commit-range` frontmatter field and writes to the
configured review output directory (gitignored working material):

  NN-<shortsha>.diff   one full patch per commit, in range order
  full-range.diff      the whole card as one diff
  REVIEW.md            commit subjects, per-file hunk pointers as
                       file:line anchors, and ready-to-paste git
                       commands for a terminal or editor review

The repo diffed against and the output directory come from the loaded
Config's [review] section; there is no hardcoded default repo.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import NamedTuple

import yaml

from boardkit.config import Config

RANGE_RE = re.compile(r"^[0-9a-f]{7,40}\.\.[0-9a-f]{7,40}$")
HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
SUFFIX_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_HUNKS_PER_FILE = 5
# Everything this module writes, and the only things a rerun may delete. The
# per-commit index is zero-padded to two digits but is not capped there: a
# card with a hundred commits writes `100-<sha>.diff`, so the sweep matches
# two or more digits. Anything else in the directory is reviewer material.
GENERATED_DIFF_RE = re.compile(r"^\d{2,}-[0-9a-f]{7,40}\.diff$")
GENERATED_NAMES = ("full-range.diff", "REVIEW.md")


class Commit(NamedTuple):
    sha: str
    subject: str


class ReviewPacketError(Exception):
    """Raised for a single fatal error while building the review packet."""


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise ReviewPacketError(f"git {' '.join(args)} failed in {repo}: {result.stderr.strip()}")
    return result.stdout


def load_card(cards_dir: Path, card_id: str) -> dict:
    matches = sorted(cards_dir.glob(f"{card_id.lower()}-*.md"))
    if not matches:
        raise ReviewPacketError(f"no card file matching '{card_id.lower()}-*.md' in {cards_dir}")
    if len(matches) > 1:
        raise ReviewPacketError(f"ambiguous card id {card_id}: {[m.name for m in matches]}")
    text = matches[0].read_text(encoding="utf-8")
    end = text.find("\n---\n", 4)
    if not text.startswith("---\n") or end < 0:
        raise ReviewPacketError(f"{matches[0].name}: missing or unterminated frontmatter")
    meta = yaml.safe_load(text[4:end])
    if not isinstance(meta, dict):
        raise ReviewPacketError(f"{matches[0].name}: frontmatter is not a mapping")
    meta["_file"] = matches[0].name
    return meta


def commit_list(repo: Path, commit_range: str) -> list[Commit]:
    lines = git(repo, "log", "--reverse", "--format=%H%x09%s", commit_range).splitlines()
    commits = [
        Commit(sha=sha, subject=subject)
        for sha, subject in (line.split("\t", 1) for line in lines)
    ]
    if not commits:
        raise ReviewPacketError(f"range {commit_range} contains no commits in {repo}")
    return commits


def strip_prefix(target: str, prefix: str) -> str | None:
    """Resolve a ---/+++ path, handling git's quoted form; None if no match."""
    if target.startswith(f'"{prefix}') and target.endswith('"'):
        return target[len(prefix) + 1 : -1]
    if target.startswith(prefix):
        return target[len(prefix) :]
    return None


def hunk_pointers(repo: Path, sha: str) -> dict[str, list[int]]:
    """Map each file in the commit to the new-side start line of its hunks.

    A deleted file gets an empty anchor list (its +++ side is /dev/null,
    so it has no new-side lines to point at).
    """
    pointers: dict[str, list[int]] = {}
    current: str | None = None
    old_path: str | None = None
    for line in git(repo, "show", "--unified=0", "--format=", sha).splitlines():
        if line.startswith("diff --git"):
            current = None
            old_path = None
        elif line.startswith("--- "):
            old_path = strip_prefix(line[4:], "a/")
        elif line.startswith("+++ "):
            current = strip_prefix(line[4:], "b/")
            if current is not None:
                pointers[current] = []
            elif line[4:] == "/dev/null" and old_path is not None:
                pointers[old_path] = []
        elif current is not None and (match := HUNK_RE.match(line)):
            pointers[current].append(int(match.group(1)))
    return pointers


def render_review(meta: dict, commit_range: str, repo: Path, commits: list[Commit]) -> str:
    lines = [
        f"# Review packet: {meta['id']} {meta['title']}",
        "",
        f"Card: `{meta['_file']}` | Repo: `{repo}`",
        f"Range: `{commit_range}` ({len(commits)} commits)",
        "",
        "Whole card at once: `full-range.diff`, or",
        f"`git -C {repo} diff {commit_range}`",
        "",
    ]
    for index, commit in enumerate(commits, start=1):
        short = commit.sha[:8]
        stat = git(repo, "show", "--shortstat", "--format=", commit.sha).strip()
        lines += [
            f"## {index}. {short} {commit.subject}",
            "",
            f"{stat}",
            f"Patch: `{index:02d}-{short}.diff` | `git -C {repo} show {short}`",
            "",
        ]
        for path, starts in hunk_pointers(repo, commit.sha).items():
            if not starts:
                lines.append(f"- {path} (deleted)")
                continue
            shown = ", ".join(f"{path}:{n}" for n in starts[:MAX_HUNKS_PER_FILE])
            extra = len(starts) - MAX_HUNKS_PER_FILE
            suffix = f" (+{extra} more hunks)" if extra > 0 else ""
            lines.append(f"- {shown}{suffix}")
        lines.append("")
    return "\n".join(lines)


def clean_generated(outdir: Path) -> None:
    """Delete this module's own outputs from `outdir`, and nothing else.

    The review directory also holds gate ledgers and reviewer transcripts
    that nothing can regenerate, so a rerun never removes the directory.
    """
    if not outdir.exists():
        return
    for stale in outdir.glob("*.diff"):
        if GENERATED_DIFF_RE.match(stale.name):
            stale.unlink()
    for name in GENERATED_NAMES:
        stale = outdir / name
        if stale.exists():
            stale.unlink()


def build_review_packet(
    config: Config,
    card_id: str,
    repo: Path | None = None,
    suffix: str | None = None,
    commit_range: str | None = None,
) -> Path:
    """Build the review packet for `card_id`; returns the output directory.

    `repo` overrides config.review.repo. `suffix` names the repo this
    packet covers, for a card whose work spans more than one repo: the
    output directory becomes `<output_dir>/<ID>-<suffix>` so an
    external-repo diff never lands in the primary packet's directory.
    `commit_range` overrides the card's `commit-range` frontmatter, which
    names shas in the primary repo only; a second repo has its own history,
    so its packet needs its own range alongside `repo` and `suffix`. With
    the override the card needs no frontmatter range at all.
    Raises ReviewPacketError on any fatal condition (missing card, missing
    commit-range, bad repo, malformed suffix, ...).
    """
    target_repo = repo if repo is not None else config.review.repo
    if suffix is not None and not SUFFIX_RE.match(suffix):
        raise ReviewPacketError(
            f"--suffix '{suffix}' is not a lowercase slug "
            "(a-z, 0-9, single dashes between them)"
        )

    meta = load_card(config.board.cards_dir, card_id)
    if str(meta.get("id", "")).upper() != card_id.upper():
        raise ReviewPacketError(
            f"{meta['_file']}: frontmatter id '{meta.get('id')}' does not "
            f"match requested '{card_id}'"
        )
    if commit_range is None:
        commit_range = meta.get("commit-range")
        source = f"{meta['_file']}: commit-range"
    else:
        source = "--commit-range"
    if not commit_range:
        raise ReviewPacketError(
            f"{meta['_file']}: no 'commit-range' frontmatter. Find the range "
            f"with: git log --oneline --grep '^Card: {card_id.upper()}$' "
            "<primary-branch>, record it on the card, and re-run."
        )
    if not RANGE_RE.match(str(commit_range)):
        raise ReviewPacketError(f"{source} '{commit_range}' is not A..B hex shas")
    if not target_repo.is_dir():
        raise ReviewPacketError(f"repo {target_repo} does not exist; pass --repo")

    commits = commit_list(target_repo, str(commit_range))
    dirname = card_id.upper() if suffix is None else f"{card_id.upper()}-{suffix}"
    outdir = config.review.output_dir / dirname
    clean_generated(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    for index, commit in enumerate(commits, start=1):
        patch = git(target_repo, "show", "--stat", "--patch", commit.sha)
        (outdir / f"{index:02d}-{commit.sha[:8]}.diff").write_text(patch, encoding="utf-8")
    full = git(target_repo, "diff", str(commit_range))
    (outdir / "full-range.diff").write_text(full, encoding="utf-8")
    review = render_review(meta, str(commit_range), target_repo, commits)
    (outdir / "REVIEW.md").write_text(review, encoding="utf-8")

    return outdir
