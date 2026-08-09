"""Tests for the R9 dag queries and the standing graph view (S22).

Fixture DAG: S1 (done) -> S2 (in-review, Gate A unticked) -> S4 (backlog);
S3 (ready, no deps) -> S4. S5 is disconnected and must stay out of S4's
closure. Gates-on-edges: the S2->S4 edge carries S2's remaining letters.
"""

from pathlib import Path

from conftest import config_text

from boardkit.board import build_board, remaining_gates
from boardkit.config import load_config
from boardkit.dag import (
    ancestor_closure,
    closure_edges,
    render_dag_mermaid,
    unblocked_frontier,
    wave_partition,
)


def _card(
    card_id: str,
    status: str,
    depends: str = "[]",
    checklist: str = "- [ ] Gate S: checks.\n- [ ] Gate A: review.",
    lane: str | None = None,
) -> str:
    lane_line = f"lane: {lane}\n" if lane else ""
    return (
        f"---\nid: {card_id}\ntitle: Card {card_id}\nstatus: {status}\n"
        f"depends: {depends}\nserialize-with: []\nlineage: none\nexecutor: any\n"
        f'gates: "S -> A"\nuser-gates: []\n{lane_line}---\n\n'
        f"# {card_id}: Card {card_id}\n\n## Gate checklist\n\n{checklist}\n\n"
        f"## Log\n\n- 2026-08-09 Minted.\n"
    )


def _board(tmp_path: Path, extra_config: str = "") -> dict[str, dict]:
    (tmp_path / "boardkit.toml").write_text(config_text() + extra_config, encoding="utf-8")
    cards_dir = tmp_path / "cards"
    cards_dir.mkdir(exist_ok=True)
    ticked = "- [x] Gate S: checks.\n- [x] Gate A: review."
    half = "- [x] Gate S: checks.\n- [ ] Gate A: review."
    (cards_dir / "s1-a.md").write_text(_card("S1", "done", checklist=ticked), encoding="utf-8")
    (cards_dir / "s2-b.md").write_text(
        _card("S2", "in-review", depends="[S1]", checklist=half), encoding="utf-8"
    )
    (cards_dir / "s3-c.md").write_text(_card("S3", "ready"), encoding="utf-8")
    (cards_dir / "s4-d.md").write_text(
        _card("S4", "backlog", depends="[S2, S3]"), encoding="utf-8"
    )
    (cards_dir / "s5-e.md").write_text(_card("S5", "ready"), encoding="utf-8")
    result = build_board(load_config(tmp_path / "boardkit.toml"))
    return {card["id"]: card for card in result.cards}


def test_ancestor_closure_excludes_disconnected_cards(tmp_path: Path) -> None:
    cards = _board(tmp_path)
    assert ancestor_closure(cards, "S4") == {"S1", "S2", "S3", "S4"}


def test_frontier_needs_all_deps_done(tmp_path: Path) -> None:
    cards = _board(tmp_path)
    closure = ancestor_closure(cards, "S4")
    # S2 waits on nothing (S1 done); S3 has no deps; S4 waits on S2.
    assert unblocked_frontier(cards, closure) == ["S2", "S3"]


def test_wave_partition_layers_remaining_work(tmp_path: Path) -> None:
    cards = _board(tmp_path)
    waves = wave_partition(cards, ancestor_closure(cards, "S4"))
    assert waves == [["S2", "S3"], ["S4"]]  # S1 is done: no wave


def test_gates_on_edges_carry_the_tails_remaining_letters(tmp_path: Path) -> None:
    cards = _board(tmp_path)
    assert remaining_gates(cards["S2"]) == ["A"]
    edges = closure_edges(cards, ancestor_closure(cards, "S4"))
    by_pair = {(dep, cid): gates for dep, cid, gates in edges}
    assert by_pair[("S2", "S4")] == "A"  # Gate S ticked, A open
    assert by_pair[("S1", "S2")] == ""  # done dependency: no gate labels
    assert by_pair[("S3", "S4")] == "S,A"  # untouched ladder


def test_mermaid_wave_plan_shapes(tmp_path: Path) -> None:
    cards = _board(tmp_path)
    rendered = render_dag_mermaid(cards, "S4")
    assert 'subgraph wave1["wave 1"]' in rendered
    assert 'S2 -->|"A"| S4' in rendered
    assert "S1 --> S2" in rendered  # done dep: unlabeled edge
    assert "S5" not in rendered  # goal-scoped: disconnected card stays out


def test_graph_view_renders_and_drift_checks(tmp_path: Path) -> None:
    lanes = '\n[[board.lanes]]\nname = "kit"\n'
    (tmp_path / "boardkit.toml").write_text(config_text() + lanes, encoding="utf-8")
    cards_dir = tmp_path / "cards"
    cards_dir.mkdir(exist_ok=True)
    (cards_dir / "s1-a.md").write_text(_card("S1", "ready", lane="kit"), encoding="utf-8")
    (cards_dir / "s2-b.md").write_text(_card("S2", "backlog", depends="[S1]"), encoding="utf-8")
    result = build_board(load_config(tmp_path / "boardkit.toml"))
    graph = result.views["graph.md"]
    assert 'subgraph lane_kit["kit"]' in graph
    assert "S1 --> S2" in graph
    assert ":::ready" in graph and ":::backlog" in graph
    assert "graph.md" in result.views  # standing view, always rendered
