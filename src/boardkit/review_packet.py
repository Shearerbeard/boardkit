"""Generate a per-card, PR-style review packet from its commit range.

Ported from terminalbench-aura's scripts/card_review_packet.py. Reads
the card's `commit-range` frontmatter field and writes to the
configured review output directory (gitignored working material):

  NN-<shortsha>.diff   one full patch per commit, in range order
  full-range.diff      the whole card as one diff
  REVIEW.md            the ranked review guide, then the design record
                       for a card that names one, then the indexed
                       commit listing with per-file hunk pointers

REVIEW.md leads with the guide because a packet that opens on commit
stats leaves the reader to find the 80/20 themselves. The guide ranks
the range's files by the lines they change in its net diff, names the
prefix that carries most of that churn, and flags the files a later
commit in the range rewrote. It is an entry point over an indexed
packet, not the packet's one path: the commit listing below it still
carries every commit and every file, for a reader who works the range
commit by commit. A card that supplies its own reading order takes the
entry point back, and the churn concentration then reports rather than
instructs - one guide never gives two contradictory places to start.
Where the net diff is binary there are no line counts to rank on, and
the guide says so rather than letting absent counts read as zero.

Two card-body conventions feed the packet, both read from the card the
packet covers:

  ## Review order    one bullet per repo-relative path in inline code.
                     The author's judgment call about reading order,
                     which churn ranking cannot make. Named files lead
                     the guide, in the order given; the rest follow by
                     churn.
  ## Design record   a card-relative markdown link to the typed-holes
                     design record. The packet links it above the
                     commit listing and lifts the record's own
                     type-relationship section into the packet.

Both live in the card body rather than in frontmatter: the card already
links its evidence and plans there, `boardkit check` already validates
that a card-relative link resolves, and neither needs a schema change.

Diff and file references render as markdown links relative to the
packet's own directory, so an editor that follows links jumps from a
guide or log line to the file or patch it names. A hunk anchor keeps
its `path:line` token as the link text, because that token is what an
editor and a terminal jump on. A file the range deletes has no
working-tree target and renders as inline code instead of a link that
would not resolve. Every link this module writes goes out through
`markdown_link`, because a git path may legally hold brackets, spaces,
parentheses, or `#`: it escapes the label, percent-encodes a `#` in the
path (angle brackets fix how markdown parses that, never the fragment a
follower would then read), and picks the destination form for the rest.
A section lifted out of a design record has its own relative targets
rebased through the same function, because they were written against the
record's directory rather than this one.

The repo diffed against and the output directory come from the loaded
Config's [review] section; there is no hardcoded default repo.
"""

from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Iterator
from pathlib import Path
from typing import NamedTuple

import yaml

from boardkit.board import LINK_RE
from boardkit.config import Config
from boardkit.contract import sections

RANGE_RE = re.compile(r"^.+\.\..+$")
HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
SUFFIX_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_HUNKS_PER_FILE = 5
# Everything this module writes, and the only things a rerun may delete. The
# per-commit index is zero-padded to two digits but is not capped there: a
# card with a hundred commits writes `100-<sha>.diff`, so the sweep matches
# two or more digits. Anything else in the directory is reviewer material.
GENERATED_DIFF_RE = re.compile(r"^\d{2,}-[0-9a-f]{7,40}\.diff$")
GENERATED_NAMES = ("full-range.diff", "REVIEW.md")

