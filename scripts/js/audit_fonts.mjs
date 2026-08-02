/* Report every font Chromium actually rasterised text with, page by page.
 *
 * The acceptance criterion in #17 is that Agda's Unicode renders in the
 * intended monospace face "with no fallback substitution".  A font's cmap can
 * be inspected offline, but whether the *browser* used that face for a given
 * run of text depends on the CSS cascade, the unicode-range split, and what
 * happens to be installed locally.  Only the layout engine knows, and
 * CSS.getPlatformFontsForNode is how it can be asked.
 *
 * The test is: inside the content area, every face Chromium reports must be a
 * downloaded webfont (`isCustomFont`).  A system font appearing there means
 * some character fell out of every subset that ships, which is precisely the
 * mid-line substitution the issue is about.
 *
 * Usage:  node scripts/js/audit_fonts.mjs [site-dir]
 *         make font-audit
 */
import fs from 'fs';
import path from 'path';
import { serve, launch } from './_browser.mjs';

const SITE = process.argv[2] || 'site';

// CSS.getPlatformFontsForNode does not report the whole subtree: asking about
// <body> comes back empty, and asking about the article misses the code blocks
// inside it.  It answers for the text an element directly contains.  So the
// page is walked first and every element holding a text node is tagged, and
// each of those is asked about individually -- which also means a failure can
// name the element it happened in.
const TAG_TEXT_NODES = () => {
  let n = 0;
  for (const el of document.querySelectorAll('body *')) {
    if (el.offsetParent === null && el.tagName !== 'BODY') continue;   // not displayed
    // KaTeX emits a parallel MathML tree for screen readers and hides it by
    // clipping rather than by display:none, so it is laid out -- in a system
    // serif, because no @font-face applies to it.  It is never seen.  The
    // visible rendering is the sibling .katex-html.
    if (el.closest('.katex-mathml')) continue;
    for (const child of el.childNodes) {
      if (child.nodeType === 3 && child.nodeValue.trim()) {
        el.setAttribute('data-fontprobe', String(n++));
        break;
      }
    }
  }
  return n;
};

function pages(dir) {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) out.push(...pages(p));
    else if (e.name.endsWith('.html')) out.push(p);
  }
  return out;
}

const server = await serve(SITE);
const browser = await launch();
const { page } = browser;
await page.send('Page.enable');
await page.send('DOM.enable');
await page.send('CSS.enable');

async function fontsFor(selector) {
  const { root } = await page.send('DOM.getDocument', { depth: 0 });
  const { nodeId } = await page.send('DOM.querySelector', { nodeId: root.nodeId, selector });
  if (!nodeId) return null;
  const { fonts } = await page.send('CSS.getPlatformFontsForNode', { nodeId });
  return fonts;
}

const seen = new Map();      // familyName -> { custom, glyphs, pages:Set }
const failures = [];
const files = pages(SITE).sort();
let nodesChecked = 0;

