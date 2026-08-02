# ADR-006: One authoritative bibliography, in CSL-JSON

**Status**: Accepted

**Date**: 2026-08-02

**Deciders**: William DeMeo

**Related**: [#29](https://github.com/williamdemeo/williamdemeo.github.io/issues/29) (M5-1), [#30](https://github.com/williamdemeo/williamdemeo.github.io/issues/30) (M5-2), [#41](https://github.com/williamdemeo/williamdemeo.github.io/issues/41) (M7-1), [#47](https://github.com/williamdemeo/williamdemeo.github.io/issues/47) (M8-2)

> **Numbering.** #29 asked for this to be ADR-004. That number was taken by the
> Nix environment decision before this issue was written, and 005 is the visual
> system, so this is 006.

---

## Context

The publication list existed in three hand-maintained copies, and they
disagreed. `scripts/python/reconcile_bibliography.py` compares them:

```
cv        6 entries
research  11 entries
zotero    6 entries

15 distinct works across all three lists
6 work(s) with conflicting metadata
```

No copy was a superset of the others. The CV carried the two most recent papers
and neither of the others did; the Zotero export carried three works absent from
both; the research page carried the pre-2005 signal-processing papers alone.

## Decision

**`bibliography.json` at the repository root is the only authoritative list**,
in CSL-JSON. `scripts/python/gen_publications.py` renders it to
`docs/_snippets/publications.md`, which the publications page (#30) and the CV
(#41) include. Neither holds a second copy.

### Why CSL-JSON over BibTeX

#29 called it a toss-up. One consideration breaks the tie: **BibTeX would cost a
dependency and CSL-JSON costs nothing.** Python has no BibTeX parser in the
standard library, so choosing it means adding `bibtexparser` to
`requirements.txt` — and ADR-004's `checks.requirements-pins` then obliges
`flake.nix` to match its version, for the sake of parsing a format that JSON
already expresses. `json` is in the standard library.

The existing Zotero export is already CSL-JSON, so it imports without
conversion, and Zotero round-trips it if a reference manager is ever wanted
again. BibTeX remains available: CSL-JSON converts to it mechanically.

### The schema extension, and why it was needed

The three lists appeared to disagree about years. They did not: **Zotero
recorded the arXiv posting date as `issued`, while the CV and the research page
recorded publication dates.** "Universal algebraic methods" is 2016 in Zotero
and 2022 in the CV — the arXiv posting and the LMCS publication, both correct.

CSL-JSON has no standard field for that distinction, so entries carry
`_preprint.arxiv-year` alongside `issued`. Underscore-prefixed keys are ignored
by CSL processors, so the file stays valid CSL-JSON. The same convention carries
`_arxiv`, `_role`, `_note`, `_source` (which lists the copies an entry came
from) and `_needs_review`.

## Consequences

- **Eight entries carry `_needs_review`** and are printed on every run of
  `make publications`. They are conflicts the three sources could not settle
  between them, not defects in the tooling. Two matter:
  - the CV titles a 2020 IJAC paper *Bounded homomorphisms and fiber products
    of lattices*; the research page says *…and finitely generated fiber
    products*. Same arXiv id. One is wrong.
  - arXiv 2101.10166 appears under two entirely different titles — *A
    machine-checked proof of Birkhoff's variety theorem in Martin-Löf type
    theory* (CV) and *The Agda Universal Algebra Library and Birkhoff's Theorem
    in Dependent Type Theory* (research page, describing it as the unabridged
    version of the TYPES submission). If those are separate works this should be
    two entries.
- **Nothing here was verified against a publisher.** `export.arxiv.org` and
  `doi.org` are both blocked from the environment this was built in. The entries
  are *reconciled* claims, not *checked* ones. `gen_publications.py` validates
  internal soundness only — unique ids, plausible years, well-formed arXiv ids —
  and deliberately does not pretend to resolve anything. Real resolution belongs
  to #47, which now records the two failure modes that make it necessary.
- The three legacy copies stay until #30 and #41 render from the generated
  Markdown; the CV's "Selected publications" section becomes an include.
  `import/legacy-bib-pubs.json` preserves the Zotero export as provenance.
- Adding a publication is one edit to `bibliography.json` plus
  `make publications`.

## Alternatives considered

**Keep BibTeX in the existing `williamdemeo/bibtex` repository and fetch it.**
Rejected: it makes the build depend on a second repository being reachable, and
the redirect work (#15) already showed how expensive a cross-repository
dependency is to verify from a sandbox.

**Generate at build time from a hook, as the redirects do.** Rejected here,
because unlike redirect stubs the output is prose a human should be able to read
in a diff before it ships. It is committed, and `make publications-check` keeps
it honest.