# The card-body sections the packet reads. Headings, not frontmatter keys:
# see the module docstring for why.
REVIEW_ORDER_SECTION = "Review order"
DESIGN_RECORD_SECTION = "Design record"
# The design record's own section the type-relationship view is lifted from.
# The record is the source of truth for how the introduced types relate, so
# the packet transcribes that section rather than inferring relationships
# from the diff.
TYPE_SECTION_RE = re.compile(r"^type[\s-]*(?:relationships?|map)\b", re.IGNORECASE)
# Share of the range's net churn the guide's focus line aims to account for,
# and the most files it will name reaching for it.
FOCUS_SHARE = 0.8
MAX_FOCUS_FILES = 5
BULLET_RE = re.compile(r"^\s*[-*]\s+(.*)$")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
# Link emission. Brackets in a label end it early, so they are escaped;
# destinations holding any of these need CommonMark's angle-bracket form.
# `#` is not among them: a `#` in a path is percent-encoded before this
# runs, and a `#` that reaches here is a fragment separator doing its job.
LABEL_ESCAPE_RE = re.compile(r"([\[\]])")
ANGLE_DESTINATION_RE = re.compile(r"[ ()<>\\]")
# An inline markdown link (image links included) in a lifted design-record
# section, split so only its destination is rewritten: group 3 carries any
# title and the closing paren through byte-for-byte. All three CommonMark
# title quotings are matched, since a title's leading space would otherwise
# end the destination and leave the link record-relative. Reference-style
# links and link-definition lines are left alone: this rewrites what it can
# parse with certainty and nothing else.
RECORD_LINK_RE = re.compile(
    r"(!?\[[^\]]*\]\()"
    r"(<[^<>]*>|[^()\s]+)"
    r"((?:(?:[ \t]+|[ \t]*\n[ \t]*)(?:\"[^\"]*\"|'[^']*'|\([^()]*\)))?[ \t]*\))"
)
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


class Commit(NamedTuple):
    sha: str
    subject: str


class FileChurn(NamedTuple):
    """One file's churn across a commit range.

    `raw` is the lines the per-commit patches touch, `net` the lines the
    range's net diff keeps. When a later commit in the range rewrites what
    an earlier one wrote, raw exceeds net and the difference is the part a
    reader can take from the net diff instead of hunk by hunk.

    `binary` marks a file the range's NET diff is binary for, which is the
    diff both counts describe. Git reports no line counts there, and zero
    counts are not the same fact as zero lines changed, so every reader of
    the counts checks this flag first. A file binary only in some
    intermediate commit is not marked: its net diff has real counts, and
    those are what the guide reports.

    One consequence rides in `raw`: a binary commit contributes no lines
    to it, so the raw count of a file that was binary at any point in the
    range is understated, and can even fall below `net`. Nothing invents
    numbers to cover that - the guide drops the raw figure from an entry
    where it cannot account for the net one.
    """

    path: str
    net: int
    raw: int
    commits: int
    binary: bool = False

    @property
    def superseded(self) -> bool:
        """True when a later commit in the range rewrote part of this file.

        Deliberately narrow: one commit cannot supersede itself, and files
        whose commits touch disjoint lines keep raw == net and are not
        flagged. Over-flagging would tell a reader to skip hunks that still
        matter, which is the failure this flag exists to avoid. A binary
        file is never flagged: its counts are absent rather than small, so
        `net < raw` there compares two numbers that mean nothing - a text
        file replaced by binary content would otherwise read as superseded.
        """
        return not self.binary and self.commits >= 2 and self.net < self.raw


class Packet(NamedTuple):
    """Everything REVIEW.md renders from, resolved once by the builder.

    `card_sections` is the card body walked once into heading -> body, so
    the two conventions the packet reads out of it share that walk.
    """

    meta: dict
    commit_range: str
    repo: Path
    commits: list[Commit]
    outdir: Path
    cards_dir: Path
    card_sections: dict[str, str]


class ReviewPacketError(Exception):
    """Raised for a single fatal error while building the review packet."""


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise ReviewPacketError(f"git {' '.join(args)} failed in {repo}: {result.stderr.strip()}")
    return result.stdout


def load_card(cards_dir: Path, card_id: str) -> dict:
    matches = sorted(cards_dir.glob(f"{card_id.lower()}-*.md"))
    if not matches:
        raise ReviewPacketError(f"no card file matching '{card_id.lower()}-*.md' in {cards_dir}")
    if len(matches) > 1:
        raise ReviewPacketError(f"ambiguous card id {card_id}: {[m.name for m in matches]}")
    text = matches[0].read_text(encoding="utf-8")
    end = text.find("\n---\n", 4)
    if not text.startswith("---\n") or end < 0:
        raise ReviewPacketError(f"{matches[0].name}: missing or unterminated frontmatter")
    meta = yaml.safe_load(text[4:end])
    if not isinstance(meta, dict):
        raise ReviewPacketError(f"{matches[0].name}: frontmatter is not a mapping")
    meta["_file"] = matches[0].name
    meta["_body"] = text[end + 5 :]
    return meta


