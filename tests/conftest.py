import shutil
from pathlib import Path

import pytest

GOLDEN_DIR = Path(__file__).parent / "golden"
GOLDEN_CARDS_DIR = GOLDEN_DIR / "aura-cards"

# The delegation contract every test board declares. Filled in with real
# values (no angle-bracket placeholders) so boards under test load the way a
# migrated repo's does, not the way a freshly scaffolded one does.
CONTRACT_BLOCK = """\
[contract]
version = 1

[routes.primary]
adapter = "test-harness"
skill = ""
pin_source = "docs/board/REVIEW-TOOLING.md#harness-bindings"
preflight = []

[roles.executor]
routes = ["primary"]

[roles.code-review]
routes = ["primary"]

[roles.prose-review]
routes = ["primary"]

[roles.frontier-review]
routes = ["primary"]

[roles.drift-audit]
routes = ["primary"]

[roles.canary]
routes = ["primary"]
"""

CONFIG_TEMPLATE = (
    """\
[board]
cards_dir = "{cards_dir}"
id_prefix = "{id_prefix}"
sentinel_ids = ["MILESTONE"]

[review]
repo = "{repo}"
output_dir = "{output_dir}"

"""
    + CONTRACT_BLOCK
)


def config_text(
    cards_dir: str = "cards",
    output_dir: str = "reviews",
    repo: str = ".",
    id_prefix: str = "S",
) -> str:
    """A complete, valid boardkit.toml — the one config schema the tests share."""
    return CONFIG_TEMPLATE.format(
        cards_dir=cards_dir,
        output_dir=output_dir,
        repo=repo,
        id_prefix=id_prefix,
    )


@pytest.fixture
def golden_board(tmp_path: Path) -> Path:
    """A boardkit.toml pointing at a fresh copy of the golden aura-cards fixture.

    Copies the whole tests/golden/ tree (not just aura-cards/) because card
    bodies link to sibling docs (../PROCESS.md, ../evidence/..., ...) one
    level up from the cards directory; those links must resolve for the
    link checker, so their placeholder targets travel with the cards dir.
    """
    for entry in GOLDEN_DIR.iterdir():
        dest_name = "cards" if entry.name == "aura-cards" else entry.name
        dest = tmp_path / dest_name
        if entry.is_dir():
            shutil.copytree(entry, dest)
        else:
            shutil.copyfile(entry, dest)
    config_path = tmp_path / "boardkit.toml"
    config_path.write_text(config_text(), encoding="utf-8")
    return config_path
