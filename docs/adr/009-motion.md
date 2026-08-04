# ADR-009: Motion

**Status**: Accepted

**Date**: 2026-08-03

**Deciders**: William DeMeo

**Related**: [#94](https://github.com/williamdemeo/williamdemeo.github.io/issues/94) (M3-2b, first motion to ship), [#95](https://github.com/williamdemeo/williamdemeo.github.io/issues/95) (M3-2c), [#96](https://github.com/williamdemeo/williamdemeo.github.io/issues/96) (M3-2d), [#97](https://github.com/williamdemeo/williamdemeo.github.io/issues/97), [#100](https://github.com/williamdemeo/williamdemeo.github.io/issues/100), [ADR-005](005-visual-system.md)

---

## Context

Until M3-2b the site had no animation, so nothing needed a rule.  The 2026-08-03
design review introduces several moving parts — a constellation that draws
itself (#94), counts that tick up (#95), a proof replay (#96), previews that
appear (#97) — and each one was argued for individually.  What is missing is
the standing rule that lets the *next* animation be judged without re-arguing
from taste, the way ADR-005 lets a new colour be judged by measurement rather
than preference.

The risk being legislated against is specific: animation is the fastest way to
make a careful site look cheap.  A site that earns attention through restraint
loses it to one bouncing card.

## Decision

Three principles, then mechanics.  Every animation on the site must satisfy
all three; the mechanics are how compliance is checked rather than asserted.

**1. Motion demonstrates or identifies — never decorates.**  A thing may move
because watching it move carries information (a proof being completed, a count
being tallied) or because it is the site's visual signature (the
constellation).  "It looks more alive" is not a reason; that is what the two
permitted reasons produce as a side effect.

**2. One signature per screen.**  At most one orchestrated moment in view at a
time.  If two want to coexist, one of them is wrong — usually the newer one.
Micro-feedback (a border colour on hover, a 120 ms underline) is not a
signature and does not count against the budget; anything with a timeline
does.

**3. Motion is evidence-honest.**  Anything replayed or counted is a replay or
a count of something real and checkable — a session that happened, a number a
script produced.  A mocked terminal or an invented statistic would pass a
visual review and fail this document.

### Mechanics

- **Reduced motion is a first-class rendering, not a degradation.**  Under
  `prefers-reduced-motion: reduce`, every animated element renders its final
  state immediately: lines drawn, counts at their values, replays showing the
  finished proof.  Nothing is missing; only the passage of time is.  This is
  also the crawler's and the JS-disabled reader's view wherever the mechanism
  allows (CSS-only components degrade this way by construction; scripted ones
  must ship final state in the HTML).
- **Timing comes from tokens.**  Durations, delays, staggers and easings are
  custom properties in `tokens.css` (`--motion-*`), consumed by `extra.css`
  the way colour tokens are.  A new animation that needs a new number adds a
  token, visibly, rather than burying a magic constant.
- **CSS before JavaScript.**  If a CSS animation can carry it, no script.
  JavaScript is reserved for motion that replays data (#95's counts, #96's
  transcript), and even then the no-JS rendering is the final state, not a
  blank.
- **Keyboard and touch parity.**  Anything hover-revealed is focus-revealed
  and dismissible (WCAG 1.4.13); anything with a replay control is operable
  by keyboard.
- **The audits still gate.**  Animated elements are text and colour like any
  others: `make contrast-audit` measures them (it already disables
  transitions before reading computed style — ADR-005 records why), and
  `make offline-audit` confirms no animation pulls anything cross-origin.

## What was verified

- The constellation (#94, the first component under this rule) renders its
  final state under emulated `prefers-reduced-motion: reduce` in Chromium —
  every line at full length, every star visible, no animation events firing.
- Both themes pass `make design-audit` with the component in the build.
- With JavaScript disabled the component is unchanged, because it uses none.

## Consequences

- A future animation PR is reviewable against a checklist rather than a
  mood: which of the two permitted purposes, where is its token, what is the
  reduced-motion frame, what does the keyboard do.
- The evidence-honesty principle binds content, not just style: #96 cannot
  ship a prettified transcript, and #95 cannot ship a rounded-up count.
  That constraint is the brand, stated once.
- Micro-interactions stay cheap to add (they are exempt from the signature
  budget), so restraint at the signature level does not freeze small
  improvements.