def validate_commit_range(repo: Path, commit_range: str) -> None:
    """A range must be A..B and both sides must resolve to commits."""
    if not RANGE_RE.match(commit_range):
        raise ReviewPacketError(f"'{commit_range}' is not a commit range (expected A..B)")
    left, _, right = commit_range.partition("..")
    for side in (left, right):
        if not side:
            raise ReviewPacketError(f"'{commit_range}' is not a commit range (expected A..B)")
        try:
            git(repo, "rev-parse", "--verify", f"{side}^{{commit}}")
        except ReviewPacketError as exc:
            raise ReviewPacketError(
                f"commit range '{commit_range}' does not resolve: {exc}"
            ) from exc


def commit_list(repo: Path, commit_range: str) -> list[Commit]:
    lines = git(repo, "log", "--reverse", "--format=%H%x09%s", commit_range).splitlines()
    commits = [
        Commit(sha=sha, subject=subject) for sha, subject in (line.split("\t", 1) for line in lines)
    ]
    if not commits:
        raise ReviewPacketError(f"range {commit_range} contains no commits in {repo}")
    return commits


def strip_prefix(target: str, prefix: str) -> str | None:
    """Resolve a ---/+++ path, handling git's quoted form; None if no match.

    git guards a header path that contains a space with a trailing tab, so
    the unified header stays parseable. That tab is not part of the name,
    and left on it rides into every reference the packet renders for the
    file. A name holding a real tab comes through the quoted form instead,
    where the tab is two characters and this split cannot reach it.
    """
    target = target.split("\t", 1)[0]
    if target.startswith(f'"{prefix}') and target.endswith('"'):
        return target[len(prefix) + 1 : -1]
    if target.startswith(prefix):
        return target[len(prefix) :]
    return None


def hunk_pointers(repo: Path, sha: str) -> dict[str, list[int]]:
    """Map each file in the commit to the new-side start line of its hunks.

    A deleted file gets an empty anchor list (its +++ side is /dev/null,
    so it has no new-side lines to point at).
    """
    pointers: dict[str, list[int]] = {}
    current: str | None = None
    old_path: str | None = None
    for line in git(repo, "show", "--unified=0", "--format=", sha).splitlines():
        if line.startswith("diff --git"):
            current = None
            old_path = None
        elif line.startswith("--- "):
            old_path = strip_prefix(line[4:], "a/")
        elif line.startswith("+++ "):
            current = strip_prefix(line[4:], "b/")
            if current is not None:
                pointers[current] = []
            elif line[4:] == "/dev/null" and old_path is not None:
                pointers[old_path] = []
        elif current is not None and (match := HUNK_RE.match(line)):
            pointers[current].append(int(match.group(1)))
    return pointers


def _numstat_rows(output: str) -> Iterator[tuple[int, int, str, bool]]:
    """(added, deleted, path, binary) per numstat row.

    git reports a binary file's counts as `-`. That is the absence of a
    line count, not a count of zero, so the flag rides alongside the
    zeroed numbers rather than being flattened into them.
    """
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added, deleted, path = parts
        yield (
            0 if added == "-" else int(added),
            0 if deleted == "-" else int(deleted),
            path,
            added == "-" or deleted == "-",
        )


