"""Tests for `boardkit resolve-route`.

Routing used to take four prose hops across three documents; this is the
mechanical answer. Two properties matter most and both are pinned here: it
fails closed rather than dispatching to a half-written route, and it is lazy
- one unfinished binding must not block every other role on the board.

The text output is byte-pinned because agents read it. A wording change that
looks cosmetic here is a parsing change downstream.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import CONTRACT_BLOCK, config_text

from boardkit.config import load_config
from boardkit.contract import (
    ContractError,
    render_resolution_json,
    render_resolution_text,
    resolve_role,
)

TWO_ROUTE_CONTRACT = """\
[contract]
version = 1

[routes.opencode-reviewer]
adapter = "opencode"
skill = "opencode-cli"
pin_source = "docs/board/REVIEW-TOOLING.md#harness-bindings"
preflight = ["opencode --version"]

[routes.codex-cli]
adapter = "codex"
skill = ""
pin_source = "docs/board/REVIEW-TOOLING.md#harness-bindings"
preflight = []

[roles.executor]
routes = ["opencode-reviewer"]

[roles.code-review]
routes = ["opencode-reviewer", "codex-cli"]

[roles.prose-review]
routes = ["codex-cli"]

[roles.frontier-review]
routes = ["codex-cli"]

[roles.drift-audit]
routes = ["codex-cli"]

