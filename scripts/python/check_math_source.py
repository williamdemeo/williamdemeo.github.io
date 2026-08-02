#!/usr/bin/env python3
"""Fail on math *source* that arithmatex and KaTeX will silently mis-render.

`make math-audit` (scripts/js/audit_math.mjs) renders every expression and
reports the ones KaTeX raises on.  It cannot see this class of defect, because
none of these raise: each one produces a page that builds cleanly, renders
without a console error, and is wrong on screen.  They all arrive the same way
-- content written for a Markdown engine that escaped `\\{`, `\\}` and `\\_` on
its way through, then handed to one that does not.

Four checks, each a case where what the source says and what the reader sees
come apart:

  over-escaped brace   `\\\\{` and `\\\\}` inside math.  KaTeX reads `\\\\` as
                       `\\newline`, so `\\\\{0, 1\\\\}` is a line break, a *group*
                       (not a brace) containing `0, 1`, and another line break.
                       The braces vanish and the expression grows two stray
                       line breaks.  This is where "extra line breaks after
                       `B = \\langle`" comes from.

  escaped underscore   `\\_` inside math.  In KaTeX that is a literal
                       underscore character, not a subscript: `A\\_1` renders
                       as `A_1` where `A₁` was meant.

  padded delimiter     `$ x $`.  arithmatex's `smart_dollar` (on by default)
                       refuses a `$` delimiter with whitespace inside it, so
                       the span is not mathematics at all and the LaTeX source
                       is published verbatim into the prose.

  stranded `$$`        `$$ ... $$` that does not begin its own Markdown block.
                       arithmatex's BlockProcessor calls `.match()`, so the
                       delimiter has to be at the start of a block: preceded by
                       a blank line, indented a multiple of four (python-markdown
                       wants four spaces inside a list item, not two), and not
                       trailing prose on the same line.  Miss any of those and
                       the inline processor takes over, matches the *inner*
                       `$...$`, and leaves one literal `$` on each side.

The first three are mechanical and `--fix` rewrites them.  The fourth is not:
the repair is a blank line, or a re-indent, or splitting a paragraph, depending
on why the block was missed -- and choosing wrong silently moves prose out of a
list item.  Those are reported with the reason so a human can pick.

That difference is also why only the first three fail the build by default.
The imported archive (M2-9) carries forty-one stranded blocks, on pages that
already ship with a "not maintained" notice and their own KaTeX errors; making
them a hard gate would block every unrelated change on content work nobody has
scheduled.  They are counted and named on every run, M2-10 (#78) schedules the
repair, and `--strict` promotes them to failures for whoever does it.

Agreement with the renderer is not approximated here: the delimiter patterns
are imported from `pymdownx.arithmatex`, the same objects the build registers,
so this checker cannot drift from what MkDocs does.

    python3 scripts/python/check_math_source.py [--fix] [--strict] [ROOT ...]

Exit status is 0 when the tree is clean and 1 otherwise, `diff(1)`-style, so it
gates in CI.  With `--fix` it is 0 once everything it can repair is repaired,
and 1 if anything is left that only a human can decide.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

from pymdownx.arithmatex import RE_DOLLAR_INLINE, RE_SMART_DOLLAR_INLINE

# Regions that render verbatim, so their contents are not mathematics: fenced
# code, HTML comments, inline code.  Same three audit_math.mjs strips, and for
# the same reason -- `$PATH` in a shell example is not an expression, and a
# defect inside a comment is one no visitor can see.
FENCE = re.compile(r"^(```|~~~).*?^\1", re.S | re.M)
COMMENT = re.compile(r"<!--.*?-->", re.S)
CODE = re.compile(r"`[^`\n]*`")

# Display math.  Masked before the inline scan so the `$ ... $` *between* the
# two halves of a `$$ ... $$` pair is not mistaken for a padded inline span --
# the block processor handles those, and it does not care about whitespace.
BLOCK = re.compile(r"\$\$(?:\\.|[^\\])+?\$\$", re.S)

INLINE = re.compile(RE_DOLLAR_INLINE)
SMART = re.compile(RE_SMART_DOLLAR_INLINE)

# A run of backslashes followed by a brace or an underscore.  Matching the
# whole run rather than a fixed `\\{` matters: in `\\\{` -- a line break and
# then a literal brace, which is correct -- a two-character pattern finds a
# false `\\{` starting at the second backslash.
ESCAPE = re.compile(r"\\+[{}_]")

MASK = "\x00"

#: A padded span is only reported when it looks like mathematics.  Prose runs
#: to real dollar signs ("this costs $5, and ...") and two of them across a
#: paragraph pair up exactly like delimiters; requiring a control sequence or a
#: sub/superscript is what keeps the checker off them.
LOOKS_LIKE_MATH = re.compile(r"\\[A-Za-z]|[_^]")
PADDED_MAX_LEN = 200


class Finding:
    """One defect, located in the source and either fixable or not."""

    def __init__(self, path, line, kind, detail, fixable):
        self.path, self.line = path, line
        self.kind, self.detail, self.fixable = kind, detail, fixable

    def __str__(self):
        mark = " " if self.fixable else "!"
        return f"{mark} {self.path}:{self.line}: {self.kind}: {self.detail}"


def _blank(m: re.Match) -> str:
    """A same-length, same-shape replacement: newlines survive, nothing else.

    Length has to be preserved so reported offsets still index the original
    text, and newlines have to be preserved so line numbers -- and the
    line-oriented `$$` check -- still line up.
    """
    return "".join(c if c == "\n" else MASK for c in m.group(0))


def mask(text: str, patterns) -> str:
    """Blank out `patterns` character-for-character, preserving every offset."""
    out = text
    for rx in patterns:
        out = rx.sub(_blank, out)
    return out


def math_regions(text: str) -> list[tuple[int, int]]:
    """Offsets of every math span's contents, display and inline alike."""
    scan = mask(text, (FENCE, COMMENT, CODE))
    regions = [(m.start(), m.end()) for m in BLOCK.finditer(scan)]

    inline_scan = mask(scan, (BLOCK,))
    for m in INLINE.finditer(inline_scan):
        if m.group(3):
            regions.append((m.start(3), m.end(3)))
    return regions


