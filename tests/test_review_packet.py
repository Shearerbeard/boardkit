"""Tests for boardkit.review_packet.

Builds a real throwaway git repo per test (no git mocking): a few commits
touching multiple files, one commit deleting a file, one file changed in
enough scattered places to exceed MAX_HUNKS_PER_FILE, and two files whose
work a later commit in the range supersedes (one rewritten, one removed
outright). Cards and config are written to tmp_path so the whole pipeline
runs against real files.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

import pytest
from conftest import config_text

from boardkit.config import Config, load_config
from boardkit.review_packet import (
    MAX_FOCUS_FILES,
    MAX_HUNKS_PER_FILE,
    FileChurn,
    ReviewPacketError,
    build_review_packet,
    focus_prefix,
)

CARD_ID = "S2"
# Lines in multi.txt that C1 rewrites; spaced apart so each is its own hunk
# under `git show --unified=0`, yielding more hunks than MAX_HUNKS_PER_FILE.
MULTI_CHANGED_LINES = (2, 6, 10, 14, 18, 22, 26)
# churn.txt: six lines written by C1 and all six rewritten by C2, so its
# per-commit patches move 18 lines where the range's net diff keeps 6.
CHURN_LINES = 6
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def _init_repo(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    # Pin the object format so a global sha256 default cannot produce
    # 64-char shas the packet's range regex rejects, and point hooks at a
    # nonexistent dir so global hooks cannot interfere with commits.
    _git(repo, "init", "-q", "--object-format=sha1")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "commit.gpgsign", "false")
    _git(repo, "config", "core.hooksPath", "hooks-disabled")


def _commit(repo: Path, message: str) -> str:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD").strip()


@dataclass(frozen=True)
class Env:
    tmp_path: Path
    repo: Path
    decoy_repo: Path
    second_repo: Path
    cards_dir: Path
    plans_dir: Path
    output_dir: Path
    base_sha: str
    mid_sha: str
    last_sha: str
    second_base_sha: str
    second_last_sha: str

    @property
    def range(self) -> str:
        return f"{self.base_sha}..{self.last_sha}"

    @property
    def second_range(self) -> str:
        return f"{self.second_base_sha}..{self.second_last_sha}"

    def write_card(self, name: str, frontmatter: str, body: str = "body\n") -> Path:
        path = self.cards_dir / name
        path.write_text(f"---\n{frontmatter}---\n\n{body}", encoding="utf-8")
        return path

    def write_record(self, text: str, name: str = "record.md") -> Path:
        """A design record beside the cards dir, as a card links one."""
        self.plans_dir.mkdir(exist_ok=True)
        path = self.plans_dir / name
        path.write_text(text, encoding="utf-8")
        return path

    def write_config(self, repo_rel: str = "repo") -> Config:
        config_path = self.tmp_path / "boardkit.toml"
        config_path.write_text(config_text(repo=repo_rel), encoding="utf-8")
        return load_config(config_path)


@pytest.fixture
def env(tmp_path: Path) -> Env:
    repo = tmp_path / "repo"
    _init_repo(repo)

    # C0: base tree — files that later get modified/deleted, plus a file
    # with room for many scattered hunks.
    (repo / "keep.txt").write_text("keep original\n", encoding="utf-8")
    (repo / "doomed.txt").write_text("delete me\n", encoding="utf-8")
    (repo / "other.txt").write_text("other original\n", encoding="utf-8")
    multi_lines = [f"line {n}\n" for n in range(1, 31)]
    (repo / "multi.txt").write_text("".join(multi_lines), encoding="utf-8")
    base_sha = _commit(repo, "C0 base tree")

    # C1: touch several files; rewrite scattered lines of multi.txt so the
    # commit has more than MAX_HUNKS_PER_FILE hunks in that one file. churn
    # and scratch are the two files C2 supersedes.
    for n in MULTI_CHANGED_LINES:
        multi_lines[n - 1] = f"CHANGED line {n}\n"
    (repo / "multi.txt").write_text("".join(multi_lines), encoding="utf-8")
    (repo / "other.txt").write_text("other rewritten\n", encoding="utf-8")
    churn_lines = [f"draft {n}\n" for n in range(1, CHURN_LINES + 1)]
    (repo / "churn.txt").write_text("".join(churn_lines), encoding="utf-8")
    (repo / "scratch.txt").write_text("scratch\n", encoding="utf-8")
    mid_sha = _commit(repo, "C1 modify many files")

    # C2: delete a tracked file and modify another; rewrite every line C1
    # wrote into churn.txt, and remove the file C1 added.
    (repo / "doomed.txt").unlink()
    (repo / "keep.txt").write_text("keep updated\n", encoding="utf-8")
    (repo / "churn.txt").write_text(
        "".join(f"final {n}\n" for n in range(1, CHURN_LINES + 1)), encoding="utf-8"
    )
    (repo / "scratch.txt").unlink()
    last_sha = _commit(repo, "C2 delete a file")

    decoy_repo = tmp_path / "decoy"
    _init_repo(decoy_repo)

    # A genuinely separate repo, as a multi-repo card's second repo is: its
    # own history, so none of `repo`'s shas resolve inside it.
    second_repo = tmp_path / "second"
    _init_repo(second_repo)
    (second_repo / "adapter.txt").write_text("adapter original\n", encoding="utf-8")
    second_base_sha = _commit(second_repo, "D0 second repo base")
    (second_repo / "adapter.txt").write_text("adapter rewritten\n", encoding="utf-8")
    second_last_sha = _commit(second_repo, "D1 second repo change")

    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()

    return Env(
        tmp_path=tmp_path,
        repo=repo,
        decoy_repo=decoy_repo,
        second_repo=second_repo,
        cards_dir=cards_dir,
        plans_dir=tmp_path / "plans",
        output_dir=tmp_path / "reviews",
        base_sha=base_sha,
        mid_sha=mid_sha,
        last_sha=last_sha,
        second_base_sha=second_base_sha,
        second_last_sha=second_last_sha,
    )


def _valid_card(env: Env, commit_range: str | None = None) -> None:
    rng = env.range if commit_range is None else commit_range
    env.write_card(
        "s2-example.md",
        f"id: {CARD_ID}\ntitle: Example card\ncommit-range: {rng}\n",
    )


def _multi_anchor_line(review: str) -> str:
    lines = [ln for ln in review.splitlines() if ln.startswith("- [multi.txt:")]
    assert len(lines) == 1, f"expected one multi.txt anchor line, got {lines}"
    return lines[0]


def _review(env: Env, dirname: str = CARD_ID) -> str:
    return (env.output_dir / dirname / "REVIEW.md").read_text(encoding="utf-8")


def _guide_entries(review: str) -> list[str]:
    """The review guide's ranked list, one string per entry, in order."""
    guide = review.split("## Review guide", 1)[1].split("\n## ", 1)[0]
    return [ln for ln in guide.splitlines() if re.match(r"^\d+\. ", ln)]


