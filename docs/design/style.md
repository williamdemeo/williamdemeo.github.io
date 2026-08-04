---
title: Style
description: >-
  The site's visual system: palette, typography, spacing, and the checks that
  keep them honest. Not part of the site's navigation.
search:
  exclude: true
---

# Style

The decided visual system, and the reasoning behind the parts of it that are
not a matter of taste. Every value lives in
[`docs/stylesheets/tokens.css`](https://github.com/williamdemeo/williamdemeo.github.io/blob/main/docs/stylesheets/tokens.css);
`extra.css` consumes those tokens and contains no raw colours or sizes of its
own. Settled in [#17](https://github.com/williamdemeo/williamdemeo.github.io/issues/17)
and recorded in ADR-005.

It also carries a live example of every reusable
[component](#components), including the cases where the optional parts are
missing, so a component that breaks breaks visibly, on one page.

The system is **Constellation**: the palette and Space Grotesk display face of
the [agda-algebras documentation site](https://agda-algebras.universalalgebra.org/),
which is also MkDocs Material. The two sites link to each other constantly, and
looking like siblings is worth more than each having a separate voice.

**Meridian** is kept as the alternative — the near-achromatic neutral ramp with
a teal accent and Newsreader for display that #17 first settled on.
[/design/options/](options/index.html) renders both, dark and light.

| | Display | Body | Accent (dark / light) |
| --- | --- | --- | --- |
| **Constellation** *(active)* | Space Grotesk 600 | Inter | `#8b88ff` / `#5b54e6`, coral hover |
| Meridian | Newsreader 500 | Inter | `#5eead4` / `#0f766e` |

Switching between them is three edits, all in `tokens.css` and all adjacent —
move the three bare selectors (`:root,`, `[data-md-color-scheme="default"],`,
`[data-md-color-scheme="slate"],`) from one block to the other. Move all three:
moving two produces a selector like `[data-md-color-scheme="default"]:root`,
which matches nothing. The comment at the top of that file spells it out.

Constellation's values are agda-algebras' own, read out of its
`stylesheets/custom.css`, with three adjusted because they do not clear AA as
text: `--c-fg-faint` in both themes, and the coral hover colour in light, which
is 2.86:1 on paper as published. Those three are the only places the two sites
deliberately differ; the before/after ratios are in `tokens.css`.

## Type

| Role | Face | Why |
| --- | --- | --- |
| Display | Space Grotesk 600 | A grotesk with enough character to mark headings without a second voice in the body copy, and the face the agda-algebras documentation already uses. |
| Body and interface | Inter 400 / 600 / 400 italic | Large x-height, unambiguous `1lI0O`, and the face agda-algebras reads in too. |
| Code and mathematics in prose | JuliaMono 400 | The only monospace face tested that covers Agda's notation, and independently the first entry in agda-algebras' own code stack. See [Monospace coverage](#monospace-coverage). |

Newsreader 500 is the alternative system's display face and is still shipped;
nothing names it while Constellation is active.

Sizes are `em`-relative to `.md-typeset`, which is what Material does; the base
is `0.85rem` and Material sets the root to 125%, so body copy is 17px.

| Token | Value | At the default root |
| --- | --- | --- |
| `--type-base` | `0.85rem` | 17 px |
| `--type-h1` | `2.25em` | 38 px |
| `--type-h2` | `1.5em` | 26 px |
| `--type-h3` | `1.1875em` | 20 px |
| `--type-h4` | `1em` | 17 px |
| `--type-small` | `0.8125em` | 14 px |
| `--type-code` | `0.875em` | 15 px |
| `--type-ui` | `0.7rem` | 14 px |

`--leading-body` is 1.7 and `--leading-heading` 1.25. Display sizes get
`--tracking-display: -0.02em`, because a geometric scale run up to 38px without
tightening looks loose.

Line length is capped at `--measure: 33rem`, about 74 characters, and applied
only to the prose blocks that are direct children of the article. Code blocks,
tables and figures keep the full column: an 80-column Agda block that wraps is
worse than one that is wider than the paragraph above it.

### Mathematics

KaTeX ships `font-size: 1.21em` on `.katex` because Computer Modern has a small
x-height. 1.21 is right for the body face KaTeX was designed against, not for
this one. Measured from the font files themselves:

| Face | x-height (em) | Ratio to KaTeX_Main |
| --- | --- | --- |
| KaTeX_Main-Regular | 0.4310 | 1.000 |
| **Inter** | **0.5459** | **1.267** |
| Source Serif 4 | 0.4998 | 1.160 |
| Newsreader | 0.4762 | 1.105 |

`--math-scale` is that ratio for the body face — `1.27em`, since both systems
read in Inter — so inline mathematics and the prose around it share an x-height
rather than being 5% apart on every line.

## Colour

One accent, used for links, the active nav item, the primary button and the
informational admonitions, and for nothing else. Everything else is a
four-step neutral ramp over three surfaces.

| Token | Role |
| --- | --- |
| `--c-bg` | page |
| `--c-bg-raised` | code blocks, table headers, cards |
| `--c-bg-sunken` | footer band |
| `--c-fg` | body text |
| `--c-fg-muted` | secondary text, captions, operators in code |
| `--c-fg-faint` | comments in code, tertiary text |
| `--c-line` / `--c-line-strong` | rules and borders |
| `--c-accent` / `--c-accent-hover` / `--c-accent-wash` / `--c-on-accent` | the one accent |

### Contrast

WCAG AA is 4.5:1 for body text and 3:1 for large text. Ratios below are
computed from the token values; the authoritative check is
`make contrast-audit`, which measures the rendered page instead — see
[Checks](#checks).

**Dark** — the default

| Token | Hex | On page | On raised | On sunken |
| --- | --- | --- | --- | --- |
| `--c-fg` | `#c3c8de` | 11.53:1 | 10.58:1 | 11.87:1 |
| `--c-fg-muted` | `#9197b6` | 6.66:1 | 6.12:1 | 6.86:1 |
| `--c-fg-faint` | `#8189af` | 5.59:1 | 5.14:1 | 5.76:1 |
| `--c-accent` | `#8b88ff` | 6.44:1 | 5.92:1 | 6.64:1 |
| `--c-accent-hover` | `#ff7a1a` | 7.34:1 | 6.74:1 | 7.56:1 |
| `--c-on-accent` | `#0c0e1d` | 6.44:1 on `--c-accent` | | |

**Light**

| Token | Hex | On page | On raised | On sunken |
| --- | --- | --- | --- | --- |
| `--c-fg` | `#181c2c` | 16.49:1 | 15.49:1 | 14.91:1 |
| `--c-fg-muted` | `#535d75` | 6.42:1 | 6.03:1 | 5.80:1 |
| `--c-fg-faint` | `#626b88` | 5.15:1 | 4.83:1 | 4.65:1 |
| `--c-accent` | `#5b54e6` | 5.31:1 | 4.99:1 | 4.80:1 |
| `--c-accent-hover` | `#b34b00` | 5.22:1 | 4.90:1 | 4.72:1 |
| `--c-on-accent` | `#ffffff` | 5.45:1 on `--c-accent` | | |

`--c-line` and `--c-line-strong` are borders, not text, and are not held to a
text threshold: 1.28:1 and 1.66:1 in dark, 1.23:1 and 1.48:1 in light.

`--c-error` is `#ff8a80` in dark (8.39:1 on the page) and `#b3261e` in light
(6.37:1). It is a token rather than a constant because KaTeX writes its
`errorColor` into an inline `style="color:…"`, and its default `#cc0000` is
3.29:1 on a dark page — a broken expression should be legible enough to fix.

Meridian, the alternative, clears AA everywhere too: worst case 4.69:1
(`--c-fg-faint` on the light sunken surface) and 4.91:1 (`--c-fg-faint` on the
dark raised surface). `make contrast-audit` measures both systems on every run,
because `/design/options/` puts both on one page.

### Theme selection

**Dark is the default.** The palette in `mkdocs.yml` has two entries, `slate`
first, and neither carries a `media` key — Material selects the first palette
when nothing is stored, and a `media` key would hand that decision back to the
operating system. One click on the header icon switches to light, and the
choice is remembered in local storage from then on.

The cost is worth stating: a visitor who has set a light-mode preference
system-wide gets a dark page until they click once. Verified in a browser with
`prefers-color-scheme` emulated at `light`, `dark` and `no-preference` — all
three land on `slate`, one click yields `default`, and the choice survives
navigation.

## Spacing

A 4px grid, expressed in rem against Material's 20px root: `--space-1` through
`--space-24` are 4px to 96px. Vertical rhythm comes from using them rather than
from a strict baseline grid, which is not worth the cost on a page that mixes
17px prose, 15px code and display mathematics.

Shape is deliberately understated: `--radius-sm` 2px, `--radius-md` 4px,
one-pixel borders, and no drop shadows anywhere. Material's `--md-shadow-z1..3`
are redefined as flat one-pixel rings, so depth reads the same in both themes.

## Components

Four components carry most of the site, and they are defined once in
`extra.css` rather than hand-styled per occurrence
([#19](https://github.com/williamdemeo/williamdemeo.github.io/issues/19)). The
consistency is what makes the site read as designed rather than assembled, and
it is what makes M4 and M5 fast to write: a page should need content, not CSS.

Everything below is real content — projects from the home page, publications
from `bibliography.json`, appointments from the CV, talks from the Zola site's
talks page — because a component that only ever meets tidy placeholder text has
not been tested. The one exception is the empty project card, which is a
deliberate floor case and says so.

Three conventions hold across all four.

**Markdown, not HTML.** The authoring form is a wrapper
`<div class="…" markdown>` around ordinary Markdown, with `{.class}` from
`attr_list` where a particular line needs naming. There is no component whose
source is a block of hand-written HTML.

**Every optional part is optional.** A publication with no DOI, a talk with no
slides, a position with no end date, a card with no links: each is shown below
in its degraded form as well as its full one. Nothing collapses, and nothing
leaves an empty separator behind.

**No component wraps itself in a link.** Making a whole card clickable means
nesting the title and the action links inside an enclosing anchor, which is
invalid HTML, does not survive keyboard navigation, and breaks text selection.
A card is a plain `<div>`; the title and the actions are ordinary sibling
links, each picking up the site-wide `:focus-visible` ring. No component sets
`overflow: hidden`, so that ring is never clipped by its own container.

### Project card

Title, one-line summary, technology tags, and links to source and
documentation. Used by the portfolio index
([#23](https://github.com/williamdemeo/williamdemeo.github.io/issues/23)) and
by the home page's featured projects.

The cards below are three real projects and one deliberate floor case. The
third has no documentation site, so it carries one action link rather than two;
the fourth has no tags, no links, and no linked title, which is as far down as
the component degrades.

<div class="project-grid" markdown>

<div class="project-card" markdown>
**[agda-algebras](https://github.com/ualib/agda-algebras)**

A library of universal algebra in Agda, containing the first constructive,
machine-checked proof of Birkhoff's HSP theorem in Martin-Löf type theory.

`Agda`{.tag} `type theory`{.tag} `universal algebra`{.tag}

[Source](https://github.com/ualib/agda-algebras) ·
[Docs](https://agda-algebras.universalalgebra.org)
{.project-links}
</div>

<div class="project-card" markdown>
**[formal-ledger-specifications](https://github.com/IntersectMBO/formal-ledger-specifications)**

Machine-checked specification of the Cardano blockchain ledger in Agda, written
with the Formal Methods team at IO.

`Agda`{.tag} `formal methods`{.tag}

[Source](https://github.com/IntersectMBO/formal-ledger-specifications) ·
[Paper](https://drops.dagstuhl.de/entities/document/10.4230/OASIcs.FMBC.2024.2)
{.project-links}
</div>

<div class="project-card" markdown>
**[agda-native-air](https://github.com/formalverification/agda-native-air)**

AI tooling for proof assistants: a semantic training-data extractor, an MCP
server exposing Agda's interaction protocol to language models, and the agent
loops built on them.

`Agda`{.tag} `MCP`{.tag} `AI tooling`{.tag}

[Source](https://github.com/formalverification/agda-native-air)
{.project-links}
</div>

<div class="project-card" markdown>
**A card with nothing optional**

Title and summary only — no linked title, no tags, no actions. This is the
floor, and it is what a project with nothing public to point at looks like.
</div>

</div>

??? example "Source"

    ```markdown
    <div class="project-grid" markdown>

    <div class="project-card" markdown>
    **[agda-algebras](https://github.com/ualib/agda-algebras)**

    A library of universal algebra in Agda, containing the first constructive,
    machine-checked proof of Birkhoff's HSP theorem in Martin-Löf type theory.

    `Agda`{.tag} `type theory`{.tag} `universal algebra`{.tag}

    [Source](https://github.com/ualib/agda-algebras) ·
    [Docs](https://agda-algebras.universalalgebra.org)
    {.project-links}
    </div>

    <div class="project-card" markdown>
    **A card with nothing optional**

    Title and summary only — no linked title, no tags, no actions.
    </div>

    </div>
    ```

The first paragraph is the title and needs no class. `.project-links` is the
one part that does, because it is pinned to the bottom of the card so that a
row of cards of unequal length still lines its actions up. Track width is
`calc(var(--measure) / 2)`: half a text column is the point below which a card
stops being a card and becomes a paragraph with a border.

Hover moves the border to `--c-line-strong` and keyboard focus anywhere inside
the card moves it to `--c-accent`, so "the pointer is over this" and "the
keyboard is in this" do not look the same.

### Tag

`Agda`{.tag} `type theory`{.tag} `invited`{.tag} `dormant`{.tag}

Written `` `Agda`{.tag} ``. It is a code span because `attr_list` attaches to
elements Markdown actually produces, and a bare `[text]{.tag}` is not one of
them — it renders literally, brackets and all. `em` and `strong` were the other
candidates and both already carry meaning in these components (venue,
emphasised author), so the neutral host is the right one. It is restyled out of
the code face entirely: these are labels, not code.

### Publication entry

Authors with the author emphasised, venue, year, and links to DOI, arXiv, and
PDF. Reverse-chronological grouping by year belongs to the publications page
([#30](https://github.com/williamdemeo/williamdemeo.github.io/issues/30)); this
is one entry.

The entries below are copied verbatim from what
`scripts/python/gen_publications.py` emits from `bibliography.json`
([#29](https://github.com/williamdemeo/williamdemeo.github.io/issues/29)). That
is the point of the component: the generator emits plain Markdown and knows
nothing about these classes, so the publications page wraps its output and adds
nothing. The last two show the degradation — an edited volume with no venue and
no identifiers at all, and a conference paper with a venue but no links.

<div class="publications" markdown>

- **Formal Specification of the Cardano Blockchain Ledger, Mechanized in Agda**  
  Andre Knispel and **William DeMeo**, et al.  *5th International Workshop on Formal Methods for Blockchains (FMBC 2024)*, 2024.  
  [DOI](https://doi.org/10.4230/OASIcs.FMBC.2024.2)

- **Bounded homomorphisms and finitely generated fiber products of lattices**  
  **William DeMeo**, Peter Mayr, and Nik Ruškuc.  *International Journal of Algebra and Computation*, **30**:693-710, 2020.  
  [DOI](https://doi.org/10.1142/S0218196720500174) · [arXiv:1907.08046](https://arxiv.org/abs/1907.08046)

- **Proceedings of Algebras and Lattices in Hawaii 2018** *(editor)*  
  Kira Adaricheva, **William DeMeo**, and Jennifer Hyndman, 2018.

- **Characterizing musical signals with Wigner-Ville interferences**  
  **William DeMeo**.  *Proceedings of the International Computer Music Conference (ICMC 2002), Gothenburg, Sweden*, 2002.

</div>

??? example "Source"

    ```markdown
    <div class="publications" markdown>

    - **Bounded homomorphisms and finitely generated fiber products of lattices**
      **William DeMeo**, Peter Mayr, and Nik Ruškuc.  *International Journal of Algebra and Computation*, **30**:693-710, 2020.
      [DOI](https://doi.org/10.1142/S0218196720500174) · [arXiv:1907.08046](https://arxiv.org/abs/1907.08046)

    - **Proceedings of Algebras and Lattices in Hawaii 2018** *(editor)*
      Kira Adaricheva, **William DeMeo**, and Jennifer Hyndman, 2018.

    </div>
    ```

    Each line of an entry ends with two trailing spaces, which is what keeps the
    three lines one paragraph. On the publications page the body of the wrapper
    is the generated snippet rather than literal entries.

An entry needs no classes at all — the wrapper carries the whole component. The
title is the first `**bold**`; the emphasised author steps forward out of the
muted metadata, and so does the volume number, which is marked up the same way
and is the one place that shows. Entries hang-indent, the way a reference list
has always been set, and that works whether or not the source has blank lines
between items: `text-indent` is inherited, so it reaches the paragraph that a
loose list wraps each entry in.

### Talk entry

Title, venue, location, year, and slides. Same grammar as a publication entry,
deliberately: a title, a line of attribution, and optional links. The slides
link goes on the title rather than in a row of its own, so a talk with no
slides is simply a title that is not a link — which is the third entry below.
The talks page ([#31](https://github.com/williamdemeo/williamdemeo.github.io/issues/31))
groups these by year and reconciles the record; these four are from the Zola
site's talks page.

<div class="talks" markdown>

- **[The Rectangularity Theorem of Barto and Kozik](https://github.com/williamdemeo/Talks/tree/master/Boulder/slides)**  
  Algebras and Algorithms: Structure and Complexity Theory, University of Colorado Boulder, 2016

- **[Algebraic CSP and Tractability of Commutative Idempotent Binars](https://github.com/williamdemeo/Talks/tree/master/BLAST/BLAST2015)**  
  BLAST Conference, University of North Texas, 2015

- **What Does a Nonabelian Group Sound Like?**  
  MAA Special Session: At the Intersection of Mathematics and the Arts, 2014

- **[Congruence Lattices of Finite Algebras](https://github.com/williamdemeo/Talks/tree/master/BLAST/BLAST2013)**  
  BLAST Conference, Chapman University, 2013 · `plenary`{.tag}

</div>

??? example "Source"

    ```markdown
    <div class="talks" markdown>

    - **[The Rectangularity Theorem of Barto and Kozik](https://github.com/williamdemeo/Talks/tree/master/Boulder/slides)**
      Algebras and Algorithms: Structure and Complexity Theory, University of Colorado Boulder, 2016

    - **What Does a Nonabelian Group Sound Like?**
      MAA Special Session: At the Intersection of Mathematics and the Arts, 2014

    - **[Congruence Lattices of Finite Algebras](https://github.com/williamdemeo/Talks/tree/master/BLAST/BLAST2013)**
      BLAST Conference, Chapman University, 2013 · `plenary`{.tag}
    </div>
    ```

`invited` and `plenary` are tags rather than a separate field, which is what
M5-3 needs to distinguish them. The venue line takes whatever of venue,
location and year the record actually has; a talk whose location was never
written down is one line shorter, not one line with a gap in it.

### Timeline entry

Positions and education, in one component, because they are the same shape: a
date, and what happened then. It is a definition list — `def_list` is already
enabled, the source reads as the thing it describes, and the CV's education and
grants sections are already written this way, so adopting it there is a wrapper
and nothing else.

The first entry below is open-ended, which is the missing-optional-field case
that matters here: `2023–` with nothing after the dash. The last is a single
year rather than a range, and an education entry rather than a position.

<div class="timeline" markdown>

2023–
:   **Formal Verification Engineer**, Formal Methods — [IO](https://iohk.io/)  
    Machine-checked specification of the Cardano blockchain ledger in Agda.

2022–2023
:   **Senior University Lecturer**, Computer Science — [NJIT](https://cs.njit.edu/)

2019–2021
:   **Postdoctoral Research Fellow**, Algebra — [Charles University, Prague](https://ka.karlin.mff.cuni.cz/)  
    NSF-funded work on the algebraic approach to constraint satisfaction.

2012
:   **PhD, Mathematics** — [University of Hawaii](https://math.hawaii.edu/)  
    Thesis: [Congruence lattices of finite algebras](https://arxiv.org/abs/1204.4305).
    Advisor: [Ralph Freese](http://math.hawaii.edu/~ralph/).

</div>

??? example "Source"

    ```markdown
    <div class="timeline" markdown>

    2023–
    :   **Formal Verification Engineer**, Formal Methods — [IO](https://iohk.io/)
        Machine-checked specification of the Cardano blockchain ledger in Agda.

    2022–2023
    :   **Senior University Lecturer**, Computer Science — [NJIT](https://cs.njit.edu/)

    </div>
    ```

The dates sit in a right-aligned gutter in tabular figures, so the ranges line
up on the dash whatever their width. Below Material's mobile breakpoint the
gutter costs more width than it earns and the entry stacks under its date,
keeping the rule and the node.

### Constellation

The identity mark, and the first component governed by [ADR-009's motion
rules](../adr/009-motion.md): Hasse diagrams drawn as star charts. N₅ and M₃
are the two lattices whose absence characterizes modularity and
distributivity; 𝟚³ is the Boolean cube. A reader who knows the diagrams reads
a signature; one who doesn't sees a night sky. It backs the home hero, and it
is the intended backdrop for the 404 and the social cards.

The drawing animates in once — lines first, stars with them, labels after —
and a few stars keep a slow shimmer. Under `prefers-reduced-motion: reduce`
the finished drawing simply appears, because the base styles *are* the final
state and motion exists only inside a `no-preference` media query. There is
no JavaScript in the component at all.

<div class="constellation-demo">
--8<-- "hero-constellation.html"
</div>

??? example "Source"

    The markup is one snippet, included where it is needed:

    ```markdown
    <div class="constellation-demo">
    --8<-- "hero-constellation.html"
    </div>
    ```

    In the hero it is included directly inside `<div class="hero" markdown>`,
    where it becomes the background layer behind both grid columns.

Every colour and stroke comes from `tokens.css` — the accent for stars, the
strong line for edges, the faint foreground for labels — so the drawing
adapts to both themes with no rules of its own. The labels are real text in
JuliaMono at full opacity: the contrast audit folds element opacity into the
foreground colour, so a faded label would fail AA where a faded circle
cannot. The timing values are the `--motion-*` tokens ADR-009 requires.

## Fonts

All three faces are self-hosted, subsetted WOFF2, built by
`scripts/python/build_fonts.py` from sources pinned by SHA-256 and regenerated
with `make fonts`. Nothing is fetched at page load.

| File | Characters | Size |
| --- | --- | --- |
| `juliamono-text.woff2` | 573 | 56 KB |
| `juliamono-symbols.woff2` | 3,029 | 253 KB |
| `juliamono-mathalpha.woff2` | 997 | 154 KB |
| `inter-400.woff2` | 510 | 39 KB |
| `inter-600.woff2` | 510 | 39 KB |
| `inter-400-italic.woff2` | 510 | 41 KB |
| `spacegrotesk-600.woff2` | 358 | 19 KB |
| `newsreader-500.woff2` | 341 | 31 KB |

Total: 631 KB across eight files, of which 75 KB is fetched by a page with no
notation on it at all. Newsreader is Meridian's display face and no rule names
it while Constellation is active, so it costs 31 KB in the repository and
nothing at page load.

JuliaMono is split three ways by `unicode-range` under one family name, so a
page pays only for the notation it shows: a page whose code is ASCII downloads
56 KB, `→` and `≡` add the symbol file, and an `𝑨` or a `𝓤` adds the
mathematical alphanumerics on top. A page of Agda that uses all three carries
about 460 KB of monospace, once, cached.

Only the regular weight of JuliaMono ships. Material's syntax highlighting is
colour-only — no bold, no italic in any token class — so a second code face
would be dead weight, and `.md-typeset code` pins `font-weight: 400` so that
inline code inside a heading cannot ask for a bold that does not exist.

JuliaMono is also the last self-hosted entry in the *text* stack. No text face
carries `∀`, `⊢` or `⨅`; a mathematical character that reaches prose should
come from a font the site ships rather than from whatever the reader's machine
offers.

### Monospace coverage

Agda's notation is the binding constraint on the monospace face, and most
programming fonts do not meet it. Measured against the 1,952 non-ASCII
characters `agda-input.el` names directly, and against a 44-character
spot-check drawn from what a page of Agda actually contains:

| Face | Glyphs | agda-input | Spot-check |
| --- | --- | --- | --- |
| **JuliaMono v0.63.2** | 11,191 | 92.8% | 44/44 |
| FreeMono | 6,858 | 77.7% | 38/44 |
| DejaVu Sans Mono | 3,322 | 45.0% | 34/44 |
| Noto Sans Mono | 3,490 | 34.5% | 36/44 |
| Fira Code | 1,551 | 19.3% | 24/44 |
| Cascadia Code | 2,426 | 17.0% | 14/44 |
| Source Code Pro | 1,334 | 16.5% | 18/44 |
| JetBrains Mono | 976 | 14.7% | 21/44 |
| IBM Plex Mono | 930 | 10.1% | 9/44 |

The 7.2% JuliaMono lacks is CJK, fullwidth forms, Ethiopic and Bamum. Every
other face fails on the Mathematical Alphanumeric Symbols block, which is where
`𝑨`, `𝓤`, `𝑆`, `𝔸`, `𝕏`, `𝒦`, `𝓞` and `𝓥` live — the characters
`agda-algebras` uses in almost every signature.

The shipped subset is defined by Unicode *block*, not by a list of characters.
The first version of this was a list, taken from `agda-input-translations`, and
it was wrong: the Agda input method inherits from Emacs' TeX method for
everything it does not redefine, so `ℓ`, `Π` and the subscript digits were
missing and fell back to DejaVu Sans Mono on a real page. `make font-audit`
caught it; nothing offline could have. Shipping whole blocks costs roughly
twice the bytes and removes the class of mistake.

## Checks

Each of these measures a rendered page in a real browser rather than reading
the CSS, because that is the only way to answer the question actually being
asked. They need `node` and a Chromium, and nothing from npm.

| Command | What it proves |
| --- | --- |
| `make font-audit` | Every face Chromium used to rasterise text is a downloaded webfont, and all 44 probe characters rendered in JuliaMono. A system font appearing in the content area means a character fell out of every shipped subset. |
| `make offline-audit` | Every request made by every page, with all `@font-face` declarations forced to load, was same-origin. |
| `make contrast-audit` | Every text-bearing element on every page clears AA against its composited background, in both themes. |
| `make fonts-check` | `docs/assets/fonts/` matches what `build_fonts.py` would produce now. |

`make design-audit` runs the first three.
