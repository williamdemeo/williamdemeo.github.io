/* Render every math expression in a content tree with KaTeX and report failures.
 *
 * The site's macro table (docs/javascripts/katex-macros.js) is the single
 * source of truth: this script evaluates that file rather than keeping its own
 * copy, so the audit and the published site can never disagree.
 *
 * Usage:  node scripts/python/audit_math.mjs <content-dir> [katex-dir]
 */
import fs from 'fs';
import path from 'path';
import vm from 'vm';
import { createRequire } from 'module';

// Load the *shipped* KaTeX bundle rather than one from node_modules.  This
// removes any npm dependency for running the audit and, more usefully, makes
// it impossible for the audit and the published site to disagree about which
// KaTeX version they are testing against.
const require = createRequire(import.meta.url);
const katex = require(path.resolve('docs/assets/katex/katex.min.js'));

const ROOT = process.argv[2] || 'import/zola-converted';
const MACRO_FILE = 'docs/javascripts/katex-macros.js';

const ctx = { window: {} };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(MACRO_FILE, 'utf8'), ctx);
const MACROS = ctx.window.KATEX_MACROS;

function* walk(d) {
  for (const e of fs.readdirSync(d, { withFileTypes: true })) {
    const p = path.join(d, e.name);
    if (e.isDirectory()) yield* walk(p);
    else if (p.endsWith('.md')) yield p;
  }
}

// Stripped before scanning, so the audit sees what MkDocs will actually
// render: fenced and inline code (`$PATH` in a shell example is not
// mathematics) and HTML comments (commented-out prose is not published, and
// flagging expressions inside it reports failures no visitor can ever see).
const strip = s => s
  .replace(/```[\s\S]*?```/g, '')
  .replace(/<!--[\s\S]*?-->/g, '')
  .replace(/`[^`\n]*`/g, '');

const fails = new Map();
let nExpr = 0, nPages = 0;
const pagesFailing = new Set();

for (const f of walk(ROOT)) {
  const body = strip(fs.readFileSync(f, 'utf8'));
  const exprs = [];
  for (const m of body.matchAll(/\$\$([\s\S]+?)\$\$/g)) exprs.push([m[1], true]);
  for (const m of body.matchAll(/(?<!\$)\$(?!\$)([^\n$]+?)(?<!\$)\$(?!\$)/g)) exprs.push([m[1], false]);
  if (exprs.length) nPages++;
  for (const [src, displayMode] of exprs) {
    nExpr++;
    try {
      // macros is mutated by KaTeX for \gdef; pass a copy per call.
      katex.renderToString(src, { displayMode, throwOnError: true, strict: false,
                                  macros: { ...MACROS } });
    } catch (e) {
      pagesFailing.add(f);
      const msg = String(e.message).replace(/ at position \d+.*$/, '').slice(0, 110);
      if (!fails.has(msg)) fails.set(msg, []);
      fails.get(msg).push(`${path.relative(ROOT, f)}: ${src.trim().slice(0, 70)}`);
    }
  }
}

const nFail = [...fails.values()].reduce((a, b) => a + b.length, 0);
console.log(`macros defined : ${Object.keys(MACROS).length}`);
console.log(`pages with math: ${nPages}`);
console.log(`expressions    : ${nExpr}`);
console.log(`failures       : ${nFail}  (on ${pagesFailing.size} page(s))`);
if (nFail) {
  console.log(`\n--- distinct failure modes (${fails.size}) ---`);
  for (const [msg, xs] of [...fails].sort((a, b) => b[1].length - a[1].length)) {
    console.log(`\n[${xs.length}] ${msg}`);
    for (const x of xs.slice(0, 3)) console.log(`      ${x}`);
  }
}
process.exit(nFail ? 1 : 0);
