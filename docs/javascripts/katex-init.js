/* KaTeX initialisation.
 *
 * pymdownx.arithmatex in generic mode rewrites `$...$` to `\(...\)` and
 * `$$...$$` to `\[...\]` before the HTML is emitted, so those are the only
 * delimiters KaTeX needs to look for -- the legacy dollar-sign syntax used
 * throughout the imported content is handled upstream.  That is also why
 * prose containing a bare `$` is safe: arithmatex decides what is math, not
 * this script.
 *
 * The subscription to `document$` rather than a DOMContentLoaded listener is
 * required: `navigation.instant` swaps page content without a reload, and a
 * one-shot listener would leave every subsequently-visited page unrendered.
 *
 * `document$` comes from Material's bundle, though, so it is not ours to
 * assume.  Referencing an undefined global throws a ReferenceError, which
 * would abort this script and every later one on the page -- turning "the
 * theme's JS did not load" into "nothing on the page works".  Falling back to
 * DOMContentLoaded degrades instead: math renders once, and instant
 * navigation stops re-rendering it, which is the correct trade when the
 * bundle providing instant navigation is the thing that is missing.  It also
 * makes a page opened straight from disk render, which is otherwise a
 * confusing way to lose an afternoon.
 */
function renderMath() {
  renderMathInElement(document.body, {
    delimiters: [
      { left: "\\(", right: "\\)", display: false },
      { left: "\\[", right: "\\]", display: true },
    ],
    macros: window.KATEX_MACROS || {},
    // Render errors in place rather than throwing, so one bad expression on a
    // page cannot blank the rest of it.  The audit script is where errors are
    // meant to be caught; this is the runtime safety net.
    throwOnError: false,
    // A token, not a constant: KaTeX writes this straight into an inline
    // `style="color:..."`, and custom properties resolve there, so one value
    // covers both themes.  Its default #cc0000 is legible on paper and 3.0:1
    // on the dark page.  See tokens.css.
    errorColor: "var(--c-error)",
    // The imported content predates any house style and uses constructs KaTeX
    // warns about; the warnings are noise in the browser console.
    strict: false,
    trust: false,
  });
}

if (typeof document$ !== "undefined") {
  document$.subscribe(renderMath);
} else {
  document.addEventListener("DOMContentLoaded", renderMath);
}
