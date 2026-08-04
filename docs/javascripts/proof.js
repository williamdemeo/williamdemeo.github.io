/* Typed replay for the proof terminal (M3-2d, #96).
 *
 * The completed session is already in the HTML -- proof_hook.py renders it,
 * so a crawler, a JS-off reader and a reduced-motion reader all see the
 * finished proof with this file doing nothing.  What this adds, when motion
 * is allowed, is the arrival: the first time a terminal scrolls into view it
 * rewinds and types the session back in -- the lines, the hole, the recorded
 * goal in the HUD, the fill, the goal count falling to zero -- and then the
 * ✓ line appears rather than types, because the visitor typed the code and
 * the compiler answers in whole lines.  It runs once; the replay button is
 * the only way to see it again (ADR-009: never loops unprompted), and the
 * button ships hidden so that without this script there is no dead control.
 *
 * Timing comes from the --motion-* tokens, read from computed style the way
 * evidence.js reads --motion-count, so tokens.css remains the one place
 * timing is decided.  Text is iterated by code point (Array.from), never
 * charAt: the vignette contains astral glyphs like 𝑻 and 𝑨, and slicing a
 * surrogate pair would flash garbage mid-word.  Colour arrives per line,
 * after the line finishes typing, by restoring the hook's markup -- this
 * file invents no output and colours no token itself.
 *
 * The `document$` subscription mirrors evidence.js, for the same reason:
 * navigation.instant swaps content without a reload.  Each fresh DOM ships
 * finished, and the data-armed guard keeps one page to one observer.
 */
function proofReplay() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  if (!("IntersectionObserver" in window)) return;

  var style = getComputedStyle(document.body);
  function ms(name, fallback) {
    var raw = style.getPropertyValue(name).trim();
    var n = parseFloat(raw);
    // NaN means the token is absent; 0 is a value someone may set on
    // purpose, and an instant type-in is still an honest replay.
    if (Number.isNaN(n)) return fallback;
    return raw.endsWith("ms") ? n : n * 1000;
  }
  var TYPE = ms("--motion-type", 24);
  var GOAL = ms("--motion-goal-beat", 900);
  var CHECK = ms("--motion-check-beat", 350);

  function wait(t) { return new Promise(function (r) { setTimeout(r, t); }); }

  document.querySelectorAll(".proof").forEach(function (term) {
    if (term.dataset.armed) return;
    term.dataset.armed = "1";

    var lines = [].slice.call(term.querySelectorAll(".proof-line")).map(
      function (el) {
        return { el: el, html: el.innerHTML, text: el.textContent };
      });
    function role(name) {
      return lines.filter(function (l) {
        return l.el.classList.contains(name);
      })[0];
    }
    var hole = role("proof-hole-line");
    var fill = role("proof-fill-line");
    var check = role("proof-check");
    var hud = term.querySelector(".proof-hud");
    var pill = term.querySelector(".proof-goals");
    var button = term.querySelector(".proof-replay");
    if (!hole || !fill || !check || !hud || !pill || !button) return;
    var open = parseInt(term.dataset.goalsOpen, 10) || 1;
    var rest = { hud: hud.textContent, goal: hud.getAttribute("data-goal") };
    var run = 0;

    function goals(n) {
      pill.textContent = n + (n === 1 ? " goal" : " goals");
      pill.classList.toggle("proof-goals-zero", n === 0);
    }

    function play() {
      var mine = ++run;
      function live() { return run === mine; }
      function step(fn) { return function () { if (live()) return fn(); }; }

      function type(line) {
        var glyphs = Array.from(line.text);
        line.el.classList.add("proof-typing");
        return new Promise(function (resolve) {
          var i = 1;
          (function tick() {
            if (!live()) { resolve(); return; }
            line.el.textContent = glyphs.slice(0, i).join("");
            if (i < glyphs.length) {
              i += 1;
              setTimeout(tick, TYPE * (0.6 + 0.8 * Math.random()));
            } else {
              line.el.classList.remove("proof-typing");
              line.el.innerHTML = line.html;
              resolve();
            }
          })();
        });
      }

      io.disconnect();
      lines.forEach(function (l) {
        l.el.textContent = "";
        l.el.classList.remove("proof-typing");
        l.el.hidden = l === fill;
      });
      hud.textContent = "";
      pill.textContent = "";
      pill.classList.remove("proof-goals-zero");

      var p = wait(CHECK);
      lines.forEach(function (line) {
        if (line === fill || line === check) return;
        if (line === hole) {
          p = p.then(step(function () { return type(hole); }))
            .then(step(function () {
              goals(open);
              hud.textContent = rest.goal;
              return wait(GOAL);
            }))
            .then(step(function () {
              hole.el.hidden = true;
              fill.el.hidden = false;
              return type(fill);
            }))
            .then(step(function () {
              goals(0);
              hud.textContent = rest.hud;
              return wait(CHECK);
            }));
        } else {
          p = p.then(step(function () { return type(line); }));
        }
      });
      p.then(step(function () { check.el.innerHTML = check.html; }));
    }

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) play();
      });
    }, { threshold: 0.35 });
    io.observe(term);
    button.hidden = false;
    button.addEventListener("click", play);
  });
}

if (typeof document$ !== "undefined") {
  document$.subscribe(proofReplay);
} else {
  document.addEventListener("DOMContentLoaded", proofReplay);
}
