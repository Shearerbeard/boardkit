"""Tests for `boardkit dispatch-brief`.

The brief's value is that it restates nothing: every clause is extracted
from the repo's own docs at generation time. So the tests that matter are
the extraction ones - a moved anchor must fail loudly rather than produce a
brief that quietly lost a clause - and the determinism ones, because a brief
that changes between runs cannot be diffed or digest-checked.

The whole-output pin is deliberate. A brief is read by an agent about to
spend a card's worth of work; a wording drift is a behavior change.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from conftest import config_text

from boardkit.brief import (
    DECISION_AUTHORITY_ANCHOR,
    DISPATCH_BRIEF_ANCHOR,
    GATE_A_ROUTING_ANCHOR,
    BriefError,
    build_brief,
    gate_tokens,
    reference_links,
)
from boardkit.config import load_config
from boardkit.contract import CONTRACT_DOCS, STAGING_CONTRACTS, TEMPLATES_DIR, contract_digest

CARD = """\
---
id: S1
title: Build the widget
status: ready
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [U]
---

# S1: Build the widget

Build it per [the spec](../spec.md), then check [the spec](../spec.md) again.

## Gate checklist

- [ ] Gate S: tests pass.
"""


def _board(tmp_path: Path, card: str = CARD) -> Path:
    """A minimal but real board: contract docs copied from the kit templates."""
    (tmp_path / "boardkit.toml").write_text(
        config_text(cards_dir="docs/board/cards"), encoding="utf-8"
    )
    cards = tmp_path / "docs" / "board" / "cards"
    cards.mkdir(parents=True)
    for template, dest in CONTRACT_DOCS:
        shutil.copyfile(TEMPLATES_DIR / template, tmp_path / dest)
    (tmp_path / "docs" / "board" / "spec.md").write_text("# Spec\n", encoding="utf-8")
    (cards / "s1-widget.md").write_text(card, encoding="utf-8")
    return tmp_path / "boardkit.toml"


def _brief(tmp_path: Path, card: str = CARD, card_id: str = "S1") -> str:
    return build_brief(load_config(_board(tmp_path, card)), card_id)


# --- structure --------------------------------------------------------------


def test_header_names_every_source_the_brief_drew_from(tmp_path: Path) -> None:
    text = _brief(tmp_path)

    assert "# Dispatch brief: S1 — Build the widget" in text
    assert "- card: `docs/board/cards/s1-widget.md`" in text
    assert "- contract: v2" in text
    assert "`boardkit.toml`" in text
    for _template, dest in CONTRACT_DOCS:
        assert f"`{dest.as_posix()}`" in text


def test_the_card_is_embedded_verbatim(tmp_path: Path) -> None:
    """The card is the specification; a summarized card is a different card."""
    text = _brief(tmp_path)

    assert CARD.rstrip("\n") in text
    assert "```markdown\n---\nid: S1" in text


def test_reference_links_are_repo_relative_and_deduped(tmp_path: Path) -> None:
    text = _brief(tmp_path)

    assert "- `docs/board/spec.md`" in text
    assert text.count("- `docs/board/spec.md`") == 1  # the card links to it twice
    assert "../spec.md`" not in text.split("## Routes")[0].split("## Reference")[1]


def test_a_card_without_links_says_so(tmp_path: Path) -> None:
    linkless = "\n".join(
        line for line in CARD.splitlines(keepends=True) if "../spec.md" not in line
    )
    text = _brief(tmp_path, linkless)

    assert "The card links to no reference material." in text


def test_both_gate_a_roles_print_with_the_routing_rule(tmp_path: Path) -> None:
    """A card records no artifact kind, so the brief cannot pick between the
    two Gate A roles; it prints both and quotes the rule for choosing."""
    text = _brief(tmp_path)

    assert "- **code-review** -> `primary`" in text
    assert "- **prose-review** -> `primary`" in text
    assert GATE_A_ROUTING_ANCHOR in text


def test_the_executor_route_always_prints(tmp_path: Path) -> None:
    text = _brief(tmp_path, CARD.replace('gates: "S -> A -> U(code-review)"', 'gates: "S -> U"'))

    assert "- **executor** -> `primary`" in text
    assert "- **code-review**" not in text


def test_only_declared_gates_are_quoted(tmp_path: Path) -> None:
    text = _brief(tmp_path)

    assert "> - Gate S, self:" in text
    assert "> - Gate A, agent:" in text
    assert "> - Gate U, user:" in text
    assert "> - Gate F, frontier review:" not in text
    assert "> - Gate D, drift audit:" not in text


def test_a_gate_bullet_stops_at_the_next_section(tmp_path: Path) -> None:
    """Gate U is the last bullet in the Gates section; without a heading
    boundary its quote swallows the Deferrals subsection wholesale."""
    text = _brief(tmp_path)

    assert "Deferrals" not in text.split("## Provenance")[0].split("## Contract clauses")[1]


def test_both_process_clauses_are_quoted(tmp_path: Path) -> None:
    text = _brief(tmp_path)

    assert DISPATCH_BRIEF_ANCHOR in text
    assert DECISION_AUTHORITY_ANCHOR in text


def test_the_provenance_footer_says_to_regenerate(tmp_path: Path) -> None:
    text = _brief(tmp_path)

    assert "Regenerate this brief rather than editing it" in text
    assert "boardkit doctor" in text


# --- determinism and digest -------------------------------------------------


def test_the_brief_carries_no_timestamp(tmp_path: Path) -> None:
    """A timestamp would make every regeneration a diff, and a diff nobody
    reads is a diff that hides a real change."""
    import datetime

    text = _brief(tmp_path)
    today = datetime.date.today()

    assert str(today.year) not in text
    assert today.isoformat() not in text


def test_two_runs_over_an_unchanged_board_are_byte_identical(tmp_path: Path) -> None:
    config = load_config(_board(tmp_path))

    assert build_brief(config, "S1") == build_brief(config, "S1")


def test_the_whole_output_is_pinned(tmp_path: Path) -> None:
    """A byte pin over the assembled shape: headings, order, and the parts
    the brief builds itself (as opposed to the parts it quotes)."""
    text = _brief(tmp_path)
    config = load_config(tmp_path / "boardkit.toml")
    digest = contract_digest(config)

    head, _, _ = text.partition("## Contract clauses")
    assert head == (
        f"# Dispatch brief: S1 — Build the widget\n"
        f"\n"
        f"- card: `docs/board/cards/s1-widget.md`\n"
        f"- contract: v2\n"
        f"- digest: `{digest}`\n"
        f"- sources: `boardkit.toml`, `docs/board/PROCESS.md`, "
        f"`docs/board/MODEL-CLASSES.md`, `docs/board/REVIEW-TOOLING.md`\n"
        f"\n"
        f"## Card\n"
        f"\n"
        f"The card, verbatim. It is the specification; nothing below overrides it.\n"
        f"\n"
        f"```markdown\n"
        f"{CARD.rstrip()}\n"
        f"```\n"
        f"\n"
        f"## Reference material\n"
        f"\n"
        f"Read these rather than a summary of them:\n"
        f"\n"
        f"- `docs/board/spec.md`\n"
        f"\n"
        f"## Routes\n"
        f"\n"
        f"- **executor** -> `primary`\n"
        f"  - adapter: `test-harness`\n"
        f"  - skill: none (this transport loads no child skill)\n"
        f"  - pin source: `docs/board/REVIEW-TOOLING.md#harness-bindings`\n"
        f"  - staging: `working-dir` - {STAGING_CONTRACTS['working-dir']}\n"
        f"  - preflight: none\n"
        f"- **code-review** -> `primary`\n"
        f"  - adapter: `test-harness`\n"
        f"  - skill: none (this transport loads no child skill)\n"
        f"  - pin source: `docs/board/REVIEW-TOOLING.md#harness-bindings`\n"
        f"  - staging: `working-dir` - {STAGING_CONTRACTS['working-dir']}\n"
        f"  - preflight: none\n"
        f"- **prose-review** -> `primary`\n"
        f"  - adapter: `test-harness`\n"
        f"  - skill: none (this transport loads no child skill)\n"
        f"  - pin source: `docs/board/REVIEW-TOOLING.md#harness-bindings`\n"
        f"  - staging: `working-dir` - {STAGING_CONTRACTS['working-dir']}\n"
        f"  - preflight: none\n"
        f"\n"
        f"> - {GATE_A_ROUTING_ANCHOR}: a code diff goes\n"
        f">   to the `code-review` role, a plan, spec, or prose artifact goes to the\n"
        f">   `prose-review` role. A card carries no field recording which kind it\n"
        f">   produced, so the board owner decides at the gate; a dispatch brief prints\n"
        f">   both routes rather than guessing on the board owner's behalf.\n"
        f"\n"
    )


def test_the_digest_is_stable_across_runs(tmp_path: Path) -> None:
    config = load_config(_board(tmp_path))

    assert contract_digest(config) == contract_digest(config)
    assert len(contract_digest(config)) == 12


def test_the_digest_changes_when_a_contract_doc_changes(tmp_path: Path) -> None:
    config = load_config(_board(tmp_path))
    before = contract_digest(config)

    process = tmp_path / "docs" / "board" / "PROCESS.md"
    process.write_text(process.read_text(encoding="utf-8") + "\nA new rule.\n", encoding="utf-8")

    assert contract_digest(config) != before


def test_the_digest_changes_when_a_route_changes(tmp_path: Path) -> None:
    config_path = _board(tmp_path)
    before = contract_digest(load_config(config_path))

    config_path.write_text(
        config_path.read_text(encoding="utf-8").replace('"test-harness"', '"other-harness"'),
        encoding="utf-8",
    )

    assert contract_digest(load_config(config_path)) != before


def test_the_digest_changes_when_a_role_reorders_its_fallbacks(tmp_path: Path) -> None:
    """Route order inside a role is the fallback order, so it is contract."""
    config_path = _board(tmp_path)
    text = config_path.read_text(encoding="utf-8")
    text = text.replace(
        "[routes.primary]",
        '[routes.secondary]\nadapter = "second"\nskill = ""\n'
        'pin_source = "docs/board/REVIEW-TOOLING.md#harness-bindings"\npreflight = []\n'
        'staging = "working-dir"\n\n'
        "[routes.primary]",
        1,
    )
    forward = text.replace(
        '[roles.code-review]\nroutes = ["primary"]',
        '[roles.code-review]\nroutes = ["primary", "secondary"]',
    )
    backward = text.replace(
        '[roles.code-review]\nroutes = ["primary"]',
        '[roles.code-review]\nroutes = ["secondary", "primary"]',
    )

    config_path.write_text(forward, encoding="utf-8")
    first = contract_digest(load_config(config_path))
    config_path.write_text(backward, encoding="utf-8")

    assert contract_digest(load_config(config_path)) != first


def test_the_digest_separates_contracts_that_differ_only_by_a_delimiter(
    tmp_path: Path,
) -> None:
    """Route values are free strings, so a delimiter-joined serialization can
    collide: `preflight = ["a|b"]` and `["a", "b"]` are different contracts
    that a `|`-join renders identically. The digest must tell them apart."""
    config_path = _board(tmp_path)
    original = config_path.read_text(encoding="utf-8")

    config_path.write_text(original.replace("preflight = []", 'preflight = ["a|b"]'), "utf-8")
    joined = contract_digest(load_config(config_path))

    config_path.write_text(original.replace("preflight = []", 'preflight = ["a", "b"]'), "utf-8")
    split = contract_digest(load_config(config_path))

    assert joined != split


def test_the_digest_separates_a_value_that_impersonates_a_field_separator(
    tmp_path: Path,
) -> None:
    """A forward guard, not a historical failure: this particular pair did not
    collide under the old delimiter join. It pins the general property, that a
    route value cannot forge the serialization's own structure."""
    config_path = _board(tmp_path)
    original = config_path.read_text(encoding="utf-8")

    config_path.write_text(
        original.replace('adapter = "test-harness"', 'adapter = "a\\tskill=b"'), "utf-8"
    )
    injected = contract_digest(load_config(config_path))

    config_path.write_text(original.replace('adapter = "test-harness"', 'adapter = "a"'), "utf-8")
    plain = contract_digest(load_config(config_path))

    assert injected != plain


