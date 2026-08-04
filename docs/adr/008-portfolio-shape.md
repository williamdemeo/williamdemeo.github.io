<!-- File: docs/adr/008-portfolio-shape.md -->

# ADR-008: The shape of a project page, and the order the portfolio is read in

**Status**: Accepted

**Date**: 2026-08-02

**Deciders**: William DeMeo

**Related**: [#23](https://github.com/williamdemeo/williamdemeo.github.io/issues/23) (M4-1), [#24](https://github.com/williamdemeo/williamdemeo.github.io/issues/24) (M4-2), [#25](https://github.com/williamdemeo/williamdemeo.github.io/issues/25) (M4-3), [#26](https://github.com/williamdemeo/williamdemeo.github.io/issues/26) (M4-4), [#27](https://github.com/williamdemeo/williamdemeo.github.io/issues/27) (M4-5), [#28](https://github.com/williamdemeo/williamdemeo.github.io/issues/28) (M4-6), [#56](https://github.com/williamdemeo/williamdemeo.github.io/issues/56) (M2-8), [#18](https://github.com/williamdemeo/williamdemeo.github.io/issues/18) (M3-2), [#19](https://github.com/williamdemeo/williamdemeo.github.io/issues/19) (M3-3), [ADR-002](002-content-triage.md), [ADR-005](005-visual-system.md)

---

## Context

M4 is where the site stops describing its author and starts showing evidence.
Every page in it is written to one shape, and that shape is decided here rather
than by whichever page happens to be written first.

Two things need settling, and they are different kinds of decision.

The **template** is a contract. Five pages have to answer the same questions in
the same order, because a reader comparing them should be comparing the work
rather than re-learning the layout. It is also what makes the pages fast to
write: the hard part of a project page is the technical substance, and a page
that arrives with its slots already named does not spend effort on structure.

The **ordering** is an editorial claim about what a reader should see first. It
is not a ranking of achievements, and it does not follow from anything; it has
to be argued.

## Decision 1 — the template

`docs/projects/_template.md` is the skeleton, and it carries its own
documentation in comments. Its slots, in order:

| Slot | What it answers |
| --- | --- |
| Summary paragraph | What it is, why it was hard, what is verifiable. |
| Status line | Role, dates, status, languages. |
| Technical substance | The interesting problem, and how it was solved. |
| Artifacts | What a reader can check, and what each one proves. |
| What is next, or what was learned | Where the work goes, honestly. |

The summary comes before the status line, deliberately. A reader who bounces
after one paragraph should have got the work, not the dates.

### The metadata contract

#23 asks for role, dates, status, languages and artifact links. All five are
**visible prose in a fixed shape**, not YAML keys.

Front matter was the obvious alternative and is the wrong choice here. MkDocs
does not render unrecognised front-matter keys, `--strict` does not validate
them, and nothing on the site would consume them — so a page could drop `role:`
and no reader and no gate would notice. A contract nobody can see is a contract
nobody keeps. The visible form fails loudly: a missing status line is a missing
line.

Concretely, one paragraph of two lines directly under the summary:

```markdown
Sole author · 2020– · `active`{.tag}
`Agda`{.tag} `type theory`{.tag} `universal algebra`{.tag}
```

The first of those two lines ends in two trailing spaces, which is what keeps
them one paragraph rather than two — the same hard-break convention the
publication and talk entries use, and the reason `.editorconfig` turns
`trim_trailing_whitespace` off for Markdown. The skeleton carries them; a
rendered `<br>` in the built page is the check.

Role and dates are prose because they are prose — "with the Formal Methods team
at IO" is not an enum. Status and languages are `.tag` spans, which is the
component #19 already ships, and are the same tags the project's card carries on
the index, so the two cannot drift apart without it being visible on one screen.

Only `.tag` is used, and it exists. **No page in M4 needs new CSS**, which was
#19's own acceptance criterion; if one does, that is a finding about #19 and
belongs in a follow-up issue rather than in a bespoke rule.

## Decision 2 — the order, and the argument for it

**AI for formal verification, then `agda-algebras`, then the Cardano ledger
specification, then universal algebra and lattice theory, then the category
theory course.**

The first three are #23's proposed order and are adopted. The fourth is an
addition; the fifth is required by ADR-002 and had nowhere to go.

### Why relevance rather than date or evidence-weight

Two other orderings are defensible and both are rejected.

*Reverse chronological* is what the reader can already get from the CV, and it
puts a decade-old thesis in front of current work.

*Strongest evidence first* would run `agda-algebras` (published theorem, DOI,
documentation site), then Cardano (FMBC 2024 paper), then the mathematics
(journal publications), then the AI tooling (a repository and no publications
yet). That ordering is an academic CV wearing a portfolio's clothes, and #18
names it explicitly as a failure mode to avoid.

Relevance wins because an index is a claim about *what this person is for*. Led
by `agda-algebras`, the site says "a formalization library author who also does
some AI work". Led by the AI tooling, it says "someone working at the
intersection of machine reasoning and verifiable domains, with a decade of
formal-methods depth behind it". The second is the true claim and is the one the
target roles are hiring against.

### Why the AI work leads, and the condition attached

It is the most relevant to the roles being sought and the most recent. It is
also, per #25, the work with the *least* existing written material.

That combination is a real risk and is recorded rather than glossed: leading
with the thinnest page puts an unsupported claim in front of a reader whose
entire job is evaluating evidence, and a reader who discounts card one discounts
everything after it.

**So the ordering is conditional.** It holds as long as #25 lands its concrete
worked example — a proof the tooling completed, with a transcript or a distilled
version — which is already one of that issue's acceptance criteria. If #25 ships
as description without a checkable artifact, this ADR is wrong and
`agda-algebras` should lead until it does not.

### Why `agda-algebras` is second

Because the reader who has just been told something ambitious should meet the
hardest evidence on the site next. Claim, then proof. It is the strongest single
artifact here — a constructive machine-checked proof of Birkhoff's HSP theorem,
a paper, a DOI, and a live documentation site — and second place is where it
does the most work.

### Why the Cardano ledger is third

It answers the question the first two leave open: does this scale to a system
with real stakes, other engineers, and a specification that has to track a
moving target. Third is the "and it works in production" beat, which only lands
after there is something to say it about.

### Why universal algebra and lattice theory is fourth, and why it is here at all

#23's list has a gap. All four of its entries are formalization or verification
work, which is evidence of what the author can *mechanize*. For a research
scientist role, "can find and prove new theorems" and "can mechanize known ones"
are different claims and need different evidence. `agda-algebras` mechanizes
Birkhoff's theorem, which is Birkhoff's.

The original mathematics — congruence lattices of finite algebras, the finite
lattice representation problem, and the later work on the algebraic approach to
constraint satisfaction — is where the evidence of original research lives, and
it is the only entry backed by peer-reviewed journal publication. The site's own
first paragraph claims the mathematician identity; a portfolio that omits it
leaves that claim as an assertion, which is the mode M4 exists to end.

Fourth rather than first, because the index is ordered by relevance to a reader
asking "can this person do our work", not "where did they come from". Fourth
rather than last, because it *explains* the three above it: Birkhoff's HSP
theorem is not an arbitrary theorem to have mechanized, it is the central
theorem of the field the author has a doctorate in. Fourth is the load-bearing
foundation, read at the point where the reader has a reason to care about it —
not the least important entry.

### Why the category theory course is fifth

ADR-002 promoted it to "a portfolio entry in its own right" and no M4 issue was
ever filed for it, so it has been sitting in a decision with nowhere to land.
Meanwhile `redirects.yml` holds `/books/` pending on "#56 and M4 — the page
splits; successor not yet chosen", so a redirect is blocked on this entry
existing.

It is fifth because it is the one expository entry and the least directly
relevant to the target reader — not because it is slight. **It is coauthored
with Venanzio Capretta and Charlotte Aten, and must carry that attribution
wherever it appears.** ADR-002 calls that a correctness requirement
rather than a courtesy, and it is repeated here because a card is exactly the
kind of compressed form where attribution gets dropped.

## Decision 3 — what the index carries, and what it does not

**`agda-native-air` is one entry with the AI tooling, not two.** #23 offered
"fourth or merged with the first"; it merges. The two would otherwise be the
same repository described twice — the site's own home page already treats
`agda-native-air` as the extractor, the MCP server, the Skills and the agent
loops, which is precisely what #25 sets out as its subject. Two thin pages about
one repository is the shape mistake #26 warns against. #26 remains the issue
that records and executes the merge; this ADR provisions one slot for it.

**The qualifying-exam corpus waits.** #56 has not settled where the corpus
lives, and the card is not writable until it does: hosted here, the title links
to `/exams/` and the entry is a section of this site; hosted at
`formalverification.io`, the entry describes a project living elsewhere and
links out. Those are different cards, and #56's own hard gate — confirming that
copy is at least as complete as the 48 imported pages — has not been cleared.

Deciding the slot now is free, though, and stops #56 from reopening this
ordering when it resolves: **the corpus lands fifth, moving the category theory
course to sixth.** It outranks the course because the solutions are the author's
own original work with an active Agda formalization planned against
`agda-algebras`, where the course is exposition built on Capretta's existing
notes.

**The secondary projects list belongs to #28** and is not stubbed here. It is a
compact list below the cards, visually subordinate to them, and an empty heading
promising it later is worse for a reader than its absence.

## Decision 4 — cards link outward until their pages exist

A card title linking to `projects/agda-algebras.md` before #24 writes it fails
`--strict`, which is working as intended. The alternative — five placeholder
pages — is worse than an honest index.

So each card's title links to the project's **primary artifact** today, and the
`.project-links` row carries the rest. When a project page lands, that issue
changes one line: the title's target becomes the internal page, and the artifact
it was pointing at is already in the links row.

The consequence worth stating is that the index is useful now rather than being
a frame waiting to be filled. A reader arriving today gets five real projects
and working links to the artifacts behind them.

## Consequences

- #24, #25, #26, #27 each fill one card and change one line of
  `docs/projects/index.md`; none of them re-opens the ordering.
- #26's merge decision is provisioned. If it goes the other way, the index gains
  a card and this ADR is amended.
- #28 appends its compact list below the grid.
- #56 gains a decided landing slot, so resolving the corpus's home does not
  reopen the ordering. Its `/exams/**` redirect stays `pending` either way.
- `/books/` (`redirects.yml`) can be resolved once the category theory entry has
  a page — one of its two successors now exists as a card.
- #18 has the ordering it needs for the home page's featured cards. The home
  page shows a subset; it must not contradict this order.
- The mathematics entry and the category theory course have cards but no issue
  and no page. Two issues need filing, and this ADR is the argument for why.
- `docs/projects/_template.md` is excluded from the build in `mkdocs.yml`.
  MkDocs does not skip underscore-prefixed files, so without that line the
  template ships as a page at `/projects/_template/`.

## What would change this

- #25 shipping without a checkable worked example. Then the AI entry is a claim
  rather than evidence, and it should not lead until it is one.
- A change in what the site is for. The whole ordering is downstream of one
  audience, named in M3-2 and in the M4 milestone description. A different
  audience is a different index, not a tweak to this one.
- Six cards becoming eight. Five is already at the edge of what a reader scans;
  past that the flagship set stops being flagship, and the fix is #28's
  secondary list rather than a longer grid.
