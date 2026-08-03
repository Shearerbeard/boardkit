"""Bind the PROCESS template's prose to the validator's constants.

The template restates rules that `board.py` enforces: the WIP limit, the
status vocabulary, the lineage vocabulary. Nothing stopped one side from
moving without the other, so a repo could ship a document that contradicts
its own validator. These tests fail when either side moves alone.
"""

from __future__ import annotations

import re
from pathlib import Path

from boardkit.board import LINEAGES, SIDE_QUEST_KEY, STATUSES, WIP_LIMIT

TEMPLATE = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "boardkit"
    / "data"
    / "templates"
    / "PROCESS.md"
)
NUMBER_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}

WIP_RE = re.compile(r"at most (\w+) cards `in-progress`")
WIP_BULLET_RE = re.compile(r"^- WIP limit:.*?(?=^- )", re.DOTALL | re.MULTILINE)
STATUS_SECTION_RE = re.compile(r"Statuses and their lifecycle:\n(.*?)\n## ", re.DOTALL)
STATUS_BULLET_RE = re.compile(r"^- `([a-z-]+)`:", re.MULTILINE)
LINEAGE_BULLET_RE = re.compile(r"^- `lineage`:(.*?)(?=^- `)", re.DOTALL | re.MULTILINE)
BACKTICKED_RE = re.compile(r"`([a-z-]+)`")
ROLES_SECTION_RE = re.compile(r"^## Roles\n(.*?)^## ", re.DOTALL | re.MULTILINE)
SESSION_CLOSE_SECTION_RE = re.compile(r"^## Session close\n(.*?)^#{2,3} ", re.DOTALL | re.MULTILINE)


def _template_text() -> str:
    return TEMPLATE.read_text(encoding="utf-8")


def _section(pattern: re.Pattern[str], name: str) -> str:
    """A named section, whitespace-collapsed, so re-wrapping is not a failure."""
    section = pattern.search(_template_text())
    assert section, f"the template no longer has a {name} section"
    return " ".join(section.group(1).split())


def test_template_states_the_enforced_wip_limit() -> None:
    found = WIP_RE.findall(_template_text())

    assert found, "the template no longer states the WIP limit in the bound phrasing"
    assert set(found) == {NUMBER_WORDS[WIP_LIMIT]}


def test_template_names_the_wip_exemption_key_the_validator_honors() -> None:
    """The exemption is only auditable if the document names the flag that
    carries it, and says the flag follows the user's declaration."""
    text = _template_text()
    bullet = WIP_BULLET_RE.search(text)
    assert bullet, "the template no longer has a WIP-limit bullet"

    assert f"`{SIDE_QUEST_KEY}: true`" in bullet.group(0)
    assert "on the user's" in bullet.group(0)
    assert f"- `{SIDE_QUEST_KEY}`:" in text, "the frontmatter field list omits the key"


def test_template_defines_exactly_the_valid_statuses() -> None:
    section = STATUS_SECTION_RE.search(_template_text())
    assert section, "the template no longer has a 'Statuses and their lifecycle' list"

    documented = STATUS_BULLET_RE.findall(section.group(1))

    assert set(documented) == set(STATUSES)
    assert len(documented) == len(STATUSES), "a status is documented twice"


def test_template_defines_exactly_the_valid_lineages() -> None:
    bullet = LINEAGE_BULLET_RE.search(_template_text())
    assert bullet, "the template no longer has a `lineage` frontmatter bullet"

    documented = set(BACKTICKED_RE.findall(bullet.group(1)))

    assert documented == LINEAGES


def test_template_states_the_card_commit_trailer_the_packet_tells_users_to_grep() -> None:
    """`review_packet` points a stuck board owner at `git log --grep '^Card:
    <ID>$'`; that search only works if the process establishes the trailer."""
    text = _template_text()

    assert "`Card: <ID>` trailer" in text
    assert "--grep '^Card: <ID>$'" in text


def test_session_close_states_the_card_read_back_duty() -> None:
    """A card edit that reports success can still fail to persist. The duty
    belongs to session close, where the commit and the gate both happen."""
    section = _section(SESSION_CLOSE_SECTION_RE, "Session close")

    assert "read the card file back" in section
    assert "before committing" in section
    assert "before presenting any gate" in section


def test_dispatch_brief_names_the_role_and_pin_source_not_a_model() -> None:
    """A model id copied into a brief goes stale, and a stale one can name
    the model that authored the diff it is dispatched to review."""
    section = _section(ROLES_SECTION_RE, "Roles")

    assert "never names a model id" in section
    assert "pin source" in section
    assert "at dispatch time" in section
