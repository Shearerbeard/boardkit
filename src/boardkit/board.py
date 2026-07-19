"""Card registry validation and generated-view rendering.

Ported from terminalbench-aura's scripts/cards_index.py. Validates card
frontmatter (schema, unique ids, dependency DAG acyclicity) and body
links (relative markdown links must resolve), then renders INDEX.md and
the Obsidian-kanban board.md. The card id scheme (prefix + sentinels)
and cards directory come from the loaded Config rather than being
hardcoded.

Deviation from the source script: an empty cards directory is valid
here (a freshly `boardkit init`-ed board has zero cards); the source
script treated that as an error.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple

import yaml

from boardkit.config import Config

STATUSES = ["ready", "in-progress", "in-review", "backlog", "done"]
EXECUTORS = {"smart", "any"}
LINEAGES = {"primary", "accepted-head", "isolated-branch", "none"}
REQUIRED = [
    "id",
    "title",
    "status",
    "depends",
    "serialize-with",
    "lineage",
    "executor",
    "gates",
    "user-gates",
]
GENERATED = {"INDEX.md", "board.md"}
WIP_LIMIT = 2  # PROCESS.md board mechanics: at most two cards in-progress

BOARD_HEADER = "---\n\nkanban-plugin: board\n\n---\n"
COLUMN_TITLES = {
    "ready": "Ready",
    "in-progress": "In Progress",
    "in-review": "In Review",
    "backlog": "Backlog",
    "done": "Done",
}

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#\s]+)(?:#[^)]*)?\)")


class BoardError(Exception):
    """Raised with the full list of validation errors found."""

    def __init__(self, errors: list[str]) -> None:
        super().__init__("\n".join(errors))
        self.errors = errors


class BoardResult(NamedTuple):
    cards: list[dict]
    views: dict[str, str]


def card_file_pattern(config: Config) -> re.Pattern[str]:
    ids = "|".join(
        [re.escape(config.board.id_prefix.lower()) + r"\d+"]
        + [re.escape(s.lower()) for s in config.board.sentinel_ids]
    )
    return re.compile(rf"^({ids})-[a-z0-9-]+\.md$")


def card_id_pattern(config: Config) -> re.Pattern[str]:
    ids = "|".join(
        [re.escape(config.board.id_prefix) + r"\d+"]
        + [re.escape(s) for s in config.board.sentinel_ids]
    )
    return re.compile(rf"^({ids})$")


def parse_card(path: Path, id_re: re.Pattern[str], errors: list[str]) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"{path.name}: missing frontmatter")
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        errors.append(f"{path.name}: unterminated frontmatter")
        return None
    try:
        meta = yaml.safe_load(text[4:end])
    except yaml.YAMLError as exc:
        errors.append(f"{path.name}: bad YAML ({exc})")
        return None
    if not isinstance(meta, dict):
        errors.append(f"{path.name}: frontmatter is not a mapping")
        return None
    for key in REQUIRED:
        if key not in meta:
            errors.append(f"{path.name}: missing required key '{key}'")
            meta.setdefault(key, [] if key.endswith("s") or "-" in key else "")
    if not id_re.match(str(meta.get("id", ""))):
        errors.append(f"{path.name}: id '{meta.get('id')}' does not match card id scheme")
    if meta.get("status") not in STATUSES:
        errors.append(f"{path.name}: status '{meta.get('status')}' not in {STATUSES}")
    if meta.get("executor") not in EXECUTORS:
        errors.append(f"{path.name}: executor '{meta.get('executor')}' not in {sorted(EXECUTORS)}")
    if meta.get("lineage") not in LINEAGES:
        errors.append(f"{path.name}: lineage '{meta.get('lineage')}' not in {sorted(LINEAGES)}")
    for listy in ("depends", "serialize-with", "user-gates"):
        if not isinstance(meta.get(listy), list):
            errors.append(f"{path.name}: '{listy}' must be a list")
    meta["_file"] = path.name
    meta["_body"] = text[end + 5 :]
    return meta


def check_links(card: dict, cards_dir: Path, errors: list[str]) -> None:
    for match in LINK_RE.finditer(card["_body"]):
        target = match.group(1)
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        if target in GENERATED:  # the generator's own outputs always exist post-run
            continue
        if not (cards_dir / target).resolve().exists():
            errors.append(f"{card['_file']}: broken link '{target}'")


def check_dag(cards: dict[str, dict], errors: list[str]) -> None:
    for card in cards.values():
        for ref_key in ("depends", "serialize-with"):
            for ref in card[ref_key]:
                if ref not in cards:
                    errors.append(f"{card['_file']}: {ref_key} references unknown card '{ref}'")
        # serialize-with must be symmetric: shared-file pairs list each other
        for ref in card["serialize-with"]:
            if ref in cards and card["id"] not in cards[ref]["serialize-with"]:
                errors.append(f"{card['_file']}: serialize-with {ref} is not reciprocated")
        # ready means every dependency is done
        if card["status"] == "ready":
            for dep in card["depends"]:
                if dep in cards and cards[dep]["status"] != "done":
                    errors.append(
                        f"{card['_file']}: ready but dependency {dep} is {cards[dep]['status']}"
                    )
    # board invariants from PROCESS.md that the views cannot show
    in_progress = [c for c in cards.values() if c["status"] == "in-progress"]
    if len(in_progress) > WIP_LIMIT:
        names = ", ".join(sorted(c["id"] for c in in_progress))
        errors.append(
            f"WIP limit exceeded: {len(in_progress)} cards in-progress ({names}), limit {WIP_LIMIT}"
        )
    for card in cards.values():
        for ref in card["serialize-with"]:
            if (
                ref in cards
                and card["status"] == "in-progress"
                and cards[ref]["status"] == "in-progress"
                and card["id"] < ref  # report each pair once
            ):
                errors.append(
                    f"{card['_file']}: serialized cards {card['id']} and {ref} "
                    "are both in-progress"
                )
        if (
            card["status"] == "in-review"
            and card["lineage"] != "none"
            and not card.get("commit-range")
        ):
            errors.append(
                f"{card['_file']}: in-review with lineage {card['lineage']} "
                "but no commit-range set"
            )

    state: dict[str, int] = {}

    def visit(cid: str, stack: list[str]) -> None:
        if state.get(cid) == 2:
            return
        if state.get(cid) == 1:
            errors.append(f"dependency cycle: {' -> '.join(stack + [cid])}")
            return
        state[cid] = 1
        for dep in cards[cid]["depends"]:
            if dep in cards:
                visit(dep, stack + [cid])
        state[cid] = 2

    for cid in cards:
        visit(cid, [])


def sort_key(card: dict, config: Config) -> tuple[int, int]:
    cid = card["id"]
    if cid in config.board.sentinel_ids:
        return (1, config.board.sentinel_ids.index(cid))
    return (0, int(cid[len(config.board.id_prefix) :]))


def render_index(cards: list[dict]) -> str:
    lines = [
        "# Card index",
        "",
        "Generated by `boardkit render`; do not edit by hand.",
        "Run it after any card status change; `--check` gates commits.",
        "Ready requires every entry in Depends to be done; the session",
        "running the board promotes eligible cards (PROCESS.md,",
        "Delegation protocol).",
        "",
        "| ID | Title | Status | Depends | Executor | Gates |",
        "|---|---|---|---|---|---|",
    ]
    for c in cards:
        deps = ", ".join(c["depends"]) or "-"
        lines.append(
            f"| [{c['id']}]({c['_file']}) | {c['title']} | {c['status']} "
            f"| {deps} | {c['executor']} | {c['gates']} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_board(cards: list[dict]) -> str:
    parts = [BOARD_HEADER]
    for status in STATUSES:
        parts.append(f"\n## {COLUMN_TITLES[status]}\n")
        for c in (c for c in cards if c["status"] == status):
            deps = ", ".join(c["depends"]) or "none"
            parts.append(
                f"- [ ] **{c['id']}** [{c['title']}]({c['_file']})\n"
                f"\tDepends: {deps}. Gates: {c['gates']}. Executor: {c['executor']}.\n"
            )
    parts.append(
        "\n%% Generated by boardkit render. Card frontmatter is the"
        " source of truth; a kanban drag here is DRIFT that --check"
        " reports. Update the card file, then regenerate. %%\n"
    )
    return "".join(parts)


def build_board(config: Config) -> BoardResult:
    """Validate every card in config.board.cards_dir and render its views.

    Raises BoardError carrying every error found, if any.
    """
    errors: list[str] = []
    cards: dict[str, dict] = {}
    file_re = card_file_pattern(config)
    id_re = card_id_pattern(config)
    cards_dir = config.board.cards_dir

    for path in sorted(cards_dir.glob("*.md")):
        if path.name in GENERATED or path.name.startswith("_"):
            continue
        if not file_re.match(path.name):
            errors.append(f"{path.name}: filename violates <id>-<slug>.md naming rule")
            continue
        card = parse_card(path, id_re, errors)
        if card is None:
            continue
        if card["id"] in cards:
            errors.append(f"{path.name}: duplicate id {card['id']}")
        cards[card["id"]] = card
        check_links(card, cards_dir, errors)
    if errors:
        raise BoardError(errors)

    check_dag(cards, errors)
    if errors:
        raise BoardError(errors)

    ordered = sorted(cards.values(), key=lambda c: sort_key(c, config))
    views = {"INDEX.md": render_index(ordered), "board.md": render_board(ordered)}
    return BoardResult(cards=ordered, views=views)
