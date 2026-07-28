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
DEFERRED_VIEW = "deferred.md"
GENERATED = {"INDEX.md", "board.md", DEFERRED_VIEW}
WIP_LIMIT = 2  # PROCESS.md board mechanics: at most two cards in-progress
# Optional boolean frontmatter key. PROCESS.md board mechanics: a flow the
# user explicitly declares a detached side quest is exempt from the WIP
# limit, and the exemption is recorded on that flow's own cards. The
# template says nothing about shared files, so the serialize-with mutex
# still applies to a side-quest card.
SIDE_QUEST_KEY = "side-quest"

BOARD_HEADER = "---\n\nkanban-plugin: board\n\n---\n"
COLUMN_TITLES = {
    "ready": "Ready",
    "in-progress": "In Progress",
    "in-review": "In Review",
    "backlog": "Backlog",
    "done": "Done",
}

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#\s]+)(?:#[^)]*)?\)")

# A deferred gate is a `Gate <X> open: deferred (<reason>)` log line whose
# checklist box is still unticked. The gate token is a letter with an
# optional qualifier, as in `Gate U (baseline)`; the reason is the
# parenthesized text right after `deferred`, so it carries no nested
# parentheses.
GATE_TOKEN = r"[A-Z](?:\s*\([^)]*\))?"
DEFERRED_RE = re.compile(rf"Gate\s+({GATE_TOKEN})\s+open:\s*deferred\s*\(([^)]*)\)")
CHECKBOX_RE = re.compile(rf"^\s*[-*]\s*\[([ xX])\]\s*(Gate\s+{GATE_TOKEN})")

# The deferral sweep reads the card's Log section only, and only its bullet
# entries: a card that documents the convention in its Scope or Notes prose
# is describing the syntax, not deferring its own gate. Inline-code spans
# come out before matching for the same reason.
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
LOG_HEADING = "log"
BULLET_RE = re.compile(r"^\s*[-*]\s+")
INLINE_CODE_RE = re.compile(r"`[^`]*`")


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
    if SIDE_QUEST_KEY in meta and not isinstance(meta[SIDE_QUEST_KEY], bool):
        errors.append(
            f"{path.name}: '{SIDE_QUEST_KEY}' must be true or false, "
            f"got {meta[SIDE_QUEST_KEY]!r}"
        )
    meta["_file"] = path.name
    meta["_body"] = text[end + 5 :]
    return meta


def check_links(card: dict, cards_dir: Path, generated: set[str], errors: list[str]) -> None:
    """Every relative link in the card body must resolve.

    `generated` is the set of this run's own outputs, which always exist
    after it. It is not the whole GENERATED set: `deferred.md` is written
    only while some gate is open-deferred, so on a board with none, a link
    to it is as broken as a link to a deleted card.
    """
    for match in LINK_RE.finditer(card["_body"]):
        target = match.group(1)
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        if target in generated:
            continue
        if target in GENERATED:
            # A generated name outside this run's outputs is stale: a copy
            # left on disk does not legitimize the link, because render
            # deletes it on the next pass.
            errors.append(f"{card['_file']}: broken link '{target}' (stale generated view)")
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
    in_progress = [
        c
        for c in cards.values()
        if c["status"] == "in-progress" and not c.get(SIDE_QUEST_KEY, False)
    ]
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


class DeferredGate(NamedTuple):
    card_id: str
    card_file: str
    gate: str
    reason: str


def gate_key(gate: str) -> str:
    """Normalize a gate token so a log line and its checklist box compare equal."""
    return re.sub(r"\s+", "", gate).upper()


def log_section_lines(body: str) -> list[str]:
    """The lines under every `Log` heading, up to the next same-or-higher one."""
    level: int | None = None
    lines: list[str] = []
    for line in body.splitlines():
        heading = HEADING_RE.match(line)
        if heading is None:
            if level is not None:
                lines.append(line)
            continue
        depth = len(heading.group(1))
        if level is not None and depth <= level:
            level = None
        if level is None and heading.group(2).strip().lower() == LOG_HEADING:
            level = depth
    return lines


def log_entries(body: str) -> list[str]:
    """Each Log bullet as one flattened line, with inline-code spans removed.

    A log entry wraps across source lines, so the bullet and its indented
    continuation lines collapse into a single string before matching; a
    blank line or the next bullet ends the entry.
    """
    blocks: list[list[str]] = []
    current: list[str] | None = None
    for line in log_section_lines(body):
        if BULLET_RE.match(line):
            if current is not None:
                blocks.append(current)
            current = [line]
        elif current is None:
            continue
        elif not line.strip():
            blocks.append(current)
            current = None
        else:
            current.append(line)
    if current is not None:
        blocks.append(current)
    return [" ".join(INLINE_CODE_RE.sub(" ", " ".join(block)).split()) for block in blocks]