def _entry_for(review: str, path: str) -> str:
    matches = [ln for ln in _guide_entries(review) if f"{path}]" in ln or f"`{path}`" in ln]
    assert len(matches) == 1, f"expected one guide entry for {path}, got {matches}"
    return matches[0]


def test_happy_path_builds_full_packet(env: Env) -> None:
    config = env.write_config()
    _valid_card(env)

    outdir = build_review_packet(config, CARD_ID)

    assert outdir == env.output_dir / CARD_ID
    assert outdir.is_dir()
    assert (outdir / "full-range.diff").is_file()

    # One patch per commit in range (C0..C2 -> C1, C2), in range order.
    diffs = sorted(p.name for p in outdir.glob("*.diff") if p.name != "full-range.diff")
    assert diffs == [
        f"01-{env.mid_sha[:8]}.diff",
        f"02-{env.last_sha[:8]}.diff",
    ]

    # Each per-commit patch carries that commit's changes and not the other's.
    c1_patch = (outdir / diffs[0]).read_text(encoding="utf-8")
    c2_patch = (outdir / diffs[1]).read_text(encoding="utf-8")
    assert "+other rewritten" in c1_patch
    assert "doomed.txt" not in c1_patch
    assert "-delete me" in c2_patch
    assert "other.txt" not in c2_patch

    # full-range.diff spans both commits.
    full = (outdir / "full-range.diff").read_text(encoding="utf-8")
    assert "+other rewritten" in full
    assert "-delete me" in full
    assert "+CHANGED line 2" in full


def test_review_md_lists_commit_subjects(env: Env) -> None:
    config = env.write_config()
    _valid_card(env)

    build_review_packet(config, CARD_ID)
    review = (env.output_dir / CARD_ID / "REVIEW.md").read_text(encoding="utf-8")

    assert "C1 modify many files" in review
    assert "C2 delete a file" in review


def test_review_md_links_hunk_anchors_relative_to_the_packet(env: Env) -> None:
    config = env.write_config()
    _valid_card(env)

    build_review_packet(config, CARD_ID)

    # other.txt is a single-hunk change in C1: the visible text stays the
    # path:new-side-line token an editor jumps on, and the target is the
    # link relative to the packet directory.
    assert "- [other.txt:1](../../repo/other.txt)" in _review(env)


def test_review_md_marks_deleted_file(env: Env) -> None:
    """A file the range deletes has no working-tree target, so it renders as
    inline code: a link there would point at nothing."""
    config = env.write_config()
    _valid_card(env)

    build_review_packet(config, CARD_ID)
    review = _review(env)

    assert "- `doomed.txt` (deleted)" in review
    # scratch.txt has hunks in C1 and is gone by the range end: the anchor
    # keeps its path:line token and loses only the link.
    assert "- `scratch.txt:1`" in review


def test_hunk_pointers_capped_at_max(env: Env) -> None:
    config = env.write_config()
    _valid_card(env)

    build_review_packet(config, CARD_ID)

    anchor_line = _multi_anchor_line(_review(env))
    # The contract is five anchors: assert the literal cap, not the
    # constant, so a drive-by change to MAX_HUNKS_PER_FILE fails here.
    # `multi.txt:` matches the link text only; the target carries no colon.
    assert MAX_HUNKS_PER_FILE == 5
    assert anchor_line.count("multi.txt:") == 5
    for line_no in MULTI_CHANGED_LINES[:5]:
        assert f"[multi.txt:{line_no}](../../repo/multi.txt)" in anchor_line
    for line_no in MULTI_CHANGED_LINES[5:]:
        assert f"multi.txt:{line_no}" not in anchor_line
    assert "(+2 more hunks)" in anchor_line


