/* Typed replay for the proof terminal (M3-2d, #96).
 *
 * The completed sessions are already in the HTML -- proof_hook.py renders
 * them, one tabpanel per lemma -- so a crawler, a JS-off reader and a
 * reduced-motion reader all see a finished proof with this file doing
 * nothing.  What this adds is in two layers.  The tabs: switching lemmas is
 * navigation, not motion, so the tab bar is revealed and wired wherever
 * this script runs at all -- a reduced-motion reader gets five finished
 * proofs, switched instantly.  The replay, only where motion is allowed:
 * after the frame's CSS entrance (tokens.css delays it so the hero's words
 * land first), the first time a panel is shown it rewinds and types its
 * session back in -- the lines, the hole, the recorded goal in the HUD,
 * then the fill typed *inside* the hole's brackets the way an editor
 * session runs, the brackets vanishing at the give, the goal count falling
 * to zero -- and the ✓ line appears rather than types, because the visitor
 * typed the code and the compiler answers in whole lines.  The five
 * sessions run once, as one performance: the first on scroll into view,
 * then each next tab taking the stage after a held beat
 * (--motion-tab-dwell), halting on the last -- a linear run, no loop, so
 * ADR-009's "never loops unprompted" holds.  Any gesture -- choosing a
 * tab, pressing ↻ -- takes the wheel and stops the auto-advance; from then
 * on a panel replays only when chosen, and the replay button is the only
 * way to see one again.  Tablist and buttons ship hidden so that without
 * this script there is no dead control.
 *
 * Timing comes from the --motion-* tokens, read from computed style the way
 * evidence.js reads --motion-count, so tokens.css remains the one place
 * timing is decided.  Text is iterated by code point (Array.from), never
 * charAt: the vignettes contain astral glyphs like 𝑻 and 𝑨, and slicing a
 * surrogate pair would flash garbage mid-word.  Colour arrives per line,
 * after the line finishes typing, by restoring the hook's markup -- this
 * file invents no output and colours no token itself.
 *
 * The `document$` subscription mirrors evidence.js, for the same reason:
 * navigation.instant swaps content without a reload.  Each fresh DOM ships
 * finished, and the data-armed guard keeps one page to one observer.
 */
