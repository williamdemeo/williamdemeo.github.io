---
title: Rendering test
description: >-
  Internal regression page for mathematics and code rendering. Not part of the
  site's navigation.
search:
  exclude: true
---

# Rendering test

Internal page. It exists so that a change to the KaTeX configuration, the macro
table, or the syntax-highlighting setup shows up as a visible regression on one
page rather than as a silent one across 44 exam solutions.

Not in the navigation, excluded from search. Reachable only by URL.

The authoritative check is `node scripts/python/audit_math.mjs`, which renders
every expression in a content tree headlessly and exits non-zero on failure.
This page is the visual counterpart.

## Mathematics

Inline: the ring $R$ acts on $M$ so that $\operatorname{ann}(x) = \{r \in R : rx = 0\}$,
and $\varphi\colon A \to B$ is a homomorphism.

Display:

$$
\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}
\qquad\text{and}\qquad
\int_{-\infty}^{\infty} e^{-x^2}\,dx = \sqrt{\pi}
$$

Delimiters are `$...$` and `$$...$$` in the source. `pymdownx.arithmatex`
rewrites them to `\(...\)` and `\[...\]`, which is what KaTeX matches on.

A bare dollar sign in prose must not trigger rendering: this costs $5, and
`echo $PATH` in code is untouched.

## Custom macros

These come from the imported qualifying-exam solutions, whose LaTeX was written
against a personal macro package that never made it to the web. Each row fails
to render — visibly, in red — if `katex-macros.js` regresses.

| Macro | Renders as |
| --- | --- |
| `\C`, `\R`, `\N`, `\Z`, `\F` | $\C$, $\R$, $\N$, $\Z$, $\F$ |
| `\UD`, `\UHP`, `\RHP` | $\UD$, $\UHP$, $\RHP$ |
| `\borel`, `\sigM`, `\sigA` | $\borel$, $\sigM$, $\sigA$ |
| `\sA`, `\sI`, `\sJ` | $\sA$, $\sI$, $\sJ$ |
| `\Hom`, `\HomR`, `\End`, `\Tor` | $\Hom$, $\HomR$, $\End$, $\Tor$ |
| `\ann`, `\im`, `\Real`, `\Imag` | $\ann$, $\im$, $\Real$, $\Imag$ |
| `\meet`, `\join`, `\dotcup` | $\meet$, $\join$, $\dotcup$ |
| `\limn` | $\limn a_n$ |
| `\vphi`, `\bphi`, `\one` | $\vphi$, $\bphi$, $\one$ |

In context, as they appear in the source:

$$
\UD = \{|z| < 1\}, \qquad
\UHP = \{z \in \C : \Imag z > 0\}, \qquad
\sigM \text{ a } \sigma\text{-algebra on } \R
$$

## Code

The Unicode question matters more here than the colours. Agda identifiers use
characters far outside ASCII, and a highlighter that mangles them or forces a
fallback font makes the library pages unreadable.

```agda
_∘_ : {A B C : Set} → (B → C) → (A → B) → (A → C)
(g ∘ f) x = g (f x)

record Algebra (𝓤 : Level) (𝑆 : Signature 𝓞 𝓥) : Set (𝓞 ⊔ 𝓥 ⊔ lsuc 𝓤) where
  field  Domain : Setoid 𝓤 𝓤
         Interp : ⟨ 𝑆 ⟩ (Carrier Domain) → Carrier Domain

∀-elim : ∀ {A : Set} {B : A → Set} → (∀ (x : A) → B x) → (M : A) → B M
∀-elim f M = f M
```

```lean
theorem birkhoff {α : Type*} [Lattice α] (a b c : α) :
    a ⊓ (b ⊔ c) = (a ⊓ b) ⊔ (a ⊓ c) ↔ IsDistribLattice α := by
  constructor <;> intro h <;> simp_all
```

```haskell
newtype Fix f = Fix { unFix :: f (Fix f) }

cata :: Functor f => (f a -> a) -> Fix f -> a
cata alg = alg . fmap (cata alg) . unFix
```

```python
def polymorphisms(algebra: Algebra, arity: int) -> Iterator[Operation]:
    """Enumerate the arity-n polymorphisms of a finite algebra."""
    yield from (op for op in candidates(arity) if preserves(op, algebra))
```

```nix
{
  devShells.default = pkgs.mkShell {
    packages = [ pkgs.python3 pkgs.cairo pkgs.pango ];
    SITE_NIX_SHELL = 1;
  };
}
```

Copy the Agda block and paste it somewhere: the round trip must preserve
`𝓤`, `𝑆`, `⊔`, `→`, and `⟨ ⟩` exactly.

## Known limitations

**`\xymatrix` does not render.** Five commutative diagrams in the ring-theory
solutions use XY-pic, which KaTeX has no equivalent for. They need converting to
Mermaid, KaTeX's `{CD}` environment, or images. Tracked as content work rather
than a rendering bug.

**Over-escaped braces.** Ninety expressions in the imported exam solutions write
`\\{` where they mean `\{`. Arithmatex passes the sequence through unchanged and
KaTeX reads `\\` as a line break. The fix is mechanical and belongs with the
exam-page migration.

**Redundant macro preambles.** Four imported pages open with a math block
containing nothing but definitions:

```
$\newcommand\FGrp{\mathbf{F}_{\mathbf{Grp}}} \newcommand\inj{\mathrm{in}}$
$\def\bA{\bf A} \def\bB{\bf B}$
```

Those definitions now live in `katex-macros.js`, which makes the preambles
redundant — and, for the `\newcommand` ones, harmful: KaTeX raises
*"attempting to redefine \FGrp; use \renewcommand"* rather than ignoring them.

The blocks should be deleted when those pages are triaged. Nothing published
is affected today, since the pages are still staged under `import/`; the
collision shows up only in `make math-audit`.
`agda-ualib/f-algebras.md`, `agda-ualib/elementary-facts.md`,
`agda-ualib/birkhoff-hsp.md`, and `2014-02-13-a-problem-of-palfy-and-saxl.md`.
