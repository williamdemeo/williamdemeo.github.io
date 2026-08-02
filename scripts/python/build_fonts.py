#!/usr/bin/env python3
"""Build the site's self-hosted webfonts: subset the sources, emit WOFF2.

Why this exists rather than a `<link>` to a font CDN: the Zola site this one
replaces loads Fira Code from `cdn.rawgit.com`, which shut down in 2019, so its
intended monospace font has silently not rendered for years.  Nothing here
reaches the network at page-load time.

Why a build script rather than hand-placed files: the interesting part of the
output is *which characters are in it*.  A page of Agda that hits one codepoint
outside the subset falls back to whatever the operating system offers, mid-line,
and looks broken.  The subset therefore has to be derived from a stated
character repertoire rather than eyeballed, and derived again whenever that
repertoire changes.

Run it with `make fonts`.  The outputs are committed, so an ordinary build --
and CI -- never runs this and never needs the network.

Sources are pinned by SHA-256 rather than by a git ref.  Upstream moving a
branch is exactly the failure this should catch, and a hash catches it whatever
the URL says.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import sys
import unicodedata
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

try:
    from fontTools.subset import Options, Subsetter
    from fontTools.ttLib import TTFont
    from fontTools.unicodedata import block
    from fontTools.varLib.instancer import instantiateVariableFont
except ImportError:  # pragma: no cover - the message is the whole point
    sys.exit("error: fonttools and brotli are required.\n"
             "       pip install 'fonttools[woff]' brotli, or use the Nix dev shell.")

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "assets" / "fonts"
CACHE = ROOT / ".fonts-cache"

GF = "https://raw.githubusercontent.com/google/fonts/main/ofl"
JM = "https://raw.githubusercontent.com/cormullion/juliamono/master"

# ── character repertoires ───────────────────────────────────────────────────
#
# For the monospace face the unit is the Unicode *block*, not a list of
# characters, and the first version of this script got that wrong in a way
# worth recording.  Enumerating `agda-input-translations` from agda-input.el
# looks like the authoritative answer -- 1,952 characters, straight from the
# input method -- and it is not: agda-input *inherits* from Emacs' TeX input
# method for everything it does not redefine.  ℓ, Π and the subscript digits
# come from there, so all four were missing from the shipped subset and fell
# back to DejaVu Sans Mono on a real page.  `make font-audit` is what caught
# it, and an offline check against the same enumeration never could have.
#
# Shipping whole blocks costs roughly twice the bytes and removes that entire
# class of mistake: any character in a listed block renders, whether or not
# anyone anticipated it.  Excluded on purpose, because they are other writing
# systems rather than mathematical notation: CJK, Cyrillic, Braille, Canadian
# Syllabics, Arabic, Hebrew, the private-use areas and the legacy-computing
# symbols -- together about 60% of JuliaMono's 11,191 glyphs.

ASCII = {chr(c) for c in range(0x20, 0x7F)}
# U+00AD soft hyphen is invisible and trips fontTools' variable-font instancer
# on some sources; nothing renders it, so it is not worth carrying.
LATIN1 = {chr(c) for c in range(0xA0, 0x100)} - {chr(0x00AD)}
# Characters from blocks too large to ship whole, but common enough in running
# prose that a substitution would show.  Deliberately not ∀ ∃ ∈ ⊆ ≅ ≡ ↦: no
# text face carries them, and asking for them would report a gap on every face
# rather than say anything.  Mathematics in prose is KaTeX's job, and anything
# that escapes it lands on JuliaMono, which is the last self-hosted entry in
# the text stack for exactly that reason.
PROSE = set("‘’“”–—…†‡•·′″⁄←→↔⇒≈≠≤≥×÷−±°©®™№§¶")
# Blocks every face carries in full.  Latin Extended-A is not decoration: the
# publication list has a š in it, and before this line existed that one
# character rendered in Liberation Sans on the CV page while the rest of the
# sentence was Inter.  Greek is the same argument one step out -- prose about
# λ-calculus or an ε-δ argument should not change font mid-word.
TEXT_BLOCKS = ["Latin Extended-A", "Greek and Coptic", "General Punctuation"]


def text_charset(cmap: set[int]) -> set[str]:
    """The prose repertoire: a fixed core, plus whole blocks where present.

    The core is requested from every face whether or not the face has it, so
    that a gap is reported rather than quietly dropped.
    """
    return ASCII | LATIN1 | PROSE | block_chars(cmap, TEXT_BLOCKS)

# Blocks Agda notation draws on.  Split in two only to keep the download
# granular: the mathematical alphanumerics are 997 of JuliaMono's glyphs and
# 154 KB on their own, and a page that mentions `→` without ever showing an 𝑨
# should not pay for them.
SYMBOL_BLOCKS = [
    "Greek and Coptic",
    "Greek Extended",
    "Superscripts and Subscripts",
    "Letterlike Symbols",
    "Arrows",
    "Mathematical Operators",
    "Miscellaneous Technical",
    "Miscellaneous Mathematical Symbols-A",
    "Miscellaneous Mathematical Symbols-B",
    "Supplemental Arrows-A",
    "Supplemental Arrows-B",
    "Supplemental Mathematical Operators",
    "General Punctuation",
    "Supplemental Punctuation",
    "Combining Diacritical Marks",
    "Combining Diacritical Marks for Symbols",
    "Phonetic Extensions",             # ᵢ ᵣ ᵤ and the rest of the subscript letters
    "Phonetic Extensions Supplement",
    "Spacing Modifier Letters",
    "IPA Extensions",
    "Latin Extended-A",
    "Latin Extended-B",                # ƛ, which PLFA and the stdlib both use
    "Number Forms",
    "Geometric Shapes",
    "Box Drawing",
]
MATHALPHA_BLOCKS = ["Mathematical Alphanumeric Symbols"]

AGDA_INPUT_URL = "https://raw.githubusercontent.com/agda/agda/master/src/data/emacs-mode/agda-input.el"
AGDA_INPUT_SHA = "7b2b8e6c17d336c6761b58536f0837e7ae051f1b31c45d0065c5ba38bfbc00a3"


@dataclass
class Face:
    """One shipped WOFF2 file."""
    out: str                      # basename under docs/assets/fonts/
    family: str                   # CSS font-family
    url: str
    sha256: str
    weight: int = 400
    style: str = "normal"
    axes: dict = field(default_factory=dict)   # variable-font instance location
    charset: str = "text"                      # text | symbols | mathalpha


FACES = [
    # ── monospace ───────────────────────────────────────────────────────────
    # Three files, one family name, disjoint unicode-ranges: a run of code that
    # mixes ASCII and 𝑨 is still one face to the layout engine, but a page that
    # never shows an 𝑨 never downloads the 154 KB it lives in.
    Face("juliamono-text.woff2", "JuliaMono",
         f"{JM}/JuliaMono-Regular.ttf",
         "40a07da0d1601215eb6b89312eb44128a3e2f36675d3e1f518264bd391fc7023",
         charset="text"),
    Face("juliamono-symbols.woff2", "JuliaMono",
         f"{JM}/JuliaMono-Regular.ttf",
         "40a07da0d1601215eb6b89312eb44128a3e2f36675d3e1f518264bd391fc7023",
         charset="symbols"),
    Face("juliamono-mathalpha.woff2", "JuliaMono",
         f"{JM}/JuliaMono-Regular.ttf",
         "40a07da0d1601215eb6b89312eb44128a3e2f36675d3e1f518264bd391fc7023",
         charset="mathalpha"),

    # ── body and UI ─────────────────────────────────────────────────────────
    Face("inter-400.woff2", "Inter",
         f"{GF}/inter/Inter%5Bopsz%2Cwght%5D.ttf",
         "29160a80ff49ddcab2c97711247e08b1fab27a484a329ce8b813d820dc559031",
         weight=400, axes={"wght": 400, "opsz": 16}),
    Face("inter-600.woff2", "Inter",
         f"{GF}/inter/Inter%5Bopsz%2Cwght%5D.ttf",
         "29160a80ff49ddcab2c97711247e08b1fab27a484a329ce8b813d820dc559031",
         weight=600, axes={"wght": 600, "opsz": 20}),
    Face("inter-400-italic.woff2", "Inter",
         f"{GF}/inter/Inter-Italic%5Bopsz%2Cwght%5D.ttf",
         "acd98e64795781b2058f07b18475e0ecee2a0fe2b42a49e2f9e37d0d6bf66ce6",
         weight=400, style="italic", axes={"wght": 400, "opsz": 16}),

    # ── display ─────────────────────────────────────────────────────────────
    Face("newsreader-500.woff2", "Newsreader",
         f"{GF}/newsreader/Newsreader%5Bopsz%2Cwght%5D.ttf",
         "8a08d13f8a6c0d51be379a60af84f945f65369a67e509ee3c3bdcc421254d7c1",
         weight=500, axes={"wght": 500, "opsz": 36}),
]

LICENSES = [
    ("OFL-JuliaMono.txt", f"{JM}/LICENSE"),
    ("OFL-Inter.txt", f"{GF}/inter/OFL.txt"),
    ("OFL-Newsreader.txt", f"{GF}/newsreader/OFL.txt"),
]


# ── plumbing ────────────────────────────────────────────────────────────────

def fetch(url: str, sha256: str | None = None) -> bytes:
    """Download with a content-addressed cache; verify the hash when given."""
    CACHE.mkdir(exist_ok=True)
    key = hashlib.sha256(url.encode()).hexdigest()[:16] + "-" + url.rsplit("/", 1)[-1][:60]
    cached = CACHE / key
    if cached.exists():
        data = cached.read_bytes()
    else:
        with urllib.request.urlopen(url, timeout=120) as r:
            data = r.read()
        cached.write_bytes(data)
    got = hashlib.sha256(data).hexdigest()
    if sha256 and got != sha256:
        cached.unlink(missing_ok=True)
        raise SystemExit(
            f"error: {url}\n"
            f"       expected sha256 {sha256}\n"
            f"       got             {got}\n"
            "       Upstream moved.  Review the change, then update the pin.")
    return data


def agda_repertoire() -> set[str]:
    """The characters agda-input.el names directly.

    A lower bound on what a page of Agda contains, not the whole of it -- the
    input method inherits the rest from Emacs' TeX method, whose table is
    generated rather than written out and so cannot be read the same way.  It
    is still worth including: it catches characters that fall outside every
    block listed above.
    """
    src = fetch(AGDA_INPUT_URL, AGDA_INPUT_SHA).decode("utf-8")
    a = src.index("(defcustom agda-input-translations")
    b = src.index("(defcustom agda-input-user-translations")
    return {c for c in src[a:b]
            if ord(c) >= 0x80 and unicodedata.category(c) not in ("Cc", "Cf")}


def block_chars(font_cmap: set[int], names: list[str]) -> set[str]:
    """Every codepoint the face has in the named Unicode blocks."""
    return {chr(cp) for cp in font_cmap if block(chr(cp)) in names}


def unicode_ranges(codepoints: set[int]) -> str:
    """Collapse a codepoint set into a CSS `unicode-range` value."""
    out, cps = [], sorted(codepoints)
    i = 0
    while i < len(cps):
        j = i
        while j + 1 < len(cps) and cps[j + 1] == cps[j] + 1:
            j += 1
        out.append(f"U+{cps[i]:X}" if i == j else f"U+{cps[i]:X}-{cps[j]:X}")
        i = j + 1
    return ",".join(out)


def subset(data: bytes, chars: set[str], axes: dict) -> tuple[bytes, int, set[int]]:
    font = TTFont(io.BytesIO(data), fontNumber=0)
    if axes and "fvar" in font:
        have = {a.axisTag for a in font["fvar"].axes}
        font = instantiateVariableFont(font, {k: v for k, v in axes.items() if k in have},
                                       updateFontNames=False)
    cmap = set(font.getBestCmap())
    wanted = sorted({ord(c) for c in chars} & cmap)

    opt = Options()
    opt.layout_features = ["*"]          # keep kerning and the code ligature set
    opt.drop_tables += ["DSIG"]
    opt.name_IDs = ["*"]                 # keep the family and licence names
    opt.name_legacy = False
    opt.notdef_outline = False
    s = Subsetter(options=opt)
    s.populate(unicodes=wanted)
    s.subset(font)
    # Otherwise fontTools stamps head.modified with the current time and every
    # run produces different bytes, which makes `--check` useless and every
    # rebuild a diff.
    font.recalcTimestamp = False
    font.flavor = "woff2"
    buf = io.BytesIO()
    font.save(buf)
    n = len(font.getGlyphOrder())
    font.close()
    return buf.getvalue(), n, set(wanted)


CSS_HEADER = """\
/* Generated by scripts/python/build_fonts.py -- do not edit.
 *
 * Every face is served from this origin.  `theme.font: false` in mkdocs.yml is
 * what stops Material emitting its own <link> to fonts.googleapis.com; without
 * it these declarations would be additions rather than replacements.
 *
 * JuliaMono is split three ways by unicode-range under one family name, so a
 * page pays only for the notation it shows.  A page with nothing but ASCII in
 * its code blocks downloads %(latin)d KB and stops; `→` and `≡` pull the
 * %(symbols)d KB symbol file; an 𝑨 or a 𝓤 pulls the %(mathalpha)d KB of
 * mathematical alphanumerics on top.
 *
 * `font-display: swap` everywhere: a flash of fallback text beats invisible
 * text, and on the code faces it is also the signal that something is wrong --
 * unstyled Agda is obvious.
 */
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="report what would change; write nothing")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)

    mono = next(f for f in FACES if f.family == "JuliaMono")
    mono_cmap = set(TTFont(io.BytesIO(fetch(mono.url, mono.sha256)), lazy=True).getBestCmap())
    mono_text = text_charset(mono_cmap)
    agda = {c for c in agda_repertoire() if ord(c) in mono_cmap}
    mathalpha = block_chars(mono_cmap, MATHALPHA_BLOCKS) - mono_text
    symbols = (block_chars(mono_cmap, SYMBOL_BLOCKS) | agda) - mono_text - mathalpha

    print(f"JuliaMono cmap            : {len(mono_cmap)} characters")
    print(f"prose repertoire          : {len(mono_text)}")
    print(f"symbol blocks             : {len(symbols)}")
    print(f"mathematical alphanumerics: {len(mathalpha)}")
    print(f"named by agda-input.el and outside every listed block: "
          f"{len(agda - mono_text - symbols - mathalpha)}\n")

    written, css, total, stale = [], [], 0, []

    for face in FACES:
        data = fetch(face.url, face.sha256)
        if face.charset == "text":
            cmap = set(TTFont(io.BytesIO(data), lazy=True).getBestCmap())
            chars = text_charset(cmap)
        else:
            chars = {"symbols": symbols, "mathalpha": mathalpha}[face.charset]
        blob, nglyphs, covered = subset(data, chars, face.axes)
        path = OUT / face.out
        missing = {ord(c) for c in chars} - covered
        if args.check:
            if not path.exists() or path.read_bytes() != blob:
                stale.append(face.out)
        else:
            path.write_bytes(blob)
        total += len(blob)
        written.append((face, len(blob), nglyphs, len(covered), missing))
        css.append(
            f"@font-face {{\n"
            f"  font-family: '{face.family}';\n"
            f"  font-style: {face.style};\n"
            f"  font-weight: {face.weight};\n"
            f"  font-display: swap;\n"
            f"  src: url('{face.out}') format('woff2');\n"
            f"  unicode-range: {unicode_ranges(covered)};\n"
            f"}}\n")

    kb = {f.out: b // 1024 for f, b, *_ in written}
    css_text = CSS_HEADER % {
        "latin": kb["juliamono-text.woff2"],
        "symbols": kb["juliamono-symbols.woff2"],
        "mathalpha": kb["juliamono-mathalpha.woff2"],
    } + "\n" + "\n".join(css)

    if args.check:
        if (OUT / "fonts.css").read_text() != css_text:
            stale.append("fonts.css")
    else:
        (OUT / "fonts.css").write_text(css_text)
        for name, url in LICENSES:
            (OUT / name).write_bytes(fetch(url))

    print(f"{'file':<32} {'glyphs':>7} {'chars':>7} {'KB':>8}  gaps")
    print("-" * 72)
    for face, nbytes, nglyphs, nchars, missing in written:
        gap = "-" if not missing else f"{len(missing)} not in the source face"
        print(f"{face.out:<32} {nglyphs:>7} {nchars:>7} {nbytes / 1024:>8.1f}  {gap}")
    print("-" * 72)
    print(f"{'total':<32} {'':>7} {'':>7} {total / 1024:>8.1f}")

    # A gap is a character the shipped face does not have, so a real page shows
    # it in whatever the operating system substitutes.  Name them while there
    # are few enough to name; summarise by Unicode block once there are not.
    print("\ngaps in detail:")
    for face, _b, _g, _c, missing in written:
        if not missing:
            continue
        if len(missing) <= 8:
            named = ", ".join(f"{chr(c)} U+{c:04X} {unicodedata.name(chr(c), '?')}" for c in sorted(missing))
            print(f"  {face.out}: {named}")
        else:
            blocks = sorted({unicodedata.name(chr(c), "?").split()[0] for c in missing})
            print(f"  {face.out}: {len(missing)} characters, all in {', '.join(blocks[:8])}")

    if args.check:
        if stale:
            print("\nstale: " + ", ".join(stale))
            print("run `make fonts`")
            return 1
        print("\nup to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