def test_the_digest_ignores_the_order_routes_are_declared_in(tmp_path: Path) -> None:
    """Table order is layout, not contract; only a role's fallback list is."""
    config_path = _board(tmp_path)
    second = (
        '[routes.secondary]\nadapter = "second"\nskill = ""\n'
        'pin_source = "docs/board/REVIEW-TOOLING.md#harness-bindings"\npreflight = []\n'
        'staging = "working-dir"\n'
    )
    original = config_path.read_text(encoding="utf-8")
    head, _, tail = original.partition("[routes.primary]")
    primary, _, roles = tail.partition("[roles.executor]")

    primary_first = f"{head}[routes.primary]{primary}{second}\n[roles.executor]{roles}"
    secondary_first = f"{head}{second}\n[routes.primary]{primary}[roles.executor]{roles}"

    config_path.write_text(primary_first, "utf-8")
    first_order = contract_digest(load_config(config_path))
    config_path.write_text(secondary_first, "utf-8")

    assert contract_digest(load_config(config_path)) == first_order


def test_the_digest_is_independent_of_where_the_repo_lives(tmp_path: Path) -> None:
    """A clone must digest identically, or every clone reads as stale."""
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    _board(first)
    shutil.copytree(first, second)

    assert contract_digest(load_config(second / "boardkit.toml")) == contract_digest(
        load_config(first / "boardkit.toml")
    )


