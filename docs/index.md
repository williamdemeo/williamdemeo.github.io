---
# The home page is the one page without the docs frame: `hide` drops the nav
# sidebar and the TOC here and nowhere else (M3-2a, #93).  Inner pages keep
# the frame they genuinely benefit from.
#
# The top of the page is a hero grid, not a float.  The second column is the
# typed-proof terminal (M3-2d, #96): replays of real Agda sessions over the
# five modules in agda/, one lemma per tab, rendered *finished* by
# proof_hook.py from the committed transcript (docs/assets/proof.json,
# `make proof`) and rewound by proof.js only where motion is allowed --
# after a CSS-only entrance holds the frame back while the words above land
# (--motion-hero-enter).  The constellation behind it (M3-2b, #94)
# holds its final frame on this page -- the replay is the home page's one
# orchestrated moment (ADR-009, amended 2026-08-04).  A portrait sat in that
# column in this page's first cut; it is gone rather than moved -- a
# photograph is decoration on a page whose argument is evidence -- and #88
# (floated images) remains open for other pages.  The h1 is the claim, not
# the name -- the name is in the header bar, the eyebrow line, and the
# <title> that `title:` below sets for nav and search.
#
# The card order is a subset of ADR-008's, in ADR-008's relative order, and the
# tags are copied from docs/projects/index.md.  Neither is a per-page call.
# (ADR-008 is the portfolio-shape decision.  It was numbered 006 until #86 gave
# it its own number; ADR-006 is the bibliography decision and is a different
# document.)
title: William DeMeo
description: >-
  Mathematician and formal verification engineer working on machine-checked
  mathematics, interactive theorem proving in Agda, and AI tooling for proof
  assistants.
hide:
  - navigation
  - toc
---

<div class="hero" markdown>

<!-- The wrapper div is load-bearing: Python-Markdown does not treat <svg> as
     a block-level element, so an unwrapped include inside this markdown div
     would be parsed as inline HTML and shredded.  A plain div is block-level
     and its contents pass through untouched. -->
<div class="constellation-wrap">
--8<-- "hero-constellation.html"
</div>

<div class="hero-copy" markdown>

William DeMeo · formal verification × AI
{ .hero-eyebrow }

# Mathematics, machine-checked.

Proofs and production systems in Agda — and tooling that lets language
models drive the proof assistant, with the typechecker as the reward
signal.
{ .hero-claim }

[Explore the projects](projects/index.md){ .md-button .md-button--primary }
[About me](about.md){ .md-button }
{ .hero-actions }

</div>

<div class="hero-side">
<!-- proof-terminal -->
</div>

</div>

<!-- evidence-strip -->

Mathematician by training with a PhD in universal algebra and lattice theory; 
formal verification engineer by trade.  I work on **machine-checked
mathematics**: proofs and production systems in Agda, and tooling that lets
language models work inside a proof assistant.

**What I'm working on now** (2026). The machine-checked specification of
the Cardano ledger in Agda, with the Formal Methods team at
[IO](https://iohk.io/), and
[agda-native-air](https://github.com/formalverification/agda-native-air),
making Agda's interaction protocol accessible to language models so they can
interact with the proof assistant the way humans do, rather than merely
type-checking complete proofs.

## Featured projects

<div class="project-grid" markdown>

<div class="project-card" markdown>
**[AI for formal verification](https://github.com/formalverification/agda-native-air)**

An MCP server exposing Agda's interaction protocol to language models, and the
agent loops built on it.

`Agda`{.tag} `MCP`{.tag} `AI tooling`{.tag}

[Source](https://github.com/formalverification/agda-native-air)
{.project-links}
</div>

<div class="project-card" markdown>
**[agda-algebras](projects/agda-algebras.md)**

A formalization of universal algebra in Agda, and a substrate for research in
it; the flagship result is a constructive, machine-checked proof of Birkhoff's
HSP theorem in Martin-Löf type theory.

`Agda`{.tag} `type theory`{.tag} `universal algebra`{.tag} `setoids`{.tag}

[Source](https://github.com/ualib/agda-algebras) ·
[Docs](https://agda-algebras.universalalgebra.org)
{.project-links}
</div>

<div class="project-card" markdown>
**[The Cardano ledger specification](projects/cardano-ledger.md)**

Formal methods at production scale: an Agda specification that must track a
system under active development.

`Agda`{.tag} `Haskell`{.tag} `formal methods`{.tag} `production`{.tag}

[Source](https://github.com/IntersectMBO/formal-ledger-specifications) ·
[Paper](https://drops.dagstuhl.de/entities/document/10.4230/OASIcs.FMBC.2024.2)
{.project-links}
</div>

<div class="project-card" markdown>
**[Universal algebra and lattice theory](projects/universal-algebra.md)**

The finite lattice representation problem, open since the 1960s, and the
algebraic approach to the complexity of constraint satisfaction.  A thesis
result, and a machine-checked revival now under way.

`universal algebra`{.tag} `lattice theory`{.tag} `complexity`{.tag}

[Thesis](https://arxiv.org/abs/1204.4305) ·
[Papers](publications.md)
{.project-links}
</div>

</div>

The through-line across all four is an interest in what is *mechanizable*:
which structures admit effective procedures, and what it takes to make an
argument checkable by a machine rather than by a referee.

The full set is in [Projects](projects/index.md).

## Recent writing

<!-- recent-posts -->

More in the [blog](blog/index.md).

## Elsewhere

Before moving into industry I held research and teaching appointments at Charles
University in Prague, the University of Colorado Boulder, the University of
Hawaii, Iowa State University, and the University of South Carolina.  The
[CV](cv.md) has the full record and [about](about.md) has the longer version.

[Email](mailto:williamdemeo@gmail.com) ·
[GitHub](https://github.com/williamdemeo) ·
[Google Scholar](https://scholar.google.com/citations?user=y1OQ07QAAAAJ) ·
[ORCID](https://orcid.org/0000-0003-1832-5690) ·
[arXiv](https://arxiv.org/a/demeo_w_1) ·
[Publications](publications.md) ·
[Contact](contact.md)

!!! note "This site is still being rebuilt"

    Content is migrating here from a Zola site at
    [williamdemeo.org](https://williamdemeo.org) and an older Octopress site.
    The publications, the projects, and the blog have landed; talks, teaching,
    a research narrative, and the graduate qualifying-exam solutions have not.
    Progress is tracked in
    [the issue tracker](https://github.com/williamdemeo/williamdemeo.github.io/issues).
