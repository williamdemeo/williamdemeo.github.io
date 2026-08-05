<!-- File: docs/adr/010-cv-pdf-toolchain.md -->

# ADR-010: Typst for the CV's PDF, and a committed PDF a check recompiles

**Status**: Accepted

**Date**: 2026-08-04

**Deciders**: William DeMeo

**Related**: [#41](https://github.com/williamdemeo/williamdemeo.github.io/issues/41) (M7-1), [#16](https://github.com/williamdemeo/williamdemeo.github.io/issues/16) (M2-7), [#42](https://github.com/williamdemeo/williamdemeo.github.io/issues/42) (M7-2), [#44](https://github.com/williamdemeo/williamdemeo.github.io/issues/44) (M7-4), [ADR-003](003-cv-single-source.md), [ADR-004](004-nix-environment.md), [ADR-005](005-visual-system.md), [ADR-006](006-bibliography-source.md)

---

## Context

ADR-003 made `cv.yml` the only authoritative CV source and left it unrendered.
#41 renders it, to a web page and to a PDF, from that one file — because a PDF
that visibly disagrees with the website is worse than no PDF, and academic and
research applications still ask for one.

The PDF it replaces is worth describing, because it is the argument. `pdfinfo`
reports `docs/assets/DeMeo-CV.pdf` as four pages produced by **pdfTeX 1.40.16 on
30 December 2016**. It predates the Charles University post, the RelationalAI
post, the NJIT post, the IO post, every publication since 2016, and both Agda
Implementors' Meetings. It has been the file behind the page's *Download PDF*
button for the whole life of this site. Nothing made it stale on purpose;
nothing could have noticed.

The choice was between Pandoc with a LaTeX template — the natural one given the
author's LaTeX background, and what #41 suggests — and Typst. Both are heavy
additions to `flake.nix` on the face of it, and ADR-004 makes any pip dependency
an obligation to pin in two places.

## Decision

**Typst, from the pinned nixpkgs, compiling a committed PDF that a check
recompiles and compares byte for byte.**

Four files, and which is written by hand matters:

| file | written by | checked by |
| --- | --- | --- |
| `docs/cv.md` | `scripts/python/gen_cv.py`, from `cv.yml` | `gen_cv.py --check`, and the coverage check below |
| `cv/cv.typ` | the same script, same run | `gen_cv.py --check` |
| `cv/publications.typ` | `gen_publications.py`, from `bibliography.json` | `gen_publications.py --check` |
| `cv/template.typ` | **by hand** — it is the layout | the PDF comparison below |
| `docs/assets/DeMeo-CV.pdf` | `typst compile` | `gen_cv.py --check --pdf` |

`checks.cv-render` in `flake.nix` runs the last of those, so every pull request
recompiles the PDF and fails if the committed one differs.

## Why Typst

### The cost was measured rather than estimated

Each candidate was realised against this repository's own `flake.lock`, and the
figures below are what `nix build --dry-run` reports as *additional* over the
store the dev shell already needs — which is exactly what CI pays on a cache
miss:

| | download | unpacked | store paths |
| --- | --- | --- | --- |
| **typst 0.13.1** | **11.5 MiB** | **35.2 MiB** | **1** |
| pandoc 3.6 | 27.3 MiB | 210.6 MiB | 4 |
| texliveSmall | 69.3 MiB | 175.6 MiB | 117 |
| pandoc + texliveSmall | 96.6 MiB | 386.2 MiB | 121 |
| weasyprint 65.1 | 4.1 MiB | 25.0 MiB | 8 |

The deploy workflow bounds its cache upload at 2 GiB and the dev shell closure is
already around 450 MiB. Typst is one store path and a rounding error against
that; the Pandoc pair is eight times the download and eleven times the unpacked
size, for a document of six pages.

### The dependency cost is not where it looked like it was

The obvious objection is ADR-004's: a second dependency set is only safe while
both agree, and `checks.requirements-pins` is what makes drift loud. That
objection does not apply to two of the three candidates and does apply to the
third, which is the reverse of what "Typst is exotic, LaTeX is standard" would
suggest.

**Neither Typst nor Pandoc is a Python package**, so neither appears in
`requirements.txt` and neither gives `requirements-pins` anything to match.
WeasyPrint is one, and would cost a pin in both places for as long as it lived
there.

`scripts/python/build_fonts.py` is the precedent, and it is explicit: `fonttools`
and `brotli` are deliberately *not* in `requirements.txt`, because adding them
would oblige `flake.nix` to match their versions for a generator that runs by
hand and whose output is committed. The CV's PDF is the same shape of thing. The
non-Nix path is untouched: `make serve` and `make check` never compile a PDF,
and the committed one is what the site build copies.

### It is reproducible, and that is what makes the check possible

Typst's output was tested rather than assumed. With the document's date set
explicitly, two compiles produce **byte-identical** files, and so does a compile
from a different directory, under a different timezone, and in a different
locale. No source path appears anywhere in the output; `xmpMM:DocumentID` is
derived from the content.

That property is the whole design. Because a fresh compile of the committed
`.typ` reproduces the committed PDF exactly, "is this PDF the one this source
produces?" is a question with a yes-or-no answer, and `checks.cv-render` asks it
on every pull request. Under Pandoc the same check needs `SOURCE_DATE_EPOCH` and
`FORCE_SOURCE_DATE` and a `\pdfvariable suppressoptionalinfo` incantation to get
close to it.

Four ways of going stale were tried against the finished check, and it caught
each: editing `cv.yml` without regenerating, editing the hand-written template
without recompiling, altering the PDF, and tampering with the build date.

### It brings its own fonts

Typst embeds Libertinus Serif, New Computer Modern and DejaVu Sans Mono, and the
compile passes `--ignore-system-fonts`. So the PDF's inputs are the Typst binary,
two `.typ` files and a date, and nothing else — no font on the machine can change
the output, which is the other half of the reproducibility argument.

The PDF therefore does **not** use the site's faces (ADR-005: Inter, Newsreader,
JuliaMono). Two reasons. Those are shipped as *subsetted* WOFF2, which Typst
cannot read and which would be missing glyphs if it could; and matching them
would mean a font package in the closure and a `--font-path` that has to be
identical on a laptop and on a runner, which is a reproducibility hazard bought
for a resemblance nobody sees, since the two documents are never read side by
side. Libertinus is what a CV in this field looks like.

