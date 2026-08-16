"""Card registry validation and generated-view rendering.

Ported from terminalbench-aura's scripts/cards_index.py. Validates card
frontmatter (schema, unique ids, dependency DAG acyclicity) and body
links (relative markdown links must resolve), then renders INDEX.md,
the Obsidian-kanban board.md, and the Mermaid graph.md. The card id
scheme (prefix + sentinels) and cards directory come from the loaded
Config rather than being hardcoded.

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
GRAPH_VIEW = "graph.md"
GENERATED = {"INDEX.md", "board.md", GRAPH_VIEW, DEFERRED_VIEW}
WIP_LIMIT = 2  # PROCESS.md board mechanics: at most two cards in-progress
# Optional boolean frontmatter key. PROCESS.md board mechanics: a flow the
# user explicitly declares a detached side quest is exempt from the WIP
# limit, and the exemption is recorded on that flow's own cards. The
# template says nothing about shared files, so the serialize-with mutex
# still applies to a side-quest card.
SIDE_QUEST_KEY = "side-quest"
# Optional string frontmatter key (R1): the card's lane, validated against
# the board-declared vocabulary in boardkit.toml. A board with no declared
# lanes accepts no lane keys.
LANE_KEY = "lane"
# Optional list frontmatter key (R3): qualified cross-board references,
# `<code>/<id>` (as in `tb/S91`). Informational only - the scheduler never
# blocks on another board's state - so shape is validated here and
# registry resolution happens in `boardkit check`, not at render time.
REFS_KEY = "refs"
REF_RE = re.compile(r"^([a-z0-9][a-z0-9-]*)/(\S+)$")
# R2 epic grouping: an epic is itself a card (`kind: epic`); member cards
# carry `epic: <id>` pointing at it. One level only - an epic card may not
# be a member of another epic, so cycles are unrepresentable.
KIND_KEY = "kind"
KINDS = {"card", "epic"}
EPIC_KEY = "epic"

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
# A pass log line, for the phantom-deferral warning only: a deferral is
# still cleared by the checklist tick alone, but a pass line landing after
# the deferral with the box left unticked is the shape sessions misread as
# a clear, so `boardkit check` calls it out. The legible shapes are the
# verdict right after the gate name - `Gate A passed`, `Gate A PASS`,
# `Gate A: PASS` - ended by punctuation (dashes and question marks
# included), a quote, a parenthetical, or the end of the entry;
# the lookahead keeps transitive uses (`Gate A passed the packet`) and
# compounds (`pass criteria`) from reading as verdicts. Wordings that put
# other words between the gate and the verdict are not legible; the
# PROCESS template names the canonical shape so log writers stay legible.
PASSED_RE = re.compile(
    rf"Gate\s+({GATE_TOKEN})(?:\s*:\s*|\s+)(?i:pass(?:ed)?)(?=\s*(?:[.,;:!?)('\"\u2013\u2014-]|$))"
)

# The deferral sweep reads the card's Log section only, and only its bullet
# entries: a card that documents the convention in its Scope or Notes prose
# is describing the syntax, not deferring its own gate. Inline-code spans
# come out before matching for the same reason.
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
LOG_HEADING = "log"
BULLET_RE = re.compile(r"^\s*[-*]\s+")
INLINE_CODE_RE = re.compile(r"`[^`]*`")

# R8: an unquoted `#` after whitespace starts a YAML comment, so
# `title: Record the #398 follow-up` parses as "Record the" and every
# consumer of the frontmatter (views, canary key, briefs) sees the
# truncated title. The fix is loud validation at parse, not renderer
# patching: compare the parsed title against the raw line and refuse.
# The matcher tolerates the key shapes YAML itself tolerates (leading
# indent, space before the colon), so those spellings cannot slip past
# the guard and truncate anyway.
TITLE_LINE_RE = re.compile(r"^[ \t]*title[ \t]*:[ \t]*(.*?)[ \t]*$", re.MULTILINE)


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
            f"{path.name}: '{SIDE_QUEST_KEY}' must be true or false, got {meta[SIDE_QUEST_KEY]!r}"
        )
    if LANE_KEY in meta and (not isinstance(meta[LANE_KEY], str) or not meta[LANE_KEY]):
        errors.append(f"{path.name}: '{LANE_KEY}' must be a non-empty string")
    if REFS_KEY in meta:
        refs = meta[REFS_KEY]
        if not isinstance(refs, list) or not all(isinstance(r, str) for r in refs):
            errors.append(f"{path.name}: '{REFS_KEY}' must be a list of strings")
        else:
            for ref in refs:
                if not REF_RE.match(ref):
                    errors.append(
                        f"{path.name}: ref '{ref}' is not a qualified <code>/<id> reference"
                    )
    if KIND_KEY in meta and (
        not isinstance(meta[KIND_KEY], str) or meta[KIND_KEY] not in KINDS
    ):
        errors.append(f"{path.name}: '{KIND_KEY}' must be one of {sorted(KINDS)}")
    title_line = TITLE_LINE_RE.search(text[4:end])
    if title_line is not None:
        raw_title = title_line.group(1)
        if "#" in raw_title:
            # The truncation signature: the parsed value is a prefix of the
            # raw line and the remainder begins at a '#'. A quoted or
            # anchored title never matches (the raw line starts with the
            # quote or anchor, not the parsed text), so legitimate YAML
            # passes; a comment-eaten title always does.
            parsed_title = str(meta.get("title") or "")
            remainder = raw_title[len(parsed_title) :].lstrip()
            if (
                parsed_title != raw_title
                and raw_title.startswith(parsed_title)
                and remainder.startswith("#")
            ):
                errors.append(
                    f"{path.name}: title is cut at '#' by YAML comment parsing "
                    f"(parsed as '{parsed_title}'); quote the whole title"
                )
    if EPIC_KEY in meta and (not isinstance(meta[EPIC_KEY], str) or not meta[EPIC_KEY]):
        errors.append(f"{path.name}: '{EPIC_KEY}' must be a card id string")
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


def check_dag(cards: dict[str, dict], errors: list[str], lanes: dict | None = None) -> None:
    lanes = lanes or {}
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
    # R2 epic membership: the target must exist, be an epic card, and an
    # epic may not be a member of anything (one level, cycle-free).
    for card in cards.values():
        target_id = card.get(EPIC_KEY)
        if target_id is None or not isinstance(target_id, str):
            continue
        if card.get(KIND_KEY) == "epic":
            errors.append(f"{card['_file']}: an epic card may not carry '{EPIC_KEY}'")
            continue
        target = cards.get(target_id)
        if target is None:
            errors.append(f"{card['_file']}: {EPIC_KEY} references unknown card '{target_id}'")
        elif target.get(KIND_KEY) != "epic":
            errors.append(
                f"{card['_file']}: {EPIC_KEY} target '{target_id}' is not an epic card "
                f"(kind: epic)"
            )
    # Finishing an epic means finishing its members (the dag closure rule):
    # an epic marked done with open members would render the initiative as
    # complete and incomplete at once.
    for card in cards.values():
        if card.get(KIND_KEY) != "epic" or card["status"] != "done":
            continue
        open_members = sorted(
            cid
            for cid, member in cards.items()
            if member.get(EPIC_KEY) == card["id"] and member["status"] != "done"
        )
        if open_members:
            errors.append(
                f"{card['_file']}: epic is done but member(s) "
                f"{', '.join(open_members)} are not"
            )
    # board invariants from PROCESS.md that the views cannot show. The
    # global WIP count skips side-quest cards (user-declared) and cards in
    # an exempt lane (board-declared); a lane's own `wip` cap counts every
    # in-progress card in the lane, exemptions included - exemption is from
    # the global count only, never from the lane's own cap.
    def _lane_exempt(card: dict) -> bool:
        lane = lanes.get(card.get(LANE_KEY, ""))
        return lane is not None and lane.exempt

    in_progress = [
        c
        for c in cards.values()
        if c["status"] == "in-progress" and not c.get(SIDE_QUEST_KEY, False) and not _lane_exempt(c)
    ]
    if len(in_progress) > WIP_LIMIT:
        names = ", ".join(sorted(c["id"] for c in in_progress))
        errors.append(
            f"WIP limit exceeded: {len(in_progress)} cards in-progress ({names}), limit {WIP_LIMIT}"
        )
    for lane in lanes.values():
        if lane.wip is None:
            continue
        in_lane = [
            c
            for c in cards.values()
            if c["status"] == "in-progress" and c.get(LANE_KEY) == lane.name
        ]
        if len(in_lane) > lane.wip:
            names = ", ".join(sorted(c["id"] for c in in_lane))
            errors.append(
                f"lane '{lane.name}' WIP exceeded: {len(in_lane)} cards in-progress "
                f"({names}), lane limit {lane.wip}"
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
                    f"{card['_file']}: serialized cards {card['id']} and {ref} are both in-progress"
                )
        if (
            card["status"] == "in-review"
            and card["lineage"] != "none"
            and not card.get("commit-range")
        ):
            errors.append(
                f"{card['_file']}: in-review with lineage {card['lineage']} but no commit-range set"
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


GATE_LETTER_RE = re.compile(r"^([A-Z])")


def gate_tokens(gates: str) -> tuple[str, ...]:
    """Parse a card's `gates` string into its gate letters.

    Accepts the qualified forms the board already allows - `U(code-review)`,
    `A (deferred)` - because the letter is what selects a route, and the
    qualifier is the board owner's note to themselves.
    """
    tokens = []
    for part in str(gates).split("->"):
        match = GATE_LETTER_RE.match(part.strip())
        if match:
            tokens.append(match.group(1))
    return tuple(tokens)


def remaining_gates(card: dict) -> list[str]:
    """The card's ladder letters whose checklist state has not cleared.

    Qualified occurrences are tracked independently: a box carrying a
    qualifier - `Gate U (mockup)` - clears exactly the same-qualified
    ladder token, so a passed `U(mockup)` no longer holds a later
    `U(launch)` open (or the reverse). Tokens without an exact-qualified
    box fall back to a per-letter pool: they clear only when the pool
    holds at least as many unclaimed boxes as there are unclaimed tokens
    of that letter and every pooled box is ticked. Either way, a ladder
    gate whose box was never written stays open rather than being
    absorbed by a ticked sibling of the same letter.
    """
    boxes: list[tuple[str, bool, bool]] = []  # (key, ticked, claimed)
    for line in card["_body"].splitlines():
        box = CHECKBOX_RE.match(line)
        if box is None:
            continue
        key = gate_key(box.group(2).removeprefix("Gate"))
        boxes.append((key, box.group(1).lower() == "x", False))
    tokens: list[tuple[str, str]] = []  # (letter, key) in ladder order
    for part in str(card.get("gates", "")).split("->"):
        match = GATE_LETTER_RE.match(part.strip())
        if match:
            tokens.append((match.group(1), gate_key(part.strip())))

    cleared: list[bool | None] = [None] * len(tokens)
    for ti, (_letter, key) in enumerate(tokens):
        if "(" not in key:
            continue
        exact = [bi for bi, (bkey, _, claimed) in enumerate(boxes) if bkey == key and not claimed]
        if exact:
            for bi in exact:
                boxes[bi] = (boxes[bi][0], boxes[bi][1], True)
            cleared[ti] = all(boxes[bi][1] for bi in exact)
    for letter in {t[0] for t in tokens}:
        open_tokens = [
            ti for ti, (tl, _) in enumerate(tokens) if tl == letter and cleared[ti] is None
        ]
        if not open_tokens:
            continue
        pool = [
            bi
            for bi, (bkey, _, claimed) in enumerate(boxes)
            if bkey[:1] == letter and not claimed
        ]
        state = len(pool) >= len(open_tokens) and all(boxes[bi][1] for bi in pool)
        for ti in open_tokens:
            cleared[ti] = state
    return [tokens[ti][0] for ti in range(len(tokens)) if not cleared[ti]]


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


def phantom_deferrals(cards: list[dict]) -> list[str]:
    """Warnings for open deferrals whose gate later logged a pass anyway.

    Clearing a deferral keys on the checklist tick, never on a pass log
    line, so a card can log `Gate A passed` after its deferral and still
    hold the gate open. That shape reads as ritual rather than rule (the
    session believes it cleared the gate), so `boardkit check` warns on it.
    Phase-scoped interim passes do not fire this: with no prior deferral on
    the gate, a pass line over an unticked box is the documented interim
    shape, not a phantom.
    """
    open_by_card: dict[str, set[str]] = {}
    for entry in deferred_gates(cards):
        open_by_card.setdefault(entry.card_id, set()).add(gate_key(entry.gate))
    warnings: list[str] = []
    for card in cards:
        open_keys = open_by_card.get(card["id"], set())
        if not open_keys:
            continue
        # Positions are (entry index, character offset), so a pass on a
        # continuation line of the deferral's own bullet still lands after
        # it, while a pass phrase inside the deferral's own text (say, in
        # its parenthesized reason) is not a verdict and never counts.
        last_deferral: dict[str, tuple[int, int]] = {}
        last_pass: dict[str, tuple[tuple[int, int], str]] = {}
        for index, entry in enumerate(log_entries(card["_body"])):
            deferral_spans = []
            for match in DEFERRED_RE.finditer(entry):
                last_deferral[gate_key(match.group(1))] = (index, match.end())
                deferral_spans.append(match.span())
            for match in PASSED_RE.finditer(entry):
                if any(start <= match.start() < end for start, end in deferral_spans):
                    continue
                gate = " ".join(match.group(1).split())
                last_pass[gate_key(match.group(1))] = ((index, match.start()), gate)
        for key, (position, gate) in sorted(last_pass.items()):
            deferred_at = last_deferral.get(key)
            if key in open_keys and deferred_at is not None and deferred_at <= position:
                warnings.append(
                    f"{card['_file']}: Gate {gate} logged as passed after its"
                    " deferral, but its checklist box is unticked, so the"
                    " deferral is still open. Tick the box if the gate passed"
                    " over the card's full scope, or leave it and the deferral"
                    " stands."
                )
    return warnings


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


# S16: statuses whose view rows carry the card's current gate position.
ACTIVE_STATUSES = {"ready", "in-progress", "in-review"}


def gate_cell(card: dict) -> str:
    """The Gates cell for a view row: the ladder, plus `@ <position>`.

    The position is the first ladder letter whose checklist state has not
    cleared (`remaining_gates`), so a cold reader of the views alone can
    answer "which gate is this card parked at". Backlog and done cards
    render the bare ladder - nothing is parked.
    """
    gates = str(card["gates"])
    if card["status"] not in ACTIVE_STATUSES:
        return gates
    remaining = remaining_gates(card)
    return f"{gates} @ {remaining[0]}" if remaining else f"{gates} @ (all ticked)"


def _charter_lines(config: Config) -> list[str]:
    """The R10 charter block rendered at the top of a generated view."""
    charter = config.charter
    if charter is None:
        return []
    lines = [
        f"CHARTER - owns: {charter.owns}",
        f"Not here: {charter.not_}",
    ]
    lines.extend(
        f"Route {code} -> {description}" for code, description in sorted(charter.route.items())
    )
    lines.append("Admission test: where does the diff land.")
    lines.append("")
    return lines


def render_index(cards: list[dict], config: Config) -> str:
    lines = [
        "# Card index",
        "",
        "Generated by `boardkit render`; do not edit by hand.",
        "Run it after any card status change; `--check` gates commits.",
        "Ready requires every entry in Depends to be done; the session",
        "running the board promotes eligible cards (PROCESS.md,",
        "Delegation protocol).",
        "",
        *_charter_lines(config),
    ]
    show_lane = bool(config.board.lanes)
    if show_lane:
        lines += [
            "| ID | Title | Lane | Status | Depends | Executor | Gates |",
            "|---|---|---|---|---|---|---|",
        ]
    else:
        lines += [
            "| ID | Title | Status | Depends | Executor | Gates |",
            "|---|---|---|---|---|---|",
        ]
    for c in cards:
        deps = ", ".join(c["depends"]) or "-"
        lane_cell = f" {c.get(LANE_KEY) or '-'} |" if show_lane else ""
        lines.append(
            f"| [{c['id']}]({c['_file']}) | {c['title']} |{lane_cell} {c['status']} "
            f"| {deps} | {c['executor']} | {gate_cell(c)} |"
        )
    lines.append("")
    epics = [c for c in cards if c.get(KIND_KEY) == "epic"]
    if epics:
        lines += ["## Epics", ""]
        for epic in epics:
            members = [c for c in cards if c.get(EPIC_KEY) == epic["id"]]
            done = sum(1 for m in members if m["status"] == "done")
            roster = (
                ", ".join(f"{m['id']} ({m['status']})" for m in members)
                or "no member cards yet"
            )
            lines.append(
                f"- [{epic['id']}]({epic['_file']}) {epic['title']} - "
                f"{done}/{len(members)} done - {roster}"
            )
        lines.append("")
    return "\n".join(lines)


def render_board(cards: list[dict], config: Config) -> str:
    parts = [BOARD_HEADER]
    charter = _charter_lines(config)
    if charter:
        # kanban plugins ignore %% comments, so the charter rides one.
        parts.append("\n%% " + " / ".join(line for line in charter if line) + " %%\n")
    for status in STATUSES:
        parts.append(f"\n## {COLUMN_TITLES[status]}\n")
        for c in (c for c in cards if c["status"] == status):
            deps = ", ".join(c["depends"]) or "none"
            lane = c.get(LANE_KEY)
            lane_note = f" Lane: {lane}." if lane else ""
            parts.append(
                f"- [ ] **{c['id']}** [{c['title']}]({c['_file']})\n"
                f"\tDepends: {deps}. Gates: {gate_cell(c)}. Executor: {c['executor']}.{lane_note}\n"
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
        if rows:
            # S16: the key answers gate position from the same computation
            # the views render, so the two can never disagree.
            for c in rows:
                remaining = remaining_gates(c)
                position = f" (at Gate {remaining[0]})" if remaining else " (all gates ticked)"
                lines.append(f"{_card_line(c)}{position}")
        else:
            lines.append("- none")
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


def view_drift(config: Config, views: dict[str, str]) -> list[str]:
    """Views on disk that no longer match what the cards render to."""
    errors: list[str] = []
    for name, want in views.items():
        path = config.board.cards_dir / name
        if not path.exists():
            errors.append(f"{name}: missing; run `boardkit render` to generate")
        elif path.read_text(encoding="utf-8") != want:
            errors.append(f"{name}: drift from frontmatter; regenerate (drags count)")
    stale_deferred = config.board.cards_dir / DEFERRED_VIEW
    if DEFERRED_VIEW not in views and stale_deferred.exists():
        errors.append(
            f"{DEFERRED_VIEW}: stale; no gate is open-deferred any more, run `boardkit render`"
        )
    return errors


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
        lane = card.get(LANE_KEY)
        if lane is not None and isinstance(lane, str) and lane not in config.board.lanes:
            declared = ", ".join(sorted(config.board.lanes)) or "none declared"
            errors.append(f"{card['_file']}: lane '{lane}' not in board lanes ({declared})")
    if errors:
        raise BoardError(errors)

    check_dag(cards, errors, config.board.lanes)
    if errors:
        raise BoardError(errors)

    ordered = sorted(cards.values(), key=lambda c: sort_key(c, config))
    views = {
        "INDEX.md": render_index(ordered, config),
        "board.md": render_board(ordered, config),
        GRAPH_VIEW: render_graph(ordered, config),
    }
    if deferred:
        views[DEFERRED_VIEW] = render_deferred(deferred_gates(ordered))
    return BoardResult(cards=ordered, views=views)


def render_graph(cards: list[dict], config: Config) -> str:
    """The standing Mermaid graph view (R9): whole board, status-colored.

    Epic subgraph clusters first (an epic card and its members share a
    cluster), then lane clusters for the rest - a member's epic wins over
    its lane because Mermaid subgraphs cannot overlap, and the epic is
    the initiative a wayfinding reader is tracing. Solid arrows are
    `depends` edges, dotted links are `serialize-with` pairs.
    """
    from boardkit.dag import MERMAID_CLASSES, node_line

    lines = [
        "# Board graph",
        "",
        "Generated by `boardkit render`; do not edit by hand.",
        "Status-colored dependency graph. Solid arrows: depends.",
        "Dotted links: serialize-with (never both in progress).",
        "Goal-scoped wave plans: `boardkit dag --to <id> --render`.",
        "",
        "```mermaid",
        "flowchart TD",
        *(f"  {c}" for c in MERMAID_CLASSES),
    ]
    clustered: set[str] = set()
    for epic in (c for c in cards if c.get(KIND_KEY) == "epic"):
        group = [epic] + [c for c in cards if c.get(EPIC_KEY) == epic["id"]]
        lines.append(f'  subgraph epic_{epic["id"]}["epic: {epic["id"]}"]')
        lines.extend(f"    {node_line(c)}" for c in group)
        lines.append("  end")
        clustered.update(c["id"] for c in group)
    rest = [c for c in cards if c["id"] not in clustered]
    if config.board.lanes:
        by_lane: dict[str, list[dict]] = {}
        for card in rest:
            by_lane.setdefault(card.get(LANE_KEY) or "", []).append(card)
        for lane in sorted(by_lane):
            if lane:
                lines.append(f'  subgraph lane_{lane}["{lane}"]')
                lines.extend(f"    {node_line(c)}" for c in by_lane[lane])
                lines.append("  end")
        lines.extend(f"  {node_line(c)}" for c in by_lane.get("", []))
    else:
        lines.extend(f"  {node_line(c)}" for c in rest)
    ids = {c["id"] for c in cards}
    for card in cards:
        lines.extend(f"  {dep} --> {card['id']}" for dep in card["depends"] if dep in ids)
        lines.extend(
            f"  {card['id']} -.- {ref}"
            for ref in card["serialize-with"]
            if ref in ids and card["id"] < ref
        )
    lines.append("```")
    lines.append("")
    return "\n".join(lines)
