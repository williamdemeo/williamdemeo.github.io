#!/usr/bin/env python3
"""
File: scripts/python/extract_octopress_posts.py

Description:

  Extract post bodies from the generated Octopress site into archive/octopress/.

  The Octopress site in this repository is deploy output: there is no
  `_config.yml`, no `_posts/`, no `Rakefile`, and no `source` branch, so the
  Markdown behind these posts does not exist here.  The generated HTML is the
  only copy.  M1-2 clears that HTML from the working tree, so this script runs
  first and preserves the part that carries content -- the `entry-content`
  div of each post -- along with the title and publication date.

  Also emits the complete list of URLs the site served, which M2-6 consumes as
  input to the redirect map.

Provenance and re-running:

  After M1-2 lands, the source HTML is no longer in the working tree.  To run
  this again, restore it from the tag first:

      git worktree add /tmp/octopress octopress-final
      python3 scripts/python/extract_octopress_posts.py --root /tmp/octopress

Usage:

    python3 scripts/python/extract_octopress_posts.py [--root DIR] [--out DIR]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

# Post directories are dated paths: YYYY/MM/DD/slug/index.html
POST_GLOB = "20[0-9][0-9]/[0-9][0-9]/[0-9][0-9]/*/index.html"

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.DOTALL | re.IGNORECASE)
TIME_RE = re.compile(r'<time datetime="([^"]+)"', re.IGNORECASE)
ENTRY_OPEN_RE = re.compile(r'<div class="entry-content"[^>]*>', re.IGNORECASE)
# Any div open or close tag, for depth tracking.
DIV_TAG_RE = re.compile(r"<(/?)div\b[^>]*>", re.IGNORECASE)


def extract_entry_content(html: str) -> str | None:
    """Return the inner HTML of the `entry-content` div.

    Octopress nests further divs inside the post body (CodeRay blocks, figures),
    so the closing tag cannot be found by a non-greedy match.  Track div depth
    from the opening tag instead.
    """
    m = ENTRY_OPEN_RE.search(html)
    if not m:
        return None
    start = m.end()
    depth = 1
    for tag in DIV_TAG_RE.finditer(html, start):
        depth += -1 if tag.group(1) else 1
        if depth == 0:
            return html[start:tag.start()].strip()
    # Unbalanced markup: return the remainder rather than nothing, so the
    # content is preserved even if the boundary is wrong.
    return html[start:].strip()


def clean_title(raw: str) -> str:
    """Strip the site-name suffix Octopress appends to every <title>."""
    title = re.sub(r"\s*-\s*William DeMeo.*$", "", raw.strip(), flags=re.DOTALL)
    return " ".join(title.split())


def extract_post(path: Path, root: Path) -> dict:
    html = path.read_text(encoding="utf-8", errors="replace")
    title_m = TITLE_RE.search(html)
    time_m = TIME_RE.search(html)
    rel = path.parent.relative_to(root)
    return {
        "slug": path.parent.name,
        "url": "/" + str(rel) + "/",
        "title": clean_title(title_m.group(1)) if title_m else path.parent.name,
        "date": time_m.group(1)[:10] if time_m else str(rel).replace("/", "-")[:10],
        "body": extract_entry_content(html) or "",
        "source": str(path.relative_to(root)),
    }


def collect_urls(root: Path) -> list[str]:
    """Every path the generated site served, as a site-root-relative URL."""
    urls = set()
    for p in root.rglob("index.html"):
        if any(part in {".git", "docs", "scripts", "archive"} for part in p.parts):
            continue
        rel = p.parent.relative_to(root)
        urls.add("/" if str(rel) == "." else "/" + str(rel) + "/")
    for extra in ("atom.xml", "sitemap.xml", "robots.txt", "humans.txt"):
        if (root / extra).exists():
            urls.add("/" + extra)
    return sorted(urls)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path("."),
                    help="Repository root holding the generated site.")
    ap.add_argument("--out", type=Path, default=Path("archive/octopress"),
                    help="Destination directory.")
    args = ap.parse_args()

    root: Path = args.root.resolve()
    out: Path = args.out if args.out.is_absolute() else root / args.out
    (out / "posts").mkdir(parents=True, exist_ok=True)

    posts = sorted(
        (extract_post(p, root) for p in root.glob(POST_GLOB)),
        key=lambda d: (d["date"], d["slug"]),
    )
    if not posts:
        print(f"error: no posts matched {POST_GLOB} under {root}")
        return 1

    for post in posts:
        target = out / "posts" / f"{post['date']}-{post['slug']}.html"
        target.write_text(
            f"<!--\n"
            f"title:  {post['title']}\n"
            f"date:   {post['date']}\n"
            f"url:    {post['url']}\n"
            f"source: {post['source']}\n"
            f"-->\n{post['body']}\n",
            encoding="utf-8",
        )
        words = len(re.sub(r"<[^>]+>", " ", post["body"]).split())
        print(f"  {post['date']}  {words:>5}w  {target.name}")

    urls = collect_urls(root)
    (out / "urls.txt").write_text("\n".join(urls) + "\n", encoding="utf-8")

    index = ["| Date | Title | Original URL | Words |", "| --- | --- | --- | --- |"]
    for post in posts:
        words = len(re.sub(r"<[^>]+>", " ", post["body"]).split())
        index.append(f"| {post['date']} | {post['title']} | `{post['url']}` | {words} |")
    (out / "POSTS.md").write_text("\n".join(index) + "\n", encoding="utf-8")

    print(f"\n{len(posts)} posts -> {out / 'posts'}")
    print(f"{len(urls)} URLs -> {out / 'urls.txt'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
