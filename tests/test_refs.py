"""Tests for R3 qualified cross-board references (S21).

Refs are informational: shape is validated at parse, the short-code and
prefix scheme resolve against the registry in `check`, and nothing about
a ref ever feeds readiness or the WIP rules.
"""

from pathlib import Path

import pytest
from conftest import config_text

from boardkit.board import BoardError, build_board
from boardkit.config import card_ref_findings, load_config


def _card(card_id: str, refs: str | None = None, status: str = "ready") -> str:
    refs_line = f"refs: {refs}\n" if refs else ""
    return (
        f"---\nid: {card_id}\ntitle: Card {card_id}\nstatus: {status}\n"
        f"depends: []\nserialize-with: []\nlineage: none\nexecutor: any\n"
        f'gates: "S -> A"\nuser-gates: []\n{refs_line}---\n\n'
        f"# {card_id}: Card {card_id}\n\n## Log\n\n- 2026-08-09 Minted.\n"
    )


def _board(tmp_path: Path, cards: dict[str, str]) -> Path:
    (tmp_path / "boardkit.toml").write_text(config_text(), encoding="utf-8")
    cards_dir = tmp_path / "cards"
    cards_dir.mkdir(exist_ok=True)
    for name, text in cards.items():
        (cards_dir / name).write_text(text, encoding="utf-8")
    return tmp_path / "boardkit.toml"


def _manifest(repo: Path, body: str) -> None:
    bk = repo / ".boardkit"
    bk.mkdir(exist_ok=True)
    (bk / "manifest.toml").write_text(body, encoding="utf-8")


TWO_BOARDS = (
    'default = "bk"\n'
    '[boards.bk]\nlocation = "dir:."\n'
    '[boards.tb]\nlocation = "external"\nid_prefix = "S"\nengine = "boardkit-v1"\n'
    'scope = "terminalbench"\n'
)


def test_unqualified_ref_shape_fails_at_parse(tmp_path: Path) -> None:
    config_path = _board(tmp_path, {"s1-a.md": _card("S1", refs="[S91]")})
    with pytest.raises(BoardError, match="not a qualified <code>/<id> reference"):
        build_board(load_config(config_path))


def test_ref_to_unknown_board_is_an_error(tmp_path: Path) -> None:
    config_path = _board(tmp_path, {"s1-a.md": _card("S1", refs="[cl/S6]")})
    _manifest(tmp_path, TWO_BOARDS)
    cards = build_board(load_config(config_path)).cards
    errors, _warnings = card_ref_findings(cards, tmp_path)
    assert len(errors) == 1
    assert "unknown board 'cl'" in errors[0]


def test_ref_prefix_mismatch_and_unreachable_are_warnings(tmp_path: Path) -> None:
    config_path = _board(tmp_path, {"s1-a.md": _card("S1", refs="[tb/W4, tb/S91]")})
    _manifest(tmp_path, TWO_BOARDS)
    cards = build_board(load_config(config_path)).cards
    errors, warnings = card_ref_findings(cards, tmp_path)
    assert errors == []
    # tb is unresolvable here, so its sentinels are unknowable and W4
    # stays a warning rather than a blind judgment.
    assert any("prefix scheme" in w and "tb/W4" in w for w in warnings)
    # tb is external with no overlay on this machine: warn, never error.
    assert any("does not resolve" in w for w in warnings)


def test_resolvable_board_sentinels_split_error_from_pass(tmp_path: Path) -> None:
    """S21 Gate A: where the target board's own config is readable, a
    non-prefix id is judged against its declared sentinels - a sentinel
    passes clean, anything else is the prefix-mismatch error."""
    config_path = _board(
        tmp_path, {"s1-a.md": _card("S1", refs="[bk/MILESTONE, bk/W4]")}
    )
    _manifest(tmp_path, TWO_BOARDS)
    cards = build_board(load_config(config_path)).cards
    errors, warnings = card_ref_findings(cards, tmp_path)
    assert any("neither" in e and "bk/W4" in e for e in errors)
    assert not any("bk/MILESTONE" in e for e in errors)
    assert not any("bk/MILESTONE" in w for w in warnings)


def test_refs_never_affect_readiness(tmp_path: Path) -> None:
    config_path = _board(tmp_path, {"s1-a.md": _card("S1", refs="[tb/S91]")})
    _manifest(tmp_path, TWO_BOARDS)
    result = build_board(load_config(config_path))
    assert result.cards[0]["status"] == "ready"


def test_refs_without_registry_fail_loudly(tmp_path: Path) -> None:
    """S21 Gate A: resolution goes through the registry, so a card that
    carries refs with no registry reachable is an error, never a pass."""
    config_path = _board(tmp_path, {"s1-a.md": _card("S1", refs="[tb/S91]")})
    cards = build_board(load_config(config_path)).cards
    errors, warnings = card_ref_findings(cards, tmp_path)
    assert warnings == []
    assert len(errors) == 1
    assert "carry refs but no .boardkit/manifest.toml is reachable" in errors[0]
    assert "s1-a.md" in errors[0]