def file_churn(repo: Path, commit_range: str) -> list[FileChurn]:
    """Every file the range touches, ranked for the review guide.

    Ranked by the lines the range's net diff changes, because that is the
    state under review; ties break on raw churn and then on path, so the
    guide is deterministic. Renames are off in both passes: a rename read
    as a delete plus an add keeps the two numbers comparable, which is
    what the supersession flag is computed from.

    Binary-ness comes from the net pass alone, because it qualifies the
    numbers the guide reports and those are the net diff's. A file the
    range adds and removes again is absent from the net diff, binary or
    not, and reads as work the range undid - which is what happened. A
    file binary only in an intermediate commit keeps the real counts its
    net diff carries.
    """
    raw: dict[str, int] = {}
    commits: dict[str, int] = {}
    log = git(repo, "log", "--reverse", "--numstat", "--no-renames", "--format=%H", commit_range)
    for added, deleted, path, _is_binary in _numstat_rows(log):
        raw[path] = raw.get(path, 0) + added + deleted
        commits[path] = commits.get(path, 0) + 1
    net: dict[str, int] = {}
    binary: set[str] = set()
    for added, deleted, path, is_binary in _numstat_rows(
        git(repo, "diff", "--numstat", "--no-renames", commit_range)
    ):
        net[path] = added + deleted
        if is_binary:
            binary.add(path)
    churn = [
        FileChurn(
            path=path,
            net=net.get(path, 0),
            raw=raw.get(path, 0),
            commits=commits.get(path, 0),
            binary=path in binary,
        )
        for path in set(raw) | set(net)
    ]
    return sorted(churn, key=lambda c: (-c.net, -c.raw, c.path))


def focus_prefix(
    ranked: list[FileChurn], share: float = FOCUS_SHARE, cap: int = MAX_FOCUS_FILES
) -> list[FileChurn]:
    """The ranked prefix worth the first pass.

    The shortest run carrying `share` of the net churn, capped at `cap`
    files: on a range whose churn is spread flat across fifty files, an
    unbounded 80% prefix names most of them and points at nothing. The
    caller reports the share the capped prefix actually covers, so the
    line stays true when the cap bites.
    """
    total = sum(entry.net for entry in ranked)
    if total == 0:
        return []
    prefix: list[FileChurn] = []
    running = 0
    for entry in ranked[:cap]:
        prefix.append(entry)
        running += entry.net
        if running >= total * share:
            break
    return prefix


def card_review_order(card_sections: dict[str, str], card_file: str) -> list[str]:
    """Repo-relative paths from the card's `Review order` section, in order.

    Each bullet names one path in inline code. A bullet that names none is
    a malformed section rather than a file to skip: the packet says so
    instead of silently dropping the author's ordering.
    """
    body = card_sections.get(REVIEW_ORDER_SECTION)
    if body is None:
        return []
    paths: list[str] = []
    for line in body.splitlines():
        bullet = BULLET_RE.match(line)
        if bullet is None:
            continue
        found = INLINE_CODE_RE.search(bullet.group(1))
        if found is None:
            raise ReviewPacketError(
                f"{card_file}: '{REVIEW_ORDER_SECTION}' bullet "
                f"'{bullet.group(1).strip()}' names no path. Each bullet names one "
                "repo-relative path in inline code."
            )
        paths.append(found.group(1).strip())
    return paths


def ordered_files(
    ranked: list[FileChurn], order: list[str], card_file: str
) -> tuple[list[FileChurn], str]:
    """The guide's file order, and the sentence that names where it came from."""
    if not order:
        return ranked, "generated, by the lines each file changes in the range's net diff"
    by_path = {entry.path: entry for entry in ranked}
    missing = [path for path in order if path not in by_path]
    if missing:
        raise ReviewPacketError(
            f"{card_file}: '{REVIEW_ORDER_SECTION}' names {', '.join(missing)}, which "
            "the card's commit range does not touch. Name paths as the range's diff "
            "spells them, or drop them from the section."
        )
    named = set(order)
    return (
        [by_path[path] for path in order] + [e for e in ranked if e.path not in named],
        f"author-supplied - the card's `{REVIEW_ORDER_SECTION}` section first, "
        "then the rest by net churn",
    )


