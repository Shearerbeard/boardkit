"""Bind the AGENTS template's bootstrap to the variable the diagnostics read.

The bootstrap only works if `BOARDKIT_HOME` is exported before the `uv run`
line: a same-line prefix expands the default inside the command before the
assignment lands, so the run silently targets the wrong checkout. That
failure is invisible when it happens, which is why the template has to name
it and why the naming is pinned here.
"""

from __future__ import annotations

import re

from boardkit.contract import BOARDKIT_HOME_VAR, TEMPLATES_DIR

TEMPLATE = TEMPLATES_DIR / "AGENTS.md.template"

EXPORT_RE = re.compile(rf"^\s*export {BOARDKIT_HOME_VAR}=\S+\s*$", re.MULTILINE)
UV_RUN_RE = re.compile(
    rf'^\s*uv run --project "\$\{{{BOARDKIT_HOME_VAR}:-[^"]+}}" boardkit check\s*$',
    re.MULTILINE,
)


def _template_text() -> str:
    return TEMPLATE.read_text(encoding="utf-8")


def _normalized() -> str:
    """Whitespace-collapsed prose, so re-wrapping a paragraph is not a failure.

    Line-anchored patterns still run against the raw text: whether the export
    stands on its own line is the whole point of the rule.
    """
    return " ".join(_template_text().split())


def test_bootstrap_exports_the_variable_on_its_own_line() -> None:
    text = _template_text()
    export = EXPORT_RE.search(text)

    assert export, f"the bootstrap no longer exports {BOARDKIT_HOME_VAR} on its own line"
    assert "export" not in export.group(0).split("=", 1)[1]


def test_bootstrap_runs_the_check_on_a_line_separate_from_the_export() -> None:
    text = _template_text()
    export = EXPORT_RE.search(text)
    uv_run = UV_RUN_RE.search(text)

    assert uv_run, "the bootstrap no longer runs `boardkit check` through uv"
    assert export, "the bootstrap no longer exports the variable"
    # a same-line prefix is the documented failure; the lines stay separate
    assert export.end() < uv_run.start()
    assert "\n" in text[export.start() : uv_run.end()]


def test_template_names_the_same_line_prefix_failure() -> None:
    text = _normalized()

    assert "must be exported on its own line" in text
    assert "before the assignment lands" in text
    assert "silently targets the default path" in text


def test_the_default_path_is_stated_as_a_default_not_a_requirement() -> None:
    """The variable is the supported knob; the sibling-checkout default is a
    convenience, so the template must not read as if the default is the rule."""
    assert f"Set `{BOARDKIT_HOME_VAR}`" in _normalized()


def test_uv_run_line_reads_the_variable_it_told_the_reader_to_export() -> None:
    uv_run = UV_RUN_RE.search(_template_text())

    assert uv_run, "the bootstrap no longer runs `boardkit check` through uv"
    assert BOARDKIT_HOME_VAR in uv_run.group(0)
