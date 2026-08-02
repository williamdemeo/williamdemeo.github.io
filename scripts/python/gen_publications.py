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
or a literal.  It resolves nothing, and needs no network to say what it says.

Whether the entries are *true* is a different question, and asking it means
asking the publishers: verify_bibliography.py does that, and exits non-zero
rather than reporting a pass when it cannot reach them.  Keeping the two apart
is the point -- this one can run anywhere, and neither is mistaken for the
other.

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


MONTHS = ("January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December")


def date_parts(item: dict) -> list:
    try:
        parts = item["issued"]["date-parts"][0]
    except (KeyError, IndexError, TypeError):
        return []
    return [p for p in parts if isinstance(p, int)]


def year(item: dict):
    parts = date_parts(item)
    return parts[0] if parts else None


def issued_text(item: dict) -> str:
    """"June 2020", "January 19, 2022", or bare "2004" -- to whatever precision
    the publisher gave, never inventing a day the record does not have."""
    parts = date_parts(item)
    if not parts:
        return ""
    if len(parts) == 1 or not 1 <= parts[1] <= 12:
        return str(parts[0])
    month = MONTHS[parts[1] - 1]
    if len(parts) == 2:
        return f"{month} {parts[0]}"
    return f"{month} {parts[2]}, {parts[0]}"


def validate(items: list[dict]) -> list[str]:
    problems = []
    seen_ids, seen_arxiv = {}, {}
    ids = {it.get("id") for it in items}

    for i, it in enumerate(items):
        # An entry may name the published work it is a preprint of.  That is
        # what lets one arXiv id sit on two entries without being a mistake.
        version_of = it.get("_version-of")
        if version_of is not None and version_of not in ids:
            problems.append(f"{it.get('id', i)}: _version-of names no entry: {version_of!r}")
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
            elif ax in seen_arxiv and version_of != seen_arxiv[ax]:
                # Sharing an id is fine between a preprint and the paper it
                # became, and a mistake between any other two entries.
                problems.append(
                    f"{where}: arXiv id {ax} also on {seen_arxiv[ax]}, "
                    f"and neither declares _version-of the other"
                )
            else:
                seen_arxiv.setdefault(ax, it.get("id", where))

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


#: How to label the link to the version of record, by CSL type.  A reader
#: scanning the list should be able to tell a refereed journal paper from a
#: conference paper without opening either.
PUBLISHED_LABEL = {
    "article-journal": "Journal",
    "paper-conference": "Proceedings",
    "chapter": "Chapter",
    "book": "Book",
    "thesis": "Thesis",
}


def published_link(item: dict) -> tuple[str, str] | None:
    """(label, url) for the version of record, or None if there isn't one.

    The label says only what the evidence supports.  A DOI is a publisher
    asserting "this is the record of that work", so the entry's type may name
    it -- Journal, Proceedings.  A bare URL is not: it may be the author's own
    copy of the PDF, as the ISMA 2004 one is, so it is called what it is.
    """
    url, doi = item.get("URL"), item.get("DOI")
    # An arXiv abstract page is not a version of record even when it sits in
    # `URL`, because those entries *are* the preprint.
    if url and "arxiv.org" in url:
        url = None
    if doi:
        return PUBLISHED_LABEL.get(item.get("type"), "Published version"), url or f"https://doi.org/{doi}"
    if url:
        return ("PDF" if url.lower().endswith(".pdf") else "Link"), url
    return None


def links_md(item: dict, by_id: dict[str, dict]) -> list[str]:
    """The published version and the preprint, side by side, in that order."""
    out = []

    # An entry that is itself a preprint borrows the published link from the
    # work it names, so the pair reads the same way from either entry.
    published = by_id.get(item.get("_version-of") or "")
    if published is not None:
        link = published_link(published)
        if link:
            out.append(f"[Published version]({link[1]})")
    else:
        link = published_link(item)
        if link:
            out.append(f"[{link[0]}]({link[1]})")

    if item.get("_arxiv"):
        out.append(f"[arXiv preprint](https://arxiv.org/abs/{item['_arxiv']})")
    return out


def imprint_md(item: dict) -> str:
    """Venue, date, volume, issue and pages -- everything the record supports.

    Deliberately in the order a citation is read aloud, and deliberately
    omitting whatever the publisher did not give: an entry with no issue number
    should say nothing about issues rather than guess one.
    """
    bits = []
    venue = item.get("container-title")
    if venue:
        short = item.get("container-title-short")
        bits.append(f"*{venue}*" + (f" ({short})" if short else ""))
    elif item.get("genre"):
        thesis = item["genre"]
        if item.get("publisher"):
            thesis += f", {item['publisher']}"
        bits.append(thesis)
    elif item.get("_arxiv"):
        # Nowhere else to say what this is.  "arXiv preprint arXiv:1234.56789"
        # is redundant read aloud and is how the things are actually cited.
        bits.append(f"arXiv preprint arXiv:{item['_arxiv']}")

    if item.get("event-place"):
        bits.append(item["event-place"])

    series = item.get("collection-title")
    if series and item.get("volume"):
        bits.append(f"{series} Volume {item['volume']}")
    elif item.get("volume"):
        bits.append(f"Volume {item['volume']}")
    if item.get("issue"):
        bits.append(f"Issue {item['issue']}")

    date = issued_text(item)
    if date:
        bits.append(date)
    if item.get("page"):
        bits.append(f"pages {item['page']}")

    line = ", ".join(bits)
    if line:
        line += "."
    # The DOI belongs in the citation, not in the row of links: it is what a
    # reader copies to cite the work, and it is what makes the entry checkable.
    if item.get("DOI"):
        line += f"  [doi:{item['DOI']}](https://doi.org/{item['DOI']})"
    return line


def render(items: list[dict]) -> str:
    lines = [
        "<!-- Generated from bibliography.json by scripts/python/gen_publications.py.",
        "     Do not edit: `make publications` regenerates it. See ADR-006. -->",
        "",
    ]
    by_id = {it["id"]: it for it in items if it.get("id")}
    for it in sorted(items, key=lambda i: (-(year(i) or 0), i.get("id", ""))):
        title = f"**{it['title']}**"
        if it.get("_role") == "editor":
            title += " *(editor)*"
        lines.append(f"- {title}  ")

        byline = authors_md(it).rstrip(".")
        if it.get("_note"):
            byline += f".  *{it['_note']}*"
        lines.append(f"  {byline.rstrip('.')}.  ")

        imprint = imprint_md(it)
        if imprint:
            lines.append(f"  {imprint}  ")

        links = links_md(it, by_id)
        if links:
            lines.append(f"  {' · '.join(links)}")
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