[roles.canary]
routes = ["opencode-reviewer"]
"""


def _board(tmp_path: Path, contract: str = TWO_ROUTE_CONTRACT):
    """A loadable board whose pin_source target actually exists."""
    base = config_text().split("[contract]")[0]
    (tmp_path / "boardkit.toml").write_text(base + contract, encoding="utf-8")
    doc = tmp_path / "docs" / "board" / "REVIEW-TOOLING.md"
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text("# Tooling\n\n## Harness bindings\n\nOne row per harness.\n", encoding="utf-8")
    return load_config(tmp_path / "boardkit.toml")


def test_resolves_the_first_route_and_keeps_the_fallbacks_ordered(tmp_path: Path) -> None:
    resolution = resolve_role(_board(tmp_path), "code-review")

    assert resolution.role == "code-review"
    assert resolution.route.name == "opencode-reviewer"
    assert [f.name for f in resolution.fallbacks] == ["codex-cli"]
    assert resolution.position == (1, 2)


def test_text_output_is_byte_stable(tmp_path: Path) -> None:
    text = render_resolution_text(resolve_role(_board(tmp_path), "code-review"))

    assert text == (
        "role: code-review\n"
        "route: opencode-reviewer (1 of 2)\n"
        "adapter: opencode\n"
        "skill: opencode-cli\n"
        "pin source: docs/board/REVIEW-TOOLING.md#harness-bindings\n"
        "preflight: opencode --version\n"
        "fallback: codex-cli\n"
    )


def test_exactly_one_skill_line(tmp_path: Path) -> None:
    """Two skill lines would be ambiguous about which child skill to load."""
    text = render_resolution_text(resolve_role(_board(tmp_path), "code-review"))

    assert len([line for line in text.splitlines() if line.startswith("skill:")]) == 1


def test_an_empty_skill_is_stated_not_omitted(tmp_path: Path) -> None:
    """A missing line reads as an oversight; the explicit none reads as a fact."""
    text = render_resolution_text(resolve_role(_board(tmp_path), "prose-review"))

    assert "skill: none (this transport loads no child skill)" in text


def test_an_empty_preflight_and_no_fallback_are_stated(tmp_path: Path) -> None:
    text = render_resolution_text(resolve_role(_board(tmp_path), "prose-review"))

    assert "preflight: none" in text
    assert "fallback: none" in text


def test_multiple_preflight_commands_each_get_a_line(tmp_path: Path) -> None:
    contract = TWO_ROUTE_CONTRACT.replace(
        'preflight = ["opencode --version"]',
        'preflight = ["opencode --version", "opencode auth list"]',
    )
    text = render_resolution_text(resolve_role(_board(tmp_path, contract), "code-review"))

    assert "preflight: opencode --version\n" in text
    assert "preflight: opencode auth list\n" in text


def test_multiple_fallbacks_each_get_a_line(tmp_path: Path) -> None:
    contract = TWO_ROUTE_CONTRACT.replace(
        '[roles.code-review]\nroutes = ["opencode-reviewer", "codex-cli"]',
        '[roles.code-review]\nroutes = ["opencode-reviewer", "codex-cli", "opencode-reviewer"]',
    )
    text = render_resolution_text(resolve_role(_board(tmp_path, contract), "code-review"))

    assert len([line for line in text.splitlines() if line.startswith("fallback:")]) == 2
    assert "route: opencode-reviewer (1 of 3)" in text


def test_unknown_role_lists_the_declared_roles(tmp_path: Path) -> None:
    with pytest.raises(ContractError) as excinfo:
        resolve_role(_board(tmp_path), "prose-reviewer")

    message = str(excinfo.value)
    assert "unknown role 'prose-reviewer'" in message
    for declared in ("executor", "code-review", "canary"):
        assert declared in message


def test_a_placeholder_first_route_fails_closed(tmp_path: Path) -> None:
    """A scaffolded route must never dispatch: `<harness-name>` is not a harness."""
    contract = TWO_ROUTE_CONTRACT.replace('adapter = "opencode"', 'adapter = "<harness-name>"')

    with pytest.raises(ContractError) as excinfo:
        resolve_role(_board(tmp_path, contract), "code-review")

    message = str(excinfo.value)
    assert "still a template" in message
    assert "<harness-name>" in message
    assert "opencode-reviewer" in message


def test_a_missing_pin_source_path_fails_closed(tmp_path: Path) -> None:
    contract = TWO_ROUTE_CONTRACT.replace(
        '[routes.opencode-reviewer]\nadapter = "opencode"\nskill = "opencode-cli"\n'
        'pin_source = "docs/board/REVIEW-TOOLING.md#harness-bindings"',
        '[routes.opencode-reviewer]\nadapter = "opencode"\nskill = "opencode-cli"\n'
        'pin_source = "docs/board/NOPE.md#harness-bindings"',
    )

    with pytest.raises(ContractError, match="does not exist"):
        resolve_role(_board(tmp_path, contract), "code-review")


def test_a_missing_pin_source_anchor_fails_closed(tmp_path: Path) -> None:
    config = _board(tmp_path)
    doc = tmp_path / "docs" / "board" / "REVIEW-TOOLING.md"
    doc.write_text("# Tooling\n\n## Something else\n\nbody\n", encoding="utf-8")

    with pytest.raises(ContractError, match="matches no heading"):
        resolve_role(config, "code-review")


def test_resolution_does_not_validate_unrelated_roles(tmp_path: Path) -> None:
    """Laziness is the point: one unfinished binding must not block the board."""
    contract = TWO_ROUTE_CONTRACT.replace(
        '[routes.codex-cli]\nadapter = "codex"', '[routes.codex-cli]\nadapter = "<fill me>"'
    )
    config = _board(tmp_path, contract)

    resolved = resolve_role(config, "executor")
    assert resolved.route.name == "opencode-reviewer"

    with pytest.raises(ContractError):
        resolve_role(config, "prose-review")


def test_a_broken_fallback_does_not_block_a_good_first_route(tmp_path: Path) -> None:
    contract = TWO_ROUTE_CONTRACT.replace(
        '[routes.codex-cli]\nadapter = "codex"', '[routes.codex-cli]\nadapter = "<fill me>"'
    )

    resolution = resolve_role(_board(tmp_path, contract), "code-review")

    assert resolution.route.name == "opencode-reviewer"
    assert [f.name for f in resolution.fallbacks] == ["codex-cli"]


def test_json_shape_is_pinned(tmp_path: Path) -> None:
    payload = json.loads(render_resolution_json(resolve_role(_board(tmp_path), "code-review")))

    assert payload == {
        "role": "code-review",
        "route": {
            "name": "opencode-reviewer",
            "adapter": "opencode",
            "skill": "opencode-cli",
            "pin_source": "docs/board/REVIEW-TOOLING.md#harness-bindings",
            "preflight": ["opencode --version"],
        },
        "position": {"index": 1, "of": 2},
        "fallbacks": [
            {
                "name": "codex-cli",
                "adapter": "codex",
                "skill": "",
                "pin_source": "docs/board/REVIEW-TOOLING.md#harness-bindings",
                "preflight": [],
            }
        ],
    }


def test_the_shared_test_contract_resolves_every_required_role(tmp_path: Path) -> None:
    """The conftest board is what most tests dispatch against; every role on it
    must resolve, or those boards are quietly unusable."""
    base = config_text().split("[contract]")[0]
    (tmp_path / "boardkit.toml").write_text(base + CONTRACT_BLOCK, encoding="utf-8")
    doc = tmp_path / "docs" / "board" / "REVIEW-TOOLING.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("# Tooling\n\n## Harness bindings\n\nbody\n", encoding="utf-8")
    config = load_config(tmp_path / "boardkit.toml")

    for role in config.contract.roles:
        assert resolve_role(config, role).route.name == "primary"
