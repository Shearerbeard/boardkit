"""Machine-facing references in the review-tooling template."""

from boardkit.contract import JOB_WORKTREE_GLOB, TEMPLATES_DIR

TEMPLATE = TEMPLATES_DIR / "REVIEW-TOOLING.md.template"


def test_cleanup_names_the_worktrees_doctor_detects() -> None:
    assert JOB_WORKTREE_GLOB in TEMPLATE.read_text(encoding="utf-8")


def test_the_harness_bindings_anchor_survives() -> None:
    assert "## Harness bindings" in TEMPLATE.read_text(encoding="utf-8").splitlines()
