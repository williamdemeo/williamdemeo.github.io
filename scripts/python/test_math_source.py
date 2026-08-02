#!/usr/bin/env python3
"""Tests for check_math_source.py.

The cases here are the ones the checker got wrong on the way to working, plus
the ones a future edit is most likely to break: what counts as "inside math",
which backslash runs are defects and which are correct LaTeX, and where the
line between a padded delimiter and a dollar sign in prose falls.

    python3 scripts/python/test_math_source.py
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import check_math_source as C  # noqa: E402

PATH = pathlib.Path("test.md")

failures: list[str] = []


def check(label, got, want):
    if got != want:
        failures.append(f"{label}\n     got:  {got!r}\n     want: {want!r}")


def kinds(text):
    """Every finding the checker would report for `text`, as a sorted list."""
    regions = C.math_regions(text)
    found = (
        list(C.find_escapes(PATH, text, regions))
        + list(C.find_padded(PATH, text))
        + list(C.find_stranded_display(PATH, text))
    )
    return sorted(f.kind for f in found)


def fixed(text):
    return C.fix_text(text)


# ── what counts as mathematics ──────────────────────────────────────────────

check("over-escaped brace inside math is a finding",
      kinds(r"Let $\\{0,1\\}$ be."), ["over-escaped brace"] * 2)

check("the same sequence in prose is not",
      kinds(r"Write \\{ to get a brace."), [])

check("...nor in an HTML comment, which is never published",
      kinds(r"<!-- $\\{0,1\\}$ -->"), [])

check("...nor in a code span, which renders verbatim",
      kinds(r"Type `$\\{0,1\\}$` to see it."), [])

check("...nor in a fenced block",
      kinds("```\n" + r"$\\{0,1\\}$" + "\n```"), [])

# The blog posts hit this: an inline span that wraps across a source line.
check("inline math spanning a newline is still math",
      kinds("text $\\\\{a,\n b\\\\}$ more"), ["over-escaped brace"] * 2)

check("display math is math too",
      kinds("text\n\n$$\n\\\\{a\\\\}\n$$\n\ntext"), ["over-escaped brace"] * 2)


# ── backslash runs ──────────────────────────────────────────────────────────
#
# The whole point of matching the run rather than the two characters.

check("a single backslash before a brace is correct LaTeX",
      kinds(r"$\{0,1\}$"), [])

check("three backslashes are a line break then a brace, also correct",
      kinds("$\\begin{matrix}a\\\\\\{b\\}\\end{matrix}$"), [])

check("a line break before a letter is a row separator, not a defect",
      kinds(r"$\begin{bmatrix}x\\y\end{bmatrix}$"), [])

check("an escaped underscore is a defect",
      kinds(r"$A\_1$"), ["escaped underscore"])

check("a plain subscript is not",
      kinds(r"$A_1$"), [])

check("a line break before a subscript is left alone",
      kinds(r"$\begin{matrix}a\\_1\end{matrix}$"), [])


# ── padded delimiters ───────────────────────────────────────────────────────

check("whitespace after the opening dollar defeats smart_dollar",
      kinds(r"Let $ \mathbf{A}$ be."), ["padded delimiter"])

check("whitespace before the closing dollar does too",
      kinds(r"Let $\mathbf{A} $ be."), ["padded delimiter"])

check("a tight span is fine",
      kinds(r"Let $\mathbf{A}$ be."), [])

check("dollar signs in prose are not delimiters",
      kinds("It costs $5, and the tip is $1 more."), [])

check("...even next to a subscript elsewhere in the paragraph",
      kinds("It costs $5 and $9, where $x_1$ is the price."), [])

check("the interior of a display block is not a padded inline span",
      kinds("text\n\n$$\n x = y\n$$\n\ntext"), [])


# ── stranded display blocks ─────────────────────────────────────────────────

check("a display block at the start of its own block is fine",
      kinds("text\n\n$$x = y$$\n\ntext"), [])

check("...and so is one indented four spaces inside a list item",
      kinds("+ item\n\n    $$x = y$$\n\n    more"), [])

check("two spaces is not enough for python-markdown",
      kinds("+ item\n\n  $$x = y$$\n\n  more"), ["stranded display"])

check("nor is a display block with no blank line before it",
      kinds("text\n$$x = y$$\n\ntext"), ["stranded display"])

check("nor one with prose ahead of it on the line",
      kinds("we have $$x = y$$ and so on.\n"), ["stranded display"])

# A block ends at a blank line as surely as it starts after one.  Missed at
# first, and the page said so: the delimiter opened a block it did not own, so
# python-markdown handed the whole thing to the inline processor and published
# a literal `$` on each side.
check("nor one the paragraph below runs into",
      kinds("text\n\n$$x = y$$\nand so on.\n"), ["stranded display"])

check("...which is not the same as a block at the end of the file",
      kinds("text\n\n$$x = y$$\n"), [])

check("the closing delimiter is not reported as a second finding",
      kinds("text\n\n$$\nx = y\n$$\n\ntext"), [])


# ── the fixer ───────────────────────────────────────────────────────────────

check("braces and underscores are repaired together",
      fixed(r"$\\{A\_1, A\_2\\}$"), r"$\{A_1, A_2\}$")

check("padding is stripped",
      fixed(r"Let $ \mathbf{A} $ be."), r"Let $\mathbf{A}$ be.")

check("a repair inside a comment is not made",
      fixed(r"<!-- $\\{a\\}$ -->"), r"<!-- $\\{a\\}$ -->")

check("correct source is left byte for byte alone",
      fixed(r"$\{A_1\}$ and $\begin{bmatrix}x\\y\end{bmatrix}$"),
      r"$\{A_1\}$ and $\begin{bmatrix}x\\y\end{bmatrix}$")

check("fixing is idempotent",
      fixed(fixed(r"$\\{A\_1\\}$")), fixed(r"$\\{A\_1\\}$"))

# Removing a `\\` shifts every offset after it, which is why the fixer rescans
# after each edit rather than collecting a batch.
check("many defects in one span are all repaired",
      fixed(r"$\\{a\_1, \\{b\_2\\}, c\_3\\}$"), r"$\{a_1, \{b_2\}, c_3\}$")

# A padded span becomes math once the padding goes, so what is "inside math"
# changes underneath the escape pass.  Both have to be applied to a fixed point.
check("a padded span's contents are repaired after it becomes math",
      fixed(r"Let $ \\{A\_1\\} $ be."), r"Let $\{A_1\}$ be.")


if failures:
    sys.stderr.write(f"✗ {len(failures)} failure(s):\n\n")
    for f in failures:
        sys.stderr.write(f"  {f}\n\n")
    raise SystemExit(1)

print("✓ check_math_source: all cases pass")