def card_design_record(
    card_sections: dict[str, str], cards_dir: Path, card_file: str
) -> Path | None:
    """The typed-holes design record the card names, or None if it names none."""
    body = card_sections.get(DESIGN_RECORD_SECTION)
    if body is None:
        return None
    match = LINK_RE.search(body)
    if match is None:
        raise ReviewPacketError(
            f"{card_file}: '{DESIGN_RECORD_SECTION}' section links no record. "
            "Link the typed-holes design record there as a card-relative markdown "
            "link, or drop the section."
        )
    record = (cards_dir / match.group(1)).resolve()
    if not record.is_file():
        raise ReviewPacketError(
            f"{card_file}: design record '{match.group(1)}' does not resolve to a file ({record})"
        )
    return record


def type_relationships(record: Path) -> tuple[str, str]:
    """The design record's type-relationship heading and its body, verbatim.

    Which types wrap, return, or consume which is a design fact the record
    already states; the packet transcribes it rather than guessing it from
    the diff. A record that states it nowhere fails loudly, because the
    packet would otherwise ship a card's type surface with no view of it.
    """
    for heading, body in sections(record.read_text(encoding="utf-8")).items():
        if TYPE_SECTION_RE.match(heading.strip()) and body.strip():
            return heading.strip(), body.strip("\n")
    raise ReviewPacketError(
        f"{record}: no type-relationship section with a body (a heading such as "
        "'Type relationships' or 'Type map'). The packet lifts that section for a "
        "card that names a design record; add one to the record, or drop the card's "
        f"'{DESIGN_RECORD_SECTION}' section."
    )


def rel(target: Path, outdir: Path) -> str:
    """`target` relative to the packet directory, POSIX-style."""
    return Path(os.path.relpath(target, outdir)).as_posix()


def destination(target: str, fragment: str = "") -> str:
    """One link destination: `target` as a path, plus an optional fragment.

    Two different problems, in order. A `#` inside a path is a URI
    problem that no markdown quoting solves: angle brackets make the
    parser read `notes#draft.txt` as one destination, and the follower
    then still opens `notes` at anchor `draft.txt`. Percent-encoding is
    the only form that survives, and `%` itself is encoded first so the
    encoding stays reversible. A caller's own `fragment` is appended
    afterwards, unencoded, because there the `#` is meant.

    Spaces and parentheses are the markdown problem, and CommonMark's
    angle-bracket destination is their answer; inside it, only `<`, `>`,
    and the escape character itself need escaping.
    """
    encoded = target.replace("%", "%25").replace("#", "%23")
    if fragment:
        encoded = f"{encoded}#{fragment}"
    if not ANGLE_DESTINATION_RE.search(encoded):
        return encoded
    escaped = encoded.replace("\\", "\\\\").replace("<", "\\<").replace(">", "\\>")
    return f"<{escaped}>"


def markdown_link(label: str, target: str) -> str:
    """The one place this module emits a link, so every path is escaped once."""
    escaped = LABEL_ESCAPE_RE.sub(r"\\\1", label)
    return f"[{escaped}]({destination(target)})"


def link(label: str, target: Path, outdir: Path) -> str:
    return markdown_link(label, rel(target, outdir))


def file_ref(path: str, repo: Path, outdir: Path) -> str:
    """A changed file as a relative link, or inline code when it is gone.

    Links point into the working tree, so a file the range deletes has no
    target. Inline code says so honestly; a link there would resolve to
    nothing.
    """
    target = repo / path
    return link(path, target, outdir) if target.is_file() else f"`{path}`"


def hunk_ref(path: str, start: int, repo: Path, outdir: Path) -> str:
    """One hunk anchor: the `path:line` token, linked to the file it names.

    The visible text stays `path:line` because that token is what the
    board owner's editor and terminal jump on; the target is the same
    packet-relative link every other reference uses. A file the range
    deletes keeps the token and loses the link, as `file_ref` does.
    """
    anchor = f"{path}:{start}"
    target = repo / path
    return link(anchor, target, outdir) if target.is_file() else f"`{anchor}`"


def _count(number: int, noun: str) -> str:
    return f"{number} {noun}" if number == 1 else f"{number} {noun}s"


