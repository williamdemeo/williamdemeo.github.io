# Absurd — the proof with no cases

One of the sessions the [home page](https://williamdemeo.github.io/)'s
terminal replays.  The contract is the one stated in `Free.lagda.md`: every
line the replay shows is a line of this file, the goal in the HUD is what
Agda reported for the hole, and `make proof` regenerates the committed
transcript (`docs/assets/proof.json`) by re-running the session with a real
Agda.  The module is self-contained — no imports — so a bare Agda checks it.

The lemma is a disequation: `true` and `false` are different.  Nothing here
is an axiom — `--safe` forbids postulates — and no case analysis is written
out.  The type `true ≡ false` has no constructor (the only one, `refl`,
needs both sides to match), so it is empty, and a function out of an empty
type is total with no clauses at all.  Agda's absurd pattern `()` says
exactly that, and the checker verifies the emptiness rather than taking our
word for it.  The whole proof is four characters.

```agda
{-# OPTIONS --cubical-compatible --exact-split --safe #-}

module Absurd where

data Bool : Set where
  true false : Bool

data ⊥ : Set where

infix 4 _≡_
data _≡_ {A : Set} (a : A) : A → Set where
  refl : a ≡ a
```

The markers delimit what the home page replays;
`scripts/python/gen_proof.py` re-derives the session from them.

<!-- replay-begin -->
```agda
-- Nothing constructs true ≡ false;
-- the absurd pattern has no cases.
true≢false : true ≡ false → ⊥
true≢false = λ ()
```
<!-- replay-end -->
