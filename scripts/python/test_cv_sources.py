#!/usr/bin/env python3
"""Tests for check_cv_sources.py.

Two kinds of case, and the second kind is why this file matters more than most.

The first kind is ordinary: what counts as a word, how each copy's shape is
read, which entries a block splits into.

The second is that a coverage checker can pass for the wrong reason. It reports
success when nothing is uncovered, and *nothing is uncovered* is also what an
extractor that has quietly stopped finding entries produces. So the cases below
include the failures the checker must still report: an entry `cv.yml` does not
carry, an omission declared for something that no longer exists, an omission
declared for something that is carried anyway, and a section heading that has
drifted out of the snapshot it was written against.

    python3 scripts/python/test_cv_sources.py
"""

from __future__ import annotations

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import check_cv_sources as C  # noqa: E402

failures: list[str] = []


def check(label, got, want):
    if got != want:
        failures.append(f"{label}\n     got:  {got!r}\n     want: {want!r}")


def problems(rows, data):
    return C.check(rows, data, explain=False)[0]


# ── what counts as a word ───────────────────────────────────────────────────

check("stopwords carry nothing",
      C.tokens("the of and a"), set())

check("diacritics fold, so Ruškuc and Ruskuc are one name",
      C.tokens("Ruškuc") == C.tokens("Ruskuc"), True)

check("...and so do Černý and Cerny",
      C.tokens("Černý") == C.tokens("Cerny"), True)

check("a URL contributes nothing, but its link text does",
      C.tokens("[Big Data](https://github.com/williamdemeo/x)"),
      {"big", "data"})

check("a bare URL contributes nothing at all",
      C.tokens("https://coursera.org/verify/4NP2MX787UAG"), set())

# A link target is only dropped when it is *a URL*.  The Zola copy writes its
# referees as `[Name](bare@address)`, with no `mailto:`, so a rule that dropped
# every target would make all seven addresses invisible and let cv.yml lose
# them without failing anything.  Raised by review on #91.
check("a link target that is not a URL still contributes",
      C.tokens("[Clifford Bergman](cbergman@iastate.edu)"),
      {"clifford", "bergman", "cbergman", "iastate", "edu"})

check("...but a mailto: target is a URL, and still goes",
      C.tokens("[jb](mailto:jb@math.hawaii.edu)"), {"jb"})

check("digits survive as words; single letters do not",
      C.tokens("Math 2001 x"), {"math", "2001"})

check("abbreviations canonicalise, both sides alike",
      C.tokens("Intl. J. of Algebra") <= C.tokens("International Journal of Algebra"),
      True)

check("...including months, which the copies write four ways",
      C.tokens("14--18 Apr 2019") == C.tokens("April 14--18, 2019"), True)

check("hyperlink labels are furniture, not content",
      C.tokens("(preprint link) (slides)"), set())

# The whole check rests on this: a word the merged file does not have means the
# entry is not covered.  If containment ever became similarity, the one thing
# this file is for would stop working.
check("containment is strict -- an extra word in the source is not covered",
      C.tokens("bounded homomorphisms and finitely generated fiber products")
      <= C.tokens("bounded homomorphisms and fiber products"),
      False)


# ── reading each copy's shape ───────────────────────────────────────────────

ATX = re.compile(r"^#\s+(.*)$")

check("an ordinal is enumeration, not a word the entry must contain",
      C.markdown_entries("# Talks\n1. Isotopic Algebras\n2. Permutability", ATX),
      [("Talks", "Isotopic Algebras"), ("Talks", "Permutability")])

check("a hard break splits entries that share a block",
      C.markdown_entries("# Service\nOrganizer, BLAST\\\nEditor, Algebra Universalis", ATX),
      [("Service", "Organizer, BLAST\\"), ("Service", "Editor, Algebra Universalis")])

check("a blank line splits too",
      C.markdown_entries("# X\nfirst\n\nsecond", ATX),
      [("X", "first"), ("X", "second")])

# Both are a run of dashes on their own line; only the line above tells them
# apart, and the Zola copy uses both within a few lines of each other.
check("a setext underline is a heading",
      C.markdown_entries("Education\n---------\nPhD", ATX, setext=True),
      [("Education", "PhD")])

