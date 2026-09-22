#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["cmarkgfm"]
# ///
"""Detect and repair the ways LLM-generated Japanese Markdown silently breaks.

Why this exists
---------------
`prettier` and `mdformat` do NOT repair these files. Measured 2026-09-01 on a
file with a mis-nested code fence: both re-serialised the *broken* parse (they
widened the outer fence to ```` and left the swallowed prose inside it), which
freezes the damage instead of undoing it. A formatter round-trips the parse
tree, and by the time the tree exists the author's intent is already lost.

The failure that matters most is silent and catastrophic: a fence opened inside
another fence terminates the outer block early, and every following section --
headings, lists, links -- is absorbed into a <pre> as literal text. Nothing
errors; the note simply loses half its content in every renderer.

So the checks here work on the source lines with a CommonMark-faithful fence
scanner, and use a real parser (cmark-gfm, the engine GitHub itself runs) as
the oracle for emphasis rather than guessing with regexes.

Fixes are applied only where the transform is provably meaning-preserving; the
nested-fence case is reported with line numbers instead, because choosing which
fence was meant to be the outer one is a human judgement.

Usage
-----
    ./md_lint.py check <path>...        # report, exit 1 if anything found
    ./md_lint.py fix   <path>...        # apply the safe fixes in place
    ./md_lint.py check --format=github <path>...   # for CI / hooks
"""

from __future__ import annotations

import argparse
import re
import unicodedata
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

try:
    import cmarkgfm
except ImportError:  # pragma: no cover - dependency is declared above
    cmarkgfm = None


