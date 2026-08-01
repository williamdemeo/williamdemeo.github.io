# ADR-002: Disposition of every legacy page

**Status**: Accepted

**Date**: 2026-07-31

**Deciders**: William DeMeo

**Related**: [#12](https://github.com/williamdemeo/williamdemeo.github.io/issues/12) (M2-3), [#13](https://github.com/williamdemeo/williamdemeo.github.io/issues/13) (M2-4), [#15](https://github.com/williamdemeo/williamdemeo.github.io/issues/15) (M2-6), [#56](https://github.com/williamdemeo/williamdemeo.github.io/issues/56) (M2-8)

---

## Context

118 legacy pages exist: 103 imported from the Zola site (95,317 words) and 15
from the retired Octopress site. Not all of them belong on a site whose job is
to represent current research work.

Deciding page by page, in writing, avoids both failure modes: dumping
everything into the new site, and quietly losing things.

The dispositions below were generated from the inventory so that every page is
accounted for exactly once, then reviewed by hand. Three were referred back as
judgment calls rather than mine to make; all three have since been decided and
are recorded below.

## Decision

Four dispositions:

| | Meaning |
| --- | --- |
| **promote** | Rewrite and feature. Front-of-site content. |
| **keep** | Migrate into the site largely as-is. |
| **archive** | Migrate into a de-emphasised area: out of the primary nav, indexed and linkable, URLs preserved. |
| **drop** | Do not migrate. Redirect the old URL to the nearest relevant page. |

Nothing is deleted without a redirect, and nothing leaves the repository at
all: the GitLab repository stays public as the archive of its own history
(ADR-001).

## Summary

| Disposition | Pages |
| --- | --- |
| promote | 52 |
| archive | 23 |
| drop | 22 |
| keep | 6 |
| **Total** | **103** Zola pages (+ 15 Octopress, below) |

## Sections

| Path | Size | Disposition | Rationale |
| --- | --- | --- | --- |
| `exams/**` | 48 pages | **promote** | Original solution work with an existing audience; source corpus for the planned Agda formalization. See #56. |
| `computing/**` | 12 pages | **drop** | Eclipse setup, `update-alternatives`, Java-on-Linux. Dead weight; redirect to the archive index. |
| `python/**` | 8 pages | **archive** | Sage/Python teaching labs. Belongs with the teaching record, not the front of the site. |
| `agda-ualib/**` | 6 pages | **archive** | Early formalization notes, superseded by agda-algebras and its documentation. Keep with a forward pointer; M4-2 cross-links them as historical context. |
| `research/csp/**` | 3 pages | **archive** | Dated CSP notes (2014–2020). Superseded by the published papers. |

## Individual pages

| Page | Disposition | Rationale |
| --- | --- | --- |
| `2014-02-05-diaconescus-theorem.md` | **keep** | Constructive mathematics, on-topic. |
| `2014-02-13-a-problem-of-palfy-and-saxl.md` | **keep** | Research note; connects to the PhD work. |
| `2014-02-13-groupsound.md` | **keep** | The GroupSound project; ties to the Magellan grant. |
| `2014-02-13-ieprops.md` | **archive** | 112 words announcing a project page. |
| `2014-02-13-isotopy.md` | **keep** | 964 words of real mathematics; the most notation-heavy post. |
| `2014-02-13-overalgebras.md` | **archive** | 141 words announcing a preprint. |
| `2014-02-13-typefunc.md` | **archive** | 81 words announcing a reading group. |
| `2014-03-19-probability-quiz.md` | **archive** | 1,621 words, self-contained probability, and genuinely good — but an interview puzzle from a quant shop reads as a tonal outlier here. Decided below. |
| `2015-01-11-three-sat-and-partition-lattices.md` | **keep** | 808 words; complexity and lattice theory. |
| `2017-04-06-conferences-in-algebra.md` | **drop** | A 2017 conference list. Stale by construction. |
| `2017-04-06-congruences-of-partial-algebras.md` | **keep** | Short research note, on-topic. |
| `2017-12-06-java-on-linux.md` | **drop** | Sysadmin note about a 2017 Java installer. |
| `2020-04-10-nobody-told-me.md` | **drop** | 47 words, personal. |
| `2021-11-12-touchpad-forensics.md` | **archive** | Useful debugging write-up, off-message for the front of the site. |
| `about/index.md` | **drop** | Superseded by `docs/about.md` (#8). Redirect. |
| `agda/index.md` | **drop** | A single line pointing at Liam O'Connor's site. Redirect there. |
| `books/index.md` | **promote** | Three book projects, two of which turn out to be the exam corpus. Split rather than promoted as one page — see below. |
| `cv/index.md` | **drop** | Superseded by `docs/cv.md` (#8), and a December 2021 snapshot. Redirect. |
| `index.md` | **drop** | Zola section index. Structural, no content. |
| `posts/index.md` | **drop** | Zola section index. Structural, no content. |
| `research/formal.md` | **drop** | Empty: front matter and a banner reference, no body. |
| `research/index.md` | **promote** | 1,498 words of research narrative. Primary source material for M5-5 (#33). |
| `research/research.md` | **drop** | Two words. A stub. |
| `talks/index.md` | **promote** | Source for the talks page, M5-3 (#31). |
| `talks/vols/index.md` | **archive** | Notes for one 2020 talk. Keep as an artifact; link from the talks entry. |
| `teaching/index.md` | **promote** | Source for the teaching page, M5-4 (#32). |

## Octopress posts

Twelve of the fifteen also exist as Zola Markdown and are covered above. The
three that do not:

| Page | Disposition | Rationale |
| --- | --- | --- |
| `commutator-as-least-fixed-point` | **keep** | Exists only as generated HTML. The one post genuinely needing HTML→Markdown conversion. |
| `cloning-an-octopress-repo` | **drop** | Documents a workflow that no longer exists. |
| `learn-you-an-agda` | **drop** | Written by Liam O'Connor-Davis, reposted with permission. Third-party; archival only, never republished. See #13. |

## The three calls that were referred back

**`books/index.md` — the most interesting thing this triage turned up.** It is
47 words, which is why it nearly got dropped, but it links three online book
projects:

- [Category Theory: a concise course](https://categorytheory.gitlab.io)
- [Exercises in Real Variables](https://realanalysis.gitlab.io)
- [Exercises in a Complex Variable](https://complexanalysis.gitlab.io)

The guess that the latter two overlap the qualifying-exam solutions was right,
and stronger than guessed: they are **the same body of work** as the corpus
being promoted in #56. The category theory course is not — it is original
work, coauthored with Venanzio Capretta with help from Charlotte Aten, built on
course notes Capretta wrote for a short course at the Midlands Graduate School.

So the page does not survive as a page. It splits:

- The two analysis collections **merge into the exam corpus**. Presenting them
  as separate "books" alongside an "exams" section would advertise one body of
  work twice.
- The category theory course becomes **a portfolio entry in its own right**,
  under M4 — and, being coauthored, it must carry attribution to Capretta and
  Aten wherever it appears. That is a correctness requirement, not a courtesy.

One question this opens is deliberately *not* settled here, because it is about
hosting rather than disposition: the exam corpus is now also served at
`formalverification.io/exams/`, so #56 has to decide whether this site hosts
the corpus, mirrors it, or describes and links it. See the consequences below.

**The six `keep` posts are a judgment about the blog's opening lineup.** They
are all 2014–2017. Publishing six decade-old posts as the entire blog on launch
day says something — possibly "this person has been quiet for ten years". The
alternative is to hold most of them in `archive/` and let the blog open with the
new writing from M6-4 (#38).

**Decision: keep them for now**, revisited when the site is closer to its
final form. Archiving later is a one-line change to this table; recovering a
post that was never migrated is not.

**`2014-03-19-probability-quiz.md` (the Jane Street test).** 1,621 words and
genuinely good, but an interview puzzle from a quant shop is a tonal outlier on
a site aimed at research labs.

**Decision: archive.** It keeps its URL and stays linkable; it just does not
sit in the blog's opening lineup. This is the one disposition changed after the
table was first generated, which is why `keep` is 6 and `archive` is 23.

## Consequences

- M2-4 (#13) converts the `keep` posts and the one Octopress-only post.
- M2-5 (#14) relocates assets for pages that survive, and the `csp/*.pdf`
  licensing question is still open there.
- M2-6 (#15) builds redirects; every **drop** above needs a target, and the
  `archive/` area must keep its URLs. The Jane Street post moves from `keep` to
  `archive`, so it needs its URL preserved rather than a redirect.
- M2-8 (#56) covers the exam corpus, which is 48 of the 52 promoted pages —
  **and now has a prior question to answer.** The corpus is also served at
  `formalverification.io/exams/`, from
  `github.com/formalverification/formalverification.io`. Two copies of 48
  math-heavy pages is the condition under which one of them silently rots, and
  this corpus has already demonstrated exactly that: its macros were undefined
  on the live site for years (#20). So #56 must pick one home before it does
  anything else. It should not be decided by which copy happens to be easier to
  edit this week.
- M4 gains a portfolio entry for the category theory course, with attribution
  to Venanzio Capretta and Charlotte Aten.
- Nothing here is irreversible: an archived page can be promoted later, and a
  dropped page is still in git history and in the GitLab repository.

## Note on method

The table was generated from the imported tree rather than assembled by hand,
with an assertion that every one of the 103 pages matches exactly one rule.
That is what makes "every legacy page appears exactly once" checkable rather
than hopeful.

The Jane Street row was subsequently changed by hand. Rather than trust that,
the reconciliation was re-derived *from this file as written* — parsing the
section rows, the individual rows and the summary table, then matching all 103
pages on disk against them — and it still holds:

```
sections listed : 5  -> 77 pages
singles listed  : 26 pages
total accounted : 103
actual on disk  : 103
claimed counts  : {archive: 23, drop: 22, keep: 6, promote: 52}
summary table   : {archive: 23, drop: 22, keep: 6, promote: 52}
pages not covered by any row: none
pages covered by >1 row     : none
CONSISTENT
```

Any further edit to the dispositions must re-establish this, by regenerating or
by re-running the reconciliation. A summary table that disagrees with its own
rows is worse than no summary table.
