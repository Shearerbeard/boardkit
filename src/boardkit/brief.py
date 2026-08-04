"""Generate a card's dispatch brief from the board and the contract.

A dispatch brief used to be hand-assembled: someone pasted the card, then
restated the process rules from memory. Restated policy goes stale silently,
so nothing here restates anything. Every clause is extracted from the
consumer's own PROCESS.md and MODEL-CLASSES.md at generation time, and a
missing anchor is a loud failure rather than a quietly shorter brief.

The output is deterministic and carries no timestamp, so two runs over an
unchanged board produce identical bytes and a brief can be diffed. It does
carry the contract digest: a brief whose digest differs from `boardkit
doctor`'s was generated against a contract that has since moved.

Gate A is the honest limit. A card records which gates it must pass but not
whether it produced code or prose, so the brief prints both Gate A routes
and quotes the rule for choosing between them.
"""

from __future__ import annotations

import posixpath
import re
from pathlib import Path

from boardkit.board import LINK_RE, build_board
from boardkit.config import CONFIG_FILENAME, Config
from boardkit.contract import (
    CONTRACT_DOCS,
    ContractError,
    Resolution,
    contract_digest,
    read_text_or_none,
    resolve_role,
    sections,
    staging_contract,
)

CONTRACT_DOC_DESTS = dict(CONTRACT_DOCS)
PROCESS_DOC = CONTRACT_DOC_DESTS["PROCESS.md"]
MODEL_CLASSES_DOC = CONTRACT_DOC_DESTS["MODEL-CLASSES.md"]

# Anchors into the consumer's own docs. Each is the opening of a paragraph
# the brief quotes verbatim; if one moves, the brief fails rather than
# shipping a clause it invented.
DISPATCH_BRIEF_ANCHOR = "A dispatch brief for a subagent contains"
DECISION_AUTHORITY_ANCHOR = "Decision authority stays with the board owner"
GATE_A_ROUTING_ANCHOR = "Gate A routing follows what the artifact is judged on"

GATES_SECTION = "Gates"
INVARIANTS_SECTION = "Invariants"

# Which contract roles a declared gate token pulls into the brief. Gate A
# maps to two because the card does not say which kind of artifact it made.
GATE_ROLES = {
    "A": ("code-review", "prose-review"),
    "F": ("frontier-review",),
    "D": ("drift-audit",),
}

GATE_TOKEN_RE = re.compile(r"^([A-Z])")
# A bullet ends at the next gate bullet or at any heading: the Gates section
# body includes its own subsections, and Gate U is the last bullet before one.
GATE_BULLET_RE = re.compile(
    r"^- Gate ([A-Z])\b.*?(?=^- Gate [A-Z]\b|^#{1,6} |\Z)", re.DOTALL | re.MULTILINE
)
BULLET_RE = re.compile(r"^- .*?(?=^- |\Z)", re.DOTALL | re.MULTILINE)


class BriefError(Exception):
    """The brief could not be built from what the repo actually contains."""


def section(text: str, heading: str, source: Path) -> str:
    body = sections(text).get(heading)
    if body is None:
        raise BriefError(f"{source}: no '{heading}' section; the brief cannot quote it")
    return body


def paragraph_at(text: str, anchor: str, source: Path) -> str:
    """The whole paragraph that starts with `anchor`, verbatim.

    Paragraphs are blank-line separated, which is how the shipped docs are
    written; quoting the paragraph rather than the sentence keeps the clause
    with its own qualifications.
    """
    for paragraph in text.split("\n\n"):
        stripped = paragraph.strip()
        if stripped.startswith(anchor):
            return stripped
    raise BriefError(
        f"{source}: no paragraph starting '{anchor}'. The brief quotes that "
        "clause rather than restating it, so it cannot be generated without it."
    )


def bullet_at(text: str, anchor: str, source: Path) -> str:
    """The whole bullet whose text starts with `anchor`, verbatim."""
    for bullet in BULLET_RE.findall(text):
        if bullet.strip().startswith(f"- {anchor}"):
            return _dedent_bullet(bullet)
    raise BriefError(f"{source}: no bullet starting '{anchor}'; the brief cannot quote it")


def _dedent_bullet(bullet: str) -> str:
    return "\n".join(line.rstrip() for line in bullet.strip().splitlines())


def gate_tokens(gates: str) -> tuple[str, ...]:
    """Parse a card's `gates` string into its gate letters.

    Accepts the qualified forms the board already allows - `U(code-review)`,
    `A (deferred)` - because the letter is what selects a route, and the
    qualifier is the board owner's note to themselves.
    """
    tokens = []
    for part in str(gates).split("->"):
        match = GATE_TOKEN_RE.match(part.strip())
        if match:
            tokens.append(match.group(1))
    return tuple(tokens)


def gate_bullets(process_text: str, tokens: tuple[str, ...]) -> list[str]:
    """The Gates-section bullet for each declared gate, in declared order."""
    section_text = section(process_text, GATES_SECTION, PROCESS_DOC)
    by_letter = {
        match.group(1): _dedent_bullet(match.group(0))
        for match in GATE_BULLET_RE.finditer(section_text)
    }
    quoted = []
    for token in tokens:
        if token not in by_letter:
            raise BriefError(
                f"{PROCESS_DOC}: the card declares Gate {token}, which the Gates "
                "section does not define; the brief cannot quote its rule"
            )
        quoted.append(by_letter[token])
    return quoted


def _repo_relative(cards_rel: Path, target: str) -> str:
    """A card-relative link as a repo-relative path.

    Resolved lexically, not on disk: the brief must read the same in a clone,
    and a symlinked checkout must not change what it prints.
    """
    return posixpath.normpath((cards_rel / target).as_posix())