function proofReplay() {
  var reduced =
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var canReplay = !reduced && "IntersectionObserver" in window;

  var style = getComputedStyle(document.body);
  function ms(name, fallback) {
    var raw = style.getPropertyValue(name).trim();
    var n = parseFloat(raw);
    // NaN means the token is absent; 0 is a value someone may set on
    // purpose, and an instant type-in is still an honest replay.
    if (Number.isNaN(n)) return fallback;
    return raw.endsWith("ms") ? n : n * 1000;
  }
  var TYPE = ms("--motion-type", 32);
  var GOAL = ms("--motion-goal-beat", 1200);
  var CHECK = ms("--motion-check-beat", 500);
  var ENTER = ms("--motion-hero-enter", 3500);
  var DWELL = ms("--motion-tab-dwell", 3000);

  function wait(t) { return new Promise(function (r) { setTimeout(r, t); }); }

  document.querySelectorAll(".proof").forEach(function (term) {
    if (term.dataset.armed) return;
    term.dataset.armed = "1";

    // One state object per tabpanel; null if the markup breaks the
    // contract, in which case the whole terminal is left at rest.
    function build(el) {
      var lines = [].slice.call(el.querySelectorAll(".proof-line")).map(
        function (l) {
          return { el: l, html: l.innerHTML, text: l.textContent };
        });
      function role(name) {
        return lines.filter(function (l) {
          return l.el.classList.contains(name);
        })[0];
      }
      var p = {
        el: el,
        lines: lines,
        hole: role("proof-hole-line"),
        fill: role("proof-fill-line"),
        check: role("proof-check"),
        hud: el.querySelector(".proof-hud"),
        pill: el.querySelector(".proof-goals"),
        button: el.querySelector(".proof-replay"),
        open: parseInt(el.dataset.goalsOpen, 10) || 1,
        played: false,
        run: 0,
      };
      if (!p.hole || !p.fill || !p.check || !p.hud || !p.pill || !p.button)
        return null;
      p.rest = { hud: p.hud.textContent,
                 goal: p.hud.getAttribute("data-goal") };
      return p;
    }

    var tablist = term.querySelector(".proof-tabs");
    var tabs = [].slice.call(term.querySelectorAll(".proof-tab"));
    var panels = [].slice.call(term.querySelectorAll(".proof-panel"))
      .map(build);
    if (!panels.length || panels.indexOf(null) !== -1) return;
    var active = 0;
    // True until the visitor's first gesture: while it holds, the finished
    // panels hand the stage to the next tab on their own.
    var auto = true;

    function goals(p, n) {
      p.pill.textContent = n + (n === 1 ? " goal" : " goals");
      p.pill.classList.toggle("proof-goals-zero", n === 0);
    }

    // A panel's final state, as the hook shipped it: used when a tab switch
    // interrupts a replay, so the abandoned panel is a finished proof the
    // next time it is shown, never a half-typed one.
    function settle(p) {
      p.run += 1;
      p.lines.forEach(function (l) {
        l.el.innerHTML = l.html;
        l.el.classList.remove("proof-typing");
        l.el.hidden = l === p.hole;
      });
      p.hud.textContent = p.rest.hud;
      goals(p, 0);
    }

    function play(p) {
      var mine = ++p.run;
      p.played = true;
      function live() { return p.run === mine; }
      function step(fn) { return function () { if (live()) return fn(); }; }

      // Type plain text into an element, one code point per beat, jittered
      // +-40% so the rhythm reads as hands; the caret rides along.
      function typeInto(el, glyphs, done) {
        el.classList.add("proof-typing");
        return new Promise(function (resolve) {
          var i = 1;
          (function tick() {
            if (!live()) { resolve(); return; }
            el.textContent = glyphs.slice(0, i).join("");
            if (i < glyphs.length) {
              i += 1;
              setTimeout(tick, TYPE * (0.6 + 0.8 * Math.random()));
            } else {
              el.classList.remove("proof-typing");
              if (done) done();
              resolve();
            }
          })();
        });
      }

      // A whole line: typed plain, then the hook's colouring restored.
      function type(line) {
        return typeInto(line.el, Array.from(line.text), function () {
          line.el.innerHTML = line.html;
        });
      }

      if (io) io.disconnect();
      p.lines.forEach(function (l) {
        l.el.textContent = "";
        l.el.classList.remove("proof-typing");
        l.el.hidden = l === p.fill;
      });
      p.hud.textContent = "";
      p.pill.textContent = "";
      p.pill.classList.remove("proof-goals-zero");

      var q = wait(CHECK);
      p.lines.forEach(function (line) {
        if (line === p.fill || line === p.check) return;
        if (line === p.hole) {
          q = q.then(step(function () { return type(p.hole); }))
            .then(step(function () {
              goals(p, p.open);
              p.hud.textContent = p.rest.goal;
              return wait(GOAL);
            }))
            .then(step(function () {
              // The fill, typed where an editor types it: inside the
              // brackets.  The hole markup was just restored by type(),
              // so the body span exists again.
              var body = p.hole.el.querySelector(".proof-hole-body");
              // indexOf, not split-with-limit: JS split(" = ", 2) drops
              // the remainder, and a fill whose term itself contains
              // " = " would type in truncated.
              var at = p.fill.text.indexOf(" = ");
              var rhs = at === -1 ? "" : p.fill.text.slice(at + 3);
              if (!body || !rhs) return;
              return typeInto(body, Array.from(" " + rhs));
            }))
            .then(step(function () { return wait(CHECK); }))
            .then(step(function () {
              // The give: brackets vanish, the checked line stands --
              // restored from the hook's markup, because the rewind
              // emptied it and nothing re-types this line.
              p.hole.el.hidden = true;
              p.fill.el.innerHTML = p.fill.html;
              p.fill.el.hidden = false;
              goals(p, 0);
              p.hud.textContent = p.rest.hud;
              return wait(CHECK);
            }));
        } else {
          q = q.then(step(function () { return type(line); }));
        }
      });
      // The caller chains the auto-advance on this; a cancelled run
      // resolves early with its steps skipped, and the chain checks the
      // wheel (auto) before moving anyway.
      return q.then(step(function () { p.check.el.innerHTML = p.check.html; }));
    }

    function select(i) {
      if (i === active) return null;
      if (canReplay) settle(panels[active]);
      panels[active].el.hidden = true;
      tabs.forEach(function (t, j) {
        t.setAttribute("aria-selected", j === i ? "true" : "false");
        if (j === i) t.removeAttribute("tabindex");
        else t.setAttribute("tabindex", "-1");
      });
      active = i;
      panels[i].el.hidden = false;
      if (canReplay && !panels[i].played) return play(panels[i]);
      return null;
    }

    // The performance: play the current tab, hold the finished proof for
    // one dwell, hand the stage to the next tab, halt after the last.
    // Focus is never moved -- the show changes, the keyboard stays put.
    function sequence(i) {
      var done = i === active && !panels[i].played
        ? play(panels[i])
        : select(i);
      Promise.resolve(done).then(function () {
        if (!auto || i + 1 >= panels.length) return;
        wait(DWELL).then(function () {
          if (auto) sequence(i + 1);
        });
      });
    }

    tabs.forEach(function (tab, i) {
      tab.addEventListener("click", function () {
        auto = false;
        select(i);
      });
    });
    if (tablist && tabs.length > 1) {
      tablist.addEventListener("keydown", function (e) {
        var at = tabs.indexOf(document.activeElement);
        if (at === -1) return;
        var to = at;
        if (e.key === "ArrowRight") to = (at + 1) % tabs.length;
        else if (e.key === "ArrowLeft")
          to = (at + tabs.length - 1) % tabs.length;
        else if (e.key === "Home") to = 0;
        else if (e.key === "End") to = tabs.length - 1;
        else return;
        e.preventDefault();
        auto = false;
        tabs[to].focus();
        select(to);
      });
      tablist.hidden = false;
    }

    // Everything past here is the replay itself, and only exists where
    // motion is allowed: the buttons stay hidden (a replay control that
    // cannot replay is a dead control) and no observer is armed.
    var io = null;
    if (!canReplay) return;

    // The frame's CSS entrance (proof-enter in extra.css) holds it out of
    // sight while the hero's words land; the first replay starts when the
    // entrance ends, not before, so the two never run at once.  If the
    // entrance already ran -- or the animation is ever removed -- the
    // opacity check and the timeout keep this from waiting forever.
    var entered = new Promise(function (resolve) {
      if (getComputedStyle(term).opacity === "1") { resolve(); return; }
      term.addEventListener("animationend", function onEnd(e) {
        if (e.animationName !== "proof-enter") return;
        term.removeEventListener("animationend", onEnd);
        resolve();
      });
      setTimeout(resolve, ENTER + 1000);
    });

    panels.forEach(function (p) {
      p.button.hidden = false;
      p.button.addEventListener("click", function () {
        auto = false;
        play(p);
      });
    });

    io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        io.disconnect();
        entered.then(function () {
          if (auto && !panels[active].played) sequence(active);
        });
      });
    }, { threshold: 0.35 });
    io.observe(term);
  });
}

if (typeof document$ !== "undefined") {
  document$.subscribe(proofReplay);
} else {
  document.addEventListener("DOMContentLoaded", proofReplay);
}
