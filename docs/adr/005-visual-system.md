# ADR-005: The visual system, and how its constraints are checked

**Status**: Accepted

**Date**: 2026-08-02

**Deciders**: William DeMeo

**Related**: [#17](https://github.com/williamdemeo/williamdemeo.github.io/issues/17) (M3-1), [#20](https://github.com/williamdemeo/williamdemeo.github.io/issues/20) (M3-4, KaTeX), [#19](https://github.com/williamdemeo/williamdemeo.github.io/issues/19) (M3-3, components), [#21](https://github.com/williamdemeo/williamdemeo.github.io/issues/21) (M3-5, social cards), [ADR-004](004-nix-environment.md)

---

## Context

#17 asks for a palette, a typographic scale and a spacing scale, settled once,
so that later pages are assembled from decided components rather than
re-litigating design on every page. Three of its requirements are not matters
of taste and can be got wrong quietly:

**Agda's Unicode has to render in the intended monospace face with no fallback
substitution.** The site's flagship technical content is `agda-algebras`, whose
signatures are full of `𝑨`, `𝓤`, `𝑆`, `⨅`, `⊔` and subscripted identifiers. A
face that covers most of that and not all of it produces a mid-line switch to
whatever the reader's operating system offers — different width, different
weight, different design — on a page whose whole purpose is to look like
careful work.

**Nothing may be fetched from another origin.** The Zola site this replaces
loads Fira Code from `cdn.rawgit.com`, which shut down in 2019. Its intended
monospace font has silently not rendered for years. That is the failure mode,
and it is invisible from the source.

**Every text element has to clear WCAG AA in both themes.** Including the parts
nobody chose: Material's footer, its search field, its admonition titles, its
syntax-highlighting palette.

None of the three can be established by reading the CSS.

## Decision

**Adopt a token-based visual system in `docs/stylesheets/tokens.css`, ship
JuliaMono as the monospace face, self-host every face as subsetted WOFF2, and
gate all three constraints on audits that measure a rendered page.**

`extra.css` consumes the tokens and defines no raw colours or sizes. Material
is restyled through its own custom properties rather than by overriding its
rules, which is the supported route and survives a theme upgrade.

**The system is Meridian**: Newsreader 500 for display, Inter for body and
interface, JuliaMono for code, over a near-achromatic neutral ramp with a
single teal accent (`#0f766e` light, `#5eead4` dark).

It was chosen from three candidates rendered side by side on the same content —
a heading, a paragraph with inline mathematics, a display equation, a block of
Agda — rather than described in prose. The other two were *Graphite* (Inter
throughout, blue accent, cool neutrals) and *Manuscript* (Source Serif 4
throughout, warm paper, brick accent). All three cleared AA in both themes, so
the choice was unconstrained and aesthetic, which is why it was the owner's to
make. The rejected two, their font files, and the comparison page at
`/design/options/` were removed once the decision was recorded; reverting that
commit restores all three.

## What was verified

Every number below was produced by running something, not by reasoning about
it. The three audits are `scripts/js/audit_fonts.mjs`,
`audit_offline.mjs` and `audit_contrast.mjs`, run over the built site through
`make font-audit`, `make offline-audit` and `make contrast-audit`.

**Monospace coverage.** Nine monospace faces were tested by reading their
`cmap` tables against the 1,952 non-ASCII characters `agda-input.el` names, and
against a 44-character probe drawn from real Agda:

| Face | Glyphs | agda-input | Probe |
| --- | --- | --- | --- |
| JuliaMono v0.63.2 | 11,191 | 92.8% | 44/44 |
| FreeMono | 6,858 | 77.7% | 38/44 |
| DejaVu Sans Mono | 3,322 | 45.0% | 34/44 |
| Noto Sans Mono | 3,490 | 34.5% | 36/44 |
| Fira Code | 1,551 | 19.3% | 24/44 |
| Cascadia Code | 2,426 | 17.0% | 14/44 |
| Source Code Pro | 1,334 | 16.5% | 18/44 |
| JetBrains Mono | 976 | 14.7% | 21/44 |
| IBM Plex Mono | 930 | 10.1% | 9/44 |

Every face except JuliaMono fails on the Mathematical Alphanumeric Symbols
block, which is where `𝑨`, `𝓤`, `𝑆`, `𝔸`, `𝕏`, `𝒦`, `𝓞` and `𝓥` live. The
7.2% JuliaMono lacks is CJK, fullwidth forms, Ethiopic and Bamum. Fira Code —
the font the Zola site meant to use — covers 24 of the 44.

**No fallback substitution, measured in a browser.** `CSS.getPlatformFontsForNode`
reports which faces Chromium actually rasterised text with. Before this change,
on the existing site, an Agda block on `/design/rendering/` was rendered by
three fonts at once: DejaVu Sans Mono for 103 glyphs, FreeSerif for 9, FreeSans
for 1. After: 11,408 text-bearing elements across the 26 real pages, every face
reported a downloaded webfont, and 44/44 probe characters in JuliaMono.

**The enumerated subset was wrong, and the audit is what caught it.** Taking
the repertoire from `agda-input-translations` looks authoritative and is not:
the Agda input method *inherits* from Emacs' TeX method for everything it does
not redefine. `ℓ`, `Π` and the subscript digits `₀₁₂` come from there, were
missing from the first subset, and fell back to DejaVu Sans Mono on a real
page. An offline check against the same enumeration would have reported full
coverage. The subset is now defined by Unicode block.

**No external requests.** Before: every page emitted
`<link rel=preconnect href="https://fonts.gstatic.com">` and a stylesheet from
`fonts.googleapis.com` for Roboto and Roboto Mono, and fetched
`api.github.com/repos/…` twice. After: 646 requests across the 26 pages, with
all 27 `@font-face` declarations forced to load, and every one same-origin.

**Contrast.** 11,303 text elements per theme, measured from computed style with
the background resolved by compositing up the ancestor chain, and element
opacity folded into the foreground alpha. Real failures found and fixed:
`.md-button` rendered white on white in light mode (Material builds it from
`--md-primary-fg-color`, which here is the paper colour); the footer's "Made
with" line at 4.00:1; and the three faint-grey tokens, which cleared AA on the
page but not on the sunken footer band. The archive pages M2-9 brought in added
one more: KaTeX writes a failed expression in `errorColor`, whose default
`#cc0000` is 3.29:1 on the dark page, so a broken formula was the least legible
thing on the page. That is now `var(--c-error)` — KaTeX passes the string
straight into an inline `style`, so one token covers both themes. Now 0 below
AA in both themes, lowest 4.89:1 in light and 5.32:1 in dark.

Two measurement errors are worth recording. Material animates colour on a
scheme change, and reading `getComputedStyle` during that animation returns an
interpolated value belonging to neither theme; the audit disables transitions
before switching, which moved four ratios by more than a point. And the
imported lab sheets use `\phantom{XXX}` to draw a fill-in-the-blank rule,
which is text with a transparent foreground — invisible on purpose, not badly
contrasted. Fully transparent foregrounds are skipped, as `visibility: hidden`
and `opacity: 0` already were.

**A real gap in the body-face subset.** The CV page contains `š`, in a
co-author's name, and it rendered in Liberation Sans while the rest of the
sentence was Inter. Latin Extended-A and Greek are now shipped in full with
every text face.

**Reproducibility.** `make fonts` is byte-reproducible — `recalcTimestamp` is
off, so `head.modified` does not change per run — and `make fonts-check`
reports clean against the committed output.

**The other gates.** `make check` builds clean under `--strict`;
`make redirect-check` exits 0 against the 147-URL inventory; `make
redirect-test` passes 18 tests. `make math-audit` reports 24 failures over
`import/zola-converted`, which is exactly what it reports on `origin/main` —
the imported exam pages documented in #20, unrelated to this change and
verified by running the audit from a clean worktree of `main`.

## Rationale

### JuliaMono, and no realistic alternative

This is not a preference. Among mainstream monospace faces JuliaMono is the
only one that covers Mathematical Alphanumeric Symbols, and Agda uses that
block constantly. The next-best free option is FreeMono at 38/44, which is
still a substitution on six of the probe characters and is not a face anyone
would choose for a code block on aesthetic grounds.

Two current builds could not be tested: Iosevka and a recent Cascadia Code
release. `api.github.com` and GitHub release assets are blocked by this
environment's egress policy, and the Iosevka available through npm (TypoPRO
3.7, 192 glyphs) is a decade-old stripped build whose 0.6% would misrepresent
the modern font. Cascadia is covered via its Google Fonts copy (17.0%, 14/44).
Iosevka is untested; it would have to clear a very high bar to displace a face
already at 44/44.