def test_the_brief_digest_matches_the_doctor_digest(tmp_path: Path) -> None:
    from boardkit.doctor import run_doctor

    config_path = _board(tmp_path)
    report = run_doctor(str(config_path), tmp_path)

    assert f"- digest: `{report.digest}`" in build_brief(load_config(config_path), "S1")


# --- fail-loud --------------------------------------------------------------


def test_an_unknown_card_id_fails_loudly(tmp_path: Path) -> None:
    with pytest.raises(BriefError) as excinfo:
        _brief(tmp_path, card_id="S99")

    assert "unknown card id 'S99'" in str(excinfo.value)
    assert "S1" in str(excinfo.value)


def test_a_missing_dispatch_brief_paragraph_fails_loudly(tmp_path: Path) -> None:
    """The brief quotes the clause; if it cannot, it must not ship a brief
    that silently lost the scope rule."""
    config_path = _board(tmp_path)
    process = tmp_path / "docs" / "board" / "PROCESS.md"
    process.write_text(
        process.read_text(encoding="utf-8").replace(DISPATCH_BRIEF_ANCHOR, "Some other opening"),
        encoding="utf-8",
    )

    with pytest.raises(BriefError) as excinfo:
        build_brief(load_config(config_path), "S1")

    assert DISPATCH_BRIEF_ANCHOR in str(excinfo.value)


