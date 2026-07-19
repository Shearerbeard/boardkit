from pathlib import Path

import pytest

from boardkit.board import BoardError, build_board
from boardkit.config import load_config

CONFIG_TEXT = """
[board]
cards_dir = "cards"
id_prefix = "S"
sentinel_ids = ["MILESTONE"]

[review]
repo = "."
output_dir = "reviews"
"""

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
---

# {id}: {title}
"""


def _write_card(cards_dir: Path, filename: str, **fields) -> None:
    values = {
        "depends": "[]",
        "serialize_with": "[]",
        "lineage": "none",
        **fields,
    }
    text = CARD_FRONTMATTER.format(**values)
    (cards_dir / filename).write_text(text, encoding="utf-8")


def test_ready_with_unfinished_dependency_fails(tmp_path: Path) -> None:
    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()
    (tmp_path / "boardkit.toml").write_text(CONFIG_TEXT, encoding="utf-8")

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
    (tmp_path / "boardkit.toml").write_text(CONFIG_TEXT, encoding="utf-8")

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
        CONFIG_TEXT.replace('id_prefix = "S"', 'id_prefix = "S."'), encoding="utf-8"
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
    (tmp_path / "boardkit.toml").write_text(CONFIG_TEXT, encoding="utf-8")
    for n in (1, 2, 3):
        _write_card(
            cards_dir, f"s{n}-c{n}.md", id=f"S{n}", title=f"C{n}", status="in-progress"
        )

    config = load_config(tmp_path / "boardkit.toml")
    with pytest.raises(BoardError) as excinfo:
        build_board(config)

    assert any("WIP limit exceeded" in e for e in excinfo.value.errors)


def test_serialized_cards_may_not_both_be_in_progress(tmp_path: Path) -> None:
    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()
    (tmp_path / "boardkit.toml").write_text(CONFIG_TEXT, encoding="utf-8")
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
    (tmp_path / "boardkit.toml").write_text(CONFIG_TEXT, encoding="utf-8")
    _write_card(
        cards_dir, "s1-a.md", id="S1", title="A", status="in-review",
        lineage="accepted-head",
    )

    config = load_config(tmp_path / "boardkit.toml")
    with pytest.raises(BoardError) as excinfo:
        build_board(config)

    assert any("no commit-range" in e for e in excinfo.value.errors)