### Subset by Unicode block rather than by a list of characters

Costs roughly twice the bytes and removes an entire class of mistake: any
character in a listed block renders, whether or not anyone anticipated it.
The listed blocks are the mathematical and notational ones; excluded are CJK,
Cyrillic, Braille, Canadian Syllabics, Arabic, Hebrew, the private-use areas
and the legacy-computing symbols — about 60% of JuliaMono's glyphs.

The alternative was already tried, in the first draft of this change, and the
browser caught it. That is the argument.

### Three files under one family name

`juliamono-text` (56 KB), `juliamono-symbols` (253 KB) and
`juliamono-mathalpha` (154 KB), split by `unicode-range`. One family name, so a
run of code mixing ASCII and `𝑨` is still one face to the layout engine, but a
page whose code is ASCII downloads 56 KB and stops. A page of Agda pays about
460 KB once. Undivided it would be 423 KB on every page with a `<code>` element
on it.

Only the regular weight ships. Material's syntax highlighting is colour-only —
no token class sets `font-weight` or `font-style` — so a bold or italic code
face would be bytes nobody sees.

### `--math-scale` rather than KaTeX's 1.21em

KaTeX sets `.katex { font-size: 1.21em }` to compensate for Computer Modern's
small x-height. Measured from the shipped font files, KaTeX_Main's x-height is
0.4310 em against Inter's 0.5459 — a ratio of 1.267, not 1.21. The token
carries the measured ratio for whichever body face is active, so inline
mathematics and the prose around it share an x-height instead of being about 5%
apart on every line.

