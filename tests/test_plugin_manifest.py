"""The plugin manifests stay valid and consistent with each other.

Claude Code discovers this plugin through two JSON files, and a mistake in
either surfaces at install time on someone else's machine with an error that
names neither. These tests keep that failure here instead.

The empty-plugin test that used to live here was deleted with the skill
bodies it was waiting on.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"

# The personal skills marketplace. Claude Code keeps one install manifest per
# source, keyed by marketplace name, so two marketplaces sharing a name prune
# each other's installs: installing from one uninstalls the other's plugins.
PERSONAL_MARKETPLACE_NAME = "my-skills"


def _marketplace() -> dict:
    return json.loads(MARKETPLACE.read_text(encoding="utf-8"))


def test_the_marketplace_manifest_is_valid_json_with_the_required_fields() -> None:
    data = _marketplace()

    assert data["name"]
    assert data["description"]
    assert data["owner"]["name"]
    assert data["owner"]["email"]
    assert data["plugins"]


def test_the_marketplace_name_differs_from_the_personal_one() -> None:
    assert _marketplace()["name"] != PERSONAL_MARKETPLACE_NAME
    assert _marketplace()["name"] == "boardkit"


def test_every_declared_plugin_source_exists() -> None:
    """A source that points nowhere fails at install time, on someone else's
    machine, with an error that does not name this file."""
    for plugin in _marketplace()["plugins"]:
        source = (REPO_ROOT / plugin["source"]).resolve()
        assert source.is_dir(), f"{plugin['name']} declares missing source {plugin['source']}"
        assert (source / ".claude-plugin" / "plugin.json").is_file()


def test_each_plugin_manifest_names_its_own_directory() -> None:
    for plugin in _marketplace()["plugins"]:
        manifest = REPO_ROOT / plugin["source"] / ".claude-plugin" / "plugin.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))

        assert data["name"] == plugin["name"]
        assert data["name"] == manifest.parent.parent.name
        assert data["version"]
        assert data["author"]["name"]
