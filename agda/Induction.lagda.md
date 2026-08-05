# Induction — recursion wearing its proof

One of the sessions the [home page](https://williamdemeo.github.io/)'s
terminal replays.  The contract is the one stated in `Free.lagda.md`: every
line the replay shows is a line of this file, the goal in the HUD is what
Agda reported for the hole, and `make proof` regenerates the committed
transcript (`docs/assets/proof.json`) by re-running the session with a real
Agda.  The module is self-contained — no imports — so a bare Agda checks it.

The lemma is the first proof by induction most people meet: `n + 0 ≡ n`.
With `_+_` recursing on its left argument, `0 + n` computes but `n + 0` does
not, so the proposition needs induction — and under Curry–Howard, induction
*is* structural recursion.  The base case holds by computation; the hole
lives in the inductive step, where the goal `suc (n + 0) ≡ suc n` is one
`cong suc` away from the recursive call.

```agda
{-# OPTIONS --cubical-compatible --exact-split --safe #-}

module Induction where

data ℕ : Set where
  zero : ℕ
  suc  : ℕ → ℕ
{-# BUILTIN NATURAL ℕ #-}

infixl 6 _+_
_+_ : ℕ → ℕ → ℕ
zero  + n = n
suc m + n = suc (m + n)

infix 4 _≡_
data _≡_ {A : Set} (a : A) : A → Set where
  refl : a ≡ a

cong : {A B : Set} (f : A → B) {x y : A} → x ≡ y → f x ≡ f y
cong f refl = refl
```

The markers delimit what the home page replays;
`scripts/python/gen_proof.py` re-derives the session from them.

<!-- replay-begin -->
```agda
-- Induction is recursion: the step
-- case calls the proof at n.
+-idʳ : ∀ n → n + 0 ≡ n
+-idʳ zero    = refl
+-idʳ (suc n) = cong suc (+-idʳ n)
```
<!-- replay-end -->
