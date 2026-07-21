"""Tests for boardkit.review_packet.

Builds a real throwaway git repo per test (no git mocking): a few commits
touching multiple files, one commit deleting a file, and one file changed
in enough scattered places to exceed MAX_HUNKS_PER_FILE. Cards and config
are written to tmp_path so the whole pipeline runs against real files.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

from boardkit.config import Config, load_config
from boardkit.review_packet import (
    MAX_HUNKS_PER_FILE,
    ReviewPacketError,
    build_review_packet,
)

CARD_ID = "S2"
# Lines in multi.txt that C1 rewrites; spaced apart so each is its own hunk
# under `git show --unified=0`, yielding more hunks than MAX_HUNKS_PER_FILE.
MULTI_CHANGED_LINES = (2, 6, 10, 14, 18, 22, 26)


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
    cards_dir: Path
    output_dir: Path
    base_sha: str
    mid_sha: str
    last_sha: str

    @property
    def range(self) -> str:
        return f"{self.base_sha}..{self.last_sha}"

    def write_card(self, name: str, frontmatter: str, body: str = "body\n") -> Path:
        path = self.cards_dir / name
        path.write_text(f"---\n{frontmatter}---\n\n{body}", encoding="utf-8")
        return path

    def write_config(self, repo_rel: str = "repo") -> Config:
        config_path = self.tmp_path / "boardkit.toml"
        config_path.write_text(
            "[board]\n"
            'cards_dir = "cards"\n'
            'id_prefix = "S"\n'
            'sentinel_ids = ["MILESTONE"]\n'
            "\n"
            "[review]\n"
            f'repo = "{repo_rel}"\n'
            'output_dir = "reviews"\n',
            encoding="utf-8",
        )
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
    # commit has more than MAX_HUNKS_PER_FILE hunks in that one file.
    for n in MULTI_CHANGED_LINES:
        multi_lines[n - 1] = f"CHANGED line {n}\n"
    (repo / "multi.txt").write_text("".join(multi_lines), encoding="utf-8")
    (repo / "other.txt").write_text("other rewritten\n", encoding="utf-8")
    mid_sha = _commit(repo, "C1 modify many files")

    # C2: delete a tracked file and modify another.
    (repo / "doomed.txt").unlink()
    (repo / "keep.txt").write_text("keep updated\n", encoding="utf-8")
    last_sha = _commit(repo, "C2 delete a file")

    decoy_repo = tmp_path / "decoy"
    _init_repo(decoy_repo)

    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()

    return Env(
        tmp_path=tmp_path,
        repo=repo,
        decoy_repo=decoy_repo,
        cards_dir=cards_dir,
        output_dir=tmp_path / "reviews",
        base_sha=base_sha,
        mid_sha=mid_sha,
        last_sha=last_sha,
    )


def _valid_card(env: Env, commit_range: str | None = None) -> None:
    rng = env.range if commit_range is None else commit_range
    env.write_card(
        "s2-example.md",
        f"id: {CARD_ID}\ntitle: Example card\ncommit-range: {rng}\n",
    )


def _multi_anchor_line(review: str) -> str:
    lines = [ln for ln in review.splitlines() if ln.startswith("- multi.txt:")]
    assert len(lines) == 1, f"expected one multi.txt anchor line, got {lines}"
    return lines[0]


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


def test_review_md_has_path_line_hunk_anchors(env: Env) -> None:
    config = env.write_config()
    _valid_card(env)

    build_review_packet(config, CARD_ID)
    review = (env.output_dir / CARD_ID / "REVIEW.md").read_text(encoding="utf-8")

    # other.txt is a single-hunk change in C1: anchor is path:new-side-line.
    assert "- other.txt:1" in review


def test_review_md_marks_deleted_file(env: Env) -> None:
    config = env.write_config()
    _valid_card(env)

    build_review_packet(config, CARD_ID)
    review = (env.output_dir / CARD_ID / "REVIEW.md").read_text(encoding="utf-8")

    assert "- doomed.txt (deleted)" in review


def test_hunk_pointers_capped_at_max(env: Env) -> None:
    config = env.write_config()
    _valid_card(env)

    build_review_packet(config, CARD_ID)
    review = (env.output_dir / CARD_ID / "REVIEW.md").read_text(encoding="utf-8")

    anchor_line = _multi_anchor_line(review)
    # The contract is five anchors: assert the literal cap, not the
    # constant, so a drive-by change to MAX_HUNKS_PER_FILE fails here.
    assert MAX_HUNKS_PER_FILE == 5
    assert anchor_line.count("multi.txt:") == 5
    for line_no in MULTI_CHANGED_LINES[:5]:
        assert f"multi.txt:{line_no}" in anchor_line
    for line_no in MULTI_CHANGED_LINES[5:]:
        assert f"multi.txt:{line_no}" not in anchor_line
    assert "(+2 more hunks)" in anchor_line


def test_output_dir_wiped_and_recreated_on_rerun(env: Env) -> None:
    config = env.write_config()
    _valid_card(env)

    outdir = build_review_packet(config, CARD_ID)
    stale = outdir / "stale.txt"
    stale.write_text("leftover\n", encoding="utf-8")

    outdir2 = build_review_packet(config, CARD_ID)

    assert outdir2 == outdir
    assert outdir.is_dir()
    assert not stale.exists()


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

    with pytest.raises(ReviewPacketError, match="not A..B hex"):
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