### What Pandoc would have bought

One real thing, and it is smaller than it appears. Pandoc could in principle
consume the same Markdown the web page uses, which is the strongest possible
version of "they cannot disagree". In practice it could not: that page carries a
`--8<--` snippet include, `attr_list` attributes and `md_in_html` component
wrappers, none of which Pandoc reads, so it would need its own generated
Markdown — and at that point it is the same architecture as this one with a
larger closure.

The familiarity argument is real and is answered by the division of labour above.
What gets edited by hand is `cv/template.typ`, 170 lines of layout. Nobody writes
Typst markup here; the generator emits data.

## Why the PDF is committed

It would be tidier for the site derivation to build the PDF into `$out` and for
git to hold no binary. That was rejected for one concrete reason: **ADR-004
promises that a contributor without Nix can build this site from
`requirements.txt`**, and `mkdocs build --strict` fails on a link to an asset
that is not in `docs/`. Generating the PDF during the site build makes a
typesetter a prerequisite for building the website, which is a real cost paid so
that git holds 90 KB less.

Committing it also matches how everything generated here is treated:
`docs/_snippets/`, `docs/publications.bib`, `docs/assets/fonts/*.woff2`,
`docs/assets/evidence.json` and `import/legacy-cv/inventory.tsv` are all
committed outputs with a `--check` beside them.

"The PDF builds in CI", which #41 asks for, is satisfied in the exact sense that
matters: CI compiles it from source on every pull request and fails if the
result differs from the file that will be served. What is published is a file a
build has verified, rather than a file a build happened to produce.

## What does not move

**The URL.** The PDF keeps the path it has, `docs/assets/DeMeo-CV.pdf`, served
at `/assets/DeMeo-CV.pdf`. Nothing in `redirects.yml` changes, and there is no
rule to add — which is also the only correct outcome, since `check_redirects.py`
fails a rule matching no URL in either legacy inventory, and neither inventory
contains this one. (The Octopress site served the file from the repository root
at `/DeMeo-CV.pdf`; that URL is not in `archive/octopress/urls.txt`, which was
derived from the crawled page list, and it has already been unserved since the
migration. `is_stubbable` would refuse it in any case: an HTML redirect stub is
the wrong response to a request for a PDF.)

**`bibliography.json` stays the only publication list.** `gen_publications.py`
gained a fourth output rather than the CV gaining a second publication renderer.
The Typst file it emits carries the same entries, in the same order, with the
same emphasis as the Markdown snippet, because both are now rendered from one
set of runs in that script — which is a property its tests check.

**The date gutter, the components, the omissions mechanism.** The page is built
from the M3-3 components (`timeline`, `talks`); `omissions:` is still where page
chrome is declared.

## The build date is the date of the render, not of the build

#41 asks for a build date in the footer. A date read from the clock at compile
time would change the PDF daily, which would make the byte comparison above
impossible — and a check that has to forgive a difference stops noticing the
differences it was written for.

So the date is stamped into `cv/cv.typ` when `make cv` runs, and the footer
prints that. It means what a reader wants it to mean: **when this document was
last rendered from its source**, not which morning a CI job happened to run. It
is visible in `git log -p cv/cv.typ`, and `--check` re-renders with the date it
finds in the committed file, so everything except that one line is compared
exactly, and a file with no date in it fails.

