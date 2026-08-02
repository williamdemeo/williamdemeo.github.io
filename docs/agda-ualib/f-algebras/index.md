---
title: F-Algebras
date: '2019-02-09'
---

--8<-- "archived.md"
<!-- zola-banner: falgebras -->

Let $\mathrm{F}$ be an endofunctor on the category Set. We define an **F-algebra** to be a pair $(A, f)$ where $f \colon \mathbf{F} A \to A$.  
$\newcommand\FGrp{\mathbf{F}_{\mathbf{Grp}}} \newcommand\inj{\mathrm{in}}$
## Example: Group
A **group** is an $\FGrp$-algebra where $\FGrp A = 1 + A + A \times A$.  

To see how to interpret the standard definition of a group, $(A, e, ^{-1}, \circ)$, in this language, observe that an element of the coproduct $\FGrp A$ has one of three forms,

+ $\mathrm{in}_0 1 : 1$, the identity element of the group;
+ $\mathrm{in}_1 x : A$, an arbitrary element of the group's universe;
+ $\mathrm{in}_2 (x, y) : A\times A$, an arbitrary pair of elements of the group's universe.

We define the group operations $f \colon \mathbf{F} A \to A$ by pattern matching as follows:

+ $f\ \mathrm{in}_0 1 = e$, the identity element of the group;
+ $f\ \mathrm{in}_1 x = x^{-1}$, the group's inverse operation;
+ $f\ \mathrm{in}_2 (x,y) = x\circ y$, the group's binary operation.

For example, in [Lean](https://leanprover.github.io/) the implementation would look something like this:

```hs
    def f : 1 + ℕ + (ℕ × ℕ) → ℕ
    | in₀ 1   := e
    | in₁ x   := x⁻¹
    | in₂ x y := x ∘ y
```

## Homomorphisms

Let $(A, f)$ and $(B, g)$ be two groups (i.e., $\FGrp$-algebras).  

A **homomorphism** from $(A, f)$ to $(B, g)$, denoted by $h\colon (A, f)\to (B, g)$, is a function from $A$ to $B$ that satisfies the identity $$h \circ f = g \circ \FGrp h$$

To make sense of this identity, we must know how the functor $\FGrp$ acts on arrows (i.e., homomorphisms, like $h$).  It does so as follows:

+ $(\operatorname{F}_{\mathbf{Grp}} h) (\mathrm{in}_0 1) = h(e)$;
+ $(\operatorname{F}_{\mathbf{Grp}} h) (\mathrm{in}_1 x) = (h(x))^{-1}$;
+ $(\operatorname{F}_{\mathbf{Grp}} h) (\mathrm{in}_2 (x,y)) = h(x)\circ h(y)$.

Equivalently, 

+ $h \circ f (\inj_0 1) = h (e)$ and $g \circ \FGrp h (\inj_0 1) = g (h(e))$;
+ $h \circ f (\inj_1 x) = h (x^{-1})$ and $g \circ \FGrp h (\inj_1 x) = g (\inj_1 h(x)) = (h(x))^{-1}$;
+ $h \circ f (\inj_2 (x,y)) = h (x \circ y)$ and $g \circ \FGrp h (\inj_2 (x,y)) = g (\inj_2 (h(x),h(y))) = h(x)\circ h(y)$.

So, in this case, the indentity $h \circ f = g \circ \FGrp h$ reduces to

+ $h (e^A) = g (h(e))$;
+ $h (x^{-1_A}) = (h(x))^{-1_B}$;
+ $h (x \circ^{A} y)= h(x)\circ^{B} h(y)$,

which are precisely the conditions we would normally verify when checking that $h$ is a group homomorphism.