def deferred_gates(cards: list[dict]) -> list[DeferredGate]:
    """Every gate a card logged as deferred and has not ticked off since.

    A gate with no checklist box at all counts as open: nothing has recorded
    it passing. Repeat deferrals of the same gate with the same reason
    collapse to one entry; a new reason is a new entry, since the log does
    not say which came last.
    """
    entries: list[DeferredGate] = []
    for card in cards:
        body = card["_body"]
        ticked: set[str] = set()
        unticked: set[str] = set()
        for line in body.splitlines():
            box = CHECKBOX_RE.match(line)
            if box is not None:
                target = ticked if box.group(1).lower() == "x" else unticked
                target.add(gate_key(box.group(2).removeprefix("Gate")))
        seen: set[tuple[str, str]] = set()
        for entry in log_entries(body):
            for match in DEFERRED_RE.finditer(entry):
                gate = " ".join(match.group(1).split())
                key = gate_key(gate)
                if key in ticked and key not in unticked:
                    continue
                reason = " ".join(match.group(2).split())
                if (key, reason) in seen:
                    continue
                seen.add((key, reason))
                entries.append(
                    DeferredGate(
                        card_id=card["id"], card_file=card["_file"], gate=gate, reason=reason
                    )
                )
    return entries


def render_deferred(entries: list[DeferredGate]) -> str:
    lines = [
        "# Deferred gates",
        "",
        "Generated by `boardkit render`; do not edit by hand.",
        "Every gate logged as `open: deferred` whose checklist box is still",
        "unticked. A deferred gate stays open until a later session runs it",
        "properly; the next user gate surfaces it rather than absorbing it.",
        "",
        "| Card | Gate | Waiting on |",
        "|---|---|---|",
    ]
    for entry in entries:
        reason = entry.reason.replace("|", r"\|") or "(no reason recorded)"
        lines.append(f"| [{entry.card_id}]({entry.card_file}) | Gate {entry.gate} | {reason} |")
    lines.append("")
    return "\n".join(lines)


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


def _card_line(card: dict) -> str:
    return f"- [{card['id']}]({card['_file']}) {card['title']}"


def render_canary_key(result: BoardResult, drift: list[str]) -> str:
    """The grading key for the orientation canary, from frontmatter alone.

    `drift` names the generated views that no longer match the cards, so a
    board owner grading a canary can see it was reading a stale surface.
    """
    cards = result.cards
    lines = [
        "# Canary key",
        "",
        "Computed by `boardkit canary-key` from card frontmatter. Grade the",
        "orientation canary's answers against this key, never against the",
        "canary's own confidence. The fourth question (who owns the board,",
        "and where must it stop) has a static key: the Roles and Gates",
        "sections of `PROCESS.md`.",
        "",
    ]

    for status, heading in (("in-review", "In Review"), ("in-progress", "In Progress")):
        rows = [c for c in cards if c["status"] == status]
        lines += [f"## {heading}", ""]
        lines += [_card_line(c) for c in rows] if rows else ["- none"]
        lines.append("")

    lines += ["## Next pull", ""]
    ready = [c for c in cards if c["status"] == "ready"]
    if ready:
        lines.append(f"{_card_line(ready[0])} (top of the ready queue)")
        lines.append("")
        lines.append(f"Ready queue: {', '.join(c['id'] for c in ready)}.")
    else:
        done = {c["id"] for c in cards if c["status"] == "done"}
        eligible = [
            c
            for c in cards
            if c["status"] == "backlog" and all(dep in done for dep in c["depends"])
        ]
        if eligible:
            lines.append(
                "- PROMOTION GAP: ready is empty, but these backlog cards have"
                " every dependency done:"
            )
            lines += [_card_line(c) for c in eligible]
            lines.append("")
            lines.append("Promoting one of them is the fix; the canary should flag this.")
        else:
            lines.append("- none: no ready card, and no backlog card has all dependencies done.")
    lines.append("")

    lines += ["## Open deferred gates", ""]
    deferred = deferred_gates(cards)
    if deferred:
        lines += [
            f"- [{e.card_id}]({e.card_file}) Gate {e.gate}: {e.reason or 'no reason recorded'}"
            for e in deferred
        ]
    else:
        lines.append("- none")
    lines.append("")

    lines += ["## Views", ""]
    if drift:
        lines.append(
            f"DRIFTED: {', '.join(sorted(drift))}. Regenerate before grading, or"
            " the canary reads a surface the cards no longer say."
        )
    else:
        lines.append(f"Current: {', '.join(sorted(result.views))}.")
    lines.append("")
    return "\n".join(lines)


def build_board(config: Config) -> BoardResult:
    """Validate every card in config.board.cards_dir and render its views.

    Raises BoardError carrying every error found, if any.
    """
    errors: list[str] = []
    cards: dict[str, dict] = {}
    parsed: list[dict] = []
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
        parsed.append(card)

    # The deferred view exists only while something is deferred: a board with
    # no open deferrals renders the two views it always did, and boards
    # rendered before this view existed stay valid. Link checking needs the
    # answer first, since a link to a view this run will not write is broken.
    deferred = deferred_gates(parsed)
    generated = GENERATED if deferred else GENERATED - {DEFERRED_VIEW}
    for card in parsed:
        check_links(card, cards_dir, generated, errors)
    if errors:
        raise BoardError(errors)

    check_dag(cards, errors)
    if errors:
        raise BoardError(errors)

    ordered = sorted(cards.values(), key=lambda c: sort_key(c, config))
    views = {"INDEX.md": render_index(ordered), "board.md": render_board(ordered)}
    if deferred:
        views[DEFERRED_VIEW] = render_deferred(deferred_gates(ordered))
    return BoardResult(cards=ordered, views=views)
