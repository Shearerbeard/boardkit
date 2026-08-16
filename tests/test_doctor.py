"""Tests for `boardkit doctor`.

The quadrant matrix is the point: a cold-start diagnostic is only worth
running if every way an installation can be broken lands in a named cell
rather than a traceback or a silence. Each quadrant test asserts the check
id that should fire, not just that something failed.

The pure helpers are tested directly, because their failure mode is a false
positive on legitimate content - a template that says `timeout <seconds>`
reported as an unfilled placeholder - and that is cheapest to pin here.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import config_text

from boardkit.cli import INIT_CONFIG_TEMPLATE, cmd_doctor, cmd_init, cmd_render
from boardkit.contract import (
    BOARDKIT_HOME_VAR,
    CONTRACT_DOCS,
    CONTRACT_VERSION,
    JOB_WORKTREE_GLOB,
    TEMPLATES_DIR,
    missing_pin_sources,
    sections,
    slugify,
)
from boardkit.doctor import (
    BOARD_SKILLS,
    REQUIRED_FILL_SECTIONS,
    SKILL_METADATA_KEY,
    Severity,
    boardkit_home_finding,
    render_json,
    render_text,
    run_doctor,
    section_placeholders,
    skill_contract_version,
    stray_job_worktrees,
    unfilled_routes,
    unfilled_sections,
)

# The published contract of the JSON output. A rename here is a breaking
# change for anything parsing doctor, so the ids are pinned literally rather
# than imported from the module under test.
EXPECTED_CHECK_IDS = {
    "config.present",
    "config.repo-root",
    "contract.version-known",
    "config.loads",
    "docs.present",
    "contract.docs-stamped",
    "contract.skills-declared",
    "review-tooling.filled",
    "review-tooling.placeholders",
    "roles.filled",
    "routes.pin-source",
    "board.parses",
    "board.gate-vocabulary",
    "views.current",
    "host.base-branch",
    "host.tree-state",
    "env.boardkit-home",
    "skills.installed",
    "worktrees.stray",
    "entry.agents-stamp",
    "entry.parity",
}

REVIEW_TOOLING = Path("docs/board/REVIEW-TOOLING.md")


class _Args:
    def __init__(self, config: str | None = None, json: bool = False) -> None:
        self.config = config
        self.json = json


def _report(root: Path):
    return run_doctor(str(root / "boardkit.toml"), root)


def _checks(report, severity: Severity | None = None) -> set[str]:
    return {f.check for f in report.findings if severity is None or f.severity is severity}


def _fresh_board(tmp_path: Path) -> Path:
    assert cmd_init(_Args(config=str(tmp_path / "boardkit.toml"))) == 0
    return tmp_path


def _filled_board(tmp_path: Path) -> Path:
    """A fresh board with the two fill-in duties actually done."""
    root = _fresh_board(tmp_path)
    config = root / "boardkit.toml"
    config.write_text(
        config.read_text(encoding="utf-8")
        .replace('"<harness-name>"', '"test-harness"')
        .replace('"<working-dir or repo-native>"', '"working-dir"'),
        encoding="utf-8",
    )
    doc = root / REVIEW_TOOLING
    text = doc.read_text(encoding="utf-8")
    for heading in REQUIRED_FILL_SECTIONS:
        body = sections(text)[heading]
        text = text.replace(body, f"\n\nThis repo uses one transport for {heading}.\n\n", 1)
    doc.write_text(text, encoding="utf-8")
    return root


# --- the quadrant matrix ----------------------------------------------------


def test_empty_directory_reports_a_missing_config_and_skips_the_rest(tmp_path: Path) -> None:
    report = run_doctor(None, tmp_path)

    assert _checks(report, Severity.ERROR) == {"config.present"}
    assert report.contract_version is None
    # silence must not read as success: every other check is reported skipped
    assert {s.check for s in report.skipped} == EXPECTED_CHECK_IDS - {"config.present"}


def test_docs_without_a_config_still_names_the_config_quadrant(tmp_path: Path) -> None:
    (tmp_path / "docs" / "board").mkdir(parents=True)
    for name, dest in CONTRACT_DOCS:
        (tmp_path / dest).write_text(
            (TEMPLATES_DIR / name).read_text(encoding="utf-8"), encoding="utf-8"
        )

    report = run_doctor(None, tmp_path)

    assert _checks(report, Severity.ERROR) == {"config.present"}


def test_a_config_that_fails_to_load_is_a_finding_not_an_exception(tmp_path: Path) -> None:
    (tmp_path / "boardkit.toml").write_text(
        config_text().replace('id_prefix = "S"', "id_prefix = 7"), encoding="utf-8"
    )

    report = _report(tmp_path)

    assert _checks(report, Severity.ERROR) == {"config.loads"}
    assert "id_prefix" in report.findings[0].message


def test_a_config_that_is_not_valid_toml_is_a_finding(tmp_path: Path) -> None:
    (tmp_path / "boardkit.toml").write_text("[board\n", encoding="utf-8")

    report = _report(tmp_path)

    assert "config.loads" in _checks(report, Severity.ERROR)
    assert any(s.check == "contract.version-known" for s in report.skipped)


def test_a_pre_contract_config_reports_the_migration(tmp_path: Path) -> None:
    pre_contract = config_text().split("[contract]")[0]
    (tmp_path / "boardkit.toml").write_text(pre_contract, encoding="utf-8")

    report = _report(tmp_path)

    assert _checks(report, Severity.ERROR) == {"config.loads"}
    message = report.findings[0].message
    assert "predates delegation contract v2" in message
    assert "boardkit doctor" in message


def test_an_unknown_contract_version_is_named_rather_than_a_load_failure(tmp_path: Path) -> None:
    (tmp_path / "boardkit.toml").write_text(
        config_text().replace("version = 2", "version = 99"), encoding="utf-8"
    )

    report = _report(tmp_path)

    assert _checks(report, Severity.ERROR) == {"contract.version-known"}
    assert "99" in report.findings[0].message
    # the loader would also refuse; the specific quadrant wins and says why
    assert any(s.check == "config.loads" and "version" in s.reason for s in report.skipped)


def test_a_fresh_init_fails_on_unfilled_roles_and_sections(tmp_path: Path) -> None:
    """By design: init scaffolds placeholders rather than lying, so a fresh
    repo passes `check` and fails doctor until someone fills it in."""
    report = _report(_fresh_board(tmp_path))

    assert _checks(report, Severity.ERROR) == {
        "roles.filled",
        "review-tooling.filled",
        "review-tooling.placeholders",
    }
    assert "config.present" in report.passed
    assert "board.parses" in report.passed


def test_a_filled_board_reports_no_errors(tmp_path: Path) -> None:
    report = _report(_filled_board(tmp_path))

    assert report.errors == ()
    assert report.contract_version == CONTRACT_VERSION


def test_defined_gate_letters_pass_the_vocabulary_check(tmp_path: Path) -> None:
    report = _report(_filled_board(tmp_path))

    assert "board.gate-vocabulary" in report.passed


def test_an_undefined_gate_letter_warns_with_the_card_named(tmp_path: Path) -> None:
    root = _filled_board(tmp_path)
    template = root / "docs/board/cards/_template.md"
    card = root / "docs/board/cards/s1-undefined-gate.md"
    card.write_text(
        template.read_text(encoding="utf-8")
        .replace("id: SX", "id: S1")
        .replace('gates: "S -> A"', 'gates: "S -> A -> Z"'),
        encoding="utf-8",
    )

    report = _report(root)

    assert "board.gate-vocabulary" in _checks(report, Severity.WARN)
    finding = next(f for f in report.findings if f.check == "board.gate-vocabulary")
    assert "S1" in finding.message
    assert "Gate Z" in finding.message


def test_gate_vocabulary_skips_when_the_board_does_not_parse(tmp_path: Path) -> None:
    root = _filled_board(tmp_path)
    (root / "docs/board/cards/s1-broken.md").write_text("no frontmatter", encoding="utf-8")

    report = _report(root)

    assert any(s.check == "board.gate-vocabulary" for s in report.skipped)


# --- exit semantics ---------------------------------------------------------


def test_any_error_exits_one(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = _fresh_board(tmp_path)

    assert cmd_doctor(_Args(config=str(root / "boardkit.toml"))) == 1
    assert "FAIL:" in capsys.readouterr().out


def test_warnings_alone_exit_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _filled_board(tmp_path)
    monkeypatch.setenv(BOARDKIT_HOME_VAR, str(tmp_path / "not-where-boardkit-lives"))
    capsys.readouterr()  # drop what the scaffold printed

    assert cmd_doctor(_Args(config=str(root / "boardkit.toml"))) == 0

    out = capsys.readouterr().out
    assert "WARN: env.boardkit-home" in out
    footer = out.rstrip().splitlines()[-1]
    assert footer.startswith("OK: ")
    assert "0 error(s)" in footer


def test_json_output_carries_stable_check_ids(tmp_path: Path) -> None:
    root = _fresh_board(tmp_path)
    payload = json.loads(render_json(_report(root)))

    reported = (
        {f["check"] for f in payload["findings"]}
        | {s["check"] for s in payload["skipped"]}
        | set(payload["passed"])
    )
    assert reported == EXPECTED_CHECK_IDS
    assert payload["ok"] is False
    assert {f["severity"] for f in payload["findings"]} <= {"error", "warn"}


def test_every_check_is_accounted_for_in_every_quadrant(tmp_path: Path) -> None:
    """A check that neither passed, failed, nor was skipped is invisible."""
    for report in (run_doctor(None, tmp_path), _report(_fresh_board(tmp_path))):
        reported = _checks(report) | {s.check for s in report.skipped} | set(report.passed)
        assert reported == EXPECTED_CHECK_IDS


def test_text_output_names_the_check_and_a_remedy(tmp_path: Path) -> None:
    text = render_text(_report(_fresh_board(tmp_path)))

    assert "ERROR: roles.filled:" in text
    assert "  fix: " in text
    assert text.rstrip().endswith("skipped")


def test_report_names_the_resolution_step_that_won(tmp_path: Path) -> None:
    """S13 Gate A: the report says which selector chose the board, so a
    stale BOARDKIT_BOARD or overlay checkout cannot win silently."""
    root = _fresh_board(tmp_path)
    report = run_doctor(str(root / "boardkit.toml"), root, resolution_source="BOARDKIT_BOARD")
    assert report.resolution_source == "BOARDKIT_BOARD"
    assert "resolved via: BOARDKIT_BOARD" in render_text(report)
    # Absent a source, the line stays out rather than printing a blank.
    silent = run_doctor(str(root / "boardkit.toml"), root)
    assert "resolved via" not in render_text(silent)


# --- stamps and views -------------------------------------------------------


def test_a_docs_stamp_mismatch_is_an_error(tmp_path: Path) -> None:
    root = _filled_board(tmp_path)
    doc = root / "docs" / "board" / "PROCESS.md"
    doc.write_text(
        doc.read_text(encoding="utf-8").replace("boardkit-contract: v2", "boardkit-contract: v9"),
        encoding="utf-8",
    )

    report = _report(root)

    assert "contract.docs-stamped" in _checks(report, Severity.ERROR)
    assert "v9" in next(f for f in report.findings if f.check == "contract.docs-stamped").message


def test_an_absent_docs_stamp_is_an_error(tmp_path: Path) -> None:
    root = _filled_board(tmp_path)
    doc = root / "docs" / "board" / "MODEL-CLASSES.md"
    doc.write_text(
        doc.read_text(encoding="utf-8").replace("<!-- boardkit-contract: v2 -->\n", ""),
        encoding="utf-8",
    )

    report = _report(root)

    assert "contract.docs-stamped" in _checks(report, Severity.ERROR)
    assert "no contract stamp" in "".join(f.message for f in report.findings)


def test_a_missing_board_doc_is_an_error(tmp_path: Path) -> None:
    root = _filled_board(tmp_path)
    (root / "docs" / "board" / "PROCESS.md").unlink()

    report = _report(root)

    assert "docs.present" in _checks(report, Severity.ERROR)


def test_an_unstamped_entry_file_is_a_warning_not_an_error(tmp_path: Path) -> None:
    """Init leaves an existing AGENTS.md untouched, so an unstamped one is a
    merge the consumer still owes, not a broken installation."""
    root = _filled_board(tmp_path)
    (root / "AGENTS.md").write_text("# My own agent file\n", encoding="utf-8")

    report = _report(root)

    assert report.errors == ()
    assert "entry.agents-stamp" in _checks(report, Severity.WARN)


def _install_skill(root: Path, name: str, declared: int | None) -> Path:
    path = root / ".claude" / "skills" / name / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = "" if declared is None else f"metadata:\n  {SKILL_METADATA_KEY}: {declared}\n"
    path.write_text(f"---\nname: {name}\n{metadata}---\n\nbody\n", encoding="utf-8")
    return path


def test_installed_skills_declaring_the_contract_pass_both_checks(tmp_path: Path) -> None:
    root = _filled_board(tmp_path)
    for name in BOARD_SKILLS:
        _install_skill(root, name, CONTRACT_VERSION)

    report = run_doctor(str(root / "boardkit.toml"), root, home=tmp_path / "nonexistent-home")

    assert report.errors == ()
    assert "skills.installed" in report.passed
    assert "contract.skills-declared" in report.passed


def test_a_project_scoped_skill_counts_as_installed(tmp_path: Path) -> None:
    """The live consumer keeps board-hygiene in the repo, not the home dir; a
    search that misses project scope warns about a skill that is right there."""
    root = _filled_board(tmp_path)
    _install_skill(root, "board-hygiene", CONTRACT_VERSION)

    report = run_doctor(str(root / "boardkit.toml"), root, home=tmp_path / "nonexistent-home")

    warning = next(f for f in report.findings if f.check == "skills.installed")
    assert "board-hygiene" not in warning.message.split("(searched")[0]
    assert "delegating-work" in warning.message


def test_an_installed_skill_without_the_declaration_is_an_error(tmp_path: Path) -> None:
    root = _filled_board(tmp_path)
    for name in BOARD_SKILLS:
        _install_skill(root, name, None)

    report = run_doctor(str(root / "boardkit.toml"), root, home=tmp_path / "nonexistent-home")

    assert "contract.skills-declared" in _checks(report, Severity.ERROR)
    assert SKILL_METADATA_KEY in "".join(f.message for f in report.findings)


def test_an_installed_skill_declaring_another_version_is_an_error(tmp_path: Path) -> None:
    root = _filled_board(tmp_path)
    for name in BOARD_SKILLS:
        _install_skill(root, name, CONTRACT_VERSION + 8)

    report = run_doctor(str(root / "boardkit.toml"), root, home=tmp_path / "nonexistent-home")

    finding = next(f for f in report.findings if f.check == "contract.skills-declared")
    assert finding.severity is Severity.ERROR
    assert f"v{CONTRACT_VERSION + 8}" in finding.message


def test_the_searched_paths_are_listed_when_a_skill_is_absent(tmp_path: Path) -> None:
    root = _filled_board(tmp_path)

    report = run_doctor(str(root / "boardkit.toml"), root, home=tmp_path / "nonexistent-home")
    warning = next(f for f in report.findings if f.check == "skills.installed")

    assert str(root) in warning.message  # project scope names the real repo path
    for fragment in (".claude/skills", ".agents/skills", ".claude/plugins"):
        assert fragment in warning.message


def test_drifted_views_are_an_error(golden_board: Path) -> None:
    root = golden_board.parent
    assert cmd_render(_Args(config=str(golden_board))) == 0
    index = root / "cards" / "INDEX.md"
    index.write_text(index.read_text(encoding="utf-8") + "\nhand-edited\n", encoding="utf-8")

    report = run_doctor(str(golden_board), root)

    assert "views.current" in _checks(report, Severity.ERROR)


def test_an_unparseable_board_skips_the_view_check(tmp_path: Path) -> None:
    root = _filled_board(tmp_path)
    (root / "docs" / "board" / "cards" / "s1-broken.md").write_text(
        "---\nid: S1\n---\n\n# S1\n", encoding="utf-8"
    )

    report = _report(root)

    assert "board.parses" in _checks(report, Severity.ERROR)
    assert any(s.check == "views.current" for s in report.skipped)


# --- pure helpers -----------------------------------------------------------


def test_placeholder_scan_ignores_prose_outside_the_fill_in_sections() -> None:
    """`timeout <seconds>` in the stall protocol is legitimate template prose.
    A whole-file angle-bracket scan would report it; the scoped one must not."""
    shipped = (TEMPLATES_DIR / "REVIEW-TOOLING.md.template").read_text(encoding="utf-8")

    assert "timeout <seconds>" in shipped
    found = section_placeholders(shipped)
    assert "timeout <seconds>" not in str(found)
    assert set(found) <= set(REQUIRED_FILL_SECTIONS)


def test_placeholder_scan_ignores_commented_out_example_rows() -> None:
    """The shipped Harness bindings section carries a commented example row;
    a consumer who fills the section in may keep it, and it is not a hole."""
    text = "## Harness bindings\n\n<!-- | codex | a real row | -->\nFilled in.\n"

    assert section_placeholders(text, ("Harness bindings",)) == {}


def test_placeholder_scan_finds_real_holes() -> None:
    text = "## Harness bindings\n\n| harness | `<fill me>` |\n"

    assert section_placeholders(text, ("Harness bindings",)) == {"Harness bindings": ["<fill me>"]}


def test_unfilled_sections_matches_the_shipped_text_and_ignores_rewrapping() -> None:
    shipped = "## Harness bindings\n\nOne row per harness.\n"
    rewrapped = "## Harness bindings\n\nOne row\nper harness.\n"
    written = "## Harness bindings\n\nWe use opencode.\n"

    assert unfilled_sections(shipped, shipped, ("Harness bindings",)) == ["Harness bindings"]
    assert unfilled_sections(rewrapped, shipped, ("Harness bindings",)) == ["Harness bindings"]
    assert unfilled_sections(written, shipped, ("Harness bindings",)) == []


def test_unfilled_sections_reports_a_deleted_section() -> None:
    shipped = "## Harness bindings\n\nOne row per harness.\n"

    assert unfilled_sections("# Other\n", shipped, ("Harness bindings",)) == ["Harness bindings"]


def test_the_required_fill_sections_exist_in_the_shipped_template() -> None:
    """The headings are a contract with the shipped file; renaming one there
    would silently disable both review-tooling checks."""
    shipped = sections((TEMPLATES_DIR / "REVIEW-TOOLING.md.template").read_text(encoding="utf-8"))

    for heading in REQUIRED_FILL_SECTIONS:
        assert heading in shipped


def test_sections_runs_a_body_to_the_next_heading_of_the_same_level() -> None:
    text = "## A\n\nalpha\n\n### A1\n\nnested\n\n## B\n\nbeta\n"
    body = sections(text)

    assert "nested" in body["A"]
    assert "beta" not in body["A"]
    assert body["B"].strip() == "beta"


def test_unfilled_routes_names_the_placeholder_tokens(tmp_path: Path) -> None:
    from boardkit.config import load_config

    (tmp_path / "boardkit.toml").write_text(INIT_CONFIG_TEMPLATE, encoding="utf-8")
    contract = load_config(tmp_path / "boardkit.toml").contract

    assert unfilled_routes(contract) == {
        "primary": ["<harness-name>", "<working-dir or repo-native>"]
    }


def test_a_filled_route_has_no_placeholders(tmp_path: Path) -> None:
    from boardkit.config import load_config

    (tmp_path / "boardkit.toml").write_text(config_text(), encoding="utf-8")

    assert unfilled_routes(load_config(tmp_path / "boardkit.toml").contract) == {}


def test_missing_pin_sources_resolves_paths_and_anchors(tmp_path: Path) -> None:
    from boardkit.config import load_config

    (tmp_path / "boardkit.toml").write_text(config_text(), encoding="utf-8")
    contract = load_config(tmp_path / "boardkit.toml").contract

    assert [reason for _name, reason in missing_pin_sources(contract, tmp_path)] == [
        "pin_source path `docs/board/REVIEW-TOOLING.md` does not exist"
    ]

    doc = tmp_path / "docs" / "board" / "REVIEW-TOOLING.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("# Tooling\n\n## Something else\n\nbody\n", encoding="utf-8")
    problems = missing_pin_sources(contract, tmp_path)
    assert "matches no heading" in problems[0][1]

    doc.write_text("# Tooling\n\n## Harness bindings\n\nbody\n", encoding="utf-8")
    assert missing_pin_sources(contract, tmp_path) == []


def test_slugify_matches_the_anchor_form_pin_sources_use() -> None:
    assert slugify("Harness bindings") == "harness-bindings"
    assert slugify("Tools, in order of preference") == "tools-in-order-of-preference"


def test_stray_job_worktrees_parses_recorded_porcelain() -> None:
    porcelain = (
        "worktree /repo\nHEAD abc\nbranch refs/heads/main\n\n"
        "worktree /repo/.agy-mcp/worktrees/job-1a2b\nHEAD def\ndetached\n\n"
        "worktree /repo/.agy-mcp/worktrees/job-3c4d\nHEAD 012\ndetached\n\n"
        "worktree /repo/.claude/worktrees/feature\nHEAD 345\ndetached\n"
    )

    stray = stray_job_worktrees(porcelain)

    assert stray == ["/repo/.agy-mcp/worktrees/job-1a2b", "/repo/.agy-mcp/worktrees/job-3c4d"]
    assert JOB_WORKTREE_GLOB.rstrip("*") in stray[0]


def test_stray_job_worktrees_on_a_clean_repo_is_empty() -> None:
    assert stray_job_worktrees("worktree /repo\nHEAD abc\nbranch refs/heads/main\n") == []


def test_boardkit_home_finding_names_both_paths(tmp_path: Path) -> None:
    install = tmp_path / "boardkit"
    repo = tmp_path / "repo"
    elsewhere = tmp_path / "other-boardkit"

    finding = boardkit_home_finding(str(elsewhere), install, repo)

    assert finding is not None
    assert str(elsewhere) in finding.message
    assert str(install) in finding.message
    assert finding.severity is Severity.WARN


def test_boardkit_home_finding_is_silent_when_the_export_matches(tmp_path: Path) -> None:
    install = (tmp_path / "boardkit").resolve()
    install.mkdir()

    assert boardkit_home_finding(str(install), install, tmp_path / "repo") is None


def test_boardkit_home_finding_warns_when_the_default_would_miss(tmp_path: Path) -> None:
    """Unset is the silent case: the bootstrap resolves `../boardkit` and the
    operator never learns it reached a different checkout than they meant."""
    repo = tmp_path / "repo"
    install = tmp_path / "elsewhere" / "boardkit"

    finding = boardkit_home_finding(None, install, repo)

    assert finding is not None
    assert "../boardkit" in finding.message


def test_boardkit_home_finding_is_silent_when_the_default_is_right(tmp_path: Path) -> None:
    repo = (tmp_path / "repo").resolve()
    install = (tmp_path / "boardkit").resolve()

    assert boardkit_home_finding(None, install, repo) is None


def test_skill_contract_version_reads_the_frontmatter_declaration() -> None:
    text = "---\nname: board-hygiene\nmetadata:\n  boardkit-contract: 1\n---\n\nbody\n"

    assert skill_contract_version(text) == 1


def test_skill_contract_version_is_none_when_undeclared() -> None:
    assert skill_contract_version("---\nname: board-hygiene\n---\n\nbody\n") is None
    assert skill_contract_version("no frontmatter at all\n") is None
    assert skill_contract_version("---\nname: [unclosed\n---\n\nbody\n") is None


def test_a_v1_config_gets_the_staging_migration_remedy(tmp_path: Path) -> None:
    """The v1 -> v2 skew is an older config, not a newer kit; the remedy
    names the staging edit rather than telling the consumer to upgrade."""
    (tmp_path / "boardkit.toml").write_text(
        config_text().replace("version = 2", "version = 1"), encoding="utf-8"
    )

    report = run_doctor(str(tmp_path / "boardkit.toml"), tmp_path)

    finding = next(f for f in report.findings if f.check == "contract.version-known")
    assert "staging" in finding.remedy
    assert "version = 2" in finding.remedy