### An override of one Material partial

`overrides/partials/source.html` drops `data-md-component="source"`, which is
what makes Material's bundle fetch `api.github.com/repos/<owner>/<repo>` on
every page load for a star and fork count.

This goes slightly beyond the letter of #17, whose acceptance criterion names
fonts, scripts and stylesheets — an XHR is none of the three. It is squarely
inside the point, and the alternative is an audit that keeps a list of blessed
exceptions, which is a weaker check than one that fails on anything
cross-origin. Flagged for review rather than buried; reverting it is deleting
one file and one line of `mkdocs.yml`.

### The audits drive a browser directly, with no npm dependency

`scripts/js/audit_math.mjs` established that these scripts need node and
nothing else. Node 22 ships a global `WebSocket`, which is all the DevTools
Protocol needs, so `scripts/js/_browser.mjs` is about 200 lines and keeps that
property rather than adding Playwright and a second browser download.

They serve the site over HTTP rather than reading `file://`, because Material's
bundle never initialises from disk — `document$` is undefined, no math renders,
and the audit would be measuring a page no visitor sees. That is the same trap
#20 documented.

### `fonttools` is not in `requirements.txt`

`make fonts` is a generator, run by hand when the character repertoire changes,
and its output is committed. Adding `fonttools` and `brotli` to
`requirements.txt` would oblige `flake.nix` to match their versions, because
ADR-004's `checks.requirements-pins` fails the build on any disagreement. That
is a standing maintenance cost for a target neither `make check` nor CI runs.
The script names what to install if the imports fail.