def test_a_missing_gates_section_fails_loudly(tmp_path: Path) -> None:
    config_path = _board(tmp_path)
    process = tmp_path / "docs" / "board" / "PROCESS.md"
    process.write_text(
        process.read_text(encoding="utf-8").replace("\n## Gates\n", "\n## Checkpoints\n"),
        encoding="utf-8",
    )

    with pytest.raises(BriefError, match="Gates"):
        build_brief(load_config(config_path), "S1")


def test_a_missing_contract_doc_fails_loudly(tmp_path: Path) -> None:
    config_path = _board(tmp_path)
    (tmp_path / "docs" / "board" / "MODEL-CLASSES.md").unlink()

    with pytest.raises(BriefError, match="MODEL-CLASSES.md"):
        build_brief(load_config(config_path), "S1")


def test_an_undefined_gate_letter_fails_loudly(tmp_path: Path) -> None:
    with pytest.raises(BriefError, match="Gate Z"):
        _brief(tmp_path, CARD.replace('gates: "S -> A -> U(code-review)"', 'gates: "S -> Z"'))


def test_an_unresolvable_reviewer_prints_in_place(tmp_path: Path) -> None:
    """The executor still needs dispatching; a broken reviewer route is
    exactly what the board owner should see, not a refusal to brief."""
    config_path = _board(tmp_path)
    config_path.write_text(
        config_path.read_text(encoding="utf-8").replace(
            '[roles.prose-review]\nroutes = ["primary"]',
            '[routes.unfilled]\nadapter = "<harness>"\nskill = ""\n'
            'pin_source = "docs/board/REVIEW-TOOLING.md#harness-bindings"\npreflight = []\n'
            'staging = "working-dir"\n\n'
            '[roles.prose-review]\nroutes = ["unfilled"]',
        ),
        encoding="utf-8",
    )

    text = build_brief(load_config(config_path), "S1")

    assert "- **prose-review**: UNRESOLVED" in text
    assert "- **executor** -> `primary`" in text


# --- pure helpers -----------------------------------------------------------


@pytest.mark.parametrize(
    ("gates", "expected"),
    [
        ("S -> A -> U", ("S", "A", "U")),
        ("S -> A -> U(code-review)", ("S", "A", "U")),
        ("S -> A (deferred) -> U", ("S", "A", "U")),
        ("S", ("S",)),
        ("", ()),
    ],
)
def test_gate_tokens_parses_the_qualified_forms(gates: str, expected: tuple[str, ...]) -> None:
    assert gate_tokens(gates) == expected


def test_reference_links_skips_absolute_urls() -> None:
    body = "See [a](../spec.md) and [b](https://example.com) and [c](mailto:x@y.z).\n"

    assert reference_links(body) == ["../spec.md"]


def test_reference_links_preserves_first_appearance_order() -> None:
    body = "[b](b.md) [a](a.md) [b again](b.md)\n"

    assert reference_links(body) == ["b.md", "a.md"]