def _guide_entry(entry: FileChurn, packet: Packet) -> str:
    ref = file_ref(entry.path, packet.repo, packet.outdir)
    if entry.binary:
        # A binary file has no line counts to do arithmetic on, so it gets
        # no counts and no supersession verdict here. Its size lives in the
        # patch, which a binary diff reports in its own terms.
        return f"{ref} - binary, no line counts, changed in {_count(entry.commits, 'commit')}"
    if entry.raw < entry.net:
        # A binary commit contributes no lines to the raw count, so a file
        # binary partway through the range can carry a raw count below its
        # net one. Print only what is countable, rather than a figure that
        # cannot account for the lines standing next to it.
        return (
            f"{ref} - {_count(entry.net, 'line')} net, changed across "
            f"{_count(entry.commits, 'commit')}"
        )
    text = (
        f"{ref} - {_count(entry.net, 'line')} net, {entry.raw} touched across "
        f"{_count(entry.commits, 'commit')}"
    )
    if not entry.superseded:
        return text
    if entry.net == 0:
        return (
            f"{text} - SUPERSEDED: the range's net diff does not touch this file. "
            "Its hunks below are intermediate state a later commit in the range "
            "removed."
        )
    full = link("full-range.diff", packet.outdir / "full-range.diff", packet.outdir)
    return (
        f"{text} - SUPERSEDED IN PART: {entry.raw - entry.net} of the {entry.raw} "
        f"touched lines do not reach the range end. Read this file in {full} "
        "rather than hunk by hunk."
    )


def _guide_lines(packet: Packet) -> list[str]:
    ranked = file_churn(packet.repo, packet.commit_range)
    card_file = packet.meta["_file"]
    order = card_review_order(packet.card_sections, card_file)
    files, source = ordered_files(ranked, order, card_file)
    total = sum(entry.net for entry in ranked)
    lines = [
        "## Review guide",
        "",
        "Where to spend the first pass. An entry point over the indexed packet,",
        "not the one path through it: the commit listing below carries every",
        "commit and every file, for a reader who works the range commit by commit.",
        "",
        f"Order: {source}.",
        "",
    ]
    if total:
        focus = focus_prefix(ranked)
        names = ", ".join(file_ref(entry.path, packet.repo, packet.outdir) for entry in focus)
        covered = sum(entry.net for entry in focus) / total
        # With an author order the card already named the entry point, and a
        # second "start here" naming other files would contradict it. The
        # churn concentration stays, as a fact rather than an instruction.
        concentration = (
            f"Net churn concentrates in {_count(len(focus), 'file')} carrying "
            f"{covered:.0%} of it: {names}."
            if order
            else f"Start here - {_count(len(focus), 'file')} carrying {covered:.0%} of it: {names}."
        )
        lines += [
            f"{_count(len(ranked), 'file')} changed, {_count(total, 'line')} in the "
            "range's net diff.",
            concentration,
            "",
        ]
    elif any(entry.binary for entry in ranked):
        lines += [
            f"{_count(len(ranked), 'file')} touched, and the range's net diff counts no",
            "lines. Binary content is why: git reports no line counts for it, so this",
            "range's changes are real and only their counts are absent.",
            "",
        ]
    else:
        lines += [
            f"{_count(len(ranked), 'file')} touched, none of them changed by the "
            "range's net diff: every line this range moves is undone again before",
            "the range ends.",
            "",
        ]
    lines += [f"{index}. {_guide_entry(entry, packet)}" for index, entry in enumerate(files, 1)]
    lines.append("")
    if any(entry.superseded for entry in files):
        lines += [
            "SUPERSEDED is a mechanical flag: more than one commit in the range",
            "touches the file, and its per-commit patches move more lines than the",
            "net diff keeps. It says a later commit already replaced part of what",
            "the earlier hunks show. It never says the file is safe to skip - what",
            "survives is as reviewable as anything else in the range.",
            "",
        ]
    return lines