def reference_links(body: str) -> list[str]:
    """Relative link targets in a card body, deduped, in first-appearance order."""
    found: dict[str, None] = {}
    for match in LINK_RE.finditer(body):
        target = match.group(1)
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        found.setdefault(target, None)
    return list(found)


def _role_resolutions(
    config: Config, tokens: tuple[str, ...]
) -> list[tuple[str, Resolution | ContractError]]:
    """(label, resolution) for the executor plus every gate-bound role.

    A role that cannot resolve is reported in place rather than aborting the
    brief: the executor still needs dispatching, and a broken reviewer route
    is exactly what the board owner should see printed.
    """
    wanted = ["executor"]
    for token in tokens:
        wanted.extend(role for role in GATE_ROLES.get(token, ()) if role not in wanted)
    resolved = []
    for role in wanted:
        try:
            resolved.append((role, resolve_role(config, role)))
        except ContractError as exc:
            resolved.append((role, exc))
    return resolved


def _render_resolution(role: str, resolution: Resolution | ContractError) -> list[str]:
    if isinstance(resolution, ContractError):
        return [f"- **{role}**: UNRESOLVED - {resolution}"]
    route = resolution.route
    skill = route.skill if route.skill else "none (this transport loads no child skill)"
    lines = [
        f"- **{role}** -> `{route.name}`",
        f"  - adapter: `{route.adapter}`",
        f"  - skill: {skill}",
        f"  - pin source: `{route.pin_source}`",
        f"  - staging: `{route.staging}` - {staging_contract(route.staging)}",
    ]
    lines.extend(f"  - preflight: `{command}`" for command in route.preflight)
    if not route.preflight:
        lines.append("  - preflight: none")
    if resolution.fallbacks:
        names = ", ".join(f"`{f.name}`" for f in resolution.fallbacks)
        lines.append(f"  - fallback: {names}")
    return lines


def _require_doc(config: Config, dest: Path) -> str:
    text = read_text_or_none(config.root / dest)
    if text is None:
        raise BriefError(
            f"{dest} is missing or unreadable; the brief quotes this repo's own "
            "contract docs and cannot be generated without them"
        )
    return text


def build_brief(config: Config, card_id: str) -> str:
    """Assemble one card's dispatch brief. Deterministic and timestamp-free."""
    result = build_board(config)
    card = next((c for c in result.cards if c["id"] == card_id), None)
    if card is None:
        known = ", ".join(sorted(c["id"] for c in result.cards)) or "none"
        raise BriefError(f"unknown card id '{card_id}'; this board declares: {known}")

    process = _require_doc(config, PROCESS_DOC)
    model_classes = _require_doc(config, MODEL_CLASSES_DOC)

    card_path = (config.board.cards_dir / card["_file"]).relative_to(config.root)
    tokens = gate_tokens(card.get("gates", ""))
    digest = contract_digest(config)

    lines = [
        f"# Dispatch brief: {card_id} — {card['title']}",
        "",
        f"- card: `{card_path.as_posix()}`",
        f"- contract: v{config.contract.version}",
        f"- digest: `{digest}`",
        f"- sources: `{CONFIG_FILENAME}`, "
        + ", ".join(f"`{dest.as_posix()}`" for _template, dest in CONTRACT_DOCS),
        "",
        "## Card",
        "",
        "The card, verbatim. It is the specification; nothing below overrides it.",
        "",
        "```markdown",
        (config.root / card_path).read_text(encoding="utf-8").rstrip("\n"),
        "```",
        "",
        "## Reference material",
        "",
    ]

    links = reference_links(card["_body"])
    if links:
        lines.append("Read these rather than a summary of them:")
        lines.append("")
        cards_rel = config.board.cards_dir.relative_to(config.root)
        lines.extend(f"- `{_repo_relative(cards_rel, target)}`" for target in links)
    else:
        lines.append("The card links to no reference material.")
    lines.append("")

    lines.append("## Routes")
    lines.append("")
    for role, resolution in _role_resolutions(config, tokens):
        lines.extend(_render_resolution(role, resolution))
    if "A" in tokens:
        # the card records no artifact kind, so both Gate A routes print and
        # the repo's own rule for choosing between them is quoted alongside
        invariants = section(model_classes, INVARIANTS_SECTION, MODEL_CLASSES_DOC)
        lines.append("")
        lines.append(_quote(bullet_at(invariants, GATE_A_ROUTING_ANCHOR, MODEL_CLASSES_DOC)))
    lines.append("")

    lines.append("## Contract clauses")
    lines.append("")
    lines.append(f"From `{PROCESS_DOC.as_posix()}`, quoted:")
    lines.append("")
    for clause in (
        paragraph_at(process, DISPATCH_BRIEF_ANCHOR, PROCESS_DOC),
        paragraph_at(process, DECISION_AUTHORITY_ANCHOR, PROCESS_DOC),
    ):
        lines.append(_quote(clause))
        lines.append("")
    for bullet in gate_bullets(process, tokens):
        lines.append(_quote(bullet))
        lines.append("")

    lines.append("## Provenance")
    lines.append("")
    lines.append("Regenerate this brief rather than editing it. Every clause above is")
    lines.append("extracted from this repo's own docs, so an edit here forks the contract")
    lines.append("into a copy that nothing re-checks.")
    lines.append("")
    lines.append(f"Generated at contract digest `{digest}`. A brief whose digest differs")
    lines.append("from `boardkit doctor`'s was built against a contract that has moved.")
    return "\n".join(lines) + "\n"


def _quote(text: str) -> str:
    return "\n".join(f"> {line}" if line else ">" for line in text.splitlines())
