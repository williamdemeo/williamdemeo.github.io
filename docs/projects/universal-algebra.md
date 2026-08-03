---
title: Universal algebra and lattice theory
description: >-
  Congruence lattices of finite algebras and the finite lattice representation
  problem: what the open problem asks, why it is hard, and what I proved about
  it.
---

# Universal algebra and lattice theory

My doctoral and postdoctoral mathematics circles a single question, easy to
state and open since the 1960s: which finite lattices arise as the congruence
lattice of a *finite* algebra?  What makes it hard is that it stops being a
question about lattices almost immediately.  A theorem of Pálfy and Pudlák turns
it into a question about intervals in the subgroup lattices of finite groups, so
a problem about arbitrary finite algebras ends up downstream of the
classification of finite simple groups, and the tools that would settle it are
group-theoretic rather than lattice-theoretic.  My thesis proved every lattice
with at most seven elements representable except one, identified that one, and
proved structural restrictions on any group that could represent it.  The
results are in peer-reviewed journals, and most of the small representations
behind them are now machine-checked Agda that a reader can type-check instead of
taking on trust.

Sole author, and joint with Barto, Bergman, Freese, Jipsen, Mayr, Mottet, Ruškuc and Valeriote · 2012– · `active`{.tag}  
`universal algebra`{.tag} `lattice theory`{.tag} `complexity`{.tag}

## What the problem asks

An **algebra** here means the general thing, not the school subject: a set
together with some operations on it.  Groups, rings, lattices and vector spaces
are algebras; so is a four-element set carrying two arbitrary unary functions and
no laws whatsoever.

A **congruence** of an algebra $\bA$ is an equivalence relation on its elements
that the operations respect, meaning that if you replace any argument by an
equivalent one the result stays equivalent.  Congruences are exactly the
relations you are allowed to quotient by, and exactly the kernels of
homomorphisms out of $\bA$.  Every algebra has the identity relation and the
all-relation among its congruences; the interesting ones lie in between.

For familiar structures the congruences are familiar objects in disguise: for a
group they correspond to normal subgroups, for a ring to ideals, for a vector
space to subspaces.  For an arbitrary algebra there is no such translation and
the congruences themselves are the object of study.  Ordered by containment they
form a lattice $\operatorname{Con} \bA$, in which any two congruences have a
greatest lower bound and a least upper bound.  That lattice is the algebra's
internal structure seen as a shape; it records how $\bA$ can be taken apart, and
whether it embeds in a product of simpler algebras.

So every algebra has a shape attached to it, and the obvious question is which
shapes occur.

!!! note "The finite lattice representation problem"

    Is every finite lattice isomorphic to $\operatorname{Con} \bA$ for some
    *finite* algebra $\bA$?

The word doing all the work is *finite*, and it is worth seeing why.  Drop it and
the answer has been known since 1963, when Grätzer and Schmidt proved that every
algebraic lattice, which includes every finite lattice, is the congruence lattice
of some algebra.  Tůma later proved the same for intervals in subgroup lattices
of infinite groups.  Insist that the algebra be finite and, sixty years on,
nobody knows.  No finite lattice has ever been shown *not* to be the congruence
lattice of a finite algebra, and no argument that they all are has been found
either.

## Why it is hard

**Embedding is easy; being the whole thing is not**.  The congruences of a
finite algebra are partitions of its universe, so a representable lattice sits
inside $\operatorname{Eq}(X)$, the lattice of all equivalence relations on a
finite set $X$.  Getting a lattice *inside* $\operatorname{Eq}(X)$ is a solved
problem: Pudlák and Tůma proved in 1980 that every finite lattice embeds as a
sublattice of a finite partition lattice.  The representation problem asks for
more, namely that some copy be *all* of the congruences of one algebra, with
nothing else accidentally respected by the operations.

That gap has an exact description, classical and due to several people
independently around 1970, and it is the tool the thesis is built on.  For a
family $L$ of equivalence relations on $X$, let $\lambda(L)$ be the set of unary
maps on $X$ respecting every relation in $L$, and let $\rho(H)$ be the set of
equivalence relations respected by every map in $H$.  The pair is a Galois
correspondence, $\rho\lambda$ is a closure operator, and:

!!! note "The closure criterion"

    If $L \le \operatorname{Eq}(X)$, then $L = \operatorname{Con} \bA$ for some
    algebra $\bA$ with universe $X$ if and only if $L$ is closed, that is
    $\rho\lambda(L) = L$.

Finding a copy of your lattice inside $\operatorname{Eq}(X)$ is therefore only
the start.  You then compute the closure of that copy and find out whether you
have grown congruences you did not ask for.  Usually you have, and the copy is
useless even though the lattice may still be representable through a different
copy.  The thesis names the worst case *superbad*: a copy whose closure is all of
$\operatorname{Eq}(X)$.

