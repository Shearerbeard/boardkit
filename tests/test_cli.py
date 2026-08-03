"""Tests for the CLI's wiring, not its commands.

Dispatch used to be a dict keyed by subcommand name, which could disagree
with the parser without anything failing until a user hit the command. The
handler now hangs off the subparser, and this pins that every subcommand has
one. `--version` is pinned against pyproject, since two places record the
version and only one of them is what `pip install` sees.
"""

import argparse
import tomllib
from pathlib import Path

import pytest

from boardkit import __version__
from boardkit.cli import build_parser, main

PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"
SUBCOMMANDS = {
    "check",
    "render",
    "doctor",
    "resolve-route",
    "dispatch-brief",
    "review-packet",
    "canary-key",
    "init",
}


def _subparsers(parser: argparse.ArgumentParser) -> dict[str, argparse.ArgumentParser]:
    actions = [a for a in parser._actions if isinstance(a, argparse._SubParsersAction)]
    assert len(actions) == 1, "expected exactly one subparser action"
    return actions[0].choices


def test_every_subcommand_binds_a_handler() -> None:
    subparsers = _subparsers(build_parser())

    assert set(subparsers) == SUBCOMMANDS
    for name, sub in subparsers.items():
        handler = sub.get_default("handler")
        assert callable(handler), f"{name} binds no handler"


def test_version_flag_prints_the_version_and_exits_zero(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as excinfo:
        build_parser().parse_args(["--version"])

    assert excinfo.value.code == 0
    assert capsys.readouterr().out == f"boardkit {__version__}\n"


def test_version_matches_pyproject() -> None:
    with PYPROJECT.open("rb") as f:
        pyproject = tomllib.load(f)

    assert __version__ == pyproject["project"]["version"]


def test_bare_invocation_prints_version_and_help(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("sys.argv", ["boardkit"])

    assert main() is None  # no SystemExit: the process exits 0

    out = capsys.readouterr().out
    assert out.startswith(f"boardkit {__version__}\n")
    assert "usage: boardkit" in out
    for name in SUBCOMMANDS:
        assert name in out