def in_math(regions, pos: int) -> bool:
    return any(a <= pos < b for a, b in regions)


def lineno(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def find_escapes(path, text, regions):
    """Over-escaped braces and escaped underscores, inside math only."""
    for m in ESCAPE.finditer(text):
        run, char = m.group(0)[:-1], m.group(0)[-1]
        if not in_math(regions, m.start()):
            continue
        if char in "{}" and len(run) == 2:
            yield Finding(path, lineno(text, m.start()), "over-escaped brace",
                          f"`\\\\{char}` should be `\\{char}`", True)
        elif char == "_" and len(run) == 1:
            yield Finding(path, lineno(text, m.start()), "escaped underscore",
                          "`\\_` is a literal underscore, not a subscript", True)


def find_padded(path, text):
    """`$ x $` spans, which smart_dollar declines and so does not render."""
    scan = mask(text, (FENCE, COMMENT, CODE, BLOCK))
    accepted = {(m.start(3), m.end(3)) for m in SMART.finditer(scan) if m.group(3)}
    for m in INLINE.finditer(scan):
        body = m.group(3)
        if not body or (m.start(3), m.end(3)) in accepted:
            continue
        if "\n\n" in body or len(body) > PADDED_MAX_LEN:
            continue
        if not LOOKS_LIKE_MATH.search(body):
            continue
        if not (body[:1].isspace() or body[-1:].isspace()):
            continue
        yield Finding(path, lineno(text, m.start()), "padded delimiter",
                      f"`${body.strip()[:48]}...$` has whitespace inside its "
                      f"`$`, so smart_dollar does not treat it as math", True)


def find_stranded_display(path, text):
    """`$$ ... $$` that will not start a Markdown block, so is not display math.

    Only the *opening* delimiter of a matched pair is examined: a closing `$$`
    sits on its own line too and is not a block start, and a lone unmatched `$$`
    is a different defect -- an unterminated expression -- that the render audit
    already reports.
    """
    scan = mask(text, (FENCE, COMMENT, CODE))
    lines = scan.split("\n")
    starts = [0]
    for line in lines[:-1]:
        starts.append(starts[-1] + len(line) + 1)

    for m in BLOCK.finditer(scan):
        i = scan.count("\n", 0, m.start())
        before = scan[starts[i]:m.start()]
        if before.strip():
            why = "prose before it on the same line, so it is mid-paragraph"
        elif len(before) % 4:
            why = (f"indented {len(before)} spaces; a block inside a list item "
                   f"needs a multiple of 4")
        elif i and lines[i - 1].strip():
            why = "no blank line before it, so it continues the paragraph above"
        else:
            continue
        yield Finding(path, i + 1, "stranded display", why, False)


def fix_text(text: str) -> str:
    """Apply every mechanical repair.

    One edit per pass, then rescan.  Every repair changes the length of the
    text and so the offset of everything after it, and removing a `\\\\` can
    change which spans the delimiter patterns see; recomputing is cheap at this
    scale and is the only version that is obviously right.
    """
    while True:
        edit = _next_escape_edit(text) or _next_padded_edit(text)
        if edit is None:
            return text
        start, end, new = edit
        text = text[:start] + new + text[end:]


def _next_escape_edit(text):
    regions = math_regions(text)
    for m in ESCAPE.finditer(text):
        run, char = m.group(0)[:-1], m.group(0)[-1]
        if not in_math(regions, m.start()):
            continue
        if char in "{}" and len(run) == 2:
            return m.start(), m.end(), "\\" + char
        if char == "_" and len(run) == 1:
            return m.start(), m.end(), "_"
    return None


def _next_padded_edit(text):
    scan = mask(text, (FENCE, COMMENT, CODE, BLOCK))
    accepted = {(m.start(3), m.end(3)) for m in SMART.finditer(scan) if m.group(3)}
    for m in INLINE.finditer(scan):
        body = m.group(3)
        if not body or (m.start(3), m.end(3)) in accepted:
            continue
        if "\n\n" in body or len(body) > PADDED_MAX_LEN:
            continue
        if not LOOKS_LIKE_MATH.search(body) or not (
            body[:1].isspace() or body[-1:].isspace()
        ):
            continue
        return m.start(3), m.end(3), body.strip()
    return None


def pages(roots):
    for root in roots:
        root = pathlib.Path(root)
        if root.is_file():
            yield root
        else:
            yield from sorted(root.rglob("*.md"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("roots", nargs="*", default=["docs"],
                    help="files or directories to check (default: docs)")
    ap.add_argument("--fix", action="store_true",
                    help="rewrite the three mechanical defects in place")
    ap.add_argument("--strict", action="store_true",
                    help="also fail on stranded display blocks (advisory otherwise)")
    args = ap.parse_args(argv)

    gating, advisory, fixed, checked = [], [], 0, 0
    for page in pages(args.roots or ["docs"]):
        text = page.read_text(encoding="utf-8")
        if "$" not in text:
            continue
        checked += 1

        if args.fix:
            new = fix_text(text)
            if new != text:
                page.write_text(new, encoding="utf-8")
                fixed += 1
                text = new

        regions = math_regions(text)
        gating += list(find_escapes(page, text, regions))
        gating += list(find_padded(page, text))
        advisory += list(find_stranded_display(page, text))

    if args.strict:
        gating, advisory = gating + advisory, []

    if args.fix and fixed:
        print(f"✎ rewrote {fixed} file(s)")

    if gating:
        report(sys.stderr, gating, f"{len(gating)} math-source defect(s)")
        if any(f.fixable for f in gating):
            sys.stderr.write(
                "Lines without a leading `!` are mechanical: rerun with --fix.\n")
        if any(not f.fixable for f in gating):
            sys.stderr.write(
                "Lines with `!` need a decision -- a blank line before the block,\n"
                "a re-indent to the list item's content column, or a paragraph\n"
                "split.  Check what the surrounding prose belongs to first.\n")
        return 1

    print(f"✓ math source is clean ({checked} page(s) with math).")
    if advisory:
        # A tally, not the list.  Forty-one lines of known archive damage on
        # every green run trains the eye to skip the output, which is the one
        # thing a checker cannot afford.  `--strict` prints them in full.
        per_file = {}
        for f in advisory:
            per_file[f.path] = per_file.get(f.path, 0) + 1
        print(f"\nnote: {len(advisory)} stranded display block(s) on "
              f"{len(per_file)} imported archive page(s), not gating:")
        for path, n in sorted(per_file.items()):
            print(f"  {n:3}  {path}")
        print("Each publishes a literal `$` on either side of its expression.\n"
              "Tracked as M2-10 (#78); `--strict` lists them and fails on them.")
    return 0


def report(stream, findings, headline):
    by_kind = {}
    for f in findings:
        by_kind.setdefault(f.kind, []).append(f)
    stream.write(
        f"{headline} in {len({f.path for f in findings})} file(s):\n\n")
    for kind, fs in sorted(by_kind.items()):
        stream.write(f"  {kind} ({len(fs)}):\n")
        for f in fs:
            stream.write(f"  {f}\n")
        stream.write("\n")


if __name__ == "__main__":
    raise SystemExit(main())
