---
title: The Algebraic CSP Dichotomy Conjecture
date: '2014-10-14'
---

**Abstract.** This page collects some old notes about algebraic CSP highlighting the main results of the past decade or two and stating one of the main (formerly open) problems in this area.

-----------------------------------------

**Contents**

- [Definition of relational CSP](@definition-of-relational-csp)
- [Connection to algebraic CSP](@connection-to-algebraic-csp)
- [The main problem](@the-main-problem)
- [Taylor terms](@taylor-terms)
  - [Taylor term iff no Type 1](@taylor-term-iff-no-type-1)
  - [No Type 1 iff no trivial divisors](@no-type-1-iff-no-trivial-divisors)
  - [Tractable only if Taylor term](@tractable-only-if-taylor-term)
  - [Taylor term iff WNU term](@taylor-term-iff-wnu-term)
  - [Taylor term iff Cyclic term](@taylor-term-iff-cyclic-term)
  - [Taylor term iff Siggers term](@taylor-term-iff-siggers-term)
- [Bibliography](@bibliography)

--------------------------------------------

## Definition of relational CSP

Given a **relational structure**,
$\mathbb{R} = \langle X, \Gamma \rangle$,
that is, set $X$ along with a collection
$\Gamma \subseteq \bigcup_{n>0} \mathcal{P}(X^n)$ of *relations* 
on $X$, we associate with $\mathbb{R}$ a
**constraint satisfaction problem**
denoted by $\operatorname{CSP}(\mathbb{R})$.
This is a decision problem that is solved by finding an algorithm or program
that does the following: take as input any

+ **instance:** a relational structure
$\mathbb{S} = \langle Y, \Gamma' \rangle$ with the same signature as $\mathbb{R}$.

and *decide* (output "yes" or "no") if there is or is not a

+ **solution:** a homomorphism $h: \mathbb{S} \to \mathbb{R}$.

If there is such an algorithm that takes at most a power of $n$ operations
to process an input $\mathbb{S}$ of size $n$ (bits of memory required
to encode $\mathbb{S}$),
then we say that $\operatorname{CSP}(\mathbb{R})$
is **tractable**.  Otherwise, we call it **intractable**.

Equivalently, if we define $\operatorname{CSP}(\mathbb{R})= \\{\mathbb{S} \mid \text{ there is a homomorphism } h : \mathbb{S} \to \mathbb{R} \\}$, then the CSP problem described above is simply the membership problem for the set $\operatorname{CSP}(\mathbb{R})$. That is, our algorithm must take as input a relational structure of the same signature as $\mathbb{R}$ and decide whether it belongs to the set $\operatorname{CSP}(\mathbb{R})$.


--------------------------------

## Connection to algebraic CSP
Let $X$ be a set, let $Op(X)$ denote the set of all operations
on $X$, and $Rel(X)$ the set of all relations on $X$.

Given $\Gamma\subseteq Rel(X)$, define the set of
all operations that leave the relations in $\Gamma$ "fixed" as follows:

$$\operatorname{Fix}(\Gamma) = \\{f \in Op(X) \mid f \text{ respects every }
\gamma \in \Gamma\\}.$$

By "$f$ respects every $\gamma$" we mean that each
$\gamma$ is a subalgebra of a (finite)
power of the algebra $\langle X, \\{ f \\} \rangle$.

If $\mathbb{R} = \langle X, \Gamma \rangle$ is
a relational structure, then the set
$\operatorname{Fix}(\Gamma)$
is sometimes called the set of *polymorphisms* of $\mathbb{R}$.

Going the other way, starting with a collection $F\subseteq Op(X)$,
define the set of all relations left "invariant" by
the functions in $F$ as follows:

$$\operatorname{Inf}(F) = \\{\gamma \in Rel(X) \mid \gamma \text{ is respected by
every } f \in F\\}.$$

It is easy to see that $\Gamma \subseteq \operatorname{Inv}(\operatorname{Fix}(\Gamma))$ and $F \subseteq \operatorname{Fix}(\operatorname{Inv}(F))$.

-----------------------------------

