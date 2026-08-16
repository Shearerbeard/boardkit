"""Tests for the R6 host-repo hazard checks and the R7 parity check (S24).

Real git repos, tiny and local: the checks under test exist because of
real hosts (a board on a feature branch, a dirty wiki with unpushed
commits), so the fixtures reproduce those shapes rather than mocking git.
"""

import subprocess
from pathlib import Path

from conftest import config_text

from boardkit.config import load_config
from boardkit.doctor import _check_entry_parity, _check_host, _Checks

IDENTITY = ["-c", "user.email=t@t", "-c", "user.name=t"]


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(cwd), *IDENTITY, *args], check=True, capture_output=True)


def _repo(tmp_path: Path, base_branch: str | None = None) -> Path:
    tmp_path.mkdir(exist_ok=True)
    extra = f'base_branch = "{base_branch}"\n' if base_branch else ""
    config = config_text().replace("[review]", extra + "[review]", 1)
    (tmp_path / "boardkit.toml").write_text(config, encoding="utf-8")
    (tmp_path / "cards").mkdir(exist_ok=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "seed")
    return tmp_path


def _findings(checks: _Checks) -> dict[str, str]:
    return {f.check: f.message for f in checks.findings}


def test_base_branch_mismatch_warns(tmp_path: Path) -> None:
    repo = _repo(tmp_path, base_branch="main")
    _git(repo, "checkout", "-q", "-b", "feature/side")
    checks = _Checks()
    _check_host(checks, load_config(repo / "boardkit.toml"))
    assert "not the declared base 'main'" in _findings(checks)["host.base-branch"]


def test_base_branch_undeclared_is_a_skip_not_a_pass(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    checks = _Checks()
    _check_host(checks, load_config(repo / "boardkit.toml"))
    assert any(s.check == "host.base-branch" for s in checks.skipped)
    assert "host.base-branch" not in checks.passed


def test_dirty_tree_and_missing_upstream_warn(tmp_path: Path) -> None:
    # A clean repo with no upstream is still local-only state (S24 Gate A):
    # the branch - and the board on it - exists on this machine alone.
    repo = _repo(tmp_path, base_branch="main")
    checks = _Checks()
    _check_host(checks, load_config(repo / "boardkit.toml"))
    assert "no upstream" in _findings(checks)["host.tree-state"]
    (repo / "scratch.txt").write_text("x", encoding="utf-8")
    checks = _Checks()
    _check_host(checks, load_config(repo / "boardkit.toml"))
    assert "dirty tree" in _findings(checks)["host.tree-state"]


def test_unpushed_commits_warn_and_pushed_clean_passes(tmp_path: Path) -> None:
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)
    repo = _repo(tmp_path / "work")
    _git(repo, "remote", "add", "origin", str(origin))
    _git(repo, "push", "-q", "-u", "origin", "main")
    checks = _Checks()
    _check_host(checks, load_config(repo / "boardkit.toml"))
    assert "host.tree-state" in checks.passed
    _git(repo, "commit", "-q", "--allow-empty", "-m", "local only")
    checks = _Checks()
    _check_host(checks, load_config(repo / "boardkit.toml"))
    assert "1 unpushed commit(s)" in _findings(checks)["host.tree-state"]


def test_parity_shim_layout_passes(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# Agent instructions\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("Read `AGENTS.md` first.\n", encoding="utf-8")
    checks = _Checks()
    _check_entry_parity(checks, tmp_path)
    assert "entry.parity" in checks.passed


def test_parity_divergent_full_text_warns(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# Agent instructions\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("# Totally different rules\n", encoding="utf-8")
    checks = _Checks()
    _check_entry_parity(checks, tmp_path)
    assert "follow different rules" in _findings(checks)["entry.parity"]


def test_parity_absent_agents_and_absent_everything_warn(tmp_path: Path) -> None:
    checks = _Checks()
    _check_entry_parity(checks, tmp_path)
    assert "every harness runs blind" in _findings(checks)["entry.parity"]
    (tmp_path / "CLAUDE.md").write_text("# Rules\n", encoding="utf-8")
    checks = _Checks()
    _check_entry_parity(checks, tmp_path)
    assert "AGENTS.md does not" in _findings(checks)["entry.parity"]


def test_parity_agents_with_no_shims_warns(tmp_path: Path) -> None:
    """S24 Gate A: an AGENTS.md nothing points at leaves single-entry-file
    harnesses blind, which is not parity."""
    (tmp_path / "AGENTS.md").write_text("# Agent instructions\n", encoding="utf-8")
    checks = _Checks()
    _check_entry_parity(checks, tmp_path)
    assert "no shim points at it" in _findings(checks)["entry.parity"]


def test_parity_shimlike_opening_with_own_rules_warns(tmp_path: Path) -> None:
    """S24 Gate A: mentioning AGENTS.md once does not make a divergent
    entry file a shim."""
    (tmp_path / "AGENTS.md").write_text("# Agent instructions\n", encoding="utf-8")
    body = "Read `AGENTS.md` first.\n\n" + "\n".join(
        f"- extra local rule {n} that AGENTS.md does not carry" for n in range(12)
    )
    (tmp_path / "CLAUDE.md").write_text(body, encoding="utf-8")
    checks = _Checks()
    _check_entry_parity(checks, tmp_path)
    assert "follow different rules" in _findings(checks)["entry.parity"]


def test_parity_resolves_the_host_root_above_a_docked_board(tmp_path: Path) -> None:
    """S24 Gate A: for a .boardkit/boards/<code> layout the entry files
    live at the host repo root, not the board root."""
    host = _repo(tmp_path)
    (host / "AGENTS.md").write_text("# Agent instructions\n", encoding="utf-8")
    (host / "CLAUDE.md").write_text("Read `AGENTS.md` first.\n", encoding="utf-8")
    board_root = host / ".boardkit" / "boards" / "bk"
    board_root.mkdir(parents=True)
    checks = _Checks()
    _check_entry_parity(checks, board_root)
    assert "entry.parity" in checks.passed