FENCE_RE = re.compile(r"^(?P<indent> {0,3})(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
HEADING_RE = re.compile(r"^ {0,3}#{1,6}\s")
LIST_ITEM_RE = re.compile(r"^(?P<indent> *)(?P<marker>[-*+]|\d+[.)])\s+\S")
FULLWIDTH_FENCE_RE = re.compile(r"^\s*｀｀｀+")
CJK_RE = re.compile(r"[぀-ヿ一-鿿]")

# `**「...」**` and friends: an emphasis delimiter placed immediately outside a
# CJK bracket. Legal at the start of a line, dead in mid-sentence.
BRACKETS = [("「", "」"), ("『", "』"), ("（", "）"), ("【", "】"), ("《", "》")]
OUTSIDE_EMPH_RE = re.compile(
    r"(?P<open>\*\*|__)(?P<lb>[「『（【《])(?P<body>[^*_\n]+?)(?P<rb>[」』）】》])(?P=open)"
)


@dataclass
class Issue:
    """One problem found in a file.

    Attributes
    ----------
    line : int
        1-indexed line number the problem is anchored to.
    col : int
        1-indexed column of the offending delimiter, or 0 when not applicable.
    code : str
        Short stable identifier, e.g. ``FENCE-SWALLOW``.
    message : str
        Human-readable description, in Japanese.
    fixable : bool
        Whether ``fix`` mode can repair it without guessing.
    """

    line: int
    code: str
    message: str
    fixable: bool = False
    col: int = 0


@dataclass
class Block:
    """A fenced code block located in the source.

    Attributes
    ----------
    start, end : int
        0-indexed line numbers of the opening and closing fence lines. ``end``
        is ``-1`` when the block was never closed.
    char : str
        The fence character, ``` ` ``` or ``~``.
    length : int
        Number of fence characters in the opener.
    info : str
        The info string (language tag), stripped.
    """

    start: int
    end: int
    char: str
    length: int
    info: str


def scan_fences(lines: Sequence[str]) -> Tuple[List[Block], List[int]]:
    """Locate fenced code blocks the way CommonMark does.

    A closing fence must use the same character and be at least as long as the
    opener, which is exactly the rule that lets a ``` inside a ``` block end it
    early. Reproducing it faithfully is the whole point.

    Parameters
    ----------
    lines : sequence of str
        The file's lines, without trailing newlines.

    Returns
    -------
    blocks : list of Block
        Every fenced block, in source order.
    fence_lines : list of int
        0-indexed line numbers of all lines that act as a fence.
    """
    blocks: List[Block] = []
    fence_lines: List[int] = []
    open_block: Optional[Block] = None

    for i, line in enumerate(lines):
        m = FENCE_RE.match(line)
        if m is None:
            continue
        fence = m.group("fence")
        char, length = fence[0], len(fence)
        info = m.group("info").strip()

        if open_block is None:
            if info and (char in info):
                # An info string may not contain a backtick; not a real opener.
                continue
            open_block = Block(start=i, end=-1, char=char, length=length, info=info)
            fence_lines.append(i)
        elif char == open_block.char and length >= open_block.length and not info:
            open_block.end = i
            blocks.append(open_block)
            fence_lines.append(i)
            open_block = None

    if open_block is not None:
        blocks.append(open_block)
        fence_lines.append(open_block.start)
    return blocks, fence_lines


def backtick_info_openers(lines: Sequence[str]) -> List[int]:
    """Return lines that look like a backtick fence but have a backtick in the info.

    CommonMark forbids a backtick in the info string of a backtick fence, so
    ```` ```{admonition} Why `S` ```` is not an opener at all. `scan_fences`
    rightly skips it, but the author meant it as one, so its closing ``` then
    opens a block of its own and every fence after it pairs up one off. In a
    MyST document the whole remainder of the page -- headings included -- ends
    up in a code block. Measured 2026-09-22 on this repository: 10 admonitions
    whose titles held inline code, every one of them breaking its page.

    Returns
    -------
    list of int
        0-indexed line numbers, in source order.
    """
    found: List[int] = []
    open_block: Optional[Block] = None
    for i, line in enumerate(lines):
        m = FENCE_RE.match(line)
        if m is None:
            continue
        fence = m.group("fence")
        char, length = fence[0], len(fence)
        info = m.group("info").strip()
        if open_block is None:
            if info and char in info:
                if char == "`":
                    found.append(i)
                continue
            open_block = Block(start=i, end=-1, char=char, length=length, info=info)
        elif char == open_block.char and length >= open_block.length and not info:
            open_block = None
    return found


def intended_closer(lines: Sequence[str], opener: int) -> Optional[int]:
    """Find the ``` that was meant to close a backtick-info opener.

    Fences nested inside (``` bash ... ```) are counted so their closer is not
    mistaken for ours. Returns None when no closer is found.
    """
    m = FENCE_RE.match(lines[opener])
    length = len(m.group("fence"))
    depth = 0
    for j in range(opener + 1, len(lines)):
        mj = FENCE_RE.match(lines[j])
        if mj is None or mj.group("fence")[0] != "`":
            continue
        if mj.group("info").strip():
            depth += 1
        elif depth:
            depth -= 1
        elif len(mj.group("fence")) >= length:
            return j
    return None


def check_info_backtick(lines: Sequence[str]) -> List[Issue]:
    """Flag backtick fences whose info string contains a backtick."""
    return [
        Issue(
            i + 1,
            "FENCE-INFO-BACKTICK",
            "``` の info 文字列（言語名や {directive} の後ろ）にバッククォートがあるので、"
            "この行はフェンスになりません。以降のフェンスの組み合わせが 1 つずつずれ、"
            "本文がコードブロックに飲み込まれます。~~~ で囲めば info にバッククォートを"
            "書けます。",
            fixable=intended_closer(lines, i) is not None,
        )
        for i in backtick_info_openers(lines)
    ]


def in_code(index: int, blocks: Sequence[Block], total: int) -> bool:
    """Return True when a 0-indexed line falls inside a fenced block."""
    for b in blocks:
        end = b.end if b.end >= 0 else total - 1
        if b.start <= index <= end:
            return True
    return False


def paragraphs(lines: Sequence[str], blocks: Sequence[Block]) -> List[Tuple[int, int]]:
    """Group the source into paragraph-sized units for inline analysis.

    Emphasis cannot span a blank line but freely spans a soft line break, so a
    single line is the wrong unit: judging `つまり**A` and `B**していた。` apart
    reports both halves of one working span as broken. Measured on this vault,
    per-line analysis produced 1133 hits, most of them exactly that artefact.

    Returns
    -------
    list of (start, end)
        Inclusive 0-indexed line ranges, code blocks and front matter excluded.
    """
    spans: List[Tuple[int, int]] = []
    start = None
    skip_to = 0
    if lines and lines[0].strip() == "---":
        for j in range(1, len(lines)):
            if lines[j].strip() in ("---", "..."):
                skip_to = j + 1
                break
    for i in range(skip_to, len(lines)):
        blank = not lines[i].strip()
        if in_code(i, blocks, len(lines)) or blank:
            if start is not None:
                spans.append((start, i - 1))
                start = None
            continue
        if start is None:
            start = i
    if start is not None:
        spans.append((start, len(lines) - 1))
    return spans


def emphasis_breaks(text: str) -> bool:
    """Return True if ``text`` still contains literal ``**``/``__`` once rendered.

    Uses cmark-gfm, so the answer is what GitHub actually does rather than an
    approximation of the left-flanking rule.
    """
    if cmarkgfm is None:
        return False
    html = cmarkgfm.github_flavored_markdown_to_html(text)
    # Look at rendered text only. Attribute values carry underscores that were
    # never emphasis markers -- a Google Drive id such as `1s__HoS6YFK9` inside
    # an href otherwise reports a perfectly good paragraph as broken.
    text_only = re.sub(r"<[^>]*>", "", html)
    return "**" in text_only or "__" in text_only


def check_fences(lines: Sequence[str], blocks: Sequence[Block]) -> List[Issue]:
    """Flag unterminated fences and blocks that swallowed the document."""
    issues: List[Issue] = []
    for b in blocks:
        if b.end < 0:
            issues.append(
                Issue(
                    b.start + 1,
                    "FENCE-UNCLOSED",
                    "フェンスが閉じられないままファイルが終わっています。"
                    "以降の本文がすべてコードブロックに飲み込まれます。",
                )
            )
            body = lines[b.start + 1 :]
        else:
            body = lines[b.start + 1 : b.end]

        headings = [j for j, ln in enumerate(body) if HEADING_RE.match(ln)]
        if headings and not b.info:
            issues.append(
                Issue(
                    b.start + 1 + headings[0] + 1,
                    "FENCE-SWALLOW",
                    "コードブロックの中に見出し行があります。内側のフェンスが外側を"
                    "早く閉じ、本文が飲み込まれた可能性が高い。外側を ```` (4本以上) "
                    "にしてください。",
                )
            )
    return issues


def check_list_fences(lines: Sequence[str], blocks: Sequence[Block]) -> List[Issue]:
    """Flag a column-0 fence opening straight after a list item.

    The fence terminates the list, so the item before and the item after render
    as two separate lists with a code block wedged between them.
    """
    issues = []
    starts = {b.start for b in blocks}
    for i, line in enumerate(lines):
        if i == 0 or i not in starts:
            continue
        prev = lines[i - 1]
        if LIST_ITEM_RE.match(prev) and not line.startswith((" ", "\t")):
            issues.append(
                Issue(
                    i + 1,
                    "FENCE-IN-LIST",
                    "箇条書きの直後にインデントなしのフェンスがあり、リストが分断され"
                    "ます。フェンスをリスト記号の幅だけ字下げしてください。",
                    fixable=True,
                )
            )
    return issues


def check_fullwidth(lines: Sequence[str]) -> List[Issue]:
    """Flag full-width backticks, which never form a code fence."""
    return [
        Issue(i + 1, "FENCE-FULLWIDTH", "全角バッククォート (｀) はフェンスになりません。", True)
        for i, line in enumerate(lines)
        if FULLWIDTH_FENCE_RE.match(line)
    ]


CODE_SPAN_RE = re.compile(r"(?P<ticks>`+)(?P<body>.+?)(?P=ticks)", re.DOTALL)


def mask_code_spans(text: str) -> str:
    """Blank out the inside of inline code spans, preserving every offset.

    `**` inside backticks is literal by design, so both the renderer probe and
    the flanking scan would otherwise report a correct `` `a **b** c` `` as
    broken. Replacing only the interior keeps the span parsing as code and keeps
    line/offset arithmetic valid.
    """
    return CODE_SPAN_RE.sub(
        lambda m: m.group("ticks")
        + re.sub(r"[^\n]", "x", m.group("body"))
        + m.group("ticks"),
        text,
    )


def _is_punct(ch: str) -> bool:
    """Return True for what CommonMark counts as punctuation (Unicode P* / S*)."""
    return bool(ch) and unicodedata.category(ch)[0] in ("P", "S")


DELIM_RUN_RE = re.compile(r"\*+|_+")
OPENERS = "「『（【《［〈［(["


def dead_delimiters(chunk: str) -> List[int]:
    """Return offsets of emphasis delimiters that can neither open nor close.

    Implements CommonMark's left/right-flanking test directly rather than
    bisecting the paragraph with the renderer, so the report points at the exact
    `**` that will show up as literal asterisks instead of at the paragraph.

    A run is left-flanking when it is not followed by whitespace and either not
    followed by punctuation or else preceded by whitespace/punctuation; the
    right-flanking rule is its mirror. A run that satisfies neither can never
    take part in an emphasis span.
    """
    dead: List[int] = []
    stranded: List[int] = []
    for m in DELIM_RUN_RE.finditer(chunk):
        before = chunk[m.start() - 1] if m.start() else ""
        after = chunk[m.end()] if m.end() < len(chunk) else ""
        before_ws = (not before) or before.isspace()
        after_ws = (not after) or after.isspace()
        left = (not after_ws) and (not _is_punct(after) or before_ws or _is_punct(before))
        right = (not before_ws) and (not _is_punct(before) or after_ws or _is_punct(after))
        if not left and not right:
            dead.append(m.start())
        elif not left and after in OPENERS and not before_ws:
            # `の**「` -- the author clearly meant to open here, but a delimiter
            # followed by punctuation only opens when preceded by whitespace or
            # punctuation. It stays flankable as a closer, so it is not provably
            # dead; still, it is the canonical Japanese break and a far better
            # thing to point at than the head of the paragraph.
            stranded.append(m.start())
    return dead or stranded


def check_emphasis(lines: Sequence[str], blocks: Sequence[Block]) -> List[Issue]:
    """Flag emphasis that the parser refuses to open, verified by rendering.

    Works on whole paragraphs so that a span opened on one line and closed on
    the next is judged as the single construct it is.
    """
    issues = []
    for start, end in paragraphs(lines, blocks):
        chunk = "\n".join(lines[start : end + 1])
        # Render a de-indented copy: a paragraph lifted out of a nested list
        # still carries the list's indentation, and 4+ spaces on its own make
        # cmark read the whole thing as an indented code block, where every `**`
        # is literal by definition. Left-stripping keeps line offsets intact
        # because only the count of newlines before a match is used.
        probe = mask_code_spans("\n".join(ln.lstrip() for ln in lines[start : end + 1]))
        if ("**" not in probe and "__" not in probe) or not emphasis_breaks(probe):
            continue
        offsets = dead_delimiters(probe)
        anchor = start
        col = 0
        if offsets:
            anchor = start + probe.count("\n", 0, offsets[0])
            line_start = probe.rfind("\n", 0, offsets[0]) + 1
            col = offsets[0] - line_start + 1
        else:
            for j in range(start, end + 1):
                if "**" in lines[j] or "__" in lines[j]:
                    anchor = j
                    break
        issues.append(
            Issue(
                anchor + 1,
                "EMPH-DEAD",
                "この位置の ** が強調として機能していません "
                "(直前が文字で直後が括弧、直前が句読点で直後が文字、など)。括弧の内側に寄せてください: "
                "これは**「A」**です → これは「**A**」です。",
                fixable=bool(OUTSIDE_EMPH_RE.search(probe)),
                col=col,
            )
        )
    return issues


def check_indented_prose(lines: Sequence[str], blocks: Sequence[Block]) -> List[Issue]:
    """Flag 4-space-indented Japanese prose that became an indented code block."""
    issues = []
    for i, line in enumerate(lines):
        if in_code(i, blocks, len(lines)) or not line.startswith("    "):
            continue
        if i > 0 and lines[i - 1].strip():
            continue  # continuation of a list item or paragraph, not a new block
        prev = next((lines[j] for j in range(i - 1, -1, -1) if lines[j].strip()), "")
        if LIST_ITEM_RE.match(prev) or LIST_ITEM_RE.match(line):
            continue  # inside a list: the indent is nesting, not a code block
        body = line.strip()
        if CJK_RE.search(body) and not re.search(r"[{};=()<>]|^\w+\s+\w+\s*=", body):
            issues.append(
                Issue(
                    i + 1,
                    "INDENT-CODE",
                    "4スペース字下げされた日本語がコードブロック扱いになっています。",
                )
            )
    return issues


def analyse(text: str) -> List[Issue]:
    """Run every check over one document's text."""
    lines = text.split("\n")
    blocks, _ = scan_fences(lines)
    issues = (
        check_info_backtick(lines)
        + check_fences(lines, blocks)
        + check_list_fences(lines, blocks)
        + check_fullwidth(lines)
        + check_emphasis(lines, blocks)
        + check_indented_prose(lines, blocks)
    )
    return sorted(issues, key=lambda x: (x.line, x.code))


def fix_text(text: str) -> Tuple[str, int]:
    """Apply the meaning-preserving repairs.

    Nested fences are deliberately left alone: deciding which fence was meant to
    be the outer one requires reading the author's intent.

    Returns
    -------
    text : str
        The repaired document.
    count : int
        Number of edits applied.
    """
    lines = text.split("\n")
    count = 0

    # 1. Full-width backticks -> ASCII, before any fence scanning depends on it.
    for i, line in enumerate(lines):
        if FULLWIDTH_FENCE_RE.match(line):
            lines[i] = line.replace("｀", "`")
            count += 1

    # 1b. A backtick in a backtick fence's info string: switch that block to
    #     tildes, which may carry backticks in the info. One at a time, because
    #     each repair changes how every later fence pairs up.
    while True:
        bad = [i for i in backtick_info_openers(lines) if intended_closer(lines, i) is not None]
        if not bad:
            break
        i = bad[0]
        j = intended_closer(lines, i)
        mi, mj = FENCE_RE.match(lines[i]), FENCE_RE.match(lines[j])
        lines[i] = mi.group("indent") + "~" * len(mi.group("fence")) + mi.group("info")
        lines[j] = mj.group("indent") + "~" * len(mj.group("fence")) + mj.group("info")
        count += 1

    # 2. Emphasis stranded outside a CJK bracket, judged per paragraph so that
    #    a span crossing a soft line break is not mistaken for two broken ones.
    blocks, _ = scan_fences(lines)
    for start, end in paragraphs(lines, blocks):
        chunk = "\n".join(lines[start : end + 1])
        probe = mask_code_spans("\n".join(ln.lstrip() for ln in lines[start : end + 1]))
        if not OUTSIDE_EMPH_RE.search(probe) or not emphasis_breaks(probe):
            continue

        def rewrite(m: "re.Match") -> str:
            # Flanking depends on the single character on each side: the opener
            # needs its left neighbour, the closer its right one. Probing with
            # only the left neighbour wrongly clears `。**「行頭」**は`, whose
            # closing ** is preceded by punctuation and followed by a letter and
            # therefore never closes. Keep both neighbours.
            before = chunk[m.start() - 1] if m.start() else ""
            after = chunk[m.end()] if m.end() < len(chunk) else ""
            if not emphasis_breaks(before + m.group(0) + after):
                return m.group(0)
            return "{lb}{o}{body}{o}{rb}".format(
                lb=m.group("lb"), rb=m.group("rb"),
                o=m.group("open"), body=m.group("body"),
            )

        candidate = OUTSIDE_EMPH_RE.sub(rewrite, chunk)
        # Only keep the rewrite if it actually made the parser open the emphasis.
        verify = mask_code_spans("\n".join(ln.lstrip() for ln in candidate.split("\n")))
        if candidate != chunk and not emphasis_breaks(verify):
            new_lines = candidate.split("\n")
            if len(new_lines) == end - start + 1:
                lines[start : end + 1] = new_lines
                count += 1

    # 3. Indent a column-0 fence that follows a list item, and its whole block.
    blocks, _ = scan_fences(lines)
    for b in reversed(blocks):
        if b.start == 0 or b.end < 0:
            continue
        prev = LIST_ITEM_RE.match(lines[b.start - 1])
        if prev is None or lines[b.start].startswith((" ", "\t")):
            continue
        pad = " " * (len(prev.group("indent")) + len(prev.group("marker")) + 1)
        for j in range(b.start, b.end + 1):
            if lines[j].strip():
                lines[j] = pad + lines[j]
        count += 1

    # 4. Blank line around fences at top level (MD031), which several renderers
    #    need before they will recognise the fence at all.
    blocks, _ = scan_fences(lines)
    out: List[str] = []
    starts = {b.start for b in blocks}
    ends = {b.end for b in blocks if b.end >= 0}
    for i, line in enumerate(lines):
        if i in starts and out and out[-1].strip() and not LIST_ITEM_RE.match(out[-1]):
            out.append("")
            count += 1
        out.append(line)
        if i in ends and i + 1 < len(lines) and lines[i + 1].strip():
            if not LIST_ITEM_RE.match(lines[i + 1]):
                out.append("")
                count += 1
    return "\n".join(out), count


READONLY_DIRS = ("04_Sources", "01_Journal")


def is_readonly(path: Path) -> bool:
    """Return True for vault areas the agent rules forbid rewriting.

    `04_Sources/` is raw primary data and `01_Journal/` is the human's own log;
    a formatter has no business editing either, however broken the Markdown is.
    """
    return any(part in READONLY_DIRS for part in path.resolve().parts)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("mode", choices=["check", "fix"])
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument(
        "--format", choices=["text", "github"], default="text",
        help="github = ::error file=...,line=... for CI and hooks",
    )
    parser.add_argument(
        "--allow-readonly", action="store_true",
        help="04_Sources/ と 01_Journal/ にも書き込む (既定では skip)",
    )
    args = parser.parse_args(argv)

    files: List[Path] = []
    for p in args.paths:
        files.extend(sorted(p.rglob("*.md")) if p.is_dir() else [p])

    total = 0
    for path in files:
        text = path.read_text(encoding="utf-8")
        if args.mode == "fix" and is_readonly(path) and not args.allow_readonly:
            hits = analyse(text)
            if hits:
                print("skip {} ({} 件, 読み取り専用ディレクトリ)".format(path, len(hits)))
            continue
        if args.mode == "fix":
            new, n = fix_text(text)
            if n:
                path.write_text(new, encoding="utf-8")
                print("fixed {} ({} 箇所)".format(path, n))
            remaining = [i for i in analyse(new) if not i.fixable]
            for issue in remaining:
                print("  要手動 {}:{}{}: [{}] {}".format(
                    path, issue.line,
                    ":{}".format(issue.col) if issue.col else "",
                    issue.code, issue.message))
            total += len(remaining)
        else:
            for issue in analyse(text):
                if args.format == "github":
                    print("::error file={},line={},col={}::[{}] {}".format(
                        path, issue.line, issue.col or 1, issue.code, issue.message))
                else:
                    where = "{}:{}".format(path, issue.line)
                    if issue.col:
                        where += ":{}".format(issue.col)
                    print("{}: [{}] {}{}".format(
                        where, issue.code, issue.message,
                        " (自動修正可)" if issue.fixable else ""))
                total += 1

    if args.mode == "check":
        print("\n{} ファイル中 {} 件".format(len(files), total), file=sys.stderr)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
