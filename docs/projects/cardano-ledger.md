---
title: The Cardano ledger specification
description: >-
  Machine-checked specification of the Cardano blockchain ledger in Agda —
  executable, extracted to Haskell for conformance testing, and the document
  engineers actually read.
---

# The Cardano ledger specification

A machine-checked specification of the Cardano blockchain ledger, written in
Agda with the Formal Methods team at [IO](https://iohk.io/). What makes it
different from formalizing mathematics is not the proofs; it is the constraints
around them. The specification has to track a system that changes underneath it,
it has to be read by engineers who are not type theorists, and it has to
*execute* — Haskell is extracted from it and run against the production
implementation, so a specification that is merely true but not runnable fails at
its job. It is public, Apache-licensed, and its design is described in a
peer-reviewed paper at FMBC 2024.

With the Formal Methods team at IO · 2023– · `active`{.tag}  
`Agda`{.tag} `Haskell`{.tag} `formal methods`{.tag} `production`{.tag}

## What a production ledger needs that a library does not

The contrast with [agda-algebras](agda-algebras.md) is the useful way in. That
library formalizes mathematics that has not changed since 1935, for readers who
already know type theory, and it is finished when it type-checks. None of those
three things is true here.

**The specification is the documentation.** The project is written entirely in
literate Agda, and the human-readable specification is generated from it — the
HTML output *replaces* the PDF documents that earlier Cardano eras shipped.
That inverts the usual relationship, in which a formal model is a separate
artifact that a prose specification hopefully agrees with. Here there is nothing
for the prose to disagree with, because the prose and the formalization are the
same file. The cost is that every definition is now read by people who did not
choose to learn Agda, which is a real editorial constraint on how things are
named and phrased, not a nicety.

**It has to run.** Agda's GHC backend extracts Haskell from the specification
(`nix build .#hs-src`), and that generated code is the basis of conformance
testing against the production ledger implementation. A library proof discharges
its obligation by type-checking. This one has to type-check *and* compile *and*
agree with a separately written implementation that a live chain is running.
Conformance testing is what turns "the specification is correct" into "the
implementation matches the specification", and those are different claims.

**It tracks a moving target.** The repository carries the ledger across eras —
Shelley through Conway, with Dijkstra in progress. Each hard fork changes the
rules the chain enforces, and the specification versions alongside them rather
than describing a fixed object. The Conway formalization is complete; parts of
earlier eras are still being backfilled, which the project says plainly rather
than papering over.

**Other people depend on it.** It has a code owner, a contributing guide, a
troubleshooting guide, nightly CI, and a dozen-plus contributors. Design
decisions have to survive review by people who will maintain them, which is a
different discipline from being right.

## Artifacts

- [Source](https://github.com/IntersectMBO/formal-ledger-specifications) — the
  specification itself, Apache 2.0, all eras. Entirely literate Agda.
- [FMBC 2024 paper](https://doi.org/10.4230/OASIcs.FMBC.2024.2) — Knispel,
  DeMeo, et al., *Formal Specification of the Cardano Blockchain Ledger,
  Mechanized in Agda*. The peer-reviewed account of the design.
- [The generated specification](https://intersectmbo.github.io/formal-ledger-specifications/site)
  — the HTML that replaced the era PDFs. This is the artifact the rest of the
  organization actually consumes.
- [`conformance-example/`](https://github.com/IntersectMBO/formal-ledger-specifications/tree/master/conformance-example)
  — a worked example of running the extracted Haskell, which is the shortest
  path to seeing that the specification really does execute.
- [Cardano formal specifications index](https://github.com/IntersectMBO/cardano-formal-specifications)
  — the wider formalization effort this is one part of.

## My part in it

This is a team effort and the interesting parts are collective, so the honest
framing is a share rather than a claim of ownership. Of 1,105 non-merge commits
in the repository's history, 359 are mine — the largest single share, though
commit counts measure activity rather than importance, and the project's code
owner is someone else. The work runs from March 2023 to the present and is
concentrated in the specification tree itself, with a secondary thread in the
build and documentation pipeline that produces the HTML specification and the
extracted Haskell.

That share is reproducible rather than asserted. In a full clone,
`git log --no-merges --format='%an' | sort | uniq -c | sort -rn` gives the
breakdown these numbers come from, and it will drift upward as the project
continues.

## What is next

The Dijkstra era is the current front. The longer-running thread is the one that
matters more: closing the remaining gaps in the pre-Conway eras, so that the
specification covers the chain's whole history rather than its recent past.

The part I find most interesting from here is the same one that motivates the
[AI tooling](index.md) work. A specification that executes, extracts, and is
conformance-tested against a real implementation is an unusually rich source of
*checkable* signal — every claim in it is mechanically falsifiable, which is
exactly the property that makes a domain a good testbed for machine reasoning
and exactly what most domains lack.
