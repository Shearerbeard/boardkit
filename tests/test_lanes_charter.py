"""Tests for R1 lanes and the R10 charter (S19/S20).

Lanes are opt-in per board: a vocabulary in config, validated on cards,
with per-lane WIP and exemption living in config rather than process
prose. The charter is an optional block whose `owns` line is mirrored
into the registry row and whose route targets must resolve to registry
short-codes.
"""

from pathlib import Path

import pytest
from conftest import config_text

from boardkit.board import BoardError, build_board
from boardkit.config import (
    board_row_errors,
    charter_route_errors,
    load_config,
)

LANES_BLOCK = """
[[board.lanes]]
name = "kit"
wip = 1

[[board.lanes]]
name = "docs"

[[board.lanes]]
name = "spike"
exempt = true
"""

CHARTER_BLOCK = """
[charter]
owns = "the kit family"
not = "consumer fixes"

[charter.route]
aura = "aura-family work"
"""


def _card(card_id: str, status: str = "ready", lane: str | None = None) -> str:
    lane_line = f"lane: {lane}\n" if lane else ""
    return (
        f"---\nid: {card_id}\ntitle: Card {card_id}\nstatus: {status}\n"
        f"depends: []\nserialize-with: []\nlineage: none\nexecutor: any\n"
        f'gates: "S -> A"\nuser-gates: []\n{lane_line}---\n\n'
        f"# {card_id}: Card {card_id}\n\n## Log\n\n- 2026-08-09 Minted.\n"
    )


def _board(tmp_path: Path, cards: dict[str, str], extra_config: str = "") -> Path:
    (tmp_path / "boardkit.toml").write_text(config_text() + extra_config, encoding="utf-8")
    cards_dir = tmp_path / "cards"
    cards_dir.mkdir(exist_ok=True)
    for name, text in cards.items():
        (cards_dir / name).write_text(text, encoding="utf-8")
    return tmp_path / "boardkit.toml"


def test_undeclared_lane_fails(tmp_path: Path) -> None:
    config_path = _board(
        tmp_path, {"s1-a.md": _card("S1", lane="rocketry")}, extra_config=LANES_BLOCK
    )
    with pytest.raises(BoardError, match="lane 'rocketry' not in board lanes"):
        build_board(load_config(config_path))


def test_lane_on_laneless_board_fails(tmp_path: Path) -> None:
    config_path = _board(tmp_path, {"s1-a.md": _card("S1", lane="kit")})
    with pytest.raises(BoardError, match="none declared"):
        build_board(load_config(config_path))


def test_per_lane_wip_cap(tmp_path: Path) -> None:
    cards = {
        "s1-a.md": _card("S1", status="in-progress", lane="kit"),
        "s2-b.md": _card("S2", status="in-progress", lane="kit"),
    }
    config_path = _board(tmp_path, cards, extra_config=LANES_BLOCK)
    with pytest.raises(BoardError, match="lane 'kit' WIP exceeded"):
        build_board(load_config(config_path))
    # Same two cards in different lanes pass.
    cards["s2-b.md"] = _card("S2", status="in-progress", lane="docs")
    config_path = _board(tmp_path, cards, extra_config=LANES_BLOCK)
    build_board(load_config(config_path))


def test_exempt_lane_skips_global_count_only(tmp_path: Path) -> None:
    # Two mainline cards sit at the global limit; a third in the exempt
    # spike lane must not trip it.
    cards = {
        "s1-a.md": _card("S1", status="in-progress", lane="kit"),
        "s2-b.md": _card("S2", status="in-progress", lane="docs"),
        "s3-c.md": _card("S3", status="in-progress", lane="spike"),
    }
    config_path = _board(tmp_path, cards, extra_config=LANES_BLOCK)
    build_board(load_config(config_path))
    # A fourth mainline card still trips the global limit.
    cards["s4-d.md"] = _card("S4", status="in-progress", lane="docs")
    config_path = _board(tmp_path, cards, extra_config=LANES_BLOCK)
    with pytest.raises(BoardError, match="WIP limit exceeded"):
        build_board(load_config(config_path))


def test_index_lane_column_is_opt_in(tmp_path: Path) -> None:
    config_path = _board(tmp_path, {"s1-a.md": _card("S1", lane="kit")}, LANES_BLOCK)
    result = build_board(load_config(config_path))
    assert "| Lane |" in result.views["INDEX.md"]
    assert "| kit |" in result.views["INDEX.md"]
    assert "Lane: kit." in result.views["board.md"]

    laneless = _board(tmp_path, {"s1-a.md": _card("S1")})
    result = build_board(load_config(laneless))
    assert "| Lane |" not in result.views["INDEX.md"]


