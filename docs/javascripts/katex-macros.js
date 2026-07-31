/* KaTeX macro definitions.
 *
 * The imported qualifying-exam solutions were written in LaTeX against a
 * personal macro package that was never carried onto the web.  Neither the
 * Zola site's MathJax nor its KaTeX ever defined these, so 259 expressions
 * across 44 pages have been rendering as errors on williamdemeo.org for years.
 * This table is what fixes them.
 *
 * Single source of truth: `scripts/python/audit_math.mjs` evaluates this same
 * file, so the audit and the site can never disagree about what is defined.
 *
 * Definitions marked INFERRED were reconstructed from usage context rather
 * than from an authoritative source, because the original .sty file is not in
 * either repository.  They render plausibly; whether each glyph is what the
 * author originally intended is a content question, not a rendering one.
 */
window.KATEX_MACROS = {
  // ── Number systems and standard sets ────────────────────────────────────
  "\\C": "\\mathbb{C}",
  "\\R": "\\mathbb{R}",
  "\\N": "\\mathbb{N}",
  "\\Z": "\\mathbb{Z}",
  "\\Q": "\\mathbb{Q}",
  "\\F": "\\mathbb{F}",

  // ── Complex analysis ────────────────────────────────────────────────────
  // INFERRED, but each is defined in the text where it first appears, e.g.
  // "\UD = \{|z|<1\}" and "\UHP = \{z : \mathrm{Im}\,z > 0\}".
  "\\UD": "\\mathbb{D}",
  "\\UHP": "\\mathbb{H}",
  "\\RHP": "\\mathbb{H}_{\\mathrm{r}}",
  "\\Real": "\\operatorname{Re}",
  "\\Imag": "\\operatorname{Im}",
  "\\FT": "\\mathcal{F}",           // INFERRED: a family, used as "\FT = \{f_n\}"

  // ── Measure theory ──────────────────────────────────────────────────────
  // \mathfrak{M} for a sigma-algebra follows Rudin, which is the convention
  // these real-analysis qualifying exams are written against.
  "\\borel": "\\mathcal{B}",
  "\\sigM": "\\mathfrak{M}",
  "\\sigN": "\\mathfrak{N}",
  "\\sigA": "\\mathfrak{A}",

  // ── Script letters ──────────────────────────────────────────────────────
  // The `s` prefix reads as "script" throughout the source.
  "\\sA": "\\mathcal{A}",
  "\\sI": "\\mathcal{I}",
  "\\sJ": "\\mathcal{J}",

  // ── Algebra ─────────────────────────────────────────────────────────────
  "\\Hom": "\\operatorname{Hom}",
  "\\HomR": "\\operatorname{Hom}_R",
  "\\End": "\\operatorname{End}",
  "\\Tor": "\\operatorname{Tor}",
  "\\ann": "\\operatorname{ann}",
  "\\im": "\\operatorname{im}",
  "\\one": "\\mathbf{1}",
  "\\0": "\\mathbf{0}",

  // ── Lattice and set operations ──────────────────────────────────────────
  "\\meet": "\\wedge",
  "\\join": "\\vee",
  "\\union": "\\cup",
  "\\intersect": "\\cap",
  "\\dotcup": "\\sqcup",

  // ── Limits ──────────────────────────────────────────────────────────────
  "\\limn": "\\lim_{n\\to\\infty}",
  "\\limit": "\\lim",

  // ── Greek variants ──────────────────────────────────────────────────────
  "\\vphi": "\\varphi",
  "\\bphi": "\\boldsymbol{\\varphi}",

  // ── Algebra posts and the agda-ualib notes ──────────────────────────────
  //
  // Unlike everything above, these are NOT inferred.  Those pages carry their
  // own preamble -- a math block containing nothing but definitions, e.g.
  //
  //     $\newcommand\FGrp{\mathbf{F}_{\mathbf{Grp}}} \newcommand\inj{\mathrm{in}}$
  //     $\def\bA{\bf A} \def\bB{\bf B}$
  //
  // and the definitions below are copied verbatim from them.
  //
  // That preamble worked under MathJax, which keeps \newcommand for the rest
  // of the page, and does not work under KaTeX, which scopes \def and
  // \newcommand to the single expression they appear in.  (Only \gdef
  // persists, and only when one macros object is shared across the page.)
  // So these pages rendered correctly on the old site and would silently
  // break on the new one -- the opposite of the exam solutions, which were
  // never defined anywhere and have been broken all along.
  //
  // Hoisting them here rather than rewriting the preambles to \gdef makes the
  // definitions greppable in one place and removes any dependence on the
  // preamble block appearing before its first use.  The preamble expressions
  // themselves are now redundant; they render as an empty span and can be
  // deleted when those pages are triaged.
  "\\FGrp": "\\mathbf{F}_{\\mathbf{Grp}}",
  "\\inj": "\\mathrm{in}",
  "\\inji": "\\mathrm{in}_i",
  // Source writes `\bf A`; `\mathbf{A}` is the modern spelling of the same
  // thing and does not leak a font switch into the surrounding expression.
  "\\bA": "\\mathbf{A}",
  "\\bB": "\\mathbf{B}",

  // ── LaTeX-only commands with no KaTeX equivalent ─────────────────────────
  // \ensuremath is a no-op here: KaTeX is always in math mode, so the wrapper
  // is redundant and the argument passes straight through.
  "\\ensuremath": "#1",
  "\\mbox": "\\text{#1}",
  // Cross-referencing and footnotes are document-level LaTeX.  Swallow the
  // argument and render nothing, so their presence does not break the
  // surrounding expression.
  "\\label": "",
  "\\footnote": "",
};