def test_review_md_leads_with_the_guide_and_keeps_the_commit_listing(env: Env) -> None:
    """The guide is an entry point over the indexed packet, not a replacement:
    it leads, and every section the packet had is still below it."""
    config = env.write_config()
    _valid_card(env)

    build_review_packet(config, CARD_ID)
    review = _review(env)
    headings = [ln for ln in review.splitlines() if ln.startswith("## ")]

    assert headings[0] == "## Review guide"
    assert headings == ["## Review guide", "## Commits", "## Retention"]
    assert review.index("## Review guide") < review.index("## Commits")
    # the commit listing itself survived the reorder
    assert "### 1. " in review
    assert "C1 modify many files" in review
    assert "C2 delete a file" in review


def test_guide_ranks_files_by_the_lines_they_change_in_the_net_diff(env: Env) -> None:
    config = env.write_config()
    _valid_card(env)

    build_review_packet(config, CARD_ID)
    entries = _guide_entries(_review(env))

    # multi.txt changes 14 lines net, churn.txt 6, the single-line files 1-2.
    assert entries[0].startswith("1. [multi.txt]")
    assert entries[1].startswith("2. [churn.txt]")
    # every file the range touches is in the guide, ranked or not
    assert len(entries) == 6
    # a file whose work is fully undone ranks last: nothing of it survives
    assert entries[-1].startswith("6. `scratch.txt`")


def test_guide_names_the_files_carrying_most_of_the_churn(env: Env) -> None:
    """Decision 7's 80/20: the packet says where to spend the first pass."""
    config = env.write_config()
    _valid_card(env)

    build_review_packet(config, CARD_ID)
    review = _review(env)

    assert "6 files changed, 25 lines in the range's net diff." in review
    assert (
        "Start here - 2 files carrying 80% of it: [multi.txt](../../repo/multi.txt), "
        "[churn.txt](../../repo/churn.txt)." in review
    )


def test_binary_file_reports_no_line_counts_and_is_never_superseded(env: Env) -> None:
    """git reports no line counts for a binary file. Reading the zeroes as
    counts would flag a text file replaced by binary content as superseded."""
    config = env.write_config()
    (env.repo / "asset.bin").write_text("plain text first\nsecond line\n", encoding="utf-8")
    text_sha = _commit(env.repo, "C3 add asset.bin as text")
    (env.repo / "asset.bin").write_bytes(bytes(range(256)) * 4)
    binary_sha = _commit(env.repo, "C4 replace asset.bin with binary content")
    _valid_card(env, commit_range=f"{env.last_sha}..{binary_sha}")

    build_review_packet(config, CARD_ID)
    entry = _entry_for(_review(env), "asset.bin")

    assert "binary, no line counts, changed in 2 commits" in entry
    assert "lines net" not in entry
    assert "SUPERSEDED" not in entry
    assert text_sha != binary_sha


def test_a_binary_file_added_and_removed_again_reads_as_undone(env: Env) -> None:
    """Binary-ness qualifies the net diff's counts, so a file absent from the
    net diff is not binary work that survived - it is work the range undid."""
    config = env.write_config()
    (env.repo / "asset.bin").write_bytes(bytes(range(256)))
    _commit(env.repo, "C3 add a binary file")
    (env.repo / "asset.bin").unlink()
    removed_sha = _commit(env.repo, "C4 remove it again")
    _valid_card(env, commit_range=f"{env.last_sha}..{removed_sha}")

    build_review_packet(config, CARD_ID)
    review = _review(env)

    assert "every line this range moves is undone again" in review
    assert "Binary content is why" not in review
    assert "binary, no line counts" not in _entry_for(review, "asset.bin")


def test_a_file_binary_only_mid_range_keeps_the_net_counts(env: Env) -> None:
    """The net diff is text at both ends, so its line counts are real and the
    intermediate binary commit must not suppress them."""
    config = env.write_config()
    swing = env.repo / "swing.txt"
    swing.write_text("one\ntwo\n", encoding="utf-8")
    start_sha = _commit(env.repo, "C3 add swing.txt as text")
    swing.write_bytes(bytes(range(256)))
    _commit(env.repo, "C4 make swing.txt binary")
    swing.write_text("one\ntwo\nthree\nfour\n", encoding="utf-8")
    end_sha = _commit(env.repo, "C5 make swing.txt text again")
    _valid_card(env, commit_range=f"{start_sha}..{end_sha}")

    build_review_packet(config, CARD_ID)
    entry = _entry_for(_review(env), "swing.txt")

    assert "2 lines net" in entry
    assert "binary" not in entry
    assert "SUPERSEDED" not in entry
    # the raw count is understated by the binary commits, so it is dropped
    # rather than printed as a figure smaller than the net one
    assert "touched across" not in entry
    assert "changed across 2 commits" in entry


def test_a_binary_only_range_does_not_claim_its_work_was_undone(env: Env) -> None:
    config = env.write_config()
    (env.repo / "asset.bin").write_bytes(bytes(range(256)))
    binary_sha = _commit(env.repo, "C3 add a binary file")
    _valid_card(env, commit_range=f"{env.last_sha}..{binary_sha}")

    build_review_packet(config, CARD_ID)
    review = _review(env)

    assert "Binary content is why: git reports no line counts for it" in review
    assert "range's changes are real and only their counts are absent" in review
    assert "undone again" not in review


