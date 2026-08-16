from pathlib import Path

import pytest
from conftest import config_text

from boardkit.board import BoardError, build_board
from boardkit.config import load_config

CARD_FRONTMATTER = """---
id: {id}
title: {title}
status: {status}
depends: {depends}
serialize-with: {serialize_with}
lineage: {lineage}
executor: any
gates: "S -> A"
user-gates: []
{extra}---

# {id}: {title}
"""


def _write_card(cards_dir: Path, filename: str, **fields) -> None:
    values = {
        "depends": "[]",
        "serialize_with": "[]",
        "lineage": "none",
        "extra": "",
        **fields,
    }
    text = CARD_FRONTMATTER.format(**values)
    (cards_dir / filename).write_text(text, encoding="utf-8")


def test_ready_with_unfinished_dependency_fails(tmp_path: Path) -> None:
    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()
    (tmp_path / "boardkit.toml").write_text(config_text(), encoding="utf-8")

    _write_card(cards_dir, "s1-base.md", id="S1", title="Base", status="backlog", depends="[]")
    _write_card(
        cards_dir,
        "s2-dependent.md",
        id="S2",
        title="Dependent",
        status="ready",
        depends="[S1]",
    )

    config = load_config(tmp_path / "boardkit.toml")
    with pytest.raises(BoardError) as excinfo:
        build_board(config)

    assert any("ready but dependency S1 is backlog" in e for e in excinfo.value.errors)


def test_dependency_cycle_detected(tmp_path: Path) -> None:
    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()
    (tmp_path / "boardkit.toml").write_text(config_text(), encoding="utf-8")

    _write_card(cards_dir, "s1-a.md", id="S1", title="A", status="backlog", depends="[S2]")
    _write_card(cards_dir, "s2-b.md", id="S2", title="B", status="backlog", depends="[S1]")

    config = load_config(tmp_path / "boardkit.toml")
    with pytest.raises(BoardError) as excinfo:
        build_board(config)

    assert any("dependency cycle" in e for e in excinfo.value.errors)


def test_regex_metacharacters_in_id_scheme_are_literal(tmp_path: Path) -> None:
    from boardkit.board import card_file_pattern, card_id_pattern

    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()
    (tmp_path / "boardkit.toml").write_text(
        config_text(id_prefix="S."), encoding="utf-8"
    )
    config = load_config(tmp_path / "boardkit.toml")

    # "S." must match only a literal "S." prefix, never "SX" via the dot wildcard
    assert not card_id_pattern(config).match("SX1")
    assert card_id_pattern(config).match("S.1")
    assert not card_file_pattern(config).match("sx1-thing.md")
    assert card_file_pattern(config).match("s.1-thing.md")


def test_wip_limit_enforced(tmp_path: Path) -> None:
    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()
    (tmp_path / "boardkit.toml").write_text(config_text(), encoding="utf-8")
    for n in (1, 2, 3):
        _write_card(
            cards_dir, f"s{n}-c{n}.md", id=f"S{n}", title=f"C{n}", status="in-progress"
        )

    config = load_config(tmp_path / "boardkit.toml")
    with pytest.raises(BoardError) as excinfo:
        build_board(config)

    assert any("WIP limit exceeded" in e for e in excinfo.value.errors)


def test_side_quest_card_does_not_count_toward_wip(tmp_path: Path) -> None:
    """PROCESS.md board mechanics: a flow the user declares a detached side
    quest is exempt from the WIP limit, so its cards do not count."""
    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()
    (tmp_path / "boardkit.toml").write_text(config_text(), encoding="utf-8")
    for n in (1, 2):
        _write_card(
            cards_dir, f"s{n}-c{n}.md", id=f"S{n}", title=f"C{n}", status="in-progress"
        )
    _write_card(
        cards_dir,
        "s3-c3.md",
        id="S3",
        title="C3",
        status="in-progress",
        extra="side-quest: true\n",
    )

    result = build_board(load_config(tmp_path / "boardkit.toml"))

    assert [c["id"] for c in result.cards] == ["S1", "S2", "S3"]


