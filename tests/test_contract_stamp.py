"""Every shipped doc declares the contract version it was written against.

The stamp is what makes a skew detectable: a consumer repo scaffolded at v1
and a kit that has moved to v2 look identical on disk without it. These
tests are also the restamp checklist - bumping `CONTRACT_VERSION` fails once
per file that still carries the old stamp, so the bump names its own work.
"""

from __future__ import annotations

import pytest

from boardkit.contract import (
    BOARD_DOCS,
    CONTRACT_VERSION,
    DATA_DIR,
    ENTRY_SHIMS,
    TEMPLATES_DIR,
    read_stamp,
)

CARD_TEMPLATE = DATA_DIR / "_template.md"
STAMPED_TEMPLATES = [name for name, _dest in (*BOARD_DOCS, *ENTRY_SHIMS)]


@pytest.mark.parametrize("name", STAMPED_TEMPLATES)
def test_shipped_template_is_stamped_at_the_current_version(name: str) -> None:
    stamp = read_stamp((TEMPLATES_DIR / name).read_text(encoding="utf-8"))

    assert stamp is not None, f"{name} carries no boardkit-contract stamp"
    assert stamp == CONTRACT_VERSION, f"{name} is stamped v{stamp}; restamp it"


def test_the_card_template_is_deliberately_unstamped() -> None:
    """Consumers copy this file into their own cards; a stamp would travel
    into every card and start lying the first time the contract moves."""
    assert read_stamp(CARD_TEMPLATE.read_text(encoding="utf-8")) is None


def test_read_stamp_returns_none_on_unstamped_text() -> None:
    assert read_stamp("# Process\n\nNo stamp here.\n") is None
    assert read_stamp("") is None


def test_read_stamp_reads_either_comment_syntax() -> None:
    assert read_stamp("<!-- boardkit-contract: v1 -->") == 1
    assert read_stamp("#!/bin/sh\n# boardkit-contract: v2\n") == 2