Let $\mathbf{A}(\mathbb{R})$ denote the algebraic structure
with universe $X$ and operations $\operatorname{Fix}(\Gamma)$.
Then every $\gamma \in \Gamma$ is a subalgebra of a power of
$\mathbf{A}(\mathbb{R})$.

Clearly
$\operatorname{Inv}(\operatorname{Fix}(\Gamma)) =
\operatorname{S}\operatorname{P}_{fin}(\mathbf{A}(\mathbb{R}))$,
the set of all subalgebras of finite powers of $\mathbf{A}(\mathbb{R})$.

The reason this Galois connection is useful is due to the following
fact that Peter Jeavons first observed in the late
1990's (see [[J](@bibliography)]):

**Theorem.** If $\langle X, \Gamma \rangle$ is a finite relational structure and if $\Gamma'\subseteq \operatorname{Inv}(\operatorname{Fix}(\Gamma))$ is finite, then $\operatorname{CSP}\langle X, \Gamma'\rangle$ is reducible in polynomial time to $\operatorname{CSP}\langle X, \Gamma \rangle$.

In particular, the tractability of a CSP depends only on its associated algebra $\mathbf{A}(\mathbb{R}) := \langle X, \operatorname{Fix}(\Gamma)\rangle$.

-------------

## The main problem

What has become known as the **CSP-dichotomy conjecture** now
boils down to the following (quoted terms are defined below):

**Conjecture:** The CSP associated with a finite idempotent algebra $\mathbf A$ is tractable iff $\mathbf A$ has a "Taylor" (or "WNU," or "cyclic," or "Siggers") term operation.

Let $\mathbf A$ be a finite idempotent algebra and let $V(\mathbf A)$ denote the variety generated by $\mathbf A$.  Then, the following are equivalent:
   
   + The TCT type set of V(**A**) omits type 1.
   + $V(\mathbf A)$ has a Taylor term.
   + $V(\mathbf A)$ has a WNU term.
   + $V(\mathbf A)$ has a cyclic term.
   + $V(\mathbf A)$ has a 4-place Siggers term.
   + No "divisor" of $\mathbf A$ is a two element algebra with only the trivial (projection) operations.

   It is known that if a CSP is tractable, then the associated algebra $\mathbf A$ must satisfy the equivalent conditions above.  (See the section
   **Tractable only if Taylor term** below.)  The converse is open.  That is,
   it is not known whether each of the equivalent conditions above is
   sufficient to prove tractability of the associated CSP. 

--------------------------------

## Taylor terms

   Walter Taylor proved in [[T](@bibliography)]
   that a variety V satisfies some nontrivial
   Malcev condition iff it satisfies the following one: for some $n$, V has an
   $n$-ary term $t$ such that, for all $i$ between 1 and $n$ there is
   an identity
   $$t(\ast, \cdots, \ast, x, \ast, \cdots, \ast) \approx t(\ast, \cdots, \ast, y, \ast, \cdots, \ast)$$
   true in V where different variables $x\neq y$ appear in the
   $i$-th position on either side of the identity.  (Such a term $t$ is called a
   "Taylor term".) 

--------------------------------

### Taylor term iff no Type 1

   Hobby and McKenzie proved in [[HM](@bibliography)] that
   a finite algebra **A** has a Taylor term iff **1** does not belong to the
   set of TCT-types of $V(\mathbf A)$. (We say $V(\mathbf A)$ "omits type 1" in this case.)

-----------------------------

### No Type 1 iff no trivial divisors

   Freese and Valeriote proved in [[FV](@bibliography)]
   that, for a finite idempotent algebra $\mathbf A$,
   $V(\mathbf A)$ omits type 1 iff $\mathbf A$ has no "trivial divisors."
   Stated more precisely, in the contrapositive,

*The TCT-type set of $V(\mathbf A)$ contains 1 iff there is a subalgebra $\mathbf B$ of $\mathbf A$, and a congruence $\eta$, such that $\mathbf{B}/\eta$
is a two element algebra with only the trivial projection operations. (That is, $\mathbf B/\eta$ is a "trivial divisor" of $\mathbf A$.) *

------------------------------