def test_a_range_whose_text_work_is_all_undone_still_says_so(env: Env) -> None:
    """The undone claim is the right one when no binary file explains the
    missing counts, so the binary fix must not swallow it."""
    config = env.write_config()
    (env.repo / "blip.txt").write_text("here\n", encoding="utf-8")
    added_sha = _commit(env.repo, "C3 add blip.txt")
    (env.repo / "blip.txt").unlink()
    removed_sha = _commit(env.repo, "C4 remove blip.txt")
    _valid_card(env, commit_range=f"{env.last_sha}..{removed_sha}")

    build_review_packet(config, CARD_ID)
    review = _review(env)

    assert "every line this range moves is undone again" in review
    assert "binary" not in review
    assert added_sha != removed_sha


def test_focus_list_is_capped_when_churn_spreads_flat() -> None:
    """An unbounded 80% prefix over a flat range names most of its files,
    which tells the reader to start everywhere."""
    ranked = [FileChurn(path=f"f{n}.py", net=10, raw=10, commits=1) for n in range(20)]

    focus = focus_prefix(ranked)

    assert len(focus) == MAX_FOCUS_FILES
    assert [entry.path for entry in focus] == [f"f{n}.py" for n in range(MAX_FOCUS_FILES)]


def test_guide_flags_a_file_a_later_commit_rewrote(env: Env) -> None:
    config = env.write_config()
    _valid_card(env)

    build_review_packet(config, CARD_ID)
    review = _review(env)

    # churn.txt: C1 writes 6 lines, C2 rewrites all of them, so 18 lines move
    # across the two patches and 6 survive.
    churn = _entry_for(review, "churn.txt")
    assert "6 lines net, 18 touched across 2 commits" in churn
    assert "SUPERSEDED IN PART: 12 of the 18 touched lines do not reach the range end" in churn
    assert "[full-range.diff](full-range.diff)" in churn

    # scratch.txt: added by C1 and removed by C2, so the net diff never sees it.
    scratch = _entry_for(review, "scratch.txt")
    assert "SUPERSEDED: the range's net diff does not touch this file" in scratch

    # and the flag's meaning is stated, including what it does not mean
    assert "It never says the file is safe to skip" in review


def test_guide_does_not_flag_a_file_only_one_commit_touched(env: Env) -> None:
    """Over-flagging would tell a reader to skip hunks that still matter."""
    config = env.write_config()
    _valid_card(env)

    build_review_packet(config, CARD_ID)
    review = _review(env)

    for path in ("multi.txt", "other.txt", "keep.txt", "doomed.txt"):
        assert "SUPERSEDED" not in _entry_for(review, path)


def test_author_supplied_order_leads_the_guide(env: Env) -> None:
    """Churn ranking cannot make the judgment calls, so the card's own order
    wins where it names files, and the rest still rank by churn."""
    config = env.write_config()
    env.write_card(
        "s2-example.md",
        f"id: {CARD_ID}\ntitle: Example card\ncommit-range: {env.range}\n",
        body="# S2\n\n## Review order\n\n- `keep.txt`, the decision this card turns on\n"
        "- `other.txt`\n",
    )

    build_review_packet(config, CARD_ID)
    review = _review(env)
    entries = _guide_entries(review)

    assert entries[0].startswith("1. [keep.txt]")
    assert entries[1].startswith("2. [other.txt]")
    assert entries[2].startswith("3. [multi.txt]")
    assert "Order: author-supplied - the card's `Review order` section first" in review


def test_author_order_leaves_the_guide_one_entry_point(env: Env) -> None:
    """Two entry points contradict each other: with an author order the card
    named the way in, so the churn concentration stops instructing."""
    config = env.write_config()
    env.write_card(
        "s2-example.md",
        f"id: {CARD_ID}\ntitle: Example card\ncommit-range: {env.range}\n",
        body="# S2\n\n## Review order\n\n- `keep.txt`\n",
    )

    build_review_packet(config, CARD_ID)
    review = _review(env)

    assert "Start here" not in review
    assert "Net churn concentrates in 2 files carrying 80% of it:" in review
    assert "Order: author-supplied - the card's `Review order` section first" in review
    assert _guide_entries(review)[0].startswith("1. [keep.txt]")


def test_without_an_author_order_the_churn_line_is_the_entry_point(env: Env) -> None:
    config = env.write_config()
    _valid_card(env)

    build_review_packet(config, CARD_ID)
    review = _review(env)

    assert "Start here - 2 files carrying 80% of it:" in review
    assert "Net churn concentrates" not in review


def test_review_order_naming_a_path_outside_the_range_is_rejected(env: Env) -> None:
    config = env.write_config()
    env.write_card(
        "s2-example.md",
        f"id: {CARD_ID}\ntitle: Example card\ncommit-range: {env.range}\n",
        body="# S2\n\n## Review order\n\n- `nowhere.txt`\n",
    )

    with pytest.raises(ReviewPacketError, match="nowhere.txt, which the card's commit range"):
        build_review_packet(config, CARD_ID)