def test_lane_declaration_validation_fails_loudly(tmp_path: Path) -> None:
    """S19 Gate A: every declaration branch refuses - missing name,
    duplicate name, bad wip, bad exempt, unknown key."""
    cases = {
        "[[board.lanes]]\nwip = 1\n": r"'name' must be a non-empty string",
        '[[board.lanes]]\nname = "kit"\n[[board.lanes]]\nname = "kit"\n': "duplicate lane",
        '[[board.lanes]]\nname = "kit"\nwip = -1\n': "'wip' must be a non-negative integer",
        '[[board.lanes]]\nname = "kit"\nwip = true\n': "'wip' must be a non-negative integer",
        '[[board.lanes]]\nname = "kit"\nexempt = "yes"\n': "'exempt' must be true or false",
        '[[board.lanes]]\nname = "kit"\ncolor = "red"\n': "unknown key",
    }
    for block, match in cases.items():
        config_path = _board(tmp_path, {}, "\n" + block)
        with pytest.raises(ValueError, match=match):
            load_config(config_path)


def test_charter_parses_and_renders_atop_views(tmp_path: Path) -> None:
    config_path = _board(tmp_path, {"s1-a.md": _card("S1")}, CHARTER_BLOCK)
    config = load_config(config_path)
    assert config.charter is not None
    assert config.charter.owns == "the kit family"
    assert config.charter.route == {"aura": "aura-family work"}
    result = build_board(config)
    index = result.views["INDEX.md"]
    assert "CHARTER - owns: the kit family" in index
    assert "Route aura -> aura-family work" in index
    assert index.index("CHARTER") < index.index("| ID |")
    assert "CHARTER - owns: the kit family" in result.views["board.md"]


def test_charter_missing_owns_fails(tmp_path: Path) -> None:
    bad = "\n[charter]\nnot = 'x'\n"
    config_path = _board(tmp_path, {}, bad)
    with pytest.raises(ValueError, match=r"\[charter\]: 'owns'"):
        load_config(config_path)


def test_charter_missing_route_fails(tmp_path: Path) -> None:
    """S20 Gate A: the charter schema is three keys; a missing route table
    would send a dispatch a refusal with no destination."""
    bad = "\n[charter]\nowns = 'x'\nnot = 'y'\n"
    config_path = _board(tmp_path, {}, bad)
    with pytest.raises(ValueError, match=r"\[charter\]: missing 'route'"):
        load_config(config_path)


def test_chartered_board_requires_the_scope_mirror(tmp_path: Path) -> None:
    """S20 Gate A: deleting the mirror is drift, not a pass."""
    config_path = _board(tmp_path, {"s1-a.md": _card("S1")}, CHARTER_BLOCK)
    config = load_config(config_path)
    bk = tmp_path / ".boardkit"
    bk.mkdir()
    (bk / "manifest.toml").write_text(
        'default = "bk"\n[boards.bk]\nlocation = "dir:."\n', encoding="utf-8"
    )
    errors = board_row_errors(config, tmp_path)
    assert any("no scope on the row" in e for e in errors)


def test_charter_route_errors_need_a_registry(tmp_path: Path) -> None:
    config_path = _board(tmp_path, {"s1-a.md": _card("S1")}, CHARTER_BLOCK)
    config = load_config(config_path)
    # No manifest anywhere: nothing to resolve against, charter stays prose.
    assert charter_route_errors(config, tmp_path) == []
    # A manifest without an aura row: the route target must fail.
    bk = tmp_path / ".boardkit"
    bk.mkdir()
    (bk / "manifest.toml").write_text(
        'default = "bk"\n[boards.bk]\nlocation = "dir:."\n', encoding="utf-8"
    )
    errors = charter_route_errors(config, tmp_path)
    assert len(errors) == 1
    assert "'aura' is not a registry short-code" in errors[0]


def test_charter_owns_mirror_must_match_registry_scope(tmp_path: Path) -> None:
    config_path = _board(tmp_path, {"s1-a.md": _card("S1")}, CHARTER_BLOCK)
    config = load_config(config_path)
    bk = tmp_path / ".boardkit"
    bk.mkdir()
    (bk / "manifest.toml").write_text(
        'default = "bk"\n[boards.bk]\nlocation = "dir:."\nscope = "something else"\n',
        encoding="utf-8",
    )
    errors = board_row_errors(config, tmp_path)
    assert any("charter `owns` mirror" in e for e in errors)
