"""Bind the REVIEW-TOOLING template's transport rules to what doctor checks.

Both rules here come from a recorded burn: a metered review harness driven
as a shell proxy through a retry loop, which spent a weekly budget, returned
no verdict, and left a dozen registered worktrees behind. The stray-worktree
path is a shared constant because doctor's `worktrees.stray` warning has to
look for the same thing the prose tells the reader to clean up.
"""

from __future__ import annotations

import re

from boardkit.contract import JOB_WORKTREE_GLOB, TEMPLATES_DIR

TEMPLATE = TEMPLATES_DIR / "REVIEW-TOOLING.md.template"

TRANSPORT_SECTION_RE = re.compile(r"^## Transport rule\n(.*?)^## ", re.DOTALL | re.MULTILINE)


def _transport_rule() -> str:
    """The Transport rule section, whitespace-collapsed: these tests bind the
    rules the section states, not the column the editor wrapped them at."""
    section = TRANSPORT_SECTION_RE.search(TEMPLATE.read_text(encoding="utf-8"))
    assert section, "the template no longer has a Transport rule section"
    return " ".join(section.group(1).split())


def test_metered_reviewer_is_reserved_for_language_shaped_review() -> None:
    text = _transport_rule()

    assert "reserved for language-shaped review" in text
    assert "never a deterministic shell proxy" in text


def test_metered_reviewer_is_not_a_permission_workaround() -> None:
    """The remedy for a reviewer that cannot read a path is a staged packet;
    without saying so here, the retry loop looks like the cheaper option."""
    text = _transport_rule()

    assert "permission failure" in text
    assert "staged packet" in text


def test_repeated_dispatch_attempts_are_capped() -> None:
    text = _transport_rule()

    assert "at three" in text
    assert "executor-fallback rule" in text


def test_session_close_accounts_for_delegated_worktrees() -> None:
    text = _transport_rule()

    assert JOB_WORKTREE_GLOB in text, "the stray-worktree path drifted from the constant"
    assert "git worktree remove" in text
    assert "Session close accounts for every worktree" in text


def test_the_harness_bindings_anchor_survives() -> None:
    """Route `pin_source` values point at this heading; renaming it breaks
    every board's contract without touching any board's config."""
    assert "## Harness bindings" in TEMPLATE.read_text(encoding="utf-8")