def test_review_order_bullet_without_a_path_is_rejected(env: Env) -> None:
    config = env.write_config()
    env.write_card(
        "s2-example.md",
        f"id: {CARD_ID}\ntitle: Example card\ncommit-range: {env.range}\n",
        body="# S2\n\n## Review order\n\n- read the parser first\n",
    )

    with pytest.raises(ReviewPacketError, match="names no path"):
        build_review_packet(config, CARD_ID)


def test_a_failed_regeneration_leaves_the_previous_packet_in_place(env: Env) -> None:
    """REVIEW.md is built from the card's own sections, so a malformed card is
    a live failure mode; it must not empty a packet a gate is reading."""
    config = env.write_config()
    _valid_card(env)
    outdir = build_review_packet(config, CARD_ID)
    before = _review(env)

    env.write_card(
        "s2-example.md",
        f"id: {CARD_ID}\ntitle: Example card\ncommit-range: {env.range}\n",
        body="# S2\n\n## Review order\n\n- `nowhere.txt`\n",
    )
    with pytest.raises(ReviewPacketError):
        build_review_packet(config, CARD_ID)

    assert _review(env) == before
    assert (outdir / "full-range.diff").is_file()
    assert (outdir / f"01-{env.mid_sha[:8]}.diff").is_file()


def test_every_file_reference_is_a_link_relative_to_the_packet_directory(env: Env) -> None:
    """The board owner reviews in an editor that follows links: every
    reference must resolve from the packet's own directory."""
    config = env.write_config()
    record = env.write_record(
        "# Type surface\n\n## Type relationships\n\n"
        "| Type | Wraps | Returns |\n|---|---|---|\n| `Packet` | `Commit` | `str` |\n"
    )
    env.write_card(
        "s2-example.md",
        f"id: {CARD_ID}\ntitle: Example card\ncommit-range: {env.range}\n",
        body=f"# S2\n\n## Design record\n\n[{record.name}](../plans/{record.name})\n",
    )

    outdir = build_review_packet(config, CARD_ID)
    targets = LINK_RE.findall(_review(env))

    assert targets, "REVIEW.md renders no links at all"
    for target in targets:
        assert not target.startswith(("/", "http://", "https://")), f"{target} is not relative"
        assert (outdir / target).exists(), f"{target} does not resolve from {outdir}"


def test_design_record_is_linked_above_the_commit_listing_with_its_type_section(
    env: Env,
) -> None:
    config = env.write_config()
    record = env.write_record(
        "# E1 type surface\n\n## Overview\n\nprose\n\n## Type relationships\n\n"
        "| Type | Wraps | Returns |\n|---|---|---|\n"
        "| `Packet` | `Commit` | `str` |\n\n## Fill order\n\nnot this section\n"
    )
    env.write_card(
        "s2-example.md",
        f"id: {CARD_ID}\ntitle: Example card\ncommit-range: {env.range}\n",
        body=f"# S2\n\n## Design record\n\n[{record.name}](../plans/{record.name})\n",
    )

    build_review_packet(config, CARD_ID)
    review = _review(env)

    assert "## Design record" in review
    assert f"[{record.name}](../../plans/{record.name})" in review
    assert review.index("## Design record") < review.index("## Commits")
    assert review.index("## Type relationships") < review.index("## Commits")
    assert "| `Packet` | `Commit` | `str` |" in review
    assert "not this section" not in review


def test_lifted_design_record_links_are_rebased_onto_the_packet(env: Env) -> None:
    """A lifted section names its siblings the way the record does, which
    resolves against the record's directory, not the packet's."""
    config = env.write_config()
    (env.plans_dir).mkdir(exist_ok=True)
    (env.plans_dir / "ledger.md").write_text("# Holes ledger\n", encoding="utf-8")
    record = env.write_record(
        "# Type surface\n\n## Type relationships\n\n"
        "The [holes ledger](ledger.md) lists them.\n"
        "The [spec](https://example.com/spec) does not.\n"
        "See [fill order](#fill-order) and [hosts](/etc/hosts).\n\n"
        "## Fill order\n\nlater\n"
    )
    env.write_card(
        "s2-example.md",
        f"id: {CARD_ID}\ntitle: Example card\ncommit-range: {env.range}\n",
        body=f"# S2\n\n## Design record\n\n[{record.name}](../plans/{record.name})\n",
    )

    outdir = build_review_packet(config, CARD_ID)
    review = _review(env)

    assert "[holes ledger](../../plans/ledger.md)" in review
    assert (outdir / "../../plans/ledger.md").exists()
    # a URI, a bare anchor, and an absolute path are left exactly as written
    assert "[spec](https://example.com/spec)" in review
    assert "[fill order](#fill-order)" in review
    assert "[hosts](/etc/hosts)" in review


