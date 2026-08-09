"""R9 goal-directed graph queries over the board.

`boardkit dag --to <id>` answers from the cards alone: the goal's
ancestor closure, its unblocked frontier, a wave partition over the
remaining work, and which gates sit on which edges. In-process stdlib
traversal, file-backed, no daemon, no external graph store; SQLite is a
documented escape hatch only, and nothing here reaches for it.

Gates-on-edges reading: an edge `dep --> card` means the card waits for
`dep` to finish, and finishing `dep` means passing its remaining gates -
so the edge is annotated with `dep`'s unticked ladder letters. A wave
plan therefore shows where reviews land, not just order.

INCOMPLETENESS (plan of record): lane clusters only. Epic clustering and
`--to <epic>` land in the post-R2 pass; R9 is recorded shipped-incomplete
until then.
"""

from __future__ import annotations

from boardkit.board import remaining_gates

STATUS_CLASS = {
    "backlog": "backlog",
    "ready": "ready",
    "in-progress": "inprogress",
    "in-review": "inreview",
    "done": "done",
}

MERMAID_CLASSES = [
    "classDef backlog fill:#e2e8f0,color:#1a202c;",
    "classDef ready fill:#bee3f8,color:#1a202c;",
    "classDef inprogress fill:#fbd38d,color:#1a202c;",
    "classDef inreview fill:#d6bcfa,color:#1a202c;",
    "classDef done fill:#c6f6d5,color:#1a202c;",
]


class DagError(Exception):
    """A dag query that cannot be answered from this board."""


def ancestor_closure(cards: dict[str, dict], goal: str) -> set[str]:
    """The goal plus everything it transitively depends on."""
    if goal not in cards:
        known = ", ".join(sorted(cards)) or "none"
        raise DagError(f"unknown card id '{goal}'; this board declares: {known}")
    seen: set[str] = set()
    stack = [goal]
    while stack:
        cid = stack.pop()
        if cid in seen:
            continue
        seen.add(cid)
        stack.extend(dep for dep in cards[cid]["depends"] if dep in cards)
    return seen


def unblocked_frontier(cards: dict[str, dict], closure: set[str]) -> list[str]:
    """Closure cards that are not done and wait on nothing unfinished."""
    return sorted(
        cid
        for cid in closure
        if cards[cid]["status"] != "done"
        and all(
            cards[dep]["status"] == "done" for dep in cards[cid]["depends"] if dep in cards
        )
    )


def wave_partition(cards: dict[str, dict], closure: set[str]) -> list[list[str]]:
    """Remaining closure cards grouped into dispatchable waves.

    Wave N holds cards whose unfinished dependencies all sit in earlier
    waves (longest-path layering). Done cards partition into no wave -
    the plan is the work left, not the history. Cycles cannot reach here:
    build_board rejects them before any query runs.
    """
    remaining = {cid for cid in closure if cards[cid]["status"] != "done"}
    level: dict[str, int] = {}

    def _level(cid: str) -> int:
        if cid in level:
            return level[cid]
        deps = [d for d in cards[cid]["depends"] if d in remaining]
        level[cid] = 1 + max((_level(d) for d in deps), default=0)
        return level[cid]

    waves: dict[int, list[str]] = {}
    for cid in remaining:
        waves.setdefault(_level(cid), []).append(cid)
    return [sorted(waves[depth]) for depth in sorted(waves)]


def closure_edges(cards: dict[str, dict], closure: set[str]) -> list[tuple[str, str, str]]:
    """(dep, card, gate annotation) for every dependency edge inside the closure.

    The annotation is the tail's remaining gate letters - empty for a done
    dependency, whose gates all passed.
    """
    edges = []
    for cid in sorted(closure):
        for dep in cards[cid]["depends"]:
            if dep not in closure:
                continue
            gates = "" if cards[dep]["status"] == "done" else ",".join(remaining_gates(cards[dep]))
            edges.append((dep, cid, gates))
    return edges


def render_dag_text(cards: dict[str, dict], goal: str) -> str:
    closure = ancestor_closure(cards, goal)
    frontier = unblocked_frontier(cards, closure)
    waves = wave_partition(cards, closure)
    edges = closure_edges(cards, closure)

    lines = [f"dag --to {goal}: {len(closure)} cards in the ancestor closure", ""]
    lines.append("closure:")
    for cid in sorted(closure):
        card = cards[cid]
        lane = card.get("lane")
        lane_note = f" [lane {lane}]" if lane else ""
        lines.append(f"  {cid} ({card['status']}){lane_note} {card['title']}")
    lines.append("")
    lines.append("unblocked frontier: " + (", ".join(frontier) or "none (all done or blocked)"))
    lines.append("")
    if waves:
        lines.append("wave plan (gates on edges are the dependency's remaining gates):")
        for index, wave in enumerate(waves, start=1):
            lines.append(f"  wave {index}: {', '.join(wave)}")
        for dep, cid, gates in edges:
            if cards[dep]["status"] != "done":
                annotation = f" [{gates}]" if gates else ""
                lines.append(f"    {dep}{annotation} -> {cid}")
    else:
        lines.append("wave plan: nothing remaining; the closure is done.")
    lines.append("")
    return "\n".join(lines)


def node_line(card: dict) -> str:
    title = card["title"].replace('"', "'")
    if len(title) > 34:
        title = title[:33] + "…"
    return f'{card["id"]}["{card["id"]} {title}"]:::{STATUS_CLASS[card["status"]]}'


def render_dag_mermaid(cards: dict[str, dict], goal: str) -> str:
    """The goal-scoped wave plan as Mermaid - the agent-to-user artifact."""
    closure = ancestor_closure(cards, goal)
    waves = wave_partition(cards, closure)
    lines = ["```mermaid", "flowchart TD", *(f"  {c}" for c in MERMAID_CLASSES)]
    for index, wave in enumerate(waves, start=1):
        lines.append(f'  subgraph wave{index}["wave {index}"]')
        lines.extend(f"    {node_line(cards[cid])}" for cid in wave)
        lines.append("  end")
    done = sorted(cid for cid in closure if cards[cid]["status"] == "done")
    lines.extend(f"  {node_line(cards[cid])}" for cid in done)
    for dep, cid, gates in closure_edges(cards, closure):
        arrow = f' -->|"{gates}"| ' if gates else " --> "
        lines.append(f"  {dep}{arrow}{cid}")
    lines.append("```")
    return "\n".join(lines) + "\n"
