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

## Verification against the publishers

Reconciling three copies makes them agree with each other. It does not make
them right, and four of the eight `_needs_review` notes were asking a question
only a publisher could answer. `scripts/python/verify_bibliography.py` asks:

```
https://api.crossref.org/works/{DOI}
https://api.datacite.org/dois/{DOI}              where Crossref does not index it
http://export.arxiv.org/api/query?id_list={id}
```

It compares title, authors, container-title, volume, page and year against what
the file claims and reports every difference. `make publications-verify` runs
it; `make publications-test` runs its unit tests, which need no network.

Eleven of the fifteen entries carry a DOI or an arXiv identifier and are now
checked. The other four have neither, and the verifier lists them as
unverifiable rather than passing over them in silence.

Two fields are compared for information rather than for agreement, because the
publisher's value and a bibliography's are different things by design: the
`container-title` of a proceedings article, where Crossref and DataCite hold
the registered title of the proceedings volume — *2021 36th Annual ACM/IEEE
Symposium on Logic in Computer Science (LICS)* — and not the name a
bibliography gives the conference; and arXiv's free-text `journal_ref`, which
is checked by containment and printed in full rather than parsed into fields it
does not really have. For a journal article `container-title` *is* the journal,
and a difference there is still a difference.

### What it is built not to do

**Report a clean run it did not earn.** Any request that fails to reach a
service — a refused CONNECT, a timeout, a 429 or 503 surviving three attempts —
exits 2, and so does a partial run. "Twelve of fifteen checked" is a failure,
not a pass. This is not hypothetical: the first version of this file was
written in a sandbox where `export.arxiv.org` and `doi.org` were both outside
the egress allowlist, and a checker that had gone green there would have
certified fifteen unverified entries.

**Trust a status code.** Crossref must answer `status: ok` carrying the DOI
that was asked for; arXiv must return a feed with one entry whose id is the one
that was asked for. A 200 holding a proxy error page fails as a transport
error, because it means we never reached the publisher. arXiv reports an
unknown identifier as a 200 whose entry points at its error vocabulary, which
is the plainest available demonstration of why.

**Mistake a limit for a defect.** Crossref 404s a DataCite DOI exactly as it
404s a DOI that does not exist. On a 404 the registration-agency endpoint says
who owns it, and a DataCite DOI is followed to DataCite. A DOI that *no* agency
claims is a defect in the file, and is reported as one.

Where an entry has both a publisher record and an arXiv posting, the publisher
holds the version of record: the preprint of the 2014 *Algebra universalis*
paper is titled *…with non-isomorphic…* and the journal's own record is
*…nonisomorphic…*. That is a fact about two documents, not an error, so it is
reported for information.

## Consequences

- **Three entries still carry `_needs_review`**, printed on every run of
  `make publications`. All three are decisions for a person, and each note now
  records what the publishers do say:
  - `demeo2022birkhoff` — one entry or two. DataCite's record for the TYPES
    proceedings paper names arXiv:2101.10166 as a version of it, so the
    publisher treats them as one work; the research page treats the preprint as
    a separate, longer work under a different title.
  - `demeo2002icmc` — the CiteSeerX link needs replacing, and neither service
    holds this paper.
  - `demeo1998eigenvalues` — one item or two, alongside the MS thesis.
- **The other five `_needs_review` notes are gone**, settled by the publishers
  rather than by choosing:
  - the LICS 2021 paper did appear in the proceedings — Crossref registers it
    as a proceedings article, pages 1–13 — so the CV was right and the research
    page's "submitted to" was stale.
  - the 2020 IJAC title *does* include "finitely generated" (World Scientific).
  - *nonisomorphic* is unhyphenated in *Algebra universalis*; Zotero was
    carrying the preprint's title.
  - arXiv 2011.07879 is the right identifier for the 2019 IJAC paper despite
    being posted in November 2020 — its own record carries that DOI.
  - the Cardano paper has seven authors, not "Knispel et al.".
- `gen_publications.py` still validates internal soundness only — unique ids,
  plausible years, well-formed arXiv ids — and still does not resolve anything.
  The two checks answer different questions and neither substitutes for the
  other, so they stay separate targets.
- **`publications-verify` is not a build gate.** CI has no network by design
  (ADR-004), and a check that fails there for reasons unrelated to the change
  would train everyone to ignore it. `checks.bibliography-verifier` runs the
  verifier's *tests* under `nix flake check`, which is the part that can be
  checked hermetically. Run `make publications-verify` when the bibliography
  changes.
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
