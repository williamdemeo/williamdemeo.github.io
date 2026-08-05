# Absorption — where the two semilattices meet

One of the sessions the [home page](https://williamdemeo.github.io/)'s
terminal replays.  The contract is the one stated in `Free.lagda.md`: every
line the replay shows is a line of this file, the goal in the HUD is what
Agda reported for the hole, and `make proof` regenerates the committed
transcript (`docs/assets/proof.json`) by re-running the session with a real
Agda.  The module is self-contained — no imports — so a bare Agda checks it.

In an equational presentation of lattices, absorption is an axiom: it is
what welds two semilattices into one lattice.  Order-theoretically it is a
theorem.  Here a lattice is a poset in which `x ∧ y` is a greatest lower
bound and `x ∨ y` an upper bound (only the halves the proof uses are
carried as fields), and `x ∧ (x ∨ y) ≡ x` falls out of antisymmetry: the
meet is below `x` because meets are, and above `x` because `x` bounds both
`x` and `x ∨ y`.  The two inequalities are named `below` and `above`, so
the session's give is just antisymmetry applied to the pair.

```agda
{-# OPTIONS --cubical-compatible --exact-split --safe #-}

module Absorption where

infix 4 _≡_
data _≡_ {A : Set} (a : A) : A → Set where
  refl : a ≡ a

record Lattice : Set₁ where
  infix  4 _≤_
  infixr 7 _∧_
  infixr 6 _∨_
  field
    L         : Set
    _≤_       : L → L → Set
    _∧_ _∨_   : L → L → L
    ≤-refl    : ∀ x → x ≤ x
    ≤-antisym : ∀ {x y} → x ≤ y → y ≤ x → x ≡ y
    ∧-lower   : ∀ x y → x ∧ y ≤ x
    ∧-glb     : ∀ {x y z} → z ≤ x → z ≤ y → z ≤ x ∧ y
    ∨-upper   : ∀ x y → x ≤ x ∨ y
```

The lemma binds its context once: an anonymous module fixes the lattice and
two of its elements, which is why the replayed lines carry their two-space
indent.

```agda
module _ (K : Lattice) (x y : Lattice.L K) where
  open Lattice K

  below : x ∧ (x ∨ y) ≤ x
  below = ∧-lower x (x ∨ y)

  above : x ≤ x ∧ (x ∨ y)
  above = ∧-glb (≤-refl x) (∨-upper x y)
```

The markers delimit what the home page replays;
`scripts/python/gen_proof.py` re-derives the session from them.

<!-- replay-begin -->
```agda
  -- The absorption law welds the two
  -- semilattices into one lattice.
  ∧-absorb : x ∧ (x ∨ y) ≡ x
  ∧-absorb = ≤-antisym below above
```
<!-- replay-end -->
