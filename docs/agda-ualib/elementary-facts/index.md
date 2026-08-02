---
title: Some elementary facts
date: '2019-02-11'
---

--8<-- "archived.md"

$\def\inj{\mathrm{in}}$ 
$\def\inji{\mathrm{in}_i}$

## Notation

The symbols $\mathbb{N}$, $\omega$, and `nat` are used interchangeably; they all denote the set of natural numbers.

If $m$ is a natural number, we write $m \colon \mathbb N$ and say "$m$ has type $\mathbb N$." (For the reader unfamiliar with type theory, it's safe in the beginning to think of this as meaning $m\in \mathbb N$.)  

For $m \colon \mathbb N$, we denote and define $\underline{m} = \{0, 1, \dots, m-1\}$. Let $a = (a_0, a_1, \dots, a_{m-1})$ be an mtuple of elements from $A$. 

(As explained in the post on composition of operations, the tuple $a$ may be identified with a function of type $\underline{m} \to A$, where $a(i) = a_i$, for each $i<m$.)

If $h \colon A \to A$, then $h\circ a : \underline{m} \to A$ is the function whose $i$-th coordinate is $(h\circ a)(i) = h(a(i)) = h(a_i)$, and we may formally identify the function $h \circ a : \underline{m} \to A$ with its "image tuple" $(h(a_0), h(a_1), \dots, h(a_{m-1}))$.

A **signature** $S = (F, \rho)$ consists of a set $F$ of operation symbols and a function $\rho \colon F \to \mathbb{N}$. We call $\rho f$ the **arity** of the symbol $f$.

If $A$ is a set and $f$ is a $\rho f$-ary operation on $A$, then we may write $f \colon A^{\rho f} \to A$. On the other hand, as the natural number $\rho f$ denotes the set $\{0, 1, \dots, \rho f -1\}$, a function $a \colon \rho f \to A$ can be identified with its graph, which is simply a $\rho f$-tuple of elements from $A$; that is, $a i : A$, for each $i: \rho f$. Then, by identifying the $\rho f$-th power $A^{\rho f}$ with the type $\rho f \to A$ of functions from $\{0, 1, \dots, \rho f -1\}$ to $A$, we thus identify the function type $A^{\rho f} \to A$ with the type $(\rho f \to A) \to A$.

**Examples.**\
a. If $g \colon (\underline{m} \to A) \to A$ is an $\underline{m}$-ary operation on $A$ and if $a : \underline{m} \to A$, then $g a = g(a_0, a_1, \dots, a_{m-1})$ has type $A$.\
b. If $f \colon (\rho f \to B) \to B$ is a $\rho f$-ary operation on $B$, if $a \colon \rho f \to A$ is a $\rho f$-tuple on $A$, and if $h \colon A \to B$, then $h \circ a \colon \rho f \to B$, so $f (h \circ a)$ has type $B$.

## Elementary facts
Let $F$ be an endofunctor on Set and let $(A, f^A)$ and $(B, f^B)$ be $F$-algebras each with $m$ operation symbols. Let $k_i$ be the arity of the $i$-th operation symbol. Then $F A : \coprod_{i=0}^{m-1}(\underline{k_i} \to A)$. (See the F-algebras post.)

Let $g$ and $h$ be homomorphisms from $(A, f^A)$ to $(B, f^B)$. That is, $g \circ f^A = f^B \circ F g$ (similarly with $h$ in place of $g$). 

Define the **equalizer** of $g$ and $h$ as follows: $E(g,h) = \{ a : A \mid g(a) = h(a) \}$.

<!-- \[ex:1.16.6\]  -->

**Fact 1.** $E(g,h)$ is a subuniverse of $(A, f^A)$.

**Proof.** Fix arbitrary $0\leq i< m$ and $a : \underline{k_i} \to E(g,h)$. We wish to show that $g (f^A (\inji a)) = h (f^A (\inji a))$, as this will show that $E(g,h)$ is closed under the $i$-th operation of $(A, f^A)$. But this is trivial since, by definition of an $F$-algebra homomorphism, we have $$(g \circ f^A)(\inji a) = (f^B \circ F g)(\inji a) = (f^B \circ F h)(\inji a) = (h \circ f^A)(\inji a).$$

**Fact 2.** If $X \subseteq A$ and $X$ generates $(A, f^A)$ and $g|_X= h|_X$, then $g = h$.

**Proof.** Suppose the subset $X \subseteq A$ generates $(A, f^A)$ and suppose $g|_X = h|_X$. Fix an arbitrary $a : A$. We show $g(a) = h(a)$. 

Since $X$ generates $(A, f^A)$, there exists a term $t$ and a tuple $x : \rho t \to X$ of generators such that $a = t^A x$. Therefore, since $F g = F h$ on $X$, we have $$g(a) = g(t^A x) = (t^B \circ F g)(x) = (t^B \circ F h)(x) = h(t^A x) = h(a).$$

**Fact 3.** If $A$ and $B$ are finite sets and $X$ generates $(A, f^A)$, then $|\mathrm{Hom}((A, f^A),(B, f^B))| \leq |B|^{|X|}$.

**Proof.** By Fact 2, a homomorphism is uniquely determined by its restriction to a generating set. If $X$ generates $(A, f^A)$, then since there are exactly $|B|^{|X|}$ functions from $X$ to $B$ we have $|\mathrm{Hom}((A, f^A),(B, f^B))| \leq |B|^{|X|}$.

**Fact 4.** Suppose $g$ and $h$ are homomorphisms from $(A, f^A)$ to $(B, f^B)$ and from $(A, f^A)$ to $(C,f^C)$, respectively. Assume $g$ is surjective, and $\ker g \subseteq \ker h$. Then there exists a homomorphism $k : (B, f^B)\to (C, f^C)$ such that $h = k \circ g$. <!-- \[ex:1.26.8\]  -->

**Proof.** We define $k : (B, f^B)\to (C, f^C)$ constructively, as follows:

Fix $b\colon B$.  Since $g$ is surjective, the set $g^{-1}\{b\} \subseteq A$ is nonempty, and since $\ker g \subseteq \ker h$, we see that every element of $g^{-1}\{b\}$ is mapped by $h$ to a single element of $C$. Label this element $c_b$. That is, $h(a) = c_b$, for all $a : g^{-1}\{b\}$.  We define $k(b) = c_b$. Since $b$ was arbitrary, $k$ is defined on all of $B$ in this way.

Now it's easy to see that $k g = h$ by construction.  Indeed, for each $a \in A$, we have $a \in g^{-1}\{g(a)\}$, so $k(g(a)) = h(a)$ by definition.

To see that $k$ is a homomorphism, let there be $m$ operation symbols and let $0\leq i< m$ be arbitrary. Fix $b \colon \underline{k_i} \to B$. Since $g$ is surjective, for each $i \colon \underline{k_i}$, the subset $g^{-1}\{b(i)\}\subseteq A$ is nonempty and is mapped by $h$ to a single point of $C$ (since $\ker g \subseteq \ker h$). Label this point $c_i$ and define $c \colon \underline{k_i} \to C$ by $c(i) = c_i$.

We want to show $(f^C \circ F k) (b) = (k \circ f^B)(b).$  The left hand side is $f^C c$, which is equal to $(h \circ f^A)(a)$ for some $a\colon \underline{k_i} \to A$, since $h$ is a homomorphism.  Therefore, $$(f^C \circ F k) (b) = (h \circ f^A) (a) = (k \circ g \circ f^A)(a) = (k \circ f^B \circ F g)(a) = (k \circ f^B)(b).$$