def rebase_links(body: str, source_dir: Path, outdir: Path) -> str:
    """Lifted markdown with its relative link targets re-pointed at `outdir`.

    A section lifted out of a design record still names its siblings the
    way the record does, and those names resolve against the record's
    directory, not the packet's. Every relative inline target is resolved
    where it was written and re-emitted relative to the packet. Absolute
    paths, targets carrying a URI scheme, and bare `#anchor`s are left
    exactly as they were, as are link titles and everything outside a
    link.
    """

    def rewrite(match: re.Match[str]) -> str:
        prefix, target, close = match.group(1), match.group(2), match.group(3)
        raw = target[1:-1] if target.startswith("<") else target
        if not raw or raw.startswith(("/", "#")) or SCHEME_RE.match(raw):
            return match.group(0)
        path, _, fragment = raw.partition("#")
        if not path:
            return match.group(0)
        # The fragment stays a fragment: it goes to `destination` as one,
        # so the path's own encoding never swallows the separator.
        return f"{prefix}{destination(rel(source_dir / path, outdir), fragment)}{close}"

    return RECORD_LINK_RE.sub(rewrite, body)


def _design_record_lines(packet: Packet) -> list[str]:
    record = card_design_record(packet.card_sections, packet.cards_dir, packet.meta["_file"])
    if record is None:
        return []
    heading, body = type_relationships(record)
    body = rebase_links(body, record.parent, packet.outdir)
    return [
        "## Design record",
        "",
        f"{link(record.name, record, packet.outdir)}, named by the card's "
        f"`{DESIGN_RECORD_SECTION}` section.",
        "",
        "Read the record before the diff. The type view below is the record's own",
        "account of how the types relate, not this packet's reading of the code.",
        "",
        "## Type relationships",
        "",
        f"Lifted from the design record's `{heading}` section. Only its relative",
        "link targets are rewritten, to point from here rather than from the record.",
        "",
        body,
        "",
    ]


def _commit_lines(packet: Packet) -> list[str]:
    repo, outdir = packet.repo, packet.outdir
    lines = [
        "## Commits",
        "",
        "Every commit in the range, in range order, each with its own patch and",
        "the new-side line of each hunk it writes.",
        "",
    ]
    for index, commit in enumerate(packet.commits, start=1):
        short = commit.sha[:8]
        stat = git(repo, "show", "--shortstat", "--format=", commit.sha).strip()
        patch = f"{index:02d}-{short}.diff"
        lines += [
            f"### {index}. {short} {commit.subject}",
            "",
            f"{stat}",
            f"Patch: {link(patch, outdir / patch, outdir)} | `git -C {repo} show {short}`",
            "",
        ]
        for path, starts in hunk_pointers(repo, commit.sha).items():
            if not starts:
                lines.append(f"- `{path}` (deleted)")
                continue
            shown = ", ".join(
                hunk_ref(path, start, repo, outdir) for start in starts[:MAX_HUNKS_PER_FILE]
            )
            extra = len(starts) - MAX_HUNKS_PER_FILE
            suffix = f" (+{extra} more hunks)" if extra > 0 else ""
            lines.append(f"- {shown}{suffix}")
        lines.append("")
    return lines


def _retention_lines() -> list[str]:
    return [
        "## Retention",
        "",
        "This packet is regenerable working material. `boardkit init` gitignores",
        "the review output directory, and `boardkit review-packet` rebuilds the",
        "packet from the card's commit range whenever a gate needs it again. The",
        "card and its log are the durable record of what was reviewed and what",
        "was decided. A repo that wants packets kept un-ignores the output",
        "directory deliberately and owns the consequence.",
        "",
    ]


def render_review(packet: Packet) -> str:
    """REVIEW.md: the guide first, then the design record, then the index."""
    meta, repo, outdir = packet.meta, packet.repo, packet.outdir
    card = packet.cards_dir / meta["_file"]
    lines = [
        f"# Review packet: {meta['id']} {meta['title']}",
        "",
        f"Card: {link(meta['_file'], card, outdir)} | Repo: `{repo}`",
        f"Range: `{packet.commit_range}` ({len(packet.commits)} commits)",
        "",
        f"Whole card at once: {link('full-range.diff', outdir / 'full-range.diff', outdir)}, or",
        f"`git -C {repo} diff {packet.commit_range}`",
        "",
        *_guide_lines(packet),
        *_design_record_lines(packet),
        *_commit_lines(packet),
        *_retention_lines(),
    ]
    return "\n".join(lines)


