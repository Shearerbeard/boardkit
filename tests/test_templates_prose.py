"""The shipped templates pass the prose standard they impose on consumers.

The PROCESS template's commit standards require every checked-in markdown
file to pass the repo's prose linter, so a consumer that copies the
templates in verbatim must not inherit a lint failure from the kit (the
D6 disposition in docs/plans/2026-08-03-feedback-drain.md). The gate runs
the kit's own `.vale.ini` over the shipped template directory.

The test needs the `vale` binary and its synced styles. When either is
absent it skips, loudly naming the setup step, rather than passing
vacuously or failing on machines that never edit templates.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = REPO_ROOT / "src" / "boardkit" / "data" / "templates"


def test_shipped_templates_pass_prose_lint() -> None:
    if shutil.which("vale") is None:
        pytest.skip("vale is not installed; install vale to run the template prose gate")
    if not (REPO_ROOT / ".vale" / "styles" / "ai-tells").is_dir():
        pytest.skip("vale styles not synced; run `vale sync` in the repo root")

    targets = sorted(
        str(p) for p in TEMPLATES_DIR.iterdir() if p.suffix in (".md", ".template")
    )
    assert targets, f"no templates found under {TEMPLATES_DIR}"

    result = subprocess.run(
        ["vale", "--output", "line", *targets],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        "shipped templates fail the kit's own prose gate:\n"
        f"{result.stdout}{result.stderr}"
    )