check("...and a rule after a blank line is not",
      C.markdown_entries("# Education\nPhD\n\n--------\n\nMS", ATX, setext=True),
      [("Education", "PhD"), ("Education", "MS")])


# ── the snapshot the PDF reader was written against ─────────────────────────
#
# PDF_SECTIONS is a fixed list, which is only honest while it still describes
# the file.  A heading that stops matching would silently file every entry
# beneath it under the previous section -- which the coverage check would not
# notice, because sections do not affect coverage.

SNAPSHOT = C.SOURCES["jobapp"][0]
if SNAPSHOT.exists():
    lines = [l.strip() for l in SNAPSHOT.read_text(encoding="utf-8").split("\n")]
    missing = [" ".join(h) for h in C.PDF_SECTIONS
               if not any(lines[i:i + len(h)] == list(h) for i in range(len(lines)))]
    check("every PDF section heading still occurs in the snapshot", missing, [])

    check("the running heads are recognised as furniture",
          sum(1 for l in lines if C.PDF_FURNITURE.match(l)), 5)

    found = {section for section, _ in C.read_pdf_text(SNAPSHOT)}
    check("nothing lands in the preamble, so no heading was missed",
          "(preamble)" in found, False)


# ── the failures it has to keep reporting ───────────────────────────────────

# A title nothing in the repository carries, so these cases test the checker
# rather than accidentally matching a real bibliography entry.
ROWS = [("cvrepo:talks:zzyzx-quiescent-frobenoids", "Talks", "Zzyzx Quiescent Frobenoids")]

check("an entry no cv.yml entry covers is a problem",
      len(problems(ROWS, {"talks": [{"title": "Permutability in Diamonds"}]})), 1)

check("...and is not one once cv.yml carries it",
      problems(ROWS, {"talks": [{"title": "Zzyzx Quiescent Frobenoids"}]}), [])

check("a declared omission covers it instead",
      problems(ROWS, {"talks": [], "omissions": [
          {"id": "cvrepo:talks:zzyzx-quiescent-frobenoids", "reason": "because"}]}), [])

check("an omission with no reason is a problem",
      len(problems(ROWS, {"omissions": [{"id": "cvrepo:talks:zzyzx-quiescent-frobenoids"}]})), 1)

# A declaration that has stopped matching anything is how "nothing was lost"
# quietly becomes untrue again: the entry it was about may have been renamed,
# and nothing else would say so.
check("an omission naming no source entry is a problem",
      len(problems(ROWS, {"talks": [{"title": "Zzyzx Quiescent Frobenoids"}],
                          "omissions": [{"id": "cvrepo:talks:gone", "reason": "x"}]})), 1)

check("an omission for an entry cv.yml does carry is a problem",
      len(problems(ROWS, {"talks": [{"title": "Zzyzx Quiescent Frobenoids"}],
                          "omissions": [{"id": "cvrepo:talks:zzyzx-quiescent-frobenoids",
                                         "reason": "x"}]})), 1)

# `sources` is excluded from an entry's own words.  Were it not, an entry could
# cover a source entry by quoting its id, which is circular.
check("bookkeeping keys do not help an entry cover anything",
      len(problems(ROWS, {"talks": [{"sources": ["Zzyzx Quiescent Frobenoids"]}]})), 1)

check("a field name counts as a word, since the copies print it as a label",
      problems([("x:e:advisor", "Education", "Advisor:")],
               {"education": [{"advisor": "Ralph Freese"}]}), [])

check("publications.carried naming no bibliography.json entry is a problem",
      len(problems([], {"publications": {"carried": ["nosuchpaper"]}})), 1)


# ── the repository's own state ──────────────────────────────────────────────

check("the committed inventory matches what the extractors find",
      C.read_inventory() == C.extract(), True)

# The three snapshots are provenance and nothing edits them; that they are
# still there is the precondition for everything above.
for name, (path, _) in C.SOURCES.items():
    check(f"the {name} copy is present", path.exists(), True)


if failures:
    sys.stderr.write(f"✗ {len(failures)} failure(s):\n\n")
    for f in failures:
        sys.stderr.write(f"  {f}\n\n")
    raise SystemExit(1)

print("✓ check_cv_sources: all cases pass")