**It is secretly a question about finite groups**.  In 1980 Pálfy and Pudlák
proved that the following two statements are equivalent: every finite lattice is
the congruence lattice of a finite algebra; and every finite lattice is
isomorphic to an interval $[H, G]$ in the subgroup lattice of a finite group,
where $[H, G]$ is the set of subgroups between $H$ and $G$ ordered by inclusion.

So a question about arbitrary finite algebras is really a question about finite
groups, and to rule out one small lattice you have to rule out every finite group
at once.  That is where the classification of finite simple groups enters, and it
is why most progress since 1980 has come from group theorists.

The subtlety most easily lost in summary is what that theorem does *not* say.
It is an equivalence between two universally quantified statements, not a
lattice-by-lattice correspondence; it does not say that a given representable
lattice is an interval in some subgroup lattice.  It says the two classes
coincide exactly when both are everything.

## What is known, and where it stops

The class of representable lattices is closed under a good deal.  The thesis
collects the closure results and their attributions: duals (Kurzweil and Netter,
1986), interval sublattices (a consequence of the same), direct products (Tůma,
1986), ordinal sums (McKenzie, 1984; Snow, 2000), parallel sums (Snow, 2000), and
unions of a filter and an ideal of a representable lattice (Snow, 2000).  Every
finite distributive lattice is representable, which Dilworth knew by the 1930s,
and is in fact the normal subgroup lattice of a finite solvable group (Silcock;
Pálfy).

Closure under *sublattices* is open, and cannot be easy.  $\operatorname{Eq}(X)$
is itself the congruence lattice of the algebra $\langle X, \emptyset \rangle$
with no operations at all, so sublattice closure together with Pudlák and Tůma's
embedding theorem would settle the whole problem affirmatively.  That single
observation explains why the positive direction has resisted: the constructions
that do work all preserve the property of being the *full* congruence lattice,
and the one operation that would finish the job does not.

## Every lattice with at most seven elements but one

There are 53 lattices with exactly seven elements, up to isomorphism.[^1]  My
thesis proves that with one possible exception every lattice with at most seven
elements is the congruence lattice of a finite algebra, and it identifies the
exception: a seven-element lattice consisting of a $2 \times 3$ grid, the product
of a two-element chain with a three-element chain, together with one extra
element sitting above the bottom, below the top, and comparable to nothing else.
That extra element is the lattice's unique element that is both an atom and a
coatom.  Fourteen years later it is still the smallest lattice for which no
representation is known.

Getting there took three kinds of work.  Most of the 53 fall out of the closure
properties above.  The thesis singles out ten that do not, and settles nine of
them: two by running the closure method on a computer over the partition lattice
$\operatorname{Eq}(8)$, several by exhibiting the lattice as the union of a filter
and an ideal inside the subgroup lattice of a small group, and one by a GAP
search that found it as an interval of index 80 in $(C_2)^4 \rtimes A_5$.  The
last of the nine, the "triple-wing pentagon", needed a new construction: begin
with an algebra whose congruence lattice is the six-element height-two lattice
with four atoms, then expand that algebra by adding elements and operations
chosen so that the congruence lattice is unchanged except that one atom has been
doubled.  Those **overalgebras** are the subject of the thesis's final chapter
and were published separately.

The tenth got a chapter of its own.  If the exceptional lattice is representable
at all, then an algebra of least cardinality representing it must be a transitive
$G$-set, so there is a finite group $G$ with a core-free subgroup $H$ and
$[H, G]$ isomorphic to the lattice.  The thesis then constrains $G$:

!!! note "Theorem 6.3.1"

    Suppose $H < G$ are finite groups with $\operatorname{core}_G(H) = 1$, and
    the exceptional lattice is isomorphic to $[H, G]$.  Then $G$ is a primitive
    permutation group; $C_G(N) = 1$ for every normal subgroup
    $N \trianglelefteq G$; $G$ has no nontrivial abelian normal subgroup; $G$ is
    not solvable; $G$ is subdirectly irreducible; and with the possible
    exception of one maximal subgroup, every proper subgroup in $[H, G]$ is
    core-free.

That solves nothing, and the thesis says so.  What it does is narrow the search
to a few classes of the O'Nan–Scott classification of primitive permutation
groups, which is the form in which the problem is still worth attacking.

