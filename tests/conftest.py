import shutil
from pathlib import Path

import pytest

GOLDEN_DIR = Path(__file__).parent / "golden"
GOLDEN_CARDS_DIR = GOLDEN_DIR / "aura-cards"

CONFIG_TEMPLATE = """\
[board]
cards_dir = "{cards_dir}"
id_prefix = "S"
sentinel_ids = ["MILESTONE"]

[review]
repo = "."
output_dir = "{output_dir}"
"""


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
    config_path.write_text(
        CONFIG_TEMPLATE.format(cards_dir="cards", output_dir="reviews"), encoding="utf-8"
    )
    return config_path
