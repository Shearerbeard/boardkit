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


def test_the_suffix_packet_is_subordinate_to_the_full_range_re_review_duty() -> None:
    """The hazard this section has to avoid teaching: a fix round reviewed on
    a suffixed packet alone, leaving the fix commits outside the card's
    durable reviewed range. The section names the PROCESS duty it defers to
    and says the supplement never replaces the full-range packet."""
    text = _section(FIX_ROUND_SECTION_RE, "Fix-round packets")

    assert "fix-commit re-review duty in `PROCESS.md` governs every fix round" in text
    assert "`commit-range` extends over the fix commit" in text
    assert "primary packet regenerates over the full range" in text
    assert "packet built on the fix diff alone is never the packet a gate is graded on" in text
    assert "`--suffix` supplements the duty" in text
    assert "extended range and its full-range packet are owed either way" in text


def test_the_suffix_packet_keeps_the_current_re_reviews_packet_intact() -> None:
    """The hazard is against the packet in play now: the mandatory full-range
    regeneration has already replaced the one the previous round read, so an
    unsuffixed supplementary run clobbers the current re-review's packet."""
    text = _section(FIX_ROUND_SECTION_RE, "Fix-round packets")

    assert "reviews/<ID>-<name>" in text
    assert "leaves `reviews/<ID>` untouched" in text
    assert "overwrites the packet the current re-review is reading" in text
    assert "--commit-range" in text


def test_the_fix_round_section_honors_the_packet_retention_contract() -> None:
    """`PROCESS.md` holds that a packet is regenerable working material and the
    cards and logs are the durable record. A section that calls any packet the
    record contradicts it, so pin the deference and the absence together."""
    text = _section(FIX_ROUND_SECTION_RE, "Fix-round packets")

    assert "Both are regenerable working material" in text
    assert "the card and its log hold the durable record" in text
    assert "retention contract in `PROCESS.md`" in text
    assert "packet stays the record" not in text


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