## Consequences

### Positive

- Agda's notation renders in one face, and a regression is a red audit rather
  than something noticed months later in a screenshot.
- No third-party origin is contacted by any page. The site works offline, and
  it does not report its readers to Google or GitHub.
- Contrast is a measured property of the rendered page, so a future change to a
  Material default cannot quietly break it.
- The design tokens are in one file, which is the precondition for M3-3
  building components without bespoke CSS, and for M3-5's social cards using
  the same palette and faces.
- ADR-004 left the social-card font family open, because choosing one was M3-1's
  job. It is Inter and Newsreader; M3-5 can seed the plugin's cache from
  `docs/assets/fonts/` or from the upstream TTFs `build_fonts.py` pins.

### Costs accepted

- **About 460 KB of monospace on a page of Agda.** Cached after the first
  visit, and split so lighter pages pay 56 KB, but it is real. The alternative
  is a smaller subset with a substitution risk, which is the thing being fixed.
- **The audits are not in CI.** They need a Chromium, which is not in the
  flake, and adding one there could not be verified from this environment
  (no Nix). They are local `make` targets until that is done. Tracked for
  M3-6.
- **A Material template override to keep in step.** Four lines of markup, and
  it silently reverts to upstream behaviour if the file is deleted rather than
  failing loudly. `make offline-audit` is what catches that.
- **Iosevka untested.** Stated above rather than glossed.
- **The comparison page and the two rejected systems are gone.** Reopening the
  choice means reverting a commit rather than editing a live switch. That is
  the right trade for not publishing 100 KB of unused faces and a scaffolding
  page, but it is a trade.

### Neutral

- `theme.font: false` is what removes Material's Google Fonts markup; the
  `@font-face` declarations in `docs/assets/fonts/fonts.css` are replacements,
  not additions.
- `primary: custom` and `accent: custom` in the palette mean "no built-in
  Material colour"; the values come from `tokens.css`.
- The colour tokens are set on the `[data-md-color-scheme]` selector, because
  that attribute lives on `<body>` — mapping them on `:root` would read them
  from an element that does not have them.
- `.fonts-cache/` holds the upstream sources, content-addressed, and is
  gitignored.
- `overrides/` is added to the `lib.fileset` in `flake.nix`. That edit could
  not be executed here; a Nix build that lost the override would still succeed
  and would silently restore the `api.github.com` fetch, which is the reason
  the line is there.

## Implementation status

| Task | Status |
| --- | --- |
| Palette for light and dark, with ratios | Done; three candidates pending #17 |
| Body, display and monospace faces with verified Agda coverage | Done |
| Self-hosted subsetted WOFF2; no external font reference | Done |
| Typographic scale, line length and vertical rhythm as custom properties | Done |
| Material palette matched, `prefers-color-scheme` default plus manual toggle | Done |
| `docs/design/style.md` | Done; components arrive with M3-3 |
| All text meets WCAG AA in both themes | Verified, `make contrast-audit` |
| Agda's Unicode renders with no fallback substitution | Verified, `make font-audit` |
| No external font, script or stylesheet requested | Verified, `make offline-audit` |
| Tokens in one place, used by the custom CSS | Done |
| Audits running in CI | Deferred to M3-6; needs a Chromium in the flake |
| Which of the three systems ships | **Meridian** |

## Notes

The audits are deliberately separate scripts with separate `make` targets, so
a failure names which of the three properties broke. `make design-audit` runs
all three.

`build_fonts.py` pins sources by SHA-256 rather than by a git ref. Upstream
moving a branch is exactly the failure that should be caught, and a hash
catches it whatever the URL says.
