#!/usr/bin/env python3
"""Pull the text layer out of a pdflatex-produced PDF.  Provenance tooling.

This produced `demeo_cv-2022.txt` once, by hand, from the `cv/demeo_cv.pdf` that
`gitlab.com/williamdemeo/job-app` carries -- the fourth CV copy in ADR-003.  No
build target runs it and nothing imports it; it lives here so that snapshot is
reproducible rather than merely asserted.  See README.md in this directory for
the checksums.

    python3 import/legacy-cv/pdf_text.py demeo_cv.pdf > demeo_cv-2022.txt

Stdlib only, and deliberately minimal: it needs to handle one Computer Modern
document, not PDF in general.

Two things are worth knowing about what it does and does not recover:

  spacing      A PDF has no space characters between words set by TeX.  The
               gaps are kerns -- numbers inside a `TJ` array, in thousandths of
               an em -- so a large negative one is where a space belongs.  The
               threshold below is what makes the output readable prose instead
               of onerunontogetherlikethis.

  hyperlinks   Not in the text layer at all.  A link is an `/Annot` object over
               a rectangle, and its target never appears in the content stream,
               so every URL is lost.  That is a property of the format, not a
               shortcut taken here.

Ligatures come back through the OT1 encoding table: Computer Modern puts `fi`
at 0x0c, so without it the extract reads "nite algebras" and "veri cation".
"""

import re
import sys
import zlib

#: OT1 codes that are not the ASCII character of the same value.  Only the ones
#: this document actually uses; an unmapped code falls through as-is.
#:
#: 0x12-0x18 and 0x7F are TeX's floating accents, and they are *dropped* rather than
#: recombined.  In OT1 an accent is a glyph of its own, set before the letter it
#: sits over, so `\'{e}` reaches the content stream as two characters and
#: "F\x13ed\x13erale" is Fédérale.  Dropping the accent leaves "Federale", which
#: is what the comparison in check_cv_sources.py folds it to anyway; keeping it
#: would leave a control character in the middle of a word.
OT1 = {
    0x0B: "ff", 0x0C: "fi", 0x0D: "fl", 0x0E: "ffi", 0x0F: "ffl",
    0x10: "i", 0x11: "j",
    0x12: "", 0x13: "", 0x14: "", 0x15: "", 0x16: "", 0x17: "", 0x18: "",
    0x19: "ss", 0x1A: "ae", 0x1B: "oe", 0x1C: "o", 0x1D: "AE", 0x1E: "OE",
    0x1F: "O", 0x7B: "--", 0x7C: "---", 0x7F: "", 0x00: "",
}

#: Kern width, in thousandths of an em, at or beyond which a gap is a space.
#: TeX's interword glue in this document lands around -170 to -280; the kerns
#: *within* a word are an order of magnitude smaller.
SPACE_KERN = -110

TOKEN = re.compile(
    rb"\((?:\\.|[^\\()])*\)|\[|\]|-?\d+\.?\d*"
    rb"|\bTJ\b|\bTj\b|\bTd\b|\bTD\b|\bT\*\b|\bBT\b|\bET\b"
)
NUMBER = re.compile(rb"-?\d+\.?\d*")

#: An embedded Type 1 font program is a compressed stream like any other, and
#: its binary happens to contain the bytes `Tj` and `TJ` often enough that
#: looking for those is not a filter.  What it does not contain is any of
#: these, and what it does contain is its own copyright notice -- which is how
#: five AMS Computer Modern licences ended up in the middle of a CV.
FONT_PROGRAM = re.compile(rb"eexec|/CharStrings|/FontType|%!(?:PS-Adobe)?Font")


def decode(body: bytes) -> str:
    """One PDF string literal, as text."""
    body = re.sub(
        rb"\\([nrtbf()\\])",
        lambda m: {b"n": b"\n", b"r": b"\r", b"t": b"\t"}.get(m.group(1), m.group(1)),
        body,
    )
    body = re.sub(rb"\\\n", b"", body)
    body = re.sub(rb"\\([0-7]{1,3})", lambda m: bytes([int(m.group(1), 8) & 0xFF]), body)
    return "".join(OT1.get(c, chr(c)) for c in body)


def stream_text(stream: bytes) -> str:
    out, in_array = [], False
    for token in TOKEN.finditer(stream):
        tok = token.group(0)
        if tok in (b"Td", b"TD", b"T*", b"BT", b"ET"):
            out.append("\n")
        elif tok == b"[":
            in_array = True
        elif tok == b"]":
            in_array = False
        elif tok.startswith(b"("):
            out.append(decode(tok[1:-1]))
        elif in_array and NUMBER.fullmatch(tok) and float(tok) <= SPACE_KERN:
            out.append(" ")
    return "".join(out)


def main(path: str) -> int:
    data = open(path, "rb").read()
    pages = []
    for match in re.finditer(rb"stream\r?\n", data):
        start = match.end()
        end = data.find(b"endstream", start)
        if end < 0:
            continue
        try:
            stream = zlib.decompress(data[start:end])
        except zlib.error:
            # Font programs and images.  Not text, and not an error.
            continue
        if FONT_PROGRAM.search(stream[:4096]):
            continue
        if b"TJ" not in stream and b"Tj" not in stream:
            continue
        pages.append(stream_text(stream))

    text = re.sub(r"[ \t]+", " ", "\n".join(pages))
    print("\n".join(line.strip() for line in text.split("\n") if line.strip()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