let stubs = 0;
for (const file of files) {
  const rel = path.relative(SITE, file);
  // The redirect stubs from redirects.yml are a <meta refresh> and nothing
  // else.  Left to itself the browser follows them, and the audit ends up
  // measuring the typography of Chromium's own network-error page.
  if (/<meta[^>]+http-equiv=["']?refresh/i.test(fs.readFileSync(file, 'utf8'))) {
    stubs++;
    continue;
  }
  await page.goto(server.origin + '/' + rel.replace(/index\.html$/, ''));
  const n = await page.eval(TAG_TEXT_NODES);
  const { root } = await page.send('DOM.getDocument', { depth: 0 });
  const { nodeIds } = await page.send('DOM.querySelectorAll',
    { nodeId: root.nodeId, selector: '[data-fontprobe]' });
  for (const nodeId of nodeIds) {
    nodesChecked++;
    const { fonts } = await page.send('CSS.getPlatformFontsForNode', { nodeId });
    for (const f of fonts) {
      const rec = seen.get(f.familyName) || { custom: f.isCustomFont, glyphs: 0, pages: new Set() };
      rec.glyphs += f.glyphCount;
      rec.pages.add(rel);
      seen.set(f.familyName, rec);
      if (!f.isCustomFont) {
        const { node } = await page.send('DOM.describeNode', { nodeId });
        const sample = await page.eval(id => {
          const el = document.querySelector(`[data-fontprobe="${id}"]`);
          return el ? el.textContent.trim().slice(0, 60) : '';
        }, node.attributes[node.attributes.indexOf('data-fontprobe') + 1]);
        failures.push({ page: rel, family: f.familyName, glyphs: f.glyphCount, tag: node.nodeName.toLowerCase(), sample });
      }
    }
  }
  if (n !== nodeIds.length) console.log(`  note: ${rel} tagged ${n} nodes, matched ${nodeIds.length}`);
}

// The characters #17 names, plus the syntax a page of Agda cannot avoid.  Each
// one is measured on its own, so the report says *which* character fell back
// rather than that some did -- and so the check does not depend on any page
// happening to contain them.
const PROBE = [...'𝑨𝓤𝑆≅⨅⊔∀∘⟨⟩→₀₁₂ₙᵢ𝔸𝕏λΠΣ≡×⊤⊥¬∈∉⊢⇒↦∙≤⊑⊎∅ℕℓ𝒦𝓞𝓥·⟦⟧'];
await page.goto(server.origin + '/');
await page.eval(chars => {
  // Inside .md-typeset, not just .md-content: the code rules are scoped to it,
  // and a probe that escaped them would be measuring the wrong cascade.
  const host = document.createElement('pre');
  host.id = 'agda-probe';
  for (const [i, c] of chars.entries()) {
    const code = document.createElement('code');
    code.className = 'probe';
    code.id = 'probe-' + i;
    code.textContent = c;
    host.appendChild(code);
  }
  document.querySelector('.md-typeset').appendChild(host);
  return document.fonts.ready.then(() => true);
}, PROBE);
await new Promise(r => setTimeout(r, 300));

const probeBad = [];
for (const [i, c] of PROBE.entries()) {
  const fonts = (await fontsFor('#probe-' + i)) || [];
  const wrong = fonts.filter(f => !f.isCustomFont || f.familyName !== 'JuliaMono');
  if (wrong.length || fonts.length === 0) {
    probeBad.push({ char: c, cp: c.codePointAt(0), fonts: fonts.map(f => f.familyName).join(', ') || '(none)' });
  }
}

console.log(`pages audited : ${files.length - stubs}  (${stubs} redirect stub(s) skipped)`);
console.log(`text nodes    : ${nodesChecked}`);
console.log(`\nfaces used, across the whole site:`);
console.log(`${'family'.padEnd(26)} ${'webfont'.padStart(8)} ${'glyphs'.padStart(8)}  pages`);
for (const [family, rec] of [...seen].sort((a, b) => b[1].glyphs - a[1].glyphs)) {
  console.log(`${family.padEnd(26)} ${String(rec.custom).padStart(8)} ${String(rec.glyphs).padStart(8)}  ${rec.pages.size}`);
}

console.log(`\nAgda probe: ${PROBE.length - probeBad.length}/${PROBE.length} characters rendered in JuliaMono`);

if (failures.length) {
  console.log(`\n--- system fonts rendering page text (${failures.length}) ---`);
  for (const f of failures.slice(0, 20)) {
    console.log(`  ${f.page} <${f.tag}>: ${f.family}, ${f.glyphs} glyph(s)  "${f.sample}"`);
  }
}
if (probeBad.length) {
  console.log(`\n--- characters that did not render in JuliaMono (${probeBad.length}) ---`);
  for (const f of probeBad) {
    console.log(`  ${f.char}  U+${f.cp.toString(16).toUpperCase().padStart(4, '0')}  -> ${f.fonts}`);
  }
}

await browser.close();
await server.close();

const bad = failures.length + probeBad.length;
console.log(bad ? `\nFAIL: ${bad} substitution(s)` : `\nOK: no fallback substitution`);
process.exit(bad ? 1 : 0);
