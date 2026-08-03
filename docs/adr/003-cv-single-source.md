# ADR-003: One authoritative CV, in YAML, with the publications left where they are

**Status**: Accepted

**Date**: 2026-08-03

**Deciders**: William DeMeo

**Related**: [#16](https://github.com/williamdemeo/williamdemeo.github.io/issues/16) (M2-7), [#41](https://github.com/williamdemeo/williamdemeo.github.io/issues/41) (M7-1), [#42](https://github.com/williamdemeo/williamdemeo.github.io/issues/42) (M7-2), [#31](https://github.com/williamdemeo/williamdemeo.github.io/issues/31) (M5-3), [#32](https://github.com/williamdemeo/williamdemeo.github.io/issues/32) (M5-4), [ADR-002](002-content-triage.md), [ADR-004](004-nix-environment.md), [ADR-006](006-bibliography-source.md)

---

## Context

Four copies of the CV existed, and they disagreed. All four are reachable, and
all four are now read by a check in this repository:

| copy | as of | where it is read from |
| --- | --- | --- |
| `williamdemeo/cv`, `README.md` | January 2025 | `import/legacy-cv/cv-repo-README.md` |
| `williamdemeo/job-app`, `cv/demeo_cv.pdf` (GitLab) | June 2022 | `import/legacy-cv/demeo_cv-2022.txt` |
| the Zola site's `content/cv/index.md` | December 2021 | `import/zola-content/cv/index.md` |
| `docs/cv.md` | current | in place |

#16 guessed the GitLab PDF might be out of reach. It is not: that repository is
public, and `cv/demeo_cv.pdf` turns out to be byte-identical to the
`demeo_cv-2022.pdf` at its root — same blob — so the PDF the Zola about page
linked to is the 2022 CV, a year newer than the Zola copy and two and a half
years older than the README.

No copy is a superset of any other. Each of the three legacy copies carries
material that no other one has:

- **Only the 2025 README** has the RelationalAI appointment, the NJIT
  appointment as *Senior University Lecturer*, three of the five NJIT courses,
  the Cardano FMBC 2024 paper, the two 2024 Agda Implementors' Meetings, and the
  TYPES 2021 talk.
- **Only the Zola copy** has the University of Hawaii graduate service — the
  Working Group on Graduate Education, the Graduate Student Organization roles,
  and mentoring in the Mathematical Biology Program — the University of South
  Carolina advising (Matthew Corley, the high-school contest committee, Pi Mu
  Epsilon), the NATO ASI in 2003, J.B. Nation as a referee, the two analysis
  exam collections, and the two pre-2010 talks: *Object reconstruction from
  multiple views* (AFOSR AMOS review, Maui 2004) and *Approximating eigenvalues
  of large stochastic matrices* (Copper Mountain, 1998).
- **Only the 2022 PDF** has the NJIT appointment as *Adjunct Instructor*, which
  is not an addition but a contradiction — and, as it turns out, an error. See
  the three disagreements below.

That is the argument for doing this at all. Any one of the four could have been
adopted as the source, and roughly a fifth of the record would have gone
missing without anyone noticing.

## Decision

**`cv.yml` at the repository root is the only authoritative CV source**, holding
contact, research interests, education, appointments, grants and awards,
teaching, talks, service, advising, certifications, summer schools and
references. #41 renders it to web and PDF; #42 brings its content current. This
file is the merge, not the rewrite.

**Publications are not in it.** `bibliography.json` is the only authoritative
publication list (ADR-006) and this issue must not undo that. `docs/cv.md`
already includes `_snippets/publications-cv.md`, which
`scripts/python/gen_publications.py` renders from the `_cv` flag there, and that
stays exactly as it is. `cv.yml` has a `publications:` block, but it holds ids
and file paths and no publication metadata — no title, no venue, no year, no
author — and it exists so the checker can resolve the publication entries in the
legacy copies against `bibliography.json` rather than against `cv.yml`. That
turns the boundary between the two files into something checked rather than
asserted: a publication that reached neither file fails the build.

### YAML, not JSON — and why ADR-006's reasoning does not carry over

#16 recommended YAML. The obvious objection is consistency: the sibling
generator reads `bibliography.json` with the standard library's `json`, and a
repository with one structured data format is simpler than one with two. That
objection was checked against ADR-006 rather than waved away, and it does not
survive, because **neither of ADR-006's two reasons transfers.**

ADR-006 called CSL-JSON versus BibTeX a tie and broke it on dependency cost:
*"BibTeX would cost a dependency and CSL-JSON costs nothing"*, since Python has
no BibTeX parser in the standard library and adding `bibtexparser` would oblige
`flake.nix` to match its version under ADR-004's `requirements-pins` check.
**YAML costs nothing either.** `scripts/python/_redirects_lib.py` already does
`import yaml`, because PyYAML arrives as a dependency of MkDocs — which is why
the Makefile runs the redirect scripts under the venv interpreter rather than
the system one. `requirements.txt` gains nothing, so `requirements-pins` has
nothing new to match.

ADR-006's second reason was that **the data was already CSL-JSON**: the Zotero
export imported without conversion, and CSL-JSON is an external standard that
other tools read and write. There is no external standard for "the positions
someone has held", and none of the four copies was machine-readable — one is a
PDF.

What is left is which format suits the file, and they are different files.
`bibliography.json` was imported from an export and is maintained by adding
entries in a fixed schema. `cv.yml` is prose that a person edits: multi-line
descriptions, em-dashes, Ruškuc and Martin-Löf and Völs am Schlern, and — most
of all — **explanations that have to sit next to the thing they explain.** JSON
has no comments. Half of what makes this file trustworthy is the note beside the
NJIT entry saying which copy said what, and in JSON that note has nowhere to
live. `redirects.yml` is the closer precedent: hand-maintained structured data
in this repository, in YAML, heavily commented, read with the same `yaml` import.

BibTeX or CSL-JSON for publications, as #16 also suggested, was settled a
milestone earlier and is not reopened here.

## Nothing was silently lost, and here is the proof

The acceptance criterion — *nothing present in an older copy has been silently
lost* — is a claim about 767 entries across four documents. Prose cannot carry
it, and a merge done by hand is exactly the kind of work where a confident
summary is worth nothing. `scripts/python/check_cv_sources.py` asks the question
mechanically:

```
  cvrepo    234 entries
  zola      167 entries
  jobapp    352 entries
  site       14 entries
  total     767

  covered  718
  omitted  49 (declared, with reasons)
```

Every entry in every copy is either **covered** — some `cv.yml` entry contains
every significant word of it — or **named in `cv.yml`'s `omissions:` list with a
reason.** There is no third outcome. `make cv-check` runs it, and
`nix flake check` runs it too, since the copies are snapshotted in the
repository and it resolves nothing and needs no network.

**Containment, not similarity.** There is no threshold to tune and no partial
credit. This is what makes the check useful rather than reassuring: "Bounded
homomorphisms and fiber products of lattices" does not cover "Bounded
homomorphisms and *finitely generated* fiber products of lattices", so the
copies' disagreements surface instead of being smoothed away by a score. It is
also what makes the check demanding — the abbreviation table and the hyperlink
stopwords in that file exist so that the failures it reports are real ones.

**Both directions.** A declared omission that no longer names a real source
entry fails, and so does one for an entry `cv.yml` turns out to carry. A
declaration cannot outlive the thing it was about, which is how "nothing was
lost" would otherwise quietly stop being true.

**The extractors are guarded too.** A coverage checker reports success when
nothing is uncovered, and an extractor that has broken and finds nothing
produces exactly that. Two things stand in the way: `inventory.tsv` is committed
and compared against a fresh extraction on every run, so what the checker reads
is reviewable in a diff; and `scripts/python/test_cv_sources.py` holds the
failures it must still report, including a section heading drifting out of the
snapshot it was written against. Both run under `nix flake check`.

### What it cannot see

- **URLs are stripped from both sides.** The copies link the same work through
  gitpitch, gitlab, lulu, arxiv and doi.org at four different moments in the
  life of each of those hosts, and requiring `cv.yml` to carry every dead one
  would make this check an argument for keeping dead links. `cv.yml` carries a
  URL per entry where a live one exists; that it is the *right* URL is not
  something this can know. **Link-checking the result is #41's, not here.**
- **Grouping is invisible.** Covering text is covering text wherever it sits, so
  an entry filed under the wrong heading still counts as covered. This proves
  nothing was lost; it does not prove everything landed well.
- **The PDF snapshot has no hyperlinks in it at all.** A PDF link is an
  annotation over a rectangle and its target is not in the text layer. Where an
  entry from that copy needed a URL, it came from another copy.
- **A fifth copy would be unchecked.** The four are listed in that file's
  `SOURCES` and in the table above.

## The 49 declared omissions

Six kinds, and only the last two are about the CV's content at all.

| kind | n | why |
| --- | --- | --- |
| referees' office addresses and telephone numbers | 29 | The referees are carried, with title and institution. A CV published on a website is not a CV mailed to a search committee, and nothing here will render a phone number. |
| William's own home address and telephone | 4 | Same, and more so. The Prague *institutional* address is kept, in `contact.aliases`. |
| a copy's own title block and list sub-headings | 3 | "CURRICULUM VITÆ … 5 Dec 2021" is about the document, not the career. |
| `docs/cv.md` page chrome | 6 | The download button, the staleness admonition, and pointers to `about.md` and to #30. #41 replaces all of them. |
| publication status at the time of writing | 3 | "accepted", "submitted", "to appear". All three works are published, and `bibliography.json` records the version of record. Carrying the status forward would carry something that has since become false. |
| bibliographic detail `bibliography.json` does not record | 4 | Below. |

The last four are the only omissions that lose something a reader might want,
and each is a change to ADR-006's file rather than to `cv.yml`:

- **Lulu Press** as publisher of the ALH 2018 proceedings. `adaricheva2018alh`
  has no publisher, and its own `_comment` already says publisher, ISBN and a
  stable URL would have to come from William.
- **The page range 12:1–12:37** for the LMCS article. `bergman2022universal`
  records volume and issue but no pages; the DOI carries the article number.
- **The venue written as "Proc. 27th Intl. Conf. …"** (twice, in two copies).
  `bibliography.json` names the conference rather than its proceedings volume,
  which is ADR-006's own rule about saying what the publisher records.

## The three things the copies disagreed about, and how they were settled

A merge is not entitled to decide which of two things someone wrote about their
own career is true, so these were referred back rather than picked. **All three
have since been decided by William**, and none is open:

1. **The NJIT appointment: *Senior University Lecturer*.** The 2022 PDF said
   *Adjunct Instructor*; that is wrong, not a different-but-defensible earlier
   title. It survives in `aliases:` only so that copy's line still resolves to
   the right entry, labelled there as the error it is. Its open-ended `2022--`
   was never really a disagreement — the document was written while the
   appointment was current, and a range left open in 2022 does not contradict
   one closed in 2025. `docs/about.md` already said 2022–2023.
2. **The Agda Universal Algebra Library: coauthored with Jacques Carette.** The
   2021 LaTeX in the job-app repository credited a second person; **that
   attribution is wrong and is not carried.** It appears in none of the four
   copies this repository checks against, so nothing here depended on it. Given
   ADR-002 makes coauthor attribution a correctness requirement rather than a
   courtesy, an attribution that is not right is worth removing rather than
   hedging.
3. **Ali Lotfi**, not *Latfi*. All three legacy copies spell it *Latfi*; the
   comprehensive-exam syllabus filed in the job-app repository spells it
   *Lotfi*, and the syllabus is right. So the majority of the copies were wrong
   together, which is a reminder of what a merge that resolves conflicts by
   counting would have produced. The misspelling stays in `aliases:` for the
   checker's sake and is marked there as an error.

Two of the three went the way the *older* or *rarer* copy pointed. Recency and
frequency were both available as tie-breakers here and both would have got one
of these wrong; that is why they were referred back instead.

## Consequences

- **`cv.yml` holds talks, teaching and service, which are M5's subject.** #31
  and #32 should render their pages from it rather than start a new copy —
  otherwise this ADR will need writing again in a milestone's time. Putting them
  here was not scope creep: leaving them out would have meant declaring
  thirty-five talks and thirty-four courses as omissions, which is a strange way
  to say "nothing was lost".
- **`docs/cv.md` is unchanged.** It is still hand-written prose that includes the
  publications snippet, and it is one of the four copies the check reads. #41
  replaces it with a rendering of `cv.yml`, and at that point the `site` rows in
  the inventory become a rendering of the source rather than a fourth opinion.
- **`DeMeo-CV.pdf` still exists** at `docs/assets/`, and the page still links it.
  #16 asked for it to go once M7-1 generates its replacement; that is still
  #41's, and deleting it now would leave the page pointing at nothing.
- **The `williamdemeo/cv` repository is not touched.** #16 asks for a deprecation
  note in its README pointing here. Nothing in this change writes to another
  repository, and that note is William's to push.
- **Adding a position, a talk or a course is one edit to `cv.yml`.** Adding a
  publication is still one edit to `bibliography.json` plus `make publications`.
- **The snapshots are permanent.** `import/legacy-cv/` is provenance, like
  `import/legacy-bib-pubs.json` before it. Nothing renders it and nothing should
  correct it: its disagreements are what the check is checking.
- **`import/legacy-cv/pdf_text.py` is committed** so the PDF snapshot is
  reproducible rather than asserted. It is provenance tooling — no build target
  runs it, it needs the PDF, and the PDF's SHA-256 is recorded beside it.

## Alternatives considered

**Depend on `williamdemeo/cv` at build time.** Rejected, as #16 recommended and
for the reason ADR-006 gives about the BibTeX repository: it makes the build
depend on a second repository being reachable, and #15 already showed what a
cross-repository dependency costs to verify from a sandbox.

**Adopt the 2025 README wholesale and diff by eye.** Rejected. It is the most
current copy and the most structured, and it is still missing the University of
Hawaii graduate service, the South Carolina advising, J.B. Nation, the NATO ASI,
and the two pre-2010 talks. "Diff it against the older copies" is what #16 asked
for; doing it by eye across four documents and 767 entries is how things get
lost, which is why the diff is a program.

**Record provenance per entry, with a `sources:` list on each.** Rejected. That
is a second copy of the correspondence, maintained by hand, and it would drift
from the copies it describes — the failure mode this whole ADR exists to close.
Provenance is proved against the snapshots on every run instead.

**Match entries by similarity rather than containment.** Rejected. A threshold
that lets "fiber products" match "finitely generated fiber products" is a
threshold that hides the disagreements, and the disagreements are the most
valuable thing this exercise produced.

**Redact the referees' contact details from the snapshots.** Rejected, though it
was close. It would put the checker in the position of certifying a coverage
claim over a file that had been edited to make the claim easier. The details are
already public — both repositories are public, and the Zola copy already in this
repository has carried the referees' email addresses since it was imported —
so the snapshot copies nothing that was not already copyable. They are omitted
from `cv.yml`, which is what governs what gets published.

## Note on method

`nix flake check` was **not** run for this change: Nix is not available in the
environment it was written in. `checks.cv-sources` is wired up the way
`checks.math-source` and `checks.bibliography-tooling` are, and its two commands
were run directly and pass, but the derivation itself is unbuilt here and the
`cvSource` fileset is unverified. Whoever has Nix should run it before merging.

Everything else was run: `mkdocs build --strict`, `make math-source`,
`make math-audit`, `python3 scripts/python/test_redirects.py`,
`gen_publications.py --check`, `make cv-check` and `make cv-test`.
