"""Command-line entry point. Subcommands land in Phase 1."""

from boardkit import __version__


def main() -> None:
    print(f"boardkit {__version__} (scaffold; subcommands land in Phase 1)")
