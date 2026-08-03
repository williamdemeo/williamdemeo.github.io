---
# Adding a card, or filling one in when its page lands: docs/projects/_template.md.
# The order is argued in ADR-008 and is not a per-page call.
#
# A YAML comment rather than an HTML one, because an HTML comment in the body
# survives into the rendered page -- verified by grepping site/projects/index.html
# for it.  Front matter is parsed and discarded, so nothing here can ship.
title: Projects
description: >-
  Machine-checked mathematics, formal verification of production systems, and
  AI tooling for proof assistants — with the source, papers, and documentation
  behind each.
---

# Projects

Machine-checked mathematics, formal verification at production scale, and
tooling that lets language models work inside a proof assistant.

Ordered by relevance to what I work on now, not by date.

<div class="project-grid" markdown>

<div class="project-card" markdown>
**[AI for formal verification](https://github.com/formalverification/agda-native-air)**

Tooling that lets language models work inside a proof assistant: an MCP server
exposing Agda's interaction protocol, a semantic training-data extractor, Claude
Skills encoding Agda workflow knowledge, and the agent loops built on them.

`Agda`{.tag} `MCP`{.tag} `AI tooling`{.tag}

[Source](https://github.com/formalverification/agda-native-air)
{.project-links}
</div>

<div class="project-card" markdown>
**[agda-algebras](agda-algebras.md)**

A library of universal algebra in Agda, containing the first constructive,
machine-checked proof of Birkhoff's HSP theorem in Martin-Löf type theory, joint
with Jacques Carette.

`Agda`{.tag} `type theory`{.tag} `universal algebra`{.tag} `setoids`{.tag}

[Source](https://github.com/ualib/agda-algebras) ·
[Docs](https://agda-algebras.universalalgebra.org)
{.project-links}
</div>

<div class="project-card" markdown>
**[The Cardano ledger specification](cardano-ledger.md)**

Machine-checked specification of the Cardano blockchain ledger in Agda, written
with the Formal Methods team at IO — a specification that has to track a system
under active development and produce artifacts the rest of the organization
consumes.

`Agda`{.tag} `Haskell`{.tag} `formal methods`{.tag} `production`{.tag}

[Source](https://github.com/IntersectMBO/formal-ledger-specifications) ·
[Paper](https://drops.dagstuhl.de/entities/document/10.4230/OASIcs.FMBC.2024.2)
{.project-links}
</div>

<div class="project-card" markdown>
**[Universal algebra and lattice theory](universal-algebra.md)**

The mathematics the rest of this rests on: congruence lattices of finite
algebras and the finite lattice representation problem, and later work on the
algebraic approach to constraint satisfaction.

`universal algebra`{.tag} `lattice theory`{.tag} `complexity`{.tag}

[Thesis](https://arxiv.org/abs/1204.4305) ·
[Papers](https://scholar.google.com/citations?user=y1OQ07QAAAAJ)
{.project-links}
</div>

<div class="project-card" markdown>
**[Category theory: a concise course](https://categorytheory.gitlab.io)**

An online course in category theory, coauthored with Venanzio Capretta and Charlotte Aten, built out from Capretta's notes for a short course at the Midlands Graduate School.

`category theory`{.tag} `exposition`{.tag}

[Course](https://categorytheory.gitlab.io)
{.project-links}
</div>

</div>