## Consequences

- **A CV edit is `make cv-pdf` and a commit.** Editing `cv.yml` and forgetting
  is caught by `checks.cv-render`; editing the template and forgetting is caught
  by the same check.
- **`nix flake check` gains one derivation and 11.5 MiB.**
- **A nixpkgs bump that moves Typst will fail the check** until the PDF is
  regenerated, since the producer string is part of the file. That is the
  contract working, and the repair is one command.
- **The page is now covered by `check_cv_sources.py` in a way it was not.** Its
  `site` rows went from 14 to 233, and every one is a rendering of a `cv.yml`
  entry that the coverage rule matches against that entry. "The page says only
  what the source says" became a check.
- **Six declared page-chrome omissions became two.** Four described hand-written
  chrome the rendering deleted, one is replaced by the publications-page
  pointer. Nothing was promoted out of `omissions:` into an entry.
- **The 2016 PDF is gone**, and with it the last hand-maintained CV copy.
- **`make cv-pdf` needs typst.** It is in the dev shell; outside Nix,
  `nix run nixpkgs#typst` or a 30 MB release binary. The script says so when it
  is missing, and no other target needs it.
- **#44's résumé variant has a template to start from** rather than a document
  to copy, and the `kind:` field on each appointment that this rendering
  deliberately does not use.

## Two defects the rendering found

Neither is this ADR's subject, and both are worth recording because they are
what rendering a file buys over reading it.

- **Seven dates in `cv.yml` were losing their year.** In a YAML *flow* mapping
  an unquoted comma ends the value, so `dates: April 12--16, 2021` parsed as
  `April 12--16` plus a stray key `2021:` with nothing under it. All seven are
  in `summer_schools[*].attended`, and all seven are now quoted. The entry's
  words are unchanged, so the coverage check is unaffected — which is why
  nothing had caught it.
- **The NSF grant's `role:` said the same thing twice**, once in figures and
  once in words, because the merge kept both copies' wording in the field that
  gets rendered. The second is now in `aliases:`, which is the field for how
  another copy wrote a thing and which nothing renders. The entry's token set is
  identical either way.

## Alternatives considered

**Pandoc with a LaTeX template.** Rejected on closure size and on
reproducibility, above. Worth revisiting if the CV ever needs something Typst
cannot set, which after six pages of it has not come up.

**WeasyPrint, rendering the site's own HTML and CSS.** The cheapest of the three
in the store, and the only one that could make the PDF look like the site by
construction. Rejected because it is the only one that costs a pip pin in two
places (ADR-004), and because its typography is browser-grade: CSS Paged Media
and no Knuth–Plass paragraph breaking, for a document whose whole purpose is to
be read on paper.

**Generating the PDF in the site derivation and committing nothing.** Rejected:
it makes a typesetter a prerequisite for `mkdocs build --strict`, which breaks
ADR-004's promise about the non-Nix path.

**Checking the PDF by extracting its text rather than comparing bytes.**
Rejected. It needs a PDF text extractor — a dependency — and it is a weaker
check: it would not notice a layout change, and layout is what the template
does. Byte comparison is available here only because Typst is reproducible, and
taking it was most of the reason to prefer Typst.

**Recording the build date in a sidecar file beside the PDF.** Rejected as
redundant once the date lives in the committed `.typ`, which is text, diffable,
and already an input to the compile.

**Rendering the full publication list rather than the six `_cv` entries.**
Rejected as not this issue's to decide: which publications the CV shows is the
`_cv` flag in `bibliography.json` (ADR-006, ADR-003), the page has always been
headed *Selected publications*, and a pointer to the full record now sits under
it. #42 can re-flag.

## Note on method

`nix flake check` was **not** run for this change: the sandbox this was prepared
in could substitute from `cache.nixos.org` but the full check was not executed
here, and saying it passed would be saying something not checked. What was run,
all of it in the dev shell:

- `checks.cv-render`'s two commands directly — `gen_cv.py --check --pdf` — and
  the four staleness cases above, each of which the check caught.
- `make cv-check` (986 entries across four copies, 941 covered, 45 declared),
  `make cv-test`, `gen_publications.py --check`, `make publications-test`.
- `mkdocs build --strict`, `make math-source`, `make math-audit`,
  `test_redirects.py`, and `check_redirects.py --verify-inventory --site site`.
- The PDF was rendered to images and read, page by page. Three things were wrong
  on the first pass and were fixed: the list bullets sat above their baseline
  (a grid aligns rows on the top of the cell, not on a shared baseline), the
  publication numbers had no gutter, and every talk spent a line on a link the
  M3-3 talk component puts on the title.
