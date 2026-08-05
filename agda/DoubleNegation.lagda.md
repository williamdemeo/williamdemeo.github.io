# DoubleNegation — classical logic, almost

One of the sessions the [home page](https://williamdemeo.github.io/)'s
terminal replays.  The contract is the one stated in `Free.lagda.md`: every
line the replay shows is a line of this file, the goal in the HUD is what
Agda reported for the hole, and `make proof` regenerates the committed
transcript (`docs/assets/proof.json`) by re-running the session with a real
Agda.  The module is self-contained — no imports — so a bare Agda checks it.

Excluded middle — `A ∨ ¬ A` for an arbitrary `A` — has no constructive
proof: a proof would be a decision procedure for every proposition at once.
Its *double negation* is a theorem, though, and the proof term is the
classic continuation trick: handed a refutation `k` of `A ∨ ¬ A`, feed it
the right disjunct, whose contents `λ a → k (inl a)` uses `k` again the
moment anyone produces an `a`.  The refuter is made to defeat itself.
Disjunction is defined here as the sum type its introduction rules describe;
`inl` and `inr` are its two verdicts.

```agda
{-# OPTIONS --cubical-compatible --exact-split --safe #-}

module DoubleNegation (A : Set) where

data ⊥ : Set where

infix 3 ¬_
¬_ : Set → Set
¬ X = X → ⊥

infixr 1 _∨_
data _∨_ (X Y : Set) : Set where
  inl : X → X ∨ Y
  inr : Y → X ∨ Y
```

The markers delimit what the home page replays;
`scripts/python/gen_proof.py` re-derives the session from them.

<!-- replay-begin -->
```agda
-- Excluded middle is out of reach,
-- but its double negation is not.
¬¬em : ¬ ¬ (A ∨ ¬ A)
¬¬em = λ k → k (inr λ a → k (inl a))
```
<!-- replay-end -->
