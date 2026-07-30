---
title: William DeMeo
description: >-
  Mathematician and formal verification engineer working on machine-checked
  mathematics, interactive theorem proving in Agda, and AI tooling for proof
  assistants.
---

# William DeMeo

I work on **machine-checked mathematics**: proving theorems in dependent type
theory, verifying production systems, and building tools that let language
models work inside a proof assistant.

Mathematician by training — PhD in universal algebra and lattice theory —
and a formal verification engineer by trade. The through-line across both is
an interest in what is *mechanizable*: which mathematical structures admit
effective procedures, and what it actually takes to make reasoning checkable
by a machine.

<!-- TODO(wjd): This is the ten-second pitch.  Everything else on the site is
     downstream of whether these three paragraphs land.  Rewrite freely. -->

## What I'm working on now

**Formal verification at IO.** Machine-checked specification of the Cardano
blockchain ledger in Agda, with the Formal Methods team. The work is public in
[`formal-ledger-specifications`](https://github.com/IntersectMBO/formal-ledger-specifications),
and the design is described in our [FMBC 2024 paper](https://drops.dagstuhl.de/entities/document/10.4230/OASIcs.FMBC.2024.2).

**AI tooling for proof assistants.** An MCP server exposing Agda's interaction
protocol to language models, Claude Skills encoding Agda-specific workflow
knowledge, and the agent loops built on top of them. This is the newest thread
and the one I find most interesting: a typechecker is an unusually good source
of dense, automatically-checkable feedback, which makes interactive theorem
proving a sharper testbed for machine reasoning than most domains.

<!-- TODO(wjd): I only know these projects by name (agda-mcp, agda-native-air,
     Claude Skills) and deliberately have not invented specifics.  Please
     correct the characterisation above and add links once you decide what is
     public.  M4-3 (#25) is the full page for this. -->

**[agda-algebras](https://github.com/ualib/agda-algebras).** A library of
universal algebra in Agda, containing what is — as far as I know — the first
machine-checked proof of Birkhoff's HSP theorem in Martin-Löf type theory,
joint with Jacques Carette. Documentation at [ualib.org](https://ualib.org).

*Last updated: July 2026.*

## Elsewhere

Before moving into industry I held research and teaching appointments at
Charles University in Prague, the University of Colorado Boulder, the
University of Hawaii, Iowa State University, and the University of South
Carolina. More in the [CV](cv.md) and [about](about.md) pages.

!!! note "This site is being rebuilt"

    Content is migrating from a Zola site at
    [williamdemeo.org](https://williamdemeo.org) and an older Octopress site.
    Publications, talks, teaching, the project portfolio, the blog, and the
    graduate qualifying-exam solutions are still being moved across; progress
    is tracked in
    [the issue tracker](https://github.com/williamdemeo/williamdemeo.github.io/issues).
