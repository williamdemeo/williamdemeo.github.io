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
 */
document$.subscribe(() => {
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
    errorColor: "#cc0000",
    // The imported content predates any house style and uses constructs KaTeX
    // warns about; the warnings are noise in the browser console.
    strict: false,
    trust: false,
  });
});