Two further pieces belong to the same thread.  [Interval enforceable properties
of finite groups](https://arxiv.org/abs/1205.1927) sets up a framework for
exactly this style of argument: call a group property *interval enforceable* via
a lattice $L$ when every finite group having $L$ as an interval must satisfy it,
and observe that a property and its negation both being enforceable would settle
the whole problem.  [Isotopic algebras with nonisomorphic congruence
lattices](https://doi.org/10.1007/s00012-014-0301-4) answers a smaller question
that had been asked in passing: isotopy, a weakening of isomorphism, does not
preserve congruence lattices.

## Bounded homomorphisms and fiber products of lattices

The 2018 collaboration with Peter Mayr and Nik Ruškuc is lattice theory rather
than representation theory, and it ends in a decision procedure.  A lattice
epimorphism $g \colon A \to D$ is **bounded**, in the sense of McKenzie and
Jónsson, when every preimage $g^{-1}(d)$ has both a least and a greatest element.
The question we started from was when the kernel of a homomorphism from a
finitely generated free lattice onto a finite lattice is a finitely generated
sublattice of the square of the free lattice; the answer turned out to be
boundedness.

The published theorem is stated for **fiber products**.  Given epimorphisms
$g \colon A \to D$ and $h \colon B \to D$ of finitely generated lattices, where
$D$ satisfies a condition (D) that comes from Dean's solution to the word problem
for finitely presented lattices, if $g$ and $h$ are bounded then the pullback

$$C = \{\, (a, b) \in A \times B \mid g(a) = h(b) \,\}$$

is a finitely generated sublattice of $A \times B$.  The converse fails in
general, and we constructed a counterexample; it does hold when $A$ and $B$ are
free, or more generally satisfy Whitman's condition and are generated by join
prime and by meet prime elements.  Together the two directions characterize
boundedness of $D$ in terms of finite generation of these kernels and fiber
products, which yields the payoff: boundedness becomes decidable, in exponential
time, for finitely presented lattices and for their finitely generated
sublattices satisfying (D).  That generalizes an unpublished result of Freese
and Nation.

## The same algebras, used for complexity

Universal algebra acquired a second audience through constraint satisfaction.
Fix a finite relational structure; the constraint satisfaction problem over it
asks whether a system of constraints drawn from those relations has a solution.
Graph 3-colouring and 3-SAT are instances.  The algebraic approach observes that
the complexity of such a problem is determined by the algebra of *polymorphisms*
of the structure, so classifying finite algebras by their equational properties
is simultaneously classifying these problems by their complexity.

Three papers of mine live there, and all three are about *deciding* something.

+  With Cliff Bergman, [universal algebraic methods for constraint satisfaction
   problems](https://doi.org/10.46298/lmcs-18(1:12)2022) develops techniques for
   algebras that resist the known classifications, and uses them to prove that
   every commutative idempotent binar (a set with one binary operation, both
   commutative and idempotent) of cardinality at most four yields a tractable
   problem.
+  With Libor Barto and Antoine Mottet, [constraint satisfaction problems over
   finite structures](https://doi.org/10.1109/LICS52264.2021.9470670) lets the
   structure carry operations as well as relations, connects that to the
   algebraic question of which finite algebras admit only polynomially many
   homomorphisms into them, and derives a complete complexity classification over
   two-element structures, extending Schaefer's 1978 classification for
   two-element relational structures.
+  With Ralph Freese and Matthew Valeriote, [polynomial-time tests for difference
   terms in idempotent varieties](https://doi.org/10.1142/S021819671950036X)
   answers a practical question: given a finite idempotent algebra, decide in
   polynomial time whether the variety it generates has a difference term, and
   construct one when it does.

## Where this meets the formalization

The thesis's small representations were computed with GAP and the Universal
Algebra Calculator and published as tables in a manuscript.  A reader who wants
to check one has to re-run the search or trust the table.  That is being fixed
inside [`agda-algebras`](agda-algebras.md), which carries an FLRP research track
under `src/FLRP/`.

The problem itself is a type there rather than a comment.  `FLRP.Problem` defines
a `Representable` record, the data of a finite algebra together with an order
isomorphism from its congruence lattice to a given finite lattice, and states
"every finite lattice is representable" as a proposition the library *states but
does not assert*.  The easy direction of Pálfy and Pudlák is proved
constructively in `FLRP.Bridge`; the hard direction is imported as a named
hypothesis rather than postulated, which is the only honest way to have it in a
library that type-checks under `--safe`.

The certificates are the part that matters here.  An unpublished manuscript with
Ralph Freese and Peter Jipsen catalogues the 35 lattices of size at most seven
that are neither distributive nor ordinal sums, which is to say the ones that
actually needed work, and prints an algebra for most of them.  That catalog is
being converted entry by entry into machine-checked Agda.  27 of the 35 now carry
a certificate module that type-checks, meaning the search-free checkers re-verify
the engine's traces and produce a `Representable` witness during compilation.
Nothing is believed on the search engine's authority: a wrong table entry makes a
decidable check compute to `no` and breaks the build.  The exercise has already
found a defect in our own manuscript, an algebra whose congruence lattice as
printed has eight congruences rather than the seven claimed.

The exceptional lattice is formalized too, as `Examples.Classical.Lattices.L7`,
and `FLRP.L7EqSix` carries a machine-checked concrete copy of it: seven
partitions of a six-element set, the smallest possible, forming a sublattice of
$\operatorname{Eq}(6)$ isomorphic to it.  By the closure theorem above a copy is
not a representation.  It is the object the closure computation runs on.

## Artifacts

+  [Congruence lattices of finite algebras](https://arxiv.org/abs/1204.4305)
   (arXiv:1204.4305): the thesis.  The classification of lattices with at most
   seven elements is Section 6.2, the structural restrictions on the exceptional
   lattice are Theorem 6.3.1, and the closure method with its Galois
   correspondence is Chapter 3.  Everything this page says about what is known,
   and about who proved it, is sourced there.
+  [Expansions of finite algebras and their congruence
   lattices](https://doi.org/10.1007/s00012-013-0226-3) (*Algebra universalis*
   69:257–278, 2013; preprint
   [arXiv:1205.1106](https://arxiv.org/abs/1205.1106)): the overalgebra
   construction, refereed and published.
+  [Interval enforceable properties of finite
   groups](https://arxiv.org/abs/1205.1927) (arXiv:1205.1927, unpublished): the
   framework for turning "this lattice is an interval" into constraints on the
   group.
+  [Bounded homomorphisms and finitely generated fiber products of
   lattices](https://doi.org/10.1142/S0218196720500174) (*International Journal
   of Algebra and Computation* 30:693–710, 2020; preprint
   [arXiv:1907.08046](https://arxiv.org/abs/1907.08046)): the theorem with Mayr
   and Ruškuc, its converse, and the decision procedure they yield together.
+  [`FLRP.Problem`](https://agda-algebras.universalalgebra.org/FLRP/Problem/) and
   [`FLRP.L7EqSix`](https://agda-algebras.universalalgebra.org/FLRP/L7EqSix/) in
   the rendered `agda-algebras` documentation: the problem as a type, and the
   minimal concrete copy of the exceptional lattice.  Every identifier links to
   its definition.
+  [`SLR01`](https://agda-algebras.universalalgebra.org/FLRP/Certificates/SmallLatticeReps/SLR01/),
   one of the 27 certificate modules: what a machine-checked representation looks
   like, from the algebra's operation tables through to the isomorphism with the
   target lattice.
+  [Publications](../publications.md): the complete record, generated from a
   single bibliography and checked against the publishers that hold it.  This
   page links only the work it actually discusses.

## What is next

The honest summary is that I identified the exceptional lattice in 2012 and did
not represent it.  The thesis narrowed the group-theoretic search; the narrowing
has not yet closed.

What has changed is the standard of evidence available.  Re-running the searches
would produce another table.  Formalizing them produces an artifact a reader can
check without trusting me, the software I used, or the typesetting.  That work is
live, and its state is specific: of the 35 catalog entries, 27 are certified,
four are parked on group-theoretic representations with carriers of 90 to 216
elements that need the interval-to-congruence bridge at that scale, two are
conditional on the Kurzweil–Netter duality theorem being registered as a
hypothesis, one is the open case, and one was refuted by the checker as printed.
It has produced no new mathematics about the representation problem.  It has made
the existing corpus checkable and found one printed representation that does not
check, which is a smaller claim than a theorem and a more useful one than another
table.

The link back to [`agda-algebras`](agda-algebras.md) is not decorative.
Birkhoff's HSP theorem, the theorem that library mechanizes, is the central
theorem of this field, and the reason the library exists in the shape it does is
that its author wanted universal algebra to be something a machine could check.

Three posts develop pieces of this at length: [overalgebras and the GAP code that
builds them](../blog/posts/2014-02-13-overalgebras.md), [a problem of Pálfy and
Saxl](../blog/posts/2014-02-13-a-problem-of-palfy-and-saxl.md) on permuting
congruences, and [3-SAT and partition
lattices](../blog/posts/2015-01-11-three-sat-and-partition-lattices.md), which
encodes satisfiability as a question about intervals in $\operatorname{Eq}(X)$.
All three are old, and are labelled as such.

[^1]: The number of unlabelled seven-element lattices is sequence A006966 in the
      OEIS.  It is recomputed here rather than taken on faith, and the
      computation is short enough to describe: every seven-element lattice is a
      poset on five elements with a new bottom and a new top adjoined, so
      enumerate the 4231 labelled posets on five points, keep the ones whose
      bounded extension has all meets and joins, and count isomorphism classes.
      That gives 53, and the same enumeration returns 1, 1, 2, 5 and 15 for sizes
      two through six.