def test_lifted_record_link_with_a_title_rebases_and_keeps_the_title(env: Env) -> None:
    """A title's leading space ends the destination, so a titled link went
    unrewritten and stayed pointed at the record's directory."""
    config = env.write_config()
    env.plans_dir.mkdir(exist_ok=True)
    (env.plans_dir / "ledger.md").write_text("# Holes ledger\n", encoding="utf-8")
    record = env.write_record(
        "# Type surface\n\n## Type relationships\n\n"
        'Titled [ledger](ledger.md "Holes ledger"), plain [ledger](ledger.md).\n'
    )
    env.write_card(
        "s2-example.md",
        f"id: {CARD_ID}\ntitle: Example card\ncommit-range: {env.range}\n",
        body=f"# S2\n\n## Design record\n\n[{record.name}](../plans/{record.name})\n",
    )

    outdir = build_review_packet(config, CARD_ID)
    review = _review(env)

    assert '[ledger](../../plans/ledger.md "Holes ledger")' in review
    assert "[ledger](../../plans/ledger.md)" in review
    assert "(ledger.md" not in review
    assert (outdir / "../../plans/ledger.md").exists()


def test_a_hash_in_a_path_is_percent_encoded_not_left_as_a_fragment(env: Env) -> None:
    """Angle brackets fix markdown parsing; they do not stop a follower from
    reading `#draft.txt` as an anchor on a file called `notes`."""
    config = env.write_config()
    (env.repo / "notes#draft.txt").write_text("draft\n", encoding="utf-8")
    sha = _commit(env.repo, "C3 add a file with a hash in its name")
    _valid_card(env, commit_range=f"{env.last_sha}..{sha}")

    outdir = build_review_packet(config, CARD_ID)
    review = _review(env)

    assert "[notes#draft.txt](../../repo/notes%23draft.txt)" in review
    assert "[notes#draft.txt:1](../../repo/notes%23draft.txt)" in review
    # decoded, the destination is the file itself
    assert (outdir / unquote("../../repo/notes%23draft.txt")).is_file()


def test_links_escape_paths_a_commonmark_parser_would_misread(env: Env) -> None:
    """Spaces and parentheses end a bare destination early; brackets end a
    label early. Both are legal in a git filename."""
    config = env.write_config()
    (env.repo / "notes (draft).txt").write_text("draft\n", encoding="utf-8")
    (env.repo / "notes[wip].txt").write_text("wip\n", encoding="utf-8")
    sha = _commit(env.repo, "C3 add awkwardly named files")
    _valid_card(env, commit_range=f"{env.last_sha}..{sha}")

    build_review_packet(config, CARD_ID)
    review = _review(env)

    # space and parens: CommonMark's angle-bracket destination takes them literally
    assert "[notes (draft).txt](<../../repo/notes (draft).txt>)" in review
    assert "[notes (draft).txt:1](<../../repo/notes (draft).txt>)" in review
    # brackets: escaped in the label, legal unescaped in a bare destination
    assert r"[notes\[wip\].txt](../../repo/notes[wip].txt)" in review
    assert r"[notes\[wip\].txt:1](../../repo/notes[wip].txt)" in review


def test_design_record_without_a_type_relationship_section_is_rejected(env: Env) -> None:
    config = env.write_config()
    record = env.write_record("# E1 type surface\n\n## Overview\n\nprose only\n")
    env.write_card(
        "s2-example.md",
        f"id: {CARD_ID}\ntitle: Example card\ncommit-range: {env.range}\n",
        body=f"# S2\n\n## Design record\n\n[{record.name}](../plans/{record.name})\n",
    )

    with pytest.raises(ReviewPacketError, match="no type-relationship section"):
        build_review_packet(config, CARD_ID)


def test_design_record_section_without_a_link_is_rejected(env: Env) -> None:
    config = env.write_config()
    env.write_card(
        "s2-example.md",
        f"id: {CARD_ID}\ntitle: Example card\ncommit-range: {env.range}\n",
        body="# S2\n\n## Design record\n\nthe one from the design panel\n",
    )

    with pytest.raises(ReviewPacketError, match="links no record"):
        build_review_packet(config, CARD_ID)


def test_design_record_link_that_does_not_resolve_is_rejected(env: Env) -> None:
    config = env.write_config()
    env.write_card(
        "s2-example.md",
        f"id: {CARD_ID}\ntitle: Example card\ncommit-range: {env.range}\n",
        body="# S2\n\n## Design record\n\n[gone.md](../plans/gone.md)\n",
    )

    with pytest.raises(ReviewPacketError, match="does not resolve to a file"):
        build_review_packet(config, CARD_ID)


def test_a_card_without_a_design_record_gets_no_type_sections(env: Env) -> None:
    config = env.write_config()
    _valid_card(env)

    build_review_packet(config, CARD_ID)
    review = _review(env)

    assert "## Design record" not in review
    assert "## Type relationships" not in review


def test_packet_states_the_retention_contract(env: Env) -> None:
    config = env.write_config()
    _valid_card(env)

    build_review_packet(config, CARD_ID)
    review = _review(env)

    assert "## Retention" in review
    assert "regenerable working material" in review
    assert "card and its log are the durable record" in review
    assert "un-ignores the output" in review


def test_rerun_keeps_reviewer_material_alongside_the_packet(env: Env) -> None:
    """The output dir also holds gate ledgers and reviewer transcripts that
    nothing can regenerate; a rerun replaces only this module's own outputs."""
    config = env.write_config()
    _valid_card(env)

    outdir = build_review_packet(config, CARD_ID)
    ledger = outdir / "gate-a-findings.md"
    ledger.write_text("1. finding, fixed in C2\n", encoding="utf-8")
    transcript = outdir / "transcripts" / "reviewer.txt"
    transcript.parent.mkdir()
    transcript.write_text("verdict: PASS\n", encoding="utf-8")

    outdir2 = build_review_packet(config, CARD_ID)

    assert outdir2 == outdir
    assert ledger.read_text(encoding="utf-8") == "1. finding, fixed in C2\n"
    assert transcript.read_text(encoding="utf-8") == "verdict: PASS\n"
    assert (outdir / "full-range.diff").is_file()
    assert (outdir / "REVIEW.md").is_file()


