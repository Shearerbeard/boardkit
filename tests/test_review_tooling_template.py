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
FIX_ROUND_SECTION_RE = re.compile(r"^## Fix-round packets\n(.*?)^## ", re.DOTALL | re.MULTILINE)
STALL_SECTION_RE = re.compile(r"^## Stall protocol\n(.*?)^## ", re.DOTALL | re.MULTILINE)


def _section(pattern: re.Pattern[str], name: str) -> str:
    """A named section, whitespace-collapsed: these tests bind the rules the
    section states, not the column the editor wrapped them at."""
    section = pattern.search(TEMPLATE.read_text(encoding="utf-8"))
    assert section, f"the template no longer has a {name} section"
    return " ".join(section.group(1).split())


def _transport_rule() -> str:
    return _section(TRANSPORT_SECTION_RE, "Transport rule")


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


def test_a_fix_round_gets_its_own_packet_directory() -> None:
    """A second `review-packet` run without `--suffix` overwrites the packet
    the first round was graded against, so the template has to name the flag
    and say what it protects."""
    text = _section(FIX_ROUND_SECTION_RE, "Fix-round packets")

    assert "--suffix" in text
    assert "reviews/<ID>-<name>" in text
    assert "overwrites" in text
    assert "--commit-range" in text


def test_the_verdict_is_read_from_the_reviewers_own_final_message() -> None:
    """A wrapper's zero exit reports delivery, not a verdict; reading one off
    the other has shipped a truncated run as a pass."""
    text = _section(STALL_SECTION_RE, "Stall protocol")

    assert "reviewer's own final message" in text
    assert "Never from the wrapper's exit code" in text
    assert "intermediate tool line" in text
    assert "tail states no explicit verdict is a failed review" in text


def test_the_harness_bindings_anchor_survives() -> None:
    """Route `pin_source` values point at this heading; renaming it breaks
    every board's contract without touching any board's config."""
    assert "## Harness bindings" in TEMPLATE.read_text(encoding="utf-8")
