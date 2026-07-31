#!/usr/bin/env python3
"""
File: scripts/python/zola_to_mkdocs.py

Description:

  Convert the imported Zola content tree (M2-1) into MkDocs-flavoured Markdown.

  The two site generators differ in ways a bulk copy would get wrong: Zola uses
  TOML front matter delimited by `+++`, MkDocs Material uses YAML delimited by
  `---`; Zola routes pages through a `path` and a `template` that no longer
  exist; and `[extra]` carries fields (notably `banner`) driven by a custom
  theme that is not being ported.

  What this script deliberately does NOT do is rewrite links to destinations
  that have not been decided yet.  Where content finally lands is the subject of
  the M2-3 triage, so aggressive path rewriting now would produce links that are
  wrong in a different way.  Only unambiguous Zola-specific forms are rewritten;
  everything else is reported for M2-3 and M2-6 to resolve with the triage table
  in hand.

  Idempotent: output is regenerated from the source tree on every run, so
  re-running after fixing the converter is safe and expected.

Usage:

    python3 scripts/python/zola_to_mkdocs.py
    python3 scripts/python/zola_to_mkdocs.py --src import/zola-content \
                                             --out import/zola-converted
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
import tomllib
from collections import defaultdict
from pathlib import Path

import yaml
import posixpath
from urllib.parse import urlsplit

# Front-matter keys worth carrying into MkDocs.  `author` is kept because at
# least one imported post is by someone else, and losing that attribution
# silently would be the worst possible outcome of this conversion.
KEEP = ("title", "date", "description", "author")

# Zola routing and templating.  All of it refers to machinery that is not being
# ported; carrying it forward would leave dead keys in every file.
DROP = ("path", "template", "layout", "weight", "sort_by", "render",
        "insert_anchor_links", "paginate_by", "in_search_index", "shortcode",
        "aliases", "x")

FM_RE = re.compile(r"\A\+\+\+\s*\n(.*?)\n\+\+\+\s*\n?", re.DOTALL)
YAML_FM_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n?", re.DOTALL)
# Zola's internal-link form: [text](@/section/page.md)
ZOLA_LINK_RE = re.compile(r"\]\(@/([^)\s]+)\)")
MD_LINK_RE = re.compile(r"\]\(([^)\s]+?)(?:\s+\"[^\"]*\")?\)")
IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)|<img[^>]+src=[\"']([^\"']+)")
MATH_RE = re.compile(r"(?<!\\)\$[^$\n]{1,200}?(?<!\\)\$")
HTML_BLOCK_RE = re.compile(r"^\s*<(div|section|table|figure|iframe|script)\b", re.M)


def parse_front_matter(text: str) -> tuple[dict, str, str]:
    """Return (metadata, body, kind) where kind is toml / yaml / none."""
    m = FM_RE.match(text)
    if m:
        try:
            return tomllib.loads(m.group(1)), text[m.end():], "toml"
        except tomllib.TOMLDecodeError as e:
            return {"__error__": str(e)}, text[m.end():], "toml"
    if YAML_FM_RE.match(text):
        # Already converted; pass through so re-runs are safe.
        return {}, text, "yaml"
    return {}, text, "none"


def build_front_matter(meta: dict, report: dict, rel: str) -> tuple[dict, list[str]]:
    """Split Zola metadata into kept YAML keys and human-readable notes."""
    out, notes = {}, []
    for k in KEEP:
        if k in meta:
            v = meta[k]
            out[k] = v.isoformat() if hasattr(v, "isoformat") else v
    for k in DROP:
        if k in meta:
            report["dropped_keys"][k].append(rel)
    extra = meta.get("extra") or {}
    if "banner" in extra:
        # The banner template is gone.  Recorded rather than carried so M3-2 can
        # decide whether any of these images earn a place in the new design.
        report["banners"][extra["banner"]].append(rel)
        notes.append(f"zola-banner: {extra['banner']}")
    for k, v in extra.items():
        if k != "banner":
            notes.append(f"zola-extra-{k}: {v}")
    for k in meta:
        if k not in KEEP and k not in DROP and k != "extra":
            report["unmapped_keys"][k].append(rel)
            notes.append(f"zola-{k}: {meta[k]}")
    return out, notes


def rewrite_links(body: str, src_rel: Path, known: set[str], report: dict) -> str:
    """Rewrite unambiguous Zola link forms; report everything questionable."""
    rel = str(src_rel)

    def zola_link(m: re.Match) -> str:
        target = m.group(1)
        if target in known:
            report["rewritten_links"].append(f"{rel}: @/{target}")
            return f"]({target})"
        report["unresolved_links"].append(f"{rel}: @/{target}  (no such page)")
        return m.group(0)

    body = ZOLA_LINK_RE.sub(zola_link, body)

    for m in MD_LINK_RE.finditer(body):
        t = m.group(1)

        # Checked before anything else, including the external-link skip: a
        # malformed URL is not a warning in MkDocs.  urlsplit raises and the
        # entire build aborts, so this is a gate, not a nicety.  The imported
        # tree contains exactly one, and it is an external link.
        try:
            urlsplit(t)
        except ValueError as e:
            report["malformed_urls"].append(f"{rel}: {t!r} — {e}")
            continue

        if t.startswith(("http://", "https://", "mailto:", "#")):
            continue
        if t.endswith(".html"):
            report["html_links"].append(f"{rel}: {t}")
        elif t.startswith("/images/") or "/images/" in t:
            report["image_links"].append(f"{rel}: {t}")
        elif t.split("#")[0].endswith(".md"):
            # Zola and MkDocs resolve relative links differently, so a link that
            # worked on the old site can silently point nowhere on the new one.
            bare = t.split("#")[0]
            target = posixpath.normpath(
                posixpath.join(posixpath.dirname(rel), bare)).lstrip("/")
            alt = target.replace("index.md", "_index.md")
            if target not in known and alt not in known:
                report["broken_relative_links"].append(f"{rel}: {t} -> {target}")
    return body


def convert(src: Path, out: Path) -> dict:
    report = {
        "converted": [], "copied": [], "no_front_matter": [], "toml_errors": [],
        "math_pages": [], "html_pages": [], "unresolved_links": [],
        "rewritten_links": [], "html_links": [], "image_links": [],
        "date_mismatches": [], "malformed_urls": [],
        "broken_relative_links": [],
        "dropped_keys": defaultdict(list), "banners": defaultdict(list),
        "unmapped_keys": defaultdict(list),
    }
    if out.exists():
        shutil.rmtree(out)

    md_files = sorted(src.rglob("*.md"))
    # Zola resolves @/ links against the content root, with _index.md as the
    # section page; record both spellings so link checking sees what Zola saw.
    known = {str(p.relative_to(src)) for p in md_files}

    for path in md_files:
        rel = path.relative_to(src)
        text = path.read_text(encoding="utf-8", errors="replace")
        meta, body, kind = parse_front_matter(text)

        if "__error__" in meta:
            report["toml_errors"].append(f"{rel}: {meta['__error__']}")
            meta = {}
        if kind == "none":
            report["no_front_matter"].append(str(rel))

        fm, notes = build_front_matter(meta, report, str(rel))
        fm.setdefault("title", path.stem.replace("-", " ").replace("_", " ").strip())
        body = rewrite_links(body, rel, known, report)

        if MATH_RE.search(body):
            report["math_pages"].append(str(rel))
        if HTML_BLOCK_RE.search(body):
            report["html_pages"].append(str(rel))

        # Dated post filenames carry a date, and so does the front matter.  In
        # the imported tree they sometimes disagree, which matters because the
        # blog plugin orders on the front-matter value while every existing
        # inbound link uses the filename.  Report rather than guess.
        fn_date = re.match(r"(\d{4}-\d{2}-\d{2})-", path.name)
        fm_date = str(fm.get("date", ""))[:10]
        if fn_date and fm_date and fn_date.group(1) != fm_date:
            report["date_mismatches"].append(
                f"{rel}: filename {fn_date.group(1)} vs front matter {fm_date}")

        # Zola's section index is _index.md; MkDocs uses index.md.
        name = "index.md" if path.name == "_index.md" else path.name
        dest = out / rel.parent / name
        dest.parent.mkdir(parents=True, exist_ok=True)

        head = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).rstrip()
        note_block = "".join(f"\n<!-- {n} -->" for n in notes)
        dest.write_text(f"---\n{head}\n---{note_block}\n\n{body.lstrip()}\n",
                        encoding="utf-8")
        report["converted"].append(str(rel))

    for path in sorted(src.rglob("*")):
        if path.is_file() and path.suffix != ".md":
            rel = path.relative_to(src)
            dest = out / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
            report["copied"].append(str(rel))
    return report


def write_report(report: dict, path: Path) -> None:
    def block(title: str, items, note: str = "") -> str:
        items = list(items)
        s = f"\n## {title} ({len(items)})\n\n"
        if note:
            s += note + "\n\n"
        if not items:
            return s + "_None._\n"
        return s + "".join(f"- `{i}`\n" for i in items)

    L = [
        "# Zola to MkDocs conversion report\n",
        "Generated by `scripts/python/zola_to_mkdocs.py`. Regenerated on every run.\n",
        f"\n**{len(report['converted'])} Markdown files converted**, "
        f"{len(report['copied'])} non-Markdown files copied verbatim.\n",
        "\nNothing here is an error in itself. These are the places where a "
        "mechanical conversion cannot decide for you, collected so that M2-3 "
        "(#12) can triage with the full picture and M2-6 (#15) can build the "
        "redirect map from real data.\n",
        block("Pages using mathematics", report["math_pages"],
              "These carry `$...$` delimiters from the Zola MathJax setup. M3-4 "
              "(#20) must confirm KaTeX renders each one, including the custom "
              "macros (`\\bA` and friends) the algebra pages rely on."),
        block("Pages with raw HTML blocks", report["html_pages"],
              "Hand-written `<div>`, `<section>`, or `<table>` markup, mostly "
              "layout scaffolding for the retired theme. Most should become "
              "Markdown or M3-3 components rather than being carried over."),
        block("Links to `.html` targets", report["html_links"],
              "Internal links written against Zola's output paths. They need "
              "rewriting once M2-3 fixes where each page lands."),
        block("Links into `/images/`", report["image_links"],
              "Image references still pointing at the Zola static path. M2-5 "
              "(#14) repoints these at `docs/assets/images/`."),
        block("Unresolved `@/` links", report["unresolved_links"],
              "Zola internal links whose target does not exist in the imported "
              "tree — already broken before the migration."),
        block("Rewritten `@/` links", report["rewritten_links"]),
        block("Malformed URLs — these BREAK the build", report["malformed_urls"],
              "MkDocs does not warn on these: `urlsplit` raises and the build "
              "aborts. Must be fixed before the affected page can be included."),
        block("Broken relative links", report["broken_relative_links"],
              "Links that resolved under Zola's routing but point nowhere under "
              "MkDocs's relative-path resolution. Fix alongside the M2-3 triage, "
              "since where each page lands determines the correct target."),
        block("Date mismatches", report["date_mismatches"],
              "The filename and the front matter disagree about the post date. "
              "This matters: the blog plugin orders on the front-matter value, "
              "while every existing inbound link uses the filename. Where the "
              "retired Octopress site also published the post, "
              "`archive/octopress/POSTS.md` is independent evidence for which "
              "is right. Resolve in M2-4 (#13)."),
        block("Files with no front matter", report["no_front_matter"]),
        block("TOML parse errors", report["toml_errors"]),
    ]
    L.append("\n## Dropped Zola routing keys\n\n"
             "Zola routing and templating directives, removed because the "
             "machinery they refer to is not being ported.\n\n")
    L.append("".join(f"- `{k}` — {len(v)} file(s)\n"
                     for k, v in sorted(report["dropped_keys"].items())) or "_None._\n")
    L.append("\n## Banner images declared\n\n"
             "The `[extra] banner` key named a per-page header image rendered by "
             "a template that no longer exists. Preserved as a comment in each "
             "converted file rather than dropped silently, so M3-2 (#18) can "
             "decide whether any earn a place in the new design.\n\n")
    L.append("".join(f"- `{k}` — {', '.join(f'`{f}`' for f in v)}\n"
                     for k, v in sorted(report["banners"].items())) or "_None._\n")
    if report["unmapped_keys"]:
        L.append("\n## Unmapped front-matter keys\n\n"
                 "Present in the source but in neither the keep nor the drop "
                 "list; preserved as comments and worth a look.\n\n")
        L.append("".join(f"- `{k}` — {len(v)} file(s)\n"
                         for k, v in sorted(report["unmapped_keys"].items())))
    path.write_text("".join(L), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", type=Path, default=Path("import/zola-content"))
    ap.add_argument("--out", type=Path, default=Path("import/zola-converted"))
    ap.add_argument("--report", type=Path, default=Path("import/CONVERSION_REPORT.md"))
    args = ap.parse_args()

    if not args.src.is_dir():
        print(f"error: {args.src} not found", file=sys.stderr)
        return 1

    report = convert(args.src, args.out)
    write_report(report, args.report)

    print(f"converted {len(report['converted'])} Markdown files -> {args.out}")
    print(f"copied    {len(report['copied'])} other files")
    for key, label in (("math_pages", "pages using mathematics"),
                       ("html_pages", "pages with raw HTML blocks"),
                       ("html_links", "links to .html targets"),
                       ("image_links", "links into /images/"),
                       ("unresolved_links", "unresolved @/ links"),
                       ("date_mismatches", "filename/front-matter date mismatches"),
                       ("malformed_urls", "malformed URLs (BUILD-BREAKING)"),
                       ("broken_relative_links", "broken relative links"),
                       ("toml_errors", "TOML parse errors")):
        print(f"  {len(report[key]):>4}  {label}")
    print(f"report -> {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