def test_rerun_removes_per_commit_diffs_from_the_previous_range(env: Env) -> None:
    """A shrunk range must not leave orphan NN-*.diff files behind, or the
    reviewer reads diffs that are no longer part of the card."""
    config = env.write_config()
    _valid_card(env)

    outdir = build_review_packet(config, CARD_ID)
    assert (outdir / f"02-{env.last_sha[:8]}.diff").is_file()

    _valid_card(env, commit_range=f"{env.base_sha}..{env.mid_sha}")
    build_review_packet(config, CARD_ID)

    assert (outdir / f"01-{env.mid_sha[:8]}.diff").is_file()
    assert not (outdir / f"02-{env.last_sha[:8]}.diff").exists()


def test_rerun_removes_three_digit_per_commit_diffs(env: Env) -> None:
    """A card with 100 or more commits writes `100-<sha>.diff`; the cleanup
    sweep has to reach those too, and still leave foreign files alone."""
    config = env.write_config()
    _valid_card(env)

    outdir = build_review_packet(config, CARD_ID)
    wide = outdir / f"100-{env.last_sha[:8]}.diff"
    wide.write_text("stale patch from a longer range\n", encoding="utf-8")
    single_digit = outdir / f"1-{env.last_sha[:8]}.diff"
    single_digit.write_text("not something this module writes\n", encoding="utf-8")

    build_review_packet(config, CARD_ID)

    assert not wide.exists()
    assert single_digit.is_file()


def test_suffix_gives_the_card_a_per_repo_output_dir(env: Env) -> None:
    config = env.write_config()
    _valid_card(env)

    outdir = build_review_packet(config, CARD_ID, suffix="adapter")

    assert outdir == env.output_dir / f"{CARD_ID}-adapter"
    assert (outdir / "REVIEW.md").is_file()
    # the unsuffixed dir stays untouched, so both repos' packets coexist
    assert not (env.output_dir / CARD_ID).exists()


def test_packets_for_two_genuinely_different_repos_coexist(env: Env) -> None:
    """A multi-repo card's second repo has its own history: the card's
    `commit-range` shas do not exist there, so the second packet needs the
    `--commit-range` override as well as `--repo` and `--suffix`."""
    config = env.write_config()
    _valid_card(env)

    primary = build_review_packet(config, CARD_ID)
    secondary = build_review_packet(
        config,
        CARD_ID,
        repo=env.second_repo,
        suffix="adapter",
        commit_range=env.second_range,
    )

    assert primary == env.output_dir / CARD_ID
    assert secondary == env.output_dir / f"{CARD_ID}-adapter"

    primary_review = (primary / "REVIEW.md").read_text(encoding="utf-8")
    secondary_review = (secondary / "REVIEW.md").read_text(encoding="utf-8")

    # each packet is built from its own repo's range, not the other's
    assert "C2 delete a file" in primary_review
    assert "D1 second repo change" not in primary_review
    assert "D1 second repo change" in secondary_review
    assert "C2 delete a file" not in secondary_review
    assert env.second_range in secondary_review
    assert env.range not in secondary_review

    secondary_full = (secondary / "full-range.diff").read_text(encoding="utf-8")
    assert "+adapter rewritten" in secondary_full
    assert (secondary / f"01-{env.second_last_sha[:8]}.diff").is_file()


def test_second_repo_without_the_override_cannot_resolve_the_cards_range(env: Env) -> None:
    """The regression the override exists for: the frontmatter range names
    shas that the second repo has never seen."""
    config = env.write_config()
    _valid_card(env)

    with pytest.raises(ReviewPacketError, match="does not resolve"):
        build_review_packet(config, CARD_ID, repo=env.second_repo, suffix="adapter")


def test_commit_range_override_beats_the_frontmatter_range(env: Env) -> None:
    config = env.write_config()
    _valid_card(env)

    outdir = build_review_packet(config, CARD_ID, commit_range=f"{env.base_sha}..{env.mid_sha}")
    review = (outdir / "REVIEW.md").read_text(encoding="utf-8")

    assert "C1 modify many files" in review
    assert "C2 delete a file" not in review


def test_revision_expression_in_commit_range_is_accepted(env: Env) -> None:
    """A range side may be any git revision expression, not just a hex sha."""
    config = env.write_config()
    _valid_card(env)

    outdir = build_review_packet(config, CARD_ID, commit_range=f"{env.base_sha[:8]}..HEAD")
    review = (outdir / "REVIEW.md").read_text(encoding="utf-8")

    assert "C1 modify many files" in review
    assert "C2 delete a file" in review


def test_malformed_commit_range_override_rejected(env: Env) -> None:
    config = env.write_config()
    _valid_card(env)

    with pytest.raises(ReviewPacketError, match="does not resolve"):
        build_review_packet(config, CARD_ID, commit_range="zzzzzzz..yyyyyyy")