### Tractable only if Taylor term

   If the algebra **B**, consisting of
   the set $\\{0, 1\\}$ along with trivial projection operations, occurs in the
   variety V(**A**), then the associated 
   $\operatorname{CSP}(\langle A, \operatorname{Inv}(\mathbf{A})\rangle)$
   is NP-complete.
  
   To see this, note that the problem $\operatorname{CSP}(\mathbb{S})$ for the
   relational structure $\mathbb{S} = \langle \\{0, 1\\}, T\rangle$, where
   $T = \\{0, 1\\}^3 - \\{(0,0,0), (1,1,1)\\}$,
   is NP-complete, and
   $\operatorname{CSP}(\mathbb{S})\leq \operatorname{CSP}(\langle A,
   \operatorname{Inv}(\mathbf{A})\rangle)$.

It follows that

*Tractability of $\operatorname{CSP}(\langle A, \operatorname{Inv}(\mathbf{A})\rangle)$ implies $V(\mathbf A)$ has a Taylor term operation.

   <!--$$T = \\{(0, 0, 1), (0,1,0), (0,1,1),  (1,0,0), (1, 0, 1), (1,1,0)\\}$$-->


-----------------------------------------

### Taylor term iff WNU term

   Maroti and McKenzie proved in [[MM](@bibliography)] that a
   finite idempotent algebra has a Taylor term iff it has a weak near-unanimity
   (WNU) term operation, that is, an idempotent term $w(x\_1, \dots, x\_k)$ such
   that
   $$w(y,x,\dots,x) \approx w(x,y,x,\dots,x) \approx \cdots \approx w(x,\dots,x,y).$$

--------------------------------

### Taylor term iff Cyclic term

   Barto and Kozik proved in [[BK](@bibliography)] that a finite
   idempotent algebra has a WNU term iff it has a special type of WNU term
   called a cyclic term. A cyclic term is a term $c(x\_1, \dots, x\_k)$ that
   satisfies
   $$c(x_1, x_2, x_3, \dots, x_k)\approx c(x_2, x_3, x_4, \dots, x_1)$$

   Note that the above term conditions place no bounds on the value of $k$, that
   is, the arity of the term operations involved in the given identities.

--------------------------------

### Taylor term iff Siggers term

   Siggers proved in [[S](@bibliography)] that the above term
   conditions are equivalent to one involving a term of bounded arity--namely, a
   six-place term operation. Kearnes, Markovic, and McKenzie in
   [[KMM](@bibliography)] improved this to a 4-place term $t(x\_1,x\_2,x\_3,x\_4)$
   satisfying $t(x,y,x,z)\approx t(y,x,z,y)$. 
   
--------------------------------

--------------------------------

## Bibliography

- [J] Jeavons, Peter, 
  [On the algebraic structure of combinatorial problems](Jeavons-AlgStructCombProbs-TCS-1998.pdf) Theoretical Computer Science **200** (1998).

- [T] Taylor, *Varieties obeying homotopy laws.* Canad. J. Math. **29** (1977).

- [HM] Hobby and McKenzie, *The structure of finite algebras.* 
  Contemporary Mathematics, AMS **76** (1988).

- [FV] Freese and Valeriote, [On the complexity of some Maltsev conditions.](http://www.math.hawaii.edu/~ralph/Preprints/IJAC_1901_P41.pdf) Internat. J. Algebra Comput. **19** (2009).

- [MM] Maroti and McKenzie, [Existence theorems for weakly symmetric operations.](MarotiMcKenzie-ExistenceTheorems-AU59-2008.pdf) 
Algebra Universalis **59** (2008).

- [BK] Barto and Kozik, [Absorbing subalgebras, cyclic terms, and the
constraint satisfaction problem.](BartoKozik-AbsorbingSubalgebras-LMCS-2012.pdf)
Log. Methods Comput. Sci. **8** (2012).

- [S] Siggers, [A strong Malcev condition for locally finite varieties omitting the unary type.](Siggers-StrongMalcevCondition-AU-2010.pdf) Algebra Universalis **64** (2010).

- [KMM] Kearnes, Markovic, and McKenzie, 
[Optimal strong Mal'cev conditions for omitting type 1 in locally finite varieties.](KearnesMarkovicMcKenzie-OptimalMalcevForNoType1-AU-2014.pdf) Algebra Universalis **72** (2014).


