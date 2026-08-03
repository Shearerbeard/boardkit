"""The config schema exists in two shipped copies; these bind them together.

`INIT_CONFIG_TEMPLATE` is what a new board gets, `conftest.config_text` is
what every test board gets. When they drift, tests keep passing against a
schema no real board has — so the drift is the thing under test here.

The one deliberate difference: init ships angle-bracket placeholders in its
route values (a scaffolded board must not look filled in), while the test
config is filled.
"""

import tomllib
from pathlib import Path

from conftest import config_text

from boardkit.cli import INIT_CONFIG_TEMPLATE
from boardkit.config import load_config
from boardkit.contract import CONTRACT_VERSION, REQUIRED_ROLES, placeholders


def _section_keys(data: dict, prefix: str = "") -> dict[str, list[str]]:
    """Every table in the document, as dotted path -> sorted key names."""
    sections = {prefix: sorted(data)} if prefix else {"": sorted(data)}
    for key, value in data.items():
        if isinstance(value, dict):
            sections.update(_section_keys(value, f"{prefix}.{key}" if prefix else key))
    return sections


def test_init_template_parses_and_declares_every_role() -> None:
    data = tomllib.loads(INIT_CONFIG_TEMPLATE)

    assert data["contract"]["version"] == CONTRACT_VERSION
    assert sorted(data["roles"]) == sorted(REQUIRED_ROLES)
    for role in REQUIRED_ROLES:
        declared = data["roles"][role]["routes"]
        assert declared, f"{role} declares no route"
        for name in declared:
            assert name in data["routes"], f"{role} routes to undeclared {name}"


def test_init_template_loads_end_to_end(tmp_path: Path) -> None:
    config_path = tmp_path / "boardkit.toml"
    config_path.write_text(INIT_CONFIG_TEMPLATE, encoding="utf-8")

    config = load_config(config_path)

    assert config.contract.version == CONTRACT_VERSION
    assert sorted(config.contract.roles) == sorted(REQUIRED_ROLES)


def test_both_templates_declare_the_same_sections_and_keys() -> None:
    init = _section_keys(tomllib.loads(INIT_CONFIG_TEMPLATE))
    test_config = _section_keys(tomllib.loads(config_text()))

    assert init == test_config


def test_init_template_route_values_still_carry_placeholders() -> None:
    routes = tomllib.loads(INIT_CONFIG_TEMPLATE)["routes"]
    found = [
        token
        for route in routes.values()
        for value in route.values()
        if isinstance(value, str)
        for token in placeholders(value)
    ]
    assert found, "init must scaffold placeholders, not values that look filled in"


def test_test_config_carries_no_placeholders() -> None:
    routes = tomllib.loads(config_text())["routes"]
    found = [
        token
        for route in routes.values()
        for value in route.values()
        if isinstance(value, str)
        for token in placeholders(value)
    ]
    assert found == []
