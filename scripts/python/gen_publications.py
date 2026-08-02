#!/usr/bin/env python3
"""Render bibliography.json to Markdown, and check it is internally sound.

bibliography.json is the only authoritative publication list (ADR-006).  This
emits the Markdown the publications page and the CV consume, so neither holds a
second copy that can drift.

Two modes:

    gen_publications.py               write the generated Markdown
    gen_publications.py --check       validate only; write nothing

Validation is deliberately about *internal* soundness -- ids unique, years
present and sane, arXiv identifiers well formed, every author naming a family
or a literal.  It does not resolve DOIs or arXiv identifiers, because the
sandbox this was written in cannot reach either, and a checker that silently
passes when the network is blocked is worse than one that never claims to
check.  M8-2 (#47) owns real resolution.

Exit codes follow diff(1): 0 fine, 1 a check failed, 2 could not run.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "bibliography.json"
OUTPUT = REPO_ROOT / "docs" / "_snippets" / "publications.md"

#: `2101.10166`, or the pre-2007 form `math/0512345`.
ARXIV_ID = re.compile(r"^(\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Z]{2})?/\d{7})$")
SURNAME = "DeMeo"


def load() -> list[dict]:
    data = json.loads(SOURCE.read_text())
    return data["items"]


def year(item: dict):
    try:
        return item["issued"]["date-parts"][0][0]
    except (KeyError, IndexError, TypeError):
        return None


def validate(items: list[dict]) -> list[str]:
    problems = []
    seen_ids, seen_arxiv = {}, {}

    for i, it in enumerate(items):
        where = it.get("id") or f"item {i}"

        if not it.get("id"):
            problems.append(f"{where}: no id")
        elif it["id"] in seen_ids:
            problems.append(f"{it['id']}: duplicate id (also item {seen_ids[it['id']]})")
        else:
            seen_ids[it["id"]] = i

        if not it.get("title"):
            problems.append(f"{where}: no title")

        y = year(it)
        if y is None:
            problems.append(f"{where}: no issued year")
        elif not (1990 <= y <= 2100):
            problems.append(f"{where}: implausible year {y}")

        authors = it.get("author") or []
        if not authors:
            problems.append(f"{where}: no authors")
        for a in authors:
            if not (a.get("family") or a.get("literal")):
                problems.append(f"{where}: author entry with neither family nor literal")
        # The site owner should appear on their own publication list.
        if not any(a.get("family") == SURNAME for a in authors) and not any(
            a.get("literal") for a in authors
        ):
            problems.append(f"{where}: {SURNAME} is not among the authors")

        ax = it.get("_arxiv")
        if ax is not None:
            if not ARXIV_ID.match(ax):
                problems.append(f"{where}: malformed arXiv id {ax!r}")
            elif ax in seen_arxiv:
                problems.append(f"{where}: arXiv id {ax} also on {seen_arxiv[ax]}")
            else:
                seen_arxiv[ax] = it.get("id", where)

        doi = it.get("DOI")
        if doi is not None and not doi.startswith("10."):
            problems.append(f"{where}: DOI {doi!r} does not start with '10.'")

        pre = (it.get("_preprint") or {}).get("arxiv-year")
        if pre is not None and y is not None and pre > y:
            problems.append(f"{where}: preprint year {pre} is after publication year {y}")

    return problems


def authors_md(item: dict) -> str:
    """Authors, with the site owner emphasised, in source order."""
    parts = []
    for a in item.get("author") or []:
        if a.get("literal"):
            parts.append(a["literal"])
            continue
        name = " ".join(filter(None, [a.get("given"), a.get("family")]))
        parts.append(f"**{name}**" if a.get("family") == SURNAME else name)
    if not parts:
        return ""
    # "et al." is a continuation, not a coordinate author: "A, B, et al.", never
    # "A and et al.".
    tail = ""
    if parts and parts[-1].lower().rstrip(".") == "et al":
        parts, tail = parts[:-1], ", et al."
    if len(parts) == 1:
        return parts[0] + tail
    joined = ", ".join(parts[:-1]) + (", and " if len(parts) > 2 else " and ") + parts[-1]
    return joined + tail


def links_md(item: dict) -> list[str]:
    out = []
    if item.get("DOI"):
        out.append(f"[DOI](https://doi.org/{item['DOI']})")
    if item.get("_arxiv"):
        out.append(f"[arXiv:{item['_arxiv']}](https://arxiv.org/abs/{item['_arxiv']})")
    url = item.get("URL")
    # Skip a URL that only restates a link already emitted -- the arXiv abstract
    # page, or a publisher page reached through the DOI.  Guard on `url` first:
    # most entries have no URL at all, and `x in None` raises.
    redundant = bool(url) and (
        (item.get("_arxiv") and item["_arxiv"] in url)
        or (item.get("DOI") and item["DOI"] in url)
    )
    if url and not redundant:
        out.append(f"[Link]({url})")
    return out


def render(items: list[dict]) -> str:
    lines = [
        "<!-- Generated from bibliography.json by scripts/python/gen_publications.py.",
        "     Do not edit: `make publications` regenerates it. See ADR-006. -->",
        "",
    ]
    for it in sorted(items, key=lambda i: (-(year(i) or 0), i.get("id", ""))):
        y = year(it)
        bits = [f"**{it['title']}**"]
        if it.get("_role") == "editor":
            bits[0] += " *(editor)*"
        line = f"- {bits[0]}  "
        lines.append(line)

        second = authors_md(it).rstrip(".")
        venue = it.get("container-title")
        if venue:
            vol = f", **{it['volume']}**" if it.get("volume") else ""
            pages = f":{it['page']}" if it.get("page") else ""
            second += f".  *{venue}*{vol}{pages}"
        elif it.get("genre"):
            second += f".  {it['genre']}"
            if it.get("publisher"):
                second += f", {it['publisher']}"
        if y:
            second += f", {y}"
        lines.append(f"  {second.rstrip('.')}.  ")

        extras = links_md(it)
        if it.get("_note"):
            extras.insert(0, f"*{it['_note']}*")
        if extras:
            lines.append(f"  {' · '.join(extras)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="validate only; write nothing")
    args = ap.parse_args()

    try:
        items = load()
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"error: {SOURCE}: {exc}", file=sys.stderr)
        return 2

    problems = validate(items)
    review = [it for it in items if it.get("_needs_review")]

    print(f"bibliography: {len(items)} item(s), {year(min(items, key=lambda i: year(i) or 9999))}"
          f"–{year(max(items, key=lambda i: year(i) or 0))}")
    print(f"  with DOI    : {sum(1 for i in items if i.get('DOI'))}")
    print(f"  with arXiv  : {sum(1 for i in items if i.get('_arxiv'))}")
    print(f"  needs review: {len(review)}")

    if problems:
        print(f"\n{len(problems)} problem(s):", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1

    if review:
        print("\nunresolved, carried from the three-way reconciliation:")
        for it in review:
            print(f"  {it['id']}: {it['_needs_review']}")

    if not args.check:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(render(items))
        print(f"\nwrote {OUTPUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
