---
title: General Relations
date: '2022-05-23'
---
<!-- zola-banner: generalrel -->

Shown above is an Agda definition of a type called Rel which represents single sorted relations of arbitrary arity in dependent type theory.  The type REL, also shown, represents completely general relations---i.e., relations of arbitrary arity and arbitrary sortedness.

## Motivation

In set theory, an n-ary relation on a set A is simply a subset of the n-fold product A × A × ⋯ × A.  As such, we could model these as predicates over the type A × A × ⋯ × A, or as relations of type A → A → ⋯ → A → Type β (for some universe β).  To implement such a relation in type theory, we would need to know the arity in advance, and then somehow form an n-fold arrow →.  It's easier and more general to instead define an arity type I : Type 𝓥, and define the type representing I-ary relations on A as the function type (I → A) → Type β.  Then, if we are specifically interested in an n-ary relation for some natural number n, we could take I to be a finite set (e.g., of type Fin n).

We define Rel to be the type (I → A) → Type β and we call this the type of *continuous relations*.  This generalizes "discrete" relations (i.e., relations of finite arity---unary, binary, etc), defined in the standard library since inhabitants of the continuous relation type can have arbitrary arity.

The relations of type Rel not completely general, however, since they are defined over a single type. Said another way, they are *single-sorted* relations. We will remove this limitation when we define the type of *dependent continuous relations* later in the module. Just as Rel A β is the single-sorted special case of the multisorted REL A B β in the standard library, so too is our continuous version, Rel I A β, the single-sorted special case of a completely general type of relations. The latter represents relations that not only have arbitrary arities, but also are defined over arbitrary families of types.

Concretely, given an arbitrary family A : I → Type α of types, we may have a relation from A i to A j to A k to …, where the collection represented by the "indexing" type I might not even be enumerable.

We refer to such relations as *dependent continuous relations* (or *dependent relations* for short) because the definition of a type that represents them requires depedent types.  The REL type defined below manifests this completely general notion of relation.

**Warning**! The type of binary relations in the standard library's Relation.Binary module is also called Rel.  Therefore, to use both the ("discrete") relation from the standard library, and our ("continuous") relation type, we recommend renaming the former when importing with a line like this

```hs,linenos
open import Relation.Binary  renaming ( REL to BinREL ; Rel to BinRel )
```


### Continuous and dependent relations

Here we define the types Rel and REL. The first of these represents predicates of arbitrary arity over a single type A. As noted above, we use the term *continuous relations* to refer to the inhabitants of Rel.
The definition of REL exploits the full power of dependent types to represent completely general relations, which we call *dependent relations*.

The tuples that belong to a relation of type REL I 𝒜 β inhabit the dependent function type 𝒜 : I → Type α (where the codomain may depend on the input coordinate i : I of the domain). Heuristically, we can think of a relation of type REL I 𝒜 β as a relation from 𝒜 i to 𝒜 j to 𝒜 k to …. Of course, this is only an heuristic since I could represent an uncountable collection.  See the discussion below for a more detailed explanation.


