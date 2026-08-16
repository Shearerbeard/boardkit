"""Tests for R2 epic cards and membership (S23), plus the post-R2 pass
that completes R9: epic clusters in graph.md and `dag --to <epic>`.
"""

from pathlib import Path

import pytest
from conftest import config_text

from boardkit.board import BoardError, build_board
from boardkit.config import load_config
from boardkit.dag import ancestor_closure, wave_partition


def _card(
    card_id: str,
    status: str = "ready",
    depends: str = "[]",
    kind: str | None = None,
    epic: str | None = None,
) -> str:
    kind_line = f"kind: {kind}\n" if kind else ""
    epic_line = f"epic: {epic}\n" if epic else ""
    return (
        f"---\nid: {card_id}\ntitle: Card {card_id}\nstatus: {status}\n"
        f"depends: {depends}\nserialize-with: []\nlineage: none\nexecutor: any\n"
        f'gates: "S -> A"\nuser-gates: []\n{kind_line}{epic_line}---\n\n'
        f"# {card_id}: Card {card_id}\n\n## Log\n\n- 2026-08-09 Minted.\n"
    )


def _board(tmp_path: Path, cards: dict[str, str]) -> Path:
    (tmp_path / "boardkit.toml").write_text(config_text(), encoding="utf-8")
    cards_dir = tmp_path / "cards"
    cards_dir.mkdir(exist_ok=True)
    for name, text in cards.items():
        (cards_dir / name).write_text(text, encoding="utf-8")
    return tmp_path / "boardkit.toml"


EPIC_BOARD = {
    "s1-epic.md": _card("S1", status="backlog", kind="epic"),
    "s2-a.md": _card("S2", status="done", epic="S1"),
    "s3-b.md": _card("S3", status="ready", depends="[S2]", epic="S1"),
    "s4-other.md": _card("S4"),
}


def test_epic_membership_validates(tmp_path: Path) -> None:
    build_board(load_config(_board(tmp_path, dict(EPIC_BOARD))))


def test_epic_ref_to_plain_card_fails(tmp_path: Path) -> None:
    cards = dict(EPIC_BOARD)
    cards["s3-b.md"] = _card("S3", epic="S4")  # S4 is kind card
    with pytest.raises(BoardError, match="is not an epic card"):
        build_board(load_config(_board(tmp_path, cards)))


def test_epic_ref_to_missing_card_fails(tmp_path: Path) -> None:
    cards = dict(EPIC_BOARD)
    cards["s3-b.md"] = _card("S3", epic="S9")
    with pytest.raises(BoardError, match="references unknown card 'S9'"):
        build_board(load_config(_board(tmp_path, cards)))


def test_non_string_kind_is_a_board_error(tmp_path: Path) -> None:
    """S23 Gate A: `kind: [epic]` is valid YAML and must be refused with a
    structured error, not a TypeError from hashing a list."""
    cards = {"s1-a.md": _card("S1", kind="[epic]")}
    with pytest.raises(BoardError, match="'kind' must be one of"):
        build_board(load_config(_board(tmp_path, cards)))


def test_done_epic_with_open_members_fails(tmp_path: Path) -> None:
    """S23 Gate A: finishing an epic means finishing its members (the dag
    closure rule); done-with-open-members would render the initiative as
    complete and incomplete at once."""
    cards = {
        "s1-epic.md": _card("S1", status="done", kind="epic"),
        "s2-a.md": _card("S2", status="done", epic="S1"),
        "s3-b.md": _card("S3", status="ready", depends="[S2]", epic="S1"),
    }
    with pytest.raises(BoardError, match="epic is done but member"):
        build_board(load_config(_board(tmp_path, cards)))


def test_epic_may_not_be_a_member(tmp_path: Path) -> None:
    cards = dict(EPIC_BOARD)
    cards["s5-nested.md"] = _card("S5", kind="epic", epic="S1")
    with pytest.raises(BoardError, match="an epic card may not carry 'epic'"):
        build_board(load_config(_board(tmp_path, cards)))


def test_index_rollup_names_members_and_progress(tmp_path: Path) -> None:
    result = build_board(load_config(_board(tmp_path, dict(EPIC_BOARD))))
    index = result.views["INDEX.md"]
    assert "## Epics" in index
    assert "1/2 done" in index
    assert "S2 (done), S3 (ready)" in index
    assert "S4" not in index.split("## Epics")[1]  # non-members stay out


def test_graph_clusters_epic_with_members(tmp_path: Path) -> None:
    result = build_board(load_config(_board(tmp_path, dict(EPIC_BOARD))))
    graph = result.views["graph.md"]
    assert 'subgraph epic_S1["epic: S1"]' in graph
    cluster = graph.split("subgraph epic_S1")[1].split("end")[0]
    assert "S2" in cluster and "S3" in cluster
    assert "S4" not in cluster


def test_dag_to_epic_closes_over_members(tmp_path: Path) -> None:
    result = build_board(load_config(_board(tmp_path, dict(EPIC_BOARD))))
    cards = {card["id"]: card for card in result.cards}
    closure = ancestor_closure(cards, "S1")
    assert closure == {"S1", "S2", "S3"}
    waves = wave_partition(cards, closure)
    assert waves == [["S1", "S3"]]  # S2 done; epic + unblocked member remain