def test_cli_passes_the_commit_range_override_through(env: Env) -> None:
    from boardkit.cli import build_parser, cmd_review_packet

    env.write_config()
    _valid_card(env)
    args = build_parser().parse_args(
        [
            "--config",
            str(env.tmp_path / "boardkit.toml"),
            "review-packet",
            CARD_ID,
            "--repo",
            str(env.second_repo),
            "--suffix",
            "adapter",
            "--commit-range",
            env.second_range,
        ]
    )

    assert cmd_review_packet(args) == 0
    review = (env.output_dir / f"{CARD_ID}-adapter" / "REVIEW.md").read_text(encoding="utf-8")
    assert "D1 second repo change" in review


@pytest.mark.parametrize(
    "suffix",
    ["Adapter", "with space", "trailing-", "-leading", "under_score", "", "a/b"],
)
def test_malformed_suffix_rejected(env: Env, suffix: str) -> None:
    config = env.write_config()
    _valid_card(env)

    with pytest.raises(ReviewPacketError, match="suffix"):
        build_review_packet(config, CARD_ID, suffix=suffix)


def test_repo_override_beats_config_repo(env: Env) -> None:
    # config points at a real git repo that lacks the card's commits; the
    # override must be used instead, so the build succeeds.
    config = env.write_config(repo_rel="decoy")
    _valid_card(env)

    outdir = build_review_packet(config, CARD_ID, repo=env.repo)

    assert outdir.is_dir()
    assert (outdir / "full-range.diff").is_file()


def test_missing_commit_range_reports_how_to_find_it(env: Env) -> None:
    config = env.write_config()
    env.write_card("s2-example.md", f"id: {CARD_ID}\ntitle: Example card\n")

    with pytest.raises(ReviewPacketError) as excinfo:
        build_review_packet(config, CARD_ID)

    message = str(excinfo.value)
    assert "commit-range" in message
    assert "git log" in message


def test_malformed_commit_range_rejected(env: Env) -> None:
    config = env.write_config()
    _valid_card(env, commit_range="zzzzzzz..yyyyyyy")

    with pytest.raises(ReviewPacketError, match="does not resolve"):
        build_review_packet(config, CARD_ID)


def test_frontmatter_id_mismatch_rejected(env: Env) -> None:
    config = env.write_config()
    env.write_card(
        "s2-example.md",
        f"id: S3\ntitle: Wrong id\ncommit-range: {env.range}\n",
    )

    with pytest.raises(ReviewPacketError, match="does not.*match requested"):
        build_review_packet(config, CARD_ID)


def test_ambiguous_card_glob_rejected(env: Env) -> None:
    config = env.write_config()
    env.write_card("s2-one.md", f"id: {CARD_ID}\ntitle: One\ncommit-range: {env.range}\n")
    env.write_card("s2-two.md", f"id: {CARD_ID}\ntitle: Two\ncommit-range: {env.range}\n")

    with pytest.raises(ReviewPacketError, match="ambiguous card id"):
        build_review_packet(config, CARD_ID)


def test_no_card_match_rejected(env: Env) -> None:
    config = env.write_config()
    _valid_card(env)

    with pytest.raises(ReviewPacketError, match="no card file matching"):
        build_review_packet(config, "S99")


def test_empty_commit_range_rejected(env: Env) -> None:
    config = env.write_config()
    _valid_card(env, commit_range=f"{env.last_sha}..{env.last_sha}")

    with pytest.raises(ReviewPacketError, match="contains no commits"):
        build_review_packet(config, CARD_ID)


def test_repo_path_not_a_directory_rejected(env: Env) -> None:
    config = env.write_config()
    _valid_card(env)
    missing = env.tmp_path / "nonexistent-repo"

    with pytest.raises(ReviewPacketError, match="does not exist; pass --repo"):
        build_review_packet(config, CARD_ID, repo=missing)


def test_repo_path_regular_file_rejected(env: Env) -> None:
    config = env.write_config()
    _valid_card(env)
    not_a_dir = env.tmp_path / "repo-as-file"
    not_a_dir.write_text("not a repo\n", encoding="utf-8")

    with pytest.raises(ReviewPacketError, match="does not exist; pass --repo"):
        build_review_packet(config, CARD_ID, repo=not_a_dir)


def test_cli_passes_suffix_through_to_the_output_dir(env: Env) -> None:
    from boardkit.cli import build_parser, cmd_review_packet

    env.write_config()
    _valid_card(env)
    args = build_parser().parse_args(
        [
            "--config",
            str(env.tmp_path / "boardkit.toml"),
            "review-packet",
            CARD_ID,
            "--suffix",
            "spike",
        ]
    )

    assert cmd_review_packet(args) == 0
    assert (env.output_dir / f"{CARD_ID}-spike" / "REVIEW.md").is_file()


def test_cli_reports_a_bad_suffix_as_an_error(env: Env) -> None:
    from boardkit.cli import build_parser, cmd_review_packet

    env.write_config()
    _valid_card(env)
    args = build_parser().parse_args(
        [
            "--config",
            str(env.tmp_path / "boardkit.toml"),
            "review-packet",
            CARD_ID,
            "--suffix",
            "Not A Slug",
        ]
    )

    assert cmd_review_packet(args) == 1
