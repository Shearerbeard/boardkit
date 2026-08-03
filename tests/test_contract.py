"""Strictness matrix for the delegation contract.

Every case here is a config a board owner could plausibly write and be wrong
about. The contract is strict in both directions on purpose: a typo and an
omission both raise, so an unfilled or drifted binding is never dispatched
against. Most cases drive `parse_contract` directly; the migration case runs
through `load_config`, because naming the migration is the loader's job.
"""

from pathlib import Path

import pytest
from conftest import config_text

from boardkit.config import load_config
from boardkit.contract import (
    REQUIRED_ROLES,
    SUPPORTED_CONTRACT_VERSIONS,
    parse_contract,
    placeholders,
)

CONTRACT = {"version": 1}


def _route(**overrides: object) -> dict:
    route = {
        "adapter": "test-harness",
        "skill": "",
        "pin_source": "docs/board/REVIEW-TOOLING.md#harness-bindings",
        "preflight": [],
    }
    route.update(overrides)
    return route


def _roles(overrides: dict[str, list[str]] | None = None) -> dict:
    roles = {name: {"routes": ["primary"]} for name in REQUIRED_ROLES}
    for name, route_names in (overrides or {}).items():
        roles[name] = {"routes": route_names}
    return roles


def test_missing_contract_section_names_the_migration(tmp_path: Path) -> None:
    pre_contract = config_text().split("[contract]")[0]
    config_path = tmp_path / "boardkit.toml"
    config_path.write_text(pre_contract, encoding="utf-8")

    with pytest.raises(ValueError) as excinfo:
        load_config(config_path)

    message = str(excinfo.value)
    assert str(config_path) in message
    assert "[contract]" in message
    assert "predates delegation contract v1" in message
    assert "boardkit doctor" in message


def test_unknown_contract_key_raises() -> None:
    with pytest.raises(ValueError, match="unknown key"):
        parse_contract({"version": 1, "digest": "abc"}, {"primary": _route()}, _roles())


def test_missing_contract_version_raises() -> None:
    with pytest.raises(ValueError, match="missing required key"):
        parse_contract({}, {"primary": _route()}, _roles())


def test_non_integer_version_raises() -> None:
    with pytest.raises(ValueError, match="version must be an integer"):
        parse_contract({"version": "1"}, {"primary": _route()}, _roles())


def test_unsupported_version_names_the_supported_set() -> None:
    with pytest.raises(ValueError) as excinfo:
        parse_contract({"version": 99}, {"primary": _route()}, _roles())

    message = str(excinfo.value)
    assert "99" in message
    assert str(sorted(SUPPORTED_CONTRACT_VERSIONS)) in message


def test_unknown_role_raises() -> None:
    roles = _roles()
    roles["prose-reviewer"] = {"routes": ["primary"]}
    with pytest.raises(ValueError) as excinfo:
        parse_contract(CONTRACT, {"primary": _route()}, roles)

    assert "unknown role" in str(excinfo.value)
    assert "prose-reviewer" in str(excinfo.value)


def test_missing_required_roles_are_named() -> None:
    roles = _roles()
    del roles["canary"]
    del roles["drift-audit"]
    with pytest.raises(ValueError) as excinfo:
        parse_contract(CONTRACT, {"primary": _route()}, roles)

    message = str(excinfo.value)
    assert "missing required role" in message
    assert "canary" in message
    assert "drift-audit" in message


def test_unknown_role_key_raises() -> None:
    roles = _roles()
    roles["canary"] = {"routes": ["primary"], "model": "some-model-id"}
    with pytest.raises(ValueError, match=r"\[roles.canary\]: unknown key"):
        parse_contract(CONTRACT, {"primary": _route()}, roles)


def test_empty_route_list_raises() -> None:
    with pytest.raises(ValueError, match=r"\[roles.executor\]: routes must name at least one"):
        parse_contract(CONTRACT, {"primary": _route()}, _roles({"executor": []}))


def test_undeclared_route_is_named_with_its_role() -> None:
    with pytest.raises(ValueError) as excinfo:
        parse_contract(CONTRACT, {"primary": _route()}, _roles({"code-review": ["frontier"]}))

    message = str(excinfo.value)
    assert "roles.code-review" in message
    assert "frontier" in message


def test_non_string_route_list_raises() -> None:
    with pytest.raises(ValueError, match=r"\[roles.canary\]: routes must be a list"):
        parse_contract(CONTRACT, {"primary": _route()}, _roles({"canary": [7]}))


def test_unknown_route_key_raises() -> None:
    routes = {"primary": _route(model="some-model-id")}
    with pytest.raises(ValueError, match=r"\[routes.primary\]: unknown key"):
        parse_contract(CONTRACT, routes, _roles())


def test_missing_route_key_raises() -> None:
    route = _route()
    del route["pin_source"]
    with pytest.raises(ValueError, match=r"\[routes.primary\]: missing required key"):
        parse_contract(CONTRACT, {"primary": route}, _roles())


@pytest.mark.parametrize("name", ["Primary", "primary_route", "primary route", "-primary", ""])
def test_non_slug_route_name_raises(name: str) -> None:
    with pytest.raises(ValueError, match="lowercase slug"):
        parse_contract(CONTRACT, {name: _route()}, _roles({"executor": [name]}))


def test_empty_adapter_raises() -> None:
    with pytest.raises(ValueError, match="adapter must be a non-empty string"):
        parse_contract(CONTRACT, {"primary": _route(adapter="")}, _roles())


def test_preflight_must_be_a_list_of_strings() -> None:
    with pytest.raises(ValueError, match="preflight must be a list of strings"):
        parse_contract(CONTRACT, {"primary": _route(preflight="check --version")}, _roles())

    with pytest.raises(ValueError, match="preflight must be a list of strings"):
        parse_contract(CONTRACT, {"primary": _route(preflight=[7])}, _roles())


def test_empty_skill_is_valid() -> None:
    contract = parse_contract(CONTRACT, {"primary": _route()}, _roles())
    assert contract.routes["primary"].skill == ""


def test_valid_contract_exposes_ordered_routes_per_role() -> None:
    routes = {"primary": _route(), "fallback": _route(adapter="other-harness")}
    contract = parse_contract(CONTRACT, routes, _roles({"code-review": ["fallback", "primary"]}))

    assert contract.version == 1
    # the declared order is the fallback order the dispatcher walks
    assert contract.roles["code-review"] == ("fallback", "primary")
    assert contract.roles["executor"] == ("primary",)
    assert tuple(contract.routes) == ("primary", "fallback")
    assert contract.routes["fallback"].adapter == "other-harness"


def test_preflight_is_frozen_into_a_tuple() -> None:
    contract = parse_contract(
        CONTRACT, {"primary": _route(preflight=["harness --version"])}, _roles()
    )
    assert contract.routes["primary"].preflight == ("harness --version",)


def test_placeholders_finds_angle_bracket_tokens() -> None:
    assert placeholders("<harness-name>") == ["<harness-name>"]
    assert placeholders("<a> and <b>") == ["<a>", "<b>"]
    assert placeholders("test-harness") == []