def test_side_quest_cards_still_count_once_they_exceed_the_limit_themselves(
    tmp_path: Path,
) -> None:
    """The exemption removes side-quest cards from the count; it does not
    disable the limit for the mainline cards that remain."""
    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()
    (tmp_path / "boardkit.toml").write_text(config_text(), encoding="utf-8")
    for n in (1, 2, 3):
        _write_card(
            cards_dir, f"s{n}-c{n}.md", id=f"S{n}", title=f"C{n}", status="in-progress"
        )
    _write_card(
        cards_dir,
        "s4-c4.md",
        id="S4",
        title="C4",
        status="in-progress",
        extra="side-quest: true\n",
    )

    with pytest.raises(BoardError) as excinfo:
        build_board(load_config(tmp_path / "boardkit.toml"))

    errors = [e for e in excinfo.value.errors if "WIP limit exceeded" in e]
    assert len(errors) == 1
    assert "S4" not in errors[0]


def test_side_quest_must_be_a_boolean(tmp_path: Path) -> None:
    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()
    (tmp_path / "boardkit.toml").write_text(config_text(), encoding="utf-8")
    _write_card(
        cards_dir,
        "s1-a.md",
        id="S1",
        title="A",
        status="in-progress",
        extra="side-quest: yes please\n",
    )

    with pytest.raises(BoardError) as excinfo:
        build_board(load_config(tmp_path / "boardkit.toml"))

    assert any("'side-quest' must be true or false" in e for e in excinfo.value.errors)


def test_side_quest_card_still_obeys_the_serialize_mutex(tmp_path: Path) -> None:
    """The template's exemption covers the WIP count only; it says nothing
    about shared files, so two serialized cards still may not run together."""
    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()
    (tmp_path / "boardkit.toml").write_text(config_text(), encoding="utf-8")
    _write_card(
        cards_dir, "s1-a.md", id="S1", title="A", status="in-progress",
        serialize_with="[S2]",
    )
    _write_card(
        cards_dir, "s2-b.md", id="S2", title="B", status="in-progress",
        serialize_with="[S1]", extra="side-quest: true\n",
    )

    with pytest.raises(BoardError) as excinfo:
        build_board(load_config(tmp_path / "boardkit.toml"))

    assert any("both in-progress" in e for e in excinfo.value.errors)


def test_serialized_cards_may_not_both_be_in_progress(tmp_path: Path) -> None:
    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()
    (tmp_path / "boardkit.toml").write_text(config_text(), encoding="utf-8")
    _write_card(
        cards_dir, "s1-a.md", id="S1", title="A", status="in-progress",
        serialize_with="[S2]",
    )
    _write_card(
        cards_dir, "s2-b.md", id="S2", title="B", status="in-progress",
        serialize_with="[S1]",
    )

    config = load_config(tmp_path / "boardkit.toml")
    with pytest.raises(BoardError) as excinfo:
        build_board(config)

    conflicts = [e for e in excinfo.value.errors if "both in-progress" in e]
    assert len(conflicts) == 1  # reported once per pair, not once per card


def test_in_review_lineage_card_requires_commit_range(tmp_path: Path) -> None:
    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()
    (tmp_path / "boardkit.toml").write_text(config_text(), encoding="utf-8")
    _write_card(
        cards_dir, "s1-a.md", id="S1", title="A", status="in-review",
        lineage="accepted-head",
    )

    config = load_config(tmp_path / "boardkit.toml")
    with pytest.raises(BoardError) as excinfo:
        build_board(config)

    assert any("no commit-range" in e for e in excinfo.value.errors)


