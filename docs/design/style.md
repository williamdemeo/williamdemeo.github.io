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

From M3-3 this page also carries a live example of every reusable component,
so a component that breaks breaks visibly, on one page.

The active system is **Meridian**, chosen from three candidates rendered side
by side on the same content. Two of those three — *Graphite* and *Manuscript* —
were removed with the decision.

A fourth, **Constellation**, is defined alongside it and kept live: it is the
palette and display face of the
[agda-algebras documentation site](https://agda-algebras.universalalgebra.org/),
which is also MkDocs Material. The two sites will link to each other
constantly, so matching them is a defensible thing to want, and the choice is
worth keeping open. [/design/options/](options/index.html) renders both, dark
and light. Switching the site is two lines in `tokens.css`, described in the
comment at the top of that file.

| | Display | Body | Accent (dark / light) |
| --- | --- | --- | --- |
| **Meridian** *(active)* | Newsreader 500 | Inter | `#5eead4` / `#0f766e` |
| Constellation | Space Grotesk 600 | Inter | `#8b88ff` / `#5b54e6`, coral hover |

Constellation's values are agda-algebras' own, read out of its
`stylesheets/custom.css`, with three adjusted because they do not clear AA as
text: `--c-fg-faint` in both themes, and the coral hover colour in light, which
is 2.86:1 on paper as published. The reasoning and the before/after ratios are
in `tokens.css`.

## Type

| Role | Face | Why |
| --- | --- | --- |
| Display | Newsreader 500 | A text serif at display sizes. It gives headings a voice without the body copy having to carry serifs down a long page of prose. |
| Body and interface | Inter 400 / 600 / 400 italic | Large x-height, unambiguous `1lI0O`, and the closest match of the candidates to KaTeX's optical size once its 1.21 em is accounted for. |
| Code and mathematics in prose | JuliaMono 400 | The only monospace face tested that covers Agda's notation. See [Monospace coverage](#monospace-coverage). |

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
| Inter | 0.5459 | 1.267 |
| Source Serif 4 | 0.4998 | 1.160 |
| Newsreader | 0.4762 | 1.105 |

`--math-scale` is that ratio for whichever body face is active — `1.27em` for
Inter — so inline mathematics and the prose around it share an x-height rather
than being 5% apart on every line.

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

**Light**

| Token | Hex | On page | On raised | On sunken |
| --- | --- | --- | --- | --- |
| `--c-fg` | `#14181a` | 17.87:1 | 16.36:1 | 15.34:1 |
| `--c-fg-muted` | `#596265` | 6.25:1 | 5.72:1 | 5.37:1 |
| `--c-fg-faint` | `#626b6e` | 5.46:1 | 5.00:1 | 4.69:1 |
| `--c-accent` | `#0f766e` | 5.47:1 | 5.01:1 | 4.70:1 |
| `--c-accent-hover` | `#0b544e` | 8.78:1 | 8.04:1 | 7.54:1 |
| `--c-on-accent` | `#ffffff` | 5.47:1 on `--c-accent` | | |

**Dark**

| Token | Hex | On page | On raised | On sunken |
| --- | --- | --- | --- | --- |
| `--c-fg` | `#e3e7e8` | 15.56:1 | 14.37:1 | 15.93:1 |
| `--c-fg-muted` | `#94a0a3` | 7.21:1 | 6.66:1 | 7.38:1 |
| `--c-fg-faint` | `#7d888b` | 5.32:1 | 4.91:1 | 5.45:1 |
| `--c-accent` | `#5eead4` | 13.10:1 | 12.10:1 | 13.41:1 |
| `--c-accent-hover` | `#99f6e4` | 15.37:1 | 14.20:1 | 15.74:1 |
| `--c-on-accent` | `#06201d` | 11.52:1 on `--c-accent` | | |

`--c-line` and `--c-line-strong` are borders, not text, and are not held to a
text threshold: 1.28:1 and 1.61:1 in light, 1.29:1 and 1.71:1 in dark.

`--c-error` is `#b3261e` in light (6.54:1 on paper) and `#ff8a80` in dark
(8.49:1). It is a token rather than a constant because KaTeX writes its
`errorColor` into an inline `style="color:…"`, and its default `#cc0000` is
3.29:1 on the dark page — a broken expression should be legible enough to fix.

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
| `newsreader-500.woff2` | 341 | 31 KB |
| `spacegrotesk-600.woff2` | 358 | 19 KB |

Total: 631 KB across eight files, of which 56 KB is fetched by a page with no
notation on it at all. Space Grotesk is Constellation's display face and no
rule names it while Meridian is active, so it costs 19 KB in the repository and
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
