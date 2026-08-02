---
title: Diaconescu's Theorem
slug: diaconescus-theorem
date: 2014-02-05
categories:
  - Mathematics
  - Formal verification
tags:
  - constructive mathematics
  - axiom of choice
  - Coq
description: >-
  Notes on Andrej Bauer's presentation of the proof that the axiom of choice
  implies the law of the excluded middle.
---

I learned about
[Diaconescu's Theorem](http://en.wikipedia.org/wiki/Diaconescu%27s_theorem)
from [Andrej Bauer's lecture](http://video.ias.edu/members/1213/0318-AndrejBauer).

This post describes the proof as it was presented by Bauer.  These notes are rough
and intended for my own reference.
Please see [Fran&#231;ois Dorais' blog post](http://dorais.org/archives/1031)
for a nice discussion of this topic.

<!-- more -->

--8<-- "dated.md"

--------------------------------------------------------------------------

+ **The Axiom of Choice** (AC) states that if $\mathcal{S}$ is a collection of nonempty
  sets, then there is a choice function $f$ that can be used to select an element
  from each set in $\mathcal{S}$.

+ **Law of the Excluded Middle** (LEM) asserts the following: if $P$ is a proposition, then $P \bigvee \neg P$.

+ **Diaconescu's Theorem:** AC $\rightarrow$ LEM.

  **Proof:**  Assume AC.  Let $P$ be any proposition.  We will prove
  $P \bigvee \neg P$.

  Define the set $\mathbf{2} = \\{0, 1\\} = \\{x \mid x = 0 \bigvee x= 1\\}$.

  Define the following sets:

  $A = \\{x \mid (x = 0) \bigvee P\\}$

  $B = \\{y \mid (y = 1) \bigvee P\\}$

  Note that $P \Rightarrow A = B = \mathbf{2}$. Therefore,
  $A \neq B \Rightarrow \neg P$.

  Both of the sets $A$ and $B$ are nonempty, since 0 belongs to $A$ and 1 belongs to $B$.

  Therefore, $\\{A, B\\}$ is a set of nonempty sets, so by AC we have a choice function,
  <!-- Note that the set $\\{A, B\\}$ is defined as $\\{A, B\\} = \\{X \in
  \mathbf{Set} | X = A \bigvee X = B\\}$ (by pairing axiom).-->

  $$f : \\{A, B\\} \rightarrow A \cup B, \text{ and note that } A\cup B = \\{0, 1\\}.$$

  Now, because equality on $\mathbb{N}$ *is* decidabile (which can be proved
  by induction on $\mathbb{N}$), we can consider cases:

  If $f(A) = 0 = f(B)$, then $0 \in B$, so $P$.

  If $f(A) = 1 = f(B)$, then $1 \in A$, so $P$.

  If $f(A) \neq f(B)$, then $A \neq B$ so $P$ cannot hold.
  (Recall, $P \Rightarrow A = B = \mathbf{2}$.)

  We have covered all cases and found that $P \bigvee \neg P$ holds.
  <span style="float:right">&#x220E;</span>

-------------------------------------------------------

## Coq

[Proofs of Diaconescu's Theorem in Coq](http://coq.inria.fr/V8.1/stdlib/Coq.Logic.Diaconescu.html)

-------------------------------------------------------

## Appendix

+ **Decidable Sets.**
  A set $S$ is **decidable** if for all $x, y \in S$ we have
  $x = y \bigvee x \neq y$. The empty set and singleton sets are trivially
  decidable, but some more complicated sets are decidable too. For example, one
  can use induction to show that the set of natural numbers is decidable.

------------------------------------------------------

## References

+ Diaconescu, "Axiom of choice and complementation," *Proc. AMS* 51 (1975), 176–178. [doi:10.1090/S0002-9939-1975-0373893-X](http://dx.doi.org/10.1090/S0002-9939-1975-0373893-X)