def test_unquoted_hash_title_refuses_instead_of_truncating(tmp_path: Path) -> None:
    """R8: YAML comment parsing eats everything after an unquoted ' #'."""
    (tmp_path / "boardkit.toml").write_text(config_text(), encoding="utf-8")
    cards = tmp_path / "cards"
    cards.mkdir()
    card = (
        "---\nid: S1\ntitle: Record the #398 follow-up\nstatus: ready\n"
        "depends: []\nserialize-with: []\nlineage: none\nexecutor: any\n"
        'gates: "S -> A"\nuser-gates: []\n---\n\n# S1: Record the\n\n## Log\n\n- x.\n'
    )
    (cards / "s1-a.md").write_text(card, encoding="utf-8")
    with pytest.raises(BoardError, match="quote the whole title"):
        build_board(load_config(tmp_path / "boardkit.toml"))

    quoted = card.replace(
        "title: Record the #398 follow-up", 'title: "Record the #398 follow-up"'
    )
    (cards / "s1-a.md").write_text(quoted, encoding="utf-8")
    result = build_board(load_config(tmp_path / "boardkit.toml"))
    assert "Record the #398 follow-up" in result.views["INDEX.md"]

    # YAML tolerates a space before the colon; the guard must too, or the
    # spelling slips past it and truncates anyway.
    spaced = card.replace(
        "title: Record the #398 follow-up", "title : Record the #398 follow-up"
    )
    (cards / "s1-a.md").write_text(spaced, encoding="utf-8")
    with pytest.raises(BoardError, match="quote the whole title"):
        build_board(load_config(tmp_path / "boardkit.toml"))

    # A uniformly indented frontmatter block is valid YAML; the guard must
    # still see its title line.
    body_start = card.index("---\n", 4)
    front = "".join("  " + line + "\n" for line in card[4:body_start].splitlines())
    indented = "---\n" + front + card[body_start:]
    (cards / "s1-a.md").write_text(indented, encoding="utf-8")
    with pytest.raises(BoardError, match="quote the whole title"):
        build_board(load_config(tmp_path / "boardkit.toml"))

    # An anchored quoted title parses intact and must not be refused.
    anchored = card.replace(
        "title: Record the #398 follow-up",
        'title: &t "Record the #398 follow-up"',
    )
    (cards / "s1-a.md").write_text(anchored, encoding="utf-8")
    result = build_board(load_config(tmp_path / "boardkit.toml"))
    assert "Record the #398 follow-up" in result.views["INDEX.md"]


def test_gate_position_renders_for_active_cards(tmp_path: Path) -> None:
    """S16: the views carry each active card's parked gate; backlog and
    done render the bare ladder; the canary key uses the same computation."""
    (tmp_path / "boardkit.toml").write_text(config_text(), encoding="utf-8")
    cards = tmp_path / "cards"
    cards.mkdir()

    def card(cid: str, status: str, checklist: str) -> str:
        return (
            f"---\nid: {cid}\ntitle: Card {cid}\nstatus: {status}\n"
            "depends: []\nserialize-with: []\nlineage: none\nexecutor: any\n"
            'gates: "S -> A -> U"\nuser-gates: [review]\n---\n\n'
            f"# {cid}: Card {cid}\n\n## Gate checklist\n\n{checklist}\n\n"
            "## Log\n\n- 2026-08-09 x.\n"
        )

    half = "- [x] Gate S: checks.\n- [x] Gate A: review.\n- [ ] Gate U: stop."
    fresh = "- [ ] Gate S: checks.\n- [ ] Gate A: review.\n- [ ] Gate U: stop."
    (cards / "s1-a.md").write_text(card("S1", "in-review", half), encoding="utf-8")
    (cards / "s2-b.md").write_text(card("S2", "backlog", fresh), encoding="utf-8")
    from boardkit.board import render_canary_key, view_drift  # noqa: F401

    result = build_board(load_config(tmp_path / "boardkit.toml"))
    index = result.views["INDEX.md"]
    assert "S -> A -> U @ U |" in index  # S and A ticked: parked at U
    assert "| backlog | - | any | S -> A -> U |" in index  # bare ladder
    assert "Gates: S -> A -> U @ U." in result.views["board.md"]

    key = render_canary_key(result, drift=[])
    assert "(at Gate U)" in key.split("## In Review")[1].split("##")[0]


def test_missing_box_for_duplicate_gate_letter_stays_open(tmp_path: Path) -> None:
    """S16 Gate A: a qualified gate whose checklist box was never written
    must not be absorbed by a ticked sibling of the same letter."""
    (tmp_path / "boardkit.toml").write_text(config_text(), encoding="utf-8")
    cards = tmp_path / "cards"
    cards.mkdir()
    checklist = "- [x] Gate U (mockup): shown.\n- [x] Gate S: checks."
    card = (
        "---\nid: S1\ntitle: Card S1\nstatus: in-review\n"
        "depends: []\nserialize-with: []\nlineage: none\nexecutor: any\n"
        'gates: "U(mockup) -> S -> U(launch)"\nuser-gates: [mockup, launch]\n---\n\n'
        f"# S1: Card S1\n\n## Gate checklist\n\n{checklist}\n\n"
        "## Log\n\n- 2026-08-09 x.\n"
    )
    (cards / "s1-a.md").write_text(card, encoding="utf-8")

    result = build_board(load_config(tmp_path / "boardkit.toml"))
    # The launch U has no box: the position parks at U, never "all ticked".
    assert "U(mockup) -> S -> U(launch) @ U |" in result.views["INDEX.md"]