def clean_generated(outdir: Path) -> None:
    """Delete this module's own outputs from `outdir`, and nothing else.

    The review directory also holds gate ledgers and reviewer transcripts
    that nothing can regenerate, so a rerun never removes the directory.
    """
    if not outdir.exists():
        return
    for stale in outdir.glob("*.diff"):
        if GENERATED_DIFF_RE.match(stale.name):
            stale.unlink()
    for name in GENERATED_NAMES:
        stale = outdir / name
        if stale.exists():
            stale.unlink()


def build_review_packet(
    config: Config,
    card_id: str,
    repo: Path | None = None,
    suffix: str | None = None,
    commit_range: str | None = None,
) -> Path:
    """Build the review packet for `card_id`; returns the output directory.

    `repo` overrides config.review.repo. `suffix` names the repo this
    packet covers, for a card whose work spans more than one repo: the
    output directory becomes `<output_dir>/<ID>-<suffix>` so an
    external-repo diff never lands in the primary packet's directory.
    `commit_range` overrides the card's `commit-range` frontmatter, which
    names shas in the primary repo only; a second repo has its own history,
    so its packet needs its own range alongside `repo` and `suffix`. With
    the override the card needs no frontmatter range at all.
    Raises ReviewPacketError on any fatal condition (missing card, missing
    commit-range, bad repo, malformed suffix, ...).
    """
    target_repo = repo if repo is not None else config.review.repo
    if suffix is not None and not SUFFIX_RE.match(suffix):
        raise ReviewPacketError(
            f"--suffix '{suffix}' is not a lowercase slug (a-z, 0-9, single dashes between them)"
        )

    meta = load_card(config.board.cards_dir, card_id)
    if str(meta.get("id", "")).upper() != card_id.upper():
        raise ReviewPacketError(
            f"{meta['_file']}: frontmatter id '{meta.get('id')}' does not "
            f"match requested '{card_id}'"
        )
    if commit_range is None:
        commit_range = meta.get("commit-range")
    if not commit_range:
        raise ReviewPacketError(
            f"{meta['_file']}: no 'commit-range' frontmatter. Find the range "
            f"with: git log --oneline --grep '^Card: {card_id.upper()}$' "
            "<primary-branch>, record it on the card, and re-run."
        )
    if not target_repo.is_dir():
        raise ReviewPacketError(f"repo {target_repo} does not exist; pass --repo")
    validate_commit_range(target_repo, str(commit_range))

    commits = commit_list(target_repo, str(commit_range))
    dirname = card_id.upper() if suffix is None else f"{card_id.upper()}-{suffix}"
    outdir = config.review.output_dir / dirname

    # Render before the sweep. REVIEW.md is built from the card's own
    # sections now, so a malformed one is a live failure mode; rendering
    # first means a card that fails to regenerate keeps the packet a gate
    # may already be reading. Link targets are path arithmetic, so nothing
    # here depends on the files being written yet.
    review = render_review(
        Packet(
            meta=meta,
            commit_range=str(commit_range),
            repo=target_repo,
            commits=commits,
            outdir=outdir,
            cards_dir=config.board.cards_dir,
            card_sections=sections(meta["_body"]),
        )
    )

    clean_generated(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for index, commit in enumerate(commits, start=1):
        patch = git(target_repo, "show", "--stat", "--patch", commit.sha)
        (outdir / f"{index:02d}-{commit.sha[:8]}.diff").write_text(patch, encoding="utf-8")
    full = git(target_repo, "diff", str(commit_range))
    (outdir / "full-range.diff").write_text(full, encoding="utf-8")
    (outdir / "REVIEW.md").write_text(review, encoding="utf-8")

    return outdir
