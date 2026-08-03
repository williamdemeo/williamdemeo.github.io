---
# Copy this file to docs/projects/<slug>.md and fill it in.  Do not link to it
# and do not build it: mkdocs.yml excludes `projects/_template.md`, because
# MkDocs does not skip underscore-prefixed files and this would otherwise ship
# as a page at /projects/_template/.
#
# Front matter first, always.  The guidance in this file is YAML comments up
# here and HTML comments below, so that a copy of it parses on the first build
# and so that nothing instructional can survive into the rendered page as text.
#
# title:       the card title on the index and the nav label.  Short.  It is
#              also the H1, so do not write a different H1 below.
# description: one sentence, used by search and by social cards.  Say what the
#              thing is, not that it is a project page.
title: PROJECT NAME
description: >-
  One sentence naming what this is and what is checkable about it.
---

# PROJECT NAME

<!--
SLOT 1 — the summary paragraph.  ADR-008.

One paragraph, and it answers three questions in this order: what it is, why it
was hard, and what is verifiable about it.

A reader who leaves after this paragraph should have got the work.  "Why it was
hard" is the sentence that distinguishes a portfolio from a list of
repositories, so it is the one worth rewriting: not "this was a large
formalization" but the specific obstacle, named.

No links in this paragraph beyond the ones a sentence genuinely needs.  The
artifacts have their own section, and a summary studded with links reads as a
bibliography.
-->

One paragraph: what it is, why it was hard, what is verifiable about it.

<!--
SLOT 2 — the status line.  This is the metadata contract from #23, and it is
visible prose rather than front matter for the reason ADR-008 gives: a YAML key
nothing renders and no gate checks is a key that goes missing silently.

Two lines, one paragraph — end the first line with two trailing spaces so the
line break survives.

  Line 1  role · dates · status
          Role is prose, because it is prose: "sole author", "with Jacques
          Carette", "with the Formal Methods team at IO".  Do not over- or
          under-claim on a team effort.
          Dates as a range.  An open range ends in an en dash and stops:
          `2020–`, not `2020–present`.
          Status is one tag, and honest: `active`, `maintained`, `paused`,
          `archived`, `exploratory`.

  Line 2  languages and technologies, as tags.

Tags are `` `Agda`{.tag} ``.  A code span, not `[text]{.tag}` — see the tag
component in docs/design/style.md for why.

These tags must be the same tags this project's card carries on the index.  Two
lists that disagree are the whole reason the component exists.
-->

Role · DATES · `status`{.tag}  
`Language`{.tag} `Technology`{.tag}

<!--
SLOT 3 — the technical substance.  The body of the page, and the reason a
reader who knows the field keeps reading.

Use real section headings that name the actual problem.  `## Technical
substance` is not a heading, it is this template leaking; `## Why setoids` and
`## What a machine-checked Birkhoff proof needs that a textbook proof does not`
are headings.

Show the work.  Real theorem statements, real code, real numbers.  Every
quantitative claim has to be checkable from something in SLOT 4 — a figure a
reader can reproduce from a linked artifact, not an estimate.

Mathematics and Agda already render; both are settled (ADR-005, #20, #71).
Nothing in this section needs new CSS.  If it appears to, that is a finding
about #19 and belongs in a follow-up issue, not in a bespoke rule.
-->

## A heading that names the actual problem

## A second one, if the work has two parts

<!--
SLOT 4 — artifacts.  What a reader can check, and what each one proves.

A bare list of links is weaker than it looks.  Say what each artifact
establishes, because the milestone's exit criterion is that every claim on the
page is backed by something independently checkable — and the reader should not
have to guess which link backs which claim.

At least one artifact must be independently verifiable: a DOI, a published
paper, a release, a live documentation site, a CI badge.  A repository alone is
the author's own word.

Check every link resolves before merging.  A 200 is not sufficient either:
`ualib.org` returns 200 and is the archived pre-3.0 library, which #24 is
explicit about not presenting as current.
-->

## Artifacts

- [Source](https://github.com/OWNER/REPO) — what a reader will find there.
- [Paper](https://example.org/) — the claim it establishes.

<!--
SLOT 5 — what is next, or what was learned.  One of the two, whichever is true.

Active work gets "what is next": the honest state, including what does not work
yet.  Finished or dormant work gets "what I learned", which is where a specific,
falsifiable observation goes — not a reflection.

An honest limitation here is worth more to the reader this site is written for
than another paragraph of achievement.  This is also where cross-links go: to
the blog posts that develop a theme at length, and to the other project pages
this one relates to.
-->

## What is next

<!--
BEFORE YOU MERGE

- Add the card to docs/projects/index.md.  Same summary line, same tags, and
  change the card title's link from the external artifact to this page — the
  artifact it pointed at is already in the card's links row.  ADR-008,
  Decision 4.
- Keep the card's position: the order is argued in ADR-008 and is not a
  per-page decision.
- `make check` (strict), then `make contrast-audit` — a new page is exactly
  what that audit exists to catch.
- Math renders over HTTP, never file://.  Use `make serve`.
-->
