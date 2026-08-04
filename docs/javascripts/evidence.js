/* Count-up for the evidence strip (M3-2c, #95).
 *
 * The final numbers are already in the HTML -- the hook renders them, so a
 * crawler, a JS-off reader and a reduced-motion reader all see the truth with
 * this file doing nothing.  What this adds, when motion is allowed, is the
 * arrival: each figure counts up from zero the first time it scrolls into
 * view (ADR-009: the animation is a way of arriving at a real value, never
 * the only carrier of it).
 *
 * The duration is a token, not a constant: ADR-009 keeps every animation
 * timing in tokens.css, and this script reads --motion-count from the
 * rendered page so the CSS remains the one place timing is decided.
 *
 * The `document$` subscription mirrors katex-init.js, and for the same
 * reason: `navigation.instant` swaps content without a reload, and a
 * one-shot listener would leave the strip static on every visit after the
 * first.  Re-running is safe -- each fresh DOM starts unanimated, and the
 * `data-done` guard stops a second pass within one page's lifetime.
 */
function animateEvidence() {
  var nodes = document.querySelectorAll(".evidence .ev-n[data-n]");
  if (!nodes.length) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  if (!("IntersectionObserver" in window)) return;

  var raw = getComputedStyle(document.body).getPropertyValue("--motion-count");
  var duration = parseFloat(raw) * (raw.trim().endsWith("ms") ? 1 : 1000) || 900;

  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        var el = entry.target;
        if (el.dataset.done) return;
        el.dataset.done = "1";
        var target = parseInt(el.dataset.n, 10);
        var start = null;
        function step(now) {
          if (start === null) start = now;
          var p = Math.min((now - start) / duration, 1);
          var eased = 1 - Math.pow(1 - p, 3);
          el.textContent = Math.round(target * eased).toLocaleString("en");
          if (p < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
      });
    },
    { threshold: 0.4 }
  );
  nodes.forEach(function (node) {
    observer.observe(node);
  });
}

if (typeof document$ !== "undefined") {
  document$.subscribe(animateEvidence);
} else {
  document.addEventListener("DOMContentLoaded", animateEvidence);
}
