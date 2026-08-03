---
title: Universal algebra and lattice theory
description: >-
  Congruence lattices of finite algebras, the finite lattice representation
  problem and the methods I developed for it, the algebraic approach to
  constraint satisfaction, and the machine-checked continuation of all of it.
---

# Universal algebra and lattice theory

Two bodies of work, and a third that is live now.  My thesis attacked the finite
lattice representation problem, open since the 1960s: which finite lattices are
the congruence lattice of a finite algebra?  It is not really a question about
lattices, which is what makes it hard; a theorem of Pálfy and Pudlák turns it
into a question about intervals in the subgroup lattices of finite groups, so it
sits downstream of the classification of finite simple groups.  The thesis
settled every lattice with at most seven elements save one, identified that one,
and contributed two general methods rather than a list of cases: a construction
that manufactures new representable lattices to order, and a framework for
proving that a lattice of a given shape forces any group representing it to look
a certain way.  The decade after the thesis went mostly elsewhere, to the
algebraic approach to constraint satisfaction, where the same finite algebras
turn out to control the complexity of computational problems.  All of it is in
peer-reviewed journals, and the representation-problem half is now being rebuilt
as machine-checked Agda in
[`agda-algebras`](https://github.com/ualib/agda-algebras), which is the part I
find most interesting: it is the first version of this problem that a proof
assistant can work on directly.

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
nobody knows.  A lattice that is $\operatorname{Con} \bA$ for a finite $\bA$ is
called **representable**, and the problem is to decide whether every finite
lattice is.

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
independently around 1970, and it is the tool much of the thesis is built on.
For a family $L$ of equivalence relations on $X$, let $\lambda(L)$ be the set of
unary maps on $X$ respecting every relation in $L$, and let $\rho(H)$ be the set
of equivalence relations respected by every map in $H$.  The pair is a Galois
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
$\operatorname{Eq}(X)$, and it proves results about when that happens, because
knowing which copies are hopeless is what makes a computer search feasible.

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

## Closing the small lattices

There are 53 lattices with exactly seven elements, up to isomorphism.[^1]  The
thesis proves that with one possible exception, every lattice with at most seven
elements is the congruence lattice of a finite algebra.

That result came out of a catalogue.  In the spring of 2011 Peter Jipsen, then
visiting the Hawaii algebra seminar, proposed listing every small finite lattice
with a known finite representation, and it turned into the classification.  Most
of the 53 fall out of the closure properties above.  The thesis singles out ten
that do not and settles nine of them, six explicitly and the other three as duals
of those by the Kurzweil–Netter theorem.  The six took genuinely different
methods:

+  Two were found by running the closure method on a computer over
   $\operatorname{Eq}(8)$, the lattice of all 4140 partitions of an eight-element
   set: search for a copy, compute $\rho\lambda$ of it, and keep going until a
   copy comes back closed.
+  Two were found inside subgroup lattices, as the union of a filter and an ideal
   of a lattice already known to be representable.  One of them lives in
   $\operatorname{Sub}(A_4)$, which is small enough to draw; the other in a group
   of order 216.
+  One came from a GAP search that turned it up as an interval of index 80 in
   $(C_2)^4 \rtimes A_5$, meaning the representing algebra has 80 elements.
+  One, the "triple-winged pentagon", needed a construction that did not exist
   yet.  That is the next section.

The classification is one of 27 new results in the thesis, and it is not the one
I would lead with.  The methods are.

## Overalgebras: manufacturing representable lattices

Ralph Freese cracked the triple-winged pentagon with an idea: start from an
algebra $\mathbf{B}$ whose congruence lattice is $M_4$, the six-element lattice
of height two with four atoms, enlarge the universe, and choose new operations so
that the congruence lattice comes back the same shape as before except that one
atom has been *doubled*.

The thesis takes that single example and turns it into a procedure.  Given a
finite algebra $\mathbf{B}$ with known congruence lattice, choose sets
$B_1, \dots, B_K$ meeting $B$ at prescribed points, and build an **overalgebra**
on $A = B \cup B_1 \cup \dots \cup B_K$ whose operations include idempotent maps
retracting $A$ onto $B$ and onto each $B_i$.  Where the intersection points go,
and which operations are included, determines the new congruence lattice.  Four
constructions are developed, each generalizing the last, with theorems
identifying $\operatorname{Con}$ of the result; Chapter 7 alone carries eight of
the thesis's new results, and the chapter was published separately in *Algebra
universalis*.

What comes out is not one lattice but a class of them.  The resulting congruence
lattice has the same overall shape as the one you started with, except that
chosen congruences are replaced by intervals that are direct products of powers
of partition lattices.  So the procedure manufactures representable lattices on
demand, which is why the paper's abstract calls the more significant
contribution the *approach* rather than the lattices: it is a way of discovering
new classes of representable lattices, not a way of checking one.

The thesis is equally clear about the limits, and they are worth repeating
because they say where the method could go next.  The new intervals have to be
products of partition lattices, which is restrictive, and the whole technique
works by realizing the old congruence lattice as a homomorphic image of the new
one, so it cannot reach a *simple* lattice at all.  The exceptional
seven-element lattice is simple.  Overalgebras were never going to get it.

## Parachutes: a strategy for a negative answer

The other method points the opposite way.  Suppose you want to prove some lattice
is *not* an interval in any finite subgroup lattice, which by Pálfy and Pudlák
would answer the whole problem negatively.  The literature already contains
theorems of the form "if this lattice is an interval $[H, G]$, then $G$ must be a
group of such-and-such a kind".  Individually they constrain; the thesis makes
them compose.

Call a group property **interval sublattice enforceable** (ISLE) if there is a
lattice $L$ such that every finite group with $L$ as an upper interval has the
property, and **cf-ISLE** if the same holds whenever the bottom of the interval
is core-free.  Now take a target lattice $L$ together with enforcing lattices
$L_1, \dots, L_n$, and glue them all onto one new bottom element while sharing
one top; the thesis calls the result a **parachute**.  If the representation
problem has a positive answer then the parachute is an interval $[H, G]$ for some
finite group $G$, and $L$ and every $L_i$ appear as upper intervals $[K, G]$ and
$[K_i, G]$ in the *same* $G$.  So $G$ has to satisfy every property that any of
them enforces, simultaneously.

That gives a concrete route to a negative answer:

!!! note "The strategy"

    If some lattice $L_0$ forces every group representing it into a class
    $\mathcal{G}$, and some lattice $L_1$ forces every group representing it out
    of $\mathcal{G}$, then the parachute built from $L_0$ and $L_1$ is an
    interval in no finite subgroup lattice at all, and the finite lattice
    representation problem is answered.

The thesis supplies the machinery this needs and stocks the catalogue.  It proves
that a parachute with a core-free bottom propagates core-freeness to every proper
subgroup above it, which is what lets an enforcement result about $L_i$ transfer
to $G$.  It shows that non-solvability is ISLE, and that being subdirectly
irreducible, having no nontrivial abelian normal subgroup, and having a trivial
centralizer for a minimal normal subgroup are all cf-ISLE.  And it records the
obstruction honestly, as Conjecture 5.1: perhaps a property and its negation can
never both be enforceable, in which case this route is closed and the fact that
it is closed is itself a theorem worth having.

One consequence is worth stating on its own, because it is the sort of thing that
makes people suspect the answer is no.

!!! note "Proposition 5.1.1"

    If the finite lattice representation problem has a positive answer, then for
    *any* finite collection of finite lattices there is a *single* finite group
    $G$ having every one of them as a core-free upper interval in
    $\operatorname{Sub}(G)$.

Take the collection to be all lattices with at most a million elements.  Some one
finite group would have to carry every one of them, each as an interval over a
core-free subgroup, and so would have that many distinct faithful permutation
representations.  Nothing rules it out.  It does concentrate the mind.

## The one that got away

The lattice the classification could not reach has seven elements: a
$2 \times 3$ grid, the product of a two-element chain with a three-element
chain, plus one extra element sitting above the bottom, below the top, and
comparable to nothing else.  That extra element is the lattice's unique element
that is both an atom and a coatom, and it makes the lattice simple, which is what
puts it out of reach of overalgebras.  It is still the smallest lattice for which
no representation is known.

It is not, though, a blank.  If it is representable at all, then an algebra of
least cardinality representing it must be a transitive $G$-set, so there is a
finite group $G$ with a core-free subgroup $H$ and $[H, G]$ isomorphic to it.
The thesis then constrains $G$ hard:

!!! note "Theorem 6.3.1"

    Suppose $H < G$ are finite groups with $\operatorname{core}_G(H) = 1$, and
    the exceptional lattice is isomorphic to $[H, G]$.  Then $G$ is a primitive
    permutation group; $C_G(N) = 1$ for every normal subgroup
    $N \trianglelefteq G$; $G$ has no nontrivial abelian normal subgroup; $G$ is
    not solvable; $G$ is subdirectly irreducible; and with the possible
    exception of one maximal subgroup, every proper subgroup in $[H, G]$ is
    core-free.

Primitivity brings the O'Nan–Scott theorem to bear, and the rest of that list
eliminates most of its cases, which is why the thesis closes by saying it expects
the problem to fall rather than to stand.  Two smaller pieces belong to the same
thread: [isotopic algebras with nonisomorphic congruence
lattices](https://doi.org/10.1007/s00012-014-0301-4) settles that isotopy, a
weakening of isomorphism, does not preserve congruence lattices, and
[Dedekind's transposition principle for lattices of equivalence
relations](https://arxiv.org/abs/1301.6788) proves the version of the
transposition principle that this line of argument keeps needing.

## Constraint satisfaction, which is where the next decade went

The postdoctoral years were mostly not about congruence lattices.  They were
about complexity, at Iowa State with Cliff Bergman, at Boulder on an NSF grant
for *Algebras and algorithms, structure and complexity theory*, and at Charles
University in Prague with Libor Barto.

Fix a finite relational structure; the constraint satisfaction problem over it
asks whether a system of constraints drawn from those relations has a solution.
Graph 3-colouring and 3-SAT are instances.  The algebraic approach observes that
the complexity of such a problem is determined by the algebra of *polymorphisms*
of the structure, so classifying finite algebras by their equational properties
is simultaneously classifying these problems by their complexity.  It is the same
subject as the first half of this page, pointed at a different question.

Three papers, and all three are about *deciding* something.

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

## Rebuilding the program in Agda

[`agda-algebras`](agda-algebras.md) is a formalization of universal algebra as a
subject: algebras, homomorphisms, congruences, terms, varieties, the equational
logic underneath them, and a growing layer of specific classical theories.
Birkhoff's HSP theorem is its flagship result, not its purpose.  The purpose is a
substrate: a machine-checked body of universal algebra big enough to do new
research inside.

The representation problem is the first place we are trying that, under
`src/FLRP/`, and it is a research program with a plan rather than a formalization
exercise.  What exists so far:

+  **The problem as a type**.  `FLRP.Problem` defines a `Representable` record,
   the data of a finite algebra together with an order isomorphism from its
   congruence lattice to a given finite lattice, and states "every finite lattice
   is representable" as a proposition the library states but does not assert.
+  **The easy half of Pálfy–Pudlák, proved constructively**, in `FLRP.Bridge`.
   The hard half is imported as a named hypothesis rather than postulated, which
   is the only honest way to have it in a tree that type-checks under `--safe`.
+  **The parachute theorem, machine-checked**, in `FLRP.Parachute`: core-freeness
   at the bottom of a parachute propagates to every proper subgroup above it.
   Formalizing it improved it.  The original argument is a proof by
   contradiction; in Agda the parachute's covering property is *data*, so the
   same steps read as a direct proof with no double negation introduced.
+  **The enforceability framework**, in `FLRP.Enforceable`, including a
   machine-checked proof that a property and its negation cannot both be
   enforceable via lattices that are *known* to be group representable.  That
   result is the reason the formalization tracks representability explicitly
   instead of quantifying it away: an enforcing lattice nobody can realize
   enforces everything vacuously, and deciding whether it can be realized is the
   original problem.
+  **Machine-checked representation certificates**.  An unpublished manuscript
   with Ralph Freese and Peter Jipsen catalogues the 35 lattices of size at most
   seven that are neither distributive nor ordinal sums, the ones that actually
   needed work, and prints an algebra for most of them.  27 of the 35 now carry a
   certificate module that type-checks: the search-free checkers re-verify the
   engine's traces and produce a `Representable` witness during compilation, so a
   wrong table entry makes a decidable check compute to `no` and breaks the
   build.  The exercise has already found a defect in our own manuscript, an
   algebra whose congruence lattice as printed has eight congruences rather than
   the seven claimed.
+  **The exceptional lattice**, as `Examples.Classical.Lattices.L7`, together
   with a machine-checked concrete copy in `FLRP.L7EqSix`: seven partitions of a
   six-element set, the smallest possible, forming a sublattice of
   $\operatorname{Eq}(6)$ isomorphic to it.  By the closure criterion a copy is
   not a representation; it is the object the closure computation runs on.

## Artifacts

+  [Congruence lattices of finite algebras](https://arxiv.org/abs/1204.4305)
   (arXiv:1204.4305): the thesis, and the source for everything on this page
   about what is known and who proved it.  The closure method is Chapter 3, the
   parachute construction and the enforceability framework are Chapter 5, the
   classification is Section 6.2, the restrictions on the exceptional lattice are
   Theorem 6.3.1, and overalgebras are Chapter 7.
+  [Expansions of finite algebras and their congruence
   lattices](https://doi.org/10.1007/s00012-013-0226-3) (*Algebra universalis*
   69:257–278, 2013; preprint
   [arXiv:1205.1106](https://arxiv.org/abs/1205.1106)): the overalgebra
   constructions and the theorems describing what they produce, refereed and
   published.
+  [Interval enforceable properties of finite
   groups](https://arxiv.org/abs/1205.1927) (arXiv:1205.1927): the enforceability
   framework as a standalone note, and the document the Agda formalization is
   written against.
+  [Bounded homomorphisms and finitely generated fiber products of
   lattices](https://doi.org/10.1142/S0218196720500174) (*International Journal
   of Algebra and Computation* 30:693–710, 2020; preprint
   [arXiv:1907.08046](https://arxiv.org/abs/1907.08046)): the theorem with Mayr
   and Ruškuc, its converse, and the decision procedure they yield together.
+  [`FLRP.Problem`](https://agda-algebras.universalalgebra.org/FLRP/Problem/),
   [`FLRP.Parachute`](https://agda-algebras.universalalgebra.org/FLRP/Parachute/)
   and [`FLRP.Enforceable`](https://agda-algebras.universalalgebra.org/FLRP/Enforceable/)
   in the rendered `agda-algebras` documentation: the problem as a type, and the
   two thesis methods as type-checked Agda.  Every identifier links to its
   definition.
+  [`SLR01`](https://agda-algebras.universalalgebra.org/FLRP/Certificates/SmallLatticeReps/SLR01/),
   one of the 27 certificate modules, and
   [`FLRP.L7EqSix`](https://agda-algebras.universalalgebra.org/FLRP/L7EqSix/),
   the minimal concrete copy of the exceptional lattice.
+  [Publications](../publications.md): the complete record, generated from a
   single bibliography and checked against the publishers that hold it.  This
   page links only the work it actually discusses.

## What is next

The program has a bet and an insurance policy.  The bet is on a negative answer,
pursued through enforceability: keep proving that particular interval shapes
force particular group structure, and try to drive the classes to an empty
intersection.  The insurance policy is the positive direction on the exceptional
lattice, so that either outcome produces a verified artifact rather than a
verified disappointment.

Being specific about the state of the machine-checked half, since that is the
part with numbers: of the 35 catalogue entries, 27 are certified, four are parked
on group-theoretic representations with carriers of 90 to 216 elements that need
the interval-to-congruence bridge at that scale, two are conditional on the
Kurzweil–Netter duality theorem being registered as a hypothesis, one is the open
case, and one was refuted by the checker as printed.  Nothing in the tree has yet
proved anything new about the representation problem.  What it has done is make
the existing corpus checkable, improve one proof in the process of formalizing
it, and find one printed representation that does not check.

The reason to think the third act is worth more than the sum of those is the
tooling.  A sixty-year-old problem in universal algebra has never before had its
methods available as a type-checked corpus that a machine can read, search and
extend, and building that corpus is also what the [AI tooling](index.md) work is
for.  Proof search over a formalized enforceability catalogue is a concrete thing
to point a model at, and the answer is either a contradiction between two
enforceable properties or a proof that no such contradiction exists.  Both are
publishable, and both are checkable by the same compiler.

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
