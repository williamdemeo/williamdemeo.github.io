# Free — the landing page's first lemma

The terminal on [the home page](https://williamdemeo.github.io/) replays
hole-filling sessions over the five small modules in this directory, one per
tab; this module is the first.  The session: the signature of `lift-hom`
types itself, a hole opens with its goal, the hole fills, and the goal count
falls to zero.  This file is that session's source, and ADR-009's
evidence-honesty rule is the contract between the two: every line the replay
shows is a line of this file, the goal in its HUD is what Agda reported for
the hole, and the closing `✓ type-checked · Agda <version>` carries the
version of the check that really ran.  `make proof` re-runs every session
with a real Agda and regenerates the committed transcript,
`docs/assets/proof.json`; the replays can go stale, but they cannot drift
from sessions that happened.

The lemma is the freeness of the term algebra — the existence half — in
miniature.  `free-lift` and `lift-hom` are
[agda-algebras](https://github.com/ualib/agda-algebras)' names for it
(`Terms.Properties` there proves it over setoids, in full generality); this
module is that development shrunk to a screenful: one sort, no universe
polymorphism, and no imports, so the file checks with a bare Agda and nothing
else.  `--safe` means Agda rejects any postulate — nothing here is assumed.

```agda
{-# OPTIONS --cubical-compatible --exact-split --safe #-}

module Free (F : Set) (ρ : F → Set) where
```

The module is parameterized by a signature: a set `F` of operation symbols
and, for each symbol `f`, a set `ρ f` indexing its arguments.  Equality and
dependent pairs are defined rather than imported, and they are the whole of
the machinery.

```agda
infix 4 _≡_
data _≡_ {A : Set} (a : A) : A → Set where
  refl : a ≡ a

infixr 4 _,_
record Σ (A : Set) (B : A → Set) : Set where
  constructor _,_
  field
    fst : A
    snd : B fst
```

An algebra is a carrier with an interpretation of every operation symbol;
`𝕌[ 𝑨 ]` names the carrier, after agda-algebras.  A homomorphism is a map
of carriers together with the proof that it commutes with every operation —
the pair, not the bare map.

```agda
record Algebra : Set₁ where
  field
    𝕌    : Set
    _⟦_⟧ : (f : F) → (ρ f → 𝕌) → 𝕌
open Algebra using (_⟦_⟧)

𝕌[_] : Algebra → Set
𝕌[ 𝑨 ] = Algebra.𝕌 𝑨

hom : Algebra → Algebra → Set
hom 𝑨 𝑩 = Σ (𝕌[ 𝑨 ] → 𝕌[ 𝑩 ])
            (λ h → ∀ f a → h ((𝑨 ⟦ f ⟧) a) ≡ (𝑩 ⟦ f ⟧) (λ i → h (a i)))
```

The term algebra over a set `X` of generators: a term is a generator, or a
symbol applied to terms, and the interpretation of a symbol is `node`
itself.

```agda
data Term (X : Set) : Set where
  ℊ    : X → Term X
  node : (f : F) (t : ρ f → Term X) → Term X

𝑻 : Set → Algebra
𝑻 X = record { 𝕌 = Term X ; _⟦_⟧ = node }
```

The lemma binds its context once, the way `Terms.Properties` does in
agda-algebras: an anonymous module fixes the generators `X`, the algebra
`𝑨` and the assignment `h`, and both definitions live inside it — which is
why the replayed lines carry their two-space indent.  `free-lift` extends
`h` to the whole of `𝑻 X` by structural recursion; the first clause is the
statement that it extends `h`.  And because the second clause is *defined*
as "interpret `f` in `𝑨` over the lifted arguments", the homomorphism
condition holds by `refl`: the equation the hole asks for is the definition
of the thing it asks about.  That is the replay's punchline, and it is the
standard proof.

```agda
module _ {X : Set} {𝑨 : Algebra} (h : X → 𝕌[ 𝑨 ]) where

  free-lift : 𝕌[ 𝑻 X ] → 𝕌[ 𝑨 ]
  free-lift (ℊ x)      = h x
  free-lift (node f t) = (𝑨 ⟦ f ⟧) (λ i → free-lift (t i))
```

The markers around the block below delimit what the home page replays.
`scripts/python/gen_proof.py` reads them, re-derives the session — put a
hole where the last line's right-hand side is, load, ask for the goal, give
the fill — and records what Agda answered.

<!-- replay-begin -->
```agda
  -- 𝑻 X is free: every map out of X
  -- extends to a homomorphism.
  lift-hom : hom (𝑻 X) 𝑨
  lift-hom = free-lift , λ f t → refl
```
<!-- replay-end -->

Uniqueness of the extension — the other half of freeness — needs function
extensionality or a setoid of homomorphisms, either of which would triple
the module; agda-algebras' `free-unique` is the full statement.  The half
above is the one the replay can show honestly in four lines.
