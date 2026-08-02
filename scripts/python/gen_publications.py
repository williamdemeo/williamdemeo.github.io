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

#: Three renderings of one list.  The page one groups by kind and carries
#: abstracts; the CV one is the entries marked `_cv`, a little tighter; the
#: BibTeX one is for anyone who wants to cite this work.  The Markdown two are
#: snippets rather than pages, so a page includes what it wants and no page
#: holds a second copy of the data.
SNIPPETS = REPO_ROOT / "docs" / "_snippets"
OUTPUTS = {
    "page": SNIPPETS / "publications-page.md",
    "cv": SNIPPETS / "publications-cv.md",
}
BIBTEX = REPO_ROOT / "docs" / "publications.bib"

#: `2101.10166`, or the pre-2007 form `math/0512345`.
ARXIV_ID = re.compile(r"^(\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Z]{2})?/\d{7})$")
SURNAME = "DeMeo"

#: How the page is divided, in order.  These name *where the work appeared*,
#: which the publisher records and this repository checks, rather than whether
#: it was refereed, which nothing here records.  A reader can still tell a
#: journal paper from a preprint at a glance, which is what #30 asked for, and
#: no heading claims something no source backs.
#:
#: `validate` fails on an entry matching no group.  A publications page that
#: silently drops a publication is the worst failure available to it.
GROUPS = [
    ("article-journal",), ("paper-conference",), ("article", "manuscript"),
    ("thesis",), ("book",),
]
GROUP_TITLES = {
    ("article-journal",): "Journal articles",
    ("paper-conference",): "Conference and workshop papers",
    ("article", "manuscript"): "Preprints and unpublished manuscripts",
    ("thesis",): "Theses",
    ("book",): "Edited volumes",
}


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

        # A publications page that silently drops a publication is the worst
        # failure available to it, so an unrecognised type is a hard error
        # rather than an entry that quietly renders nowhere.
        if group_of(it) is None:
            problems.append(f"{where}: type {it.get('type')!r} belongs to no group on the page")

    return problems


def artifactless(items: list[dict]) -> list[str]:
    """Entries linking to nothing a reader can open.

    #30's acceptance criteria ask that every entry link to at least one
    resolvable artifact.  This is reported rather than enforced: the entry that
    fails it fails because the paper is genuinely hard to find online, and
    deleting it to make a check pass would be the wrong repair.
    """
    return [
        it.get("id", "?") for it in items
        if not (it.get("DOI") or it.get("_arxiv") or it.get("URL")
                or it.get("_version-of"))
    ]


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


def imprint_md(item: dict, *, compact: bool = False) -> str:
    """Venue, date, volume, issue and pages -- everything the record supports.

    Deliberately in the order a citation is read aloud, and deliberately
    omitting whatever the publisher did not give: an entry with no issue number
    should say nothing about issues rather than guess one.

    `compact` is the CV's rendering: the year instead of the full date, and no
    DOI, since the link beside it already goes there and a CV is read down a
    page rather than cited from.
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

    date = str(year(item) or "") if compact else issued_text(item)
    if date:
        bits.append(date)
    if item.get("page"):
        bits.append(f"pages {item['page']}")

    line = ", ".join(bits)
    if line:
        line += "."
    # The DOI belongs in the citation, not in the row of links: it is what a
    # reader copies to cite the work, and it is what makes the entry checkable.
    if item.get("DOI") and not compact:
        line += f"  [doi:{item['DOI']}](https://doi.org/{item['DOI']})"
    return line


def selected(items: list[dict], style: str) -> list[dict]:
    """The entries a rendering covers, newest first."""
    chosen = [i for i in items if i.get("_cv")] if style == "cv" else items
    return sorted(chosen, key=lambda i: (-(year(i) or 0), i.get("id", "")))


def group_of(item: dict):
    for group in GROUPS:
        if item.get("type") in group:
            return group
    return None


HEADER = [
    "<!-- Generated from bibliography.json by scripts/python/gen_publications.py.",
    "     Do not edit: `make publications` regenerates it. See ADR-006. -->",
    "",
]


def entry_md(item: dict, by_id: dict[str, dict], *, compact: bool) -> list[str]:
    """One entry, as the three lines and a link row it always renders as."""
    bullet, indent = ("1.", "   ") if compact else ("-", "  ")
    # The anchor lets the "selected" list at the top of the page point into the
    # record below rather than reprinting six entries.  attr_list attaches it
    # to the title's <strong>.
    anchor = "" if compact else f"{{ #{item['id']} }}"

    title = f"**{item['title']}**{anchor}"
    if item.get("_role") == "editor":
        title += " *(editor)*"
    lines = [f"{bullet} {title}  "]

    byline = authors_md(item).rstrip(".")
    if item.get("_note"):
        byline += f".  *{item['_note']}*"
    lines.append(f"{indent}{byline.rstrip('.')}.  ")

    imprint = imprint_md(item, compact=compact)
    if imprint:
        lines.append(f"{indent}{imprint}  ")

    links = links_md(item, by_id)
    if links:
        lines.append(f"{indent}{' · '.join(links)}")

    # Collapsed, because the page is for scanning and this is one click away.
    #
    # Four spaces, not `indent`: a block following a blank line inside a list
    # item needs a full tab_length of indentation in Python-Markdown, whatever
    # the bullet's width.  At two it leaves the list, and the `???` renders as
    # literal text above a code block -- which is what it did.
    if not compact and item.get("abstract"):
        lines += ["", '    ??? quote "Abstract"', "",
                  f"        {item['abstract']}"]
    lines.append("")
    return lines


def render(items: list[dict], style: str = "page") -> str:
    """The CV's list, or the whole record grouped by where it appeared."""
    # Resolving `_version-of` needs every entry, not just the rendered ones: the
    # CV may carry a proceedings paper whose preprint it does not list.
    by_id = {it["id"]: it for it in items if it.get("id")}
    lines = list(HEADER)

    if style == "cv":
        for it in selected(items, "cv"):
            lines += entry_md(it, by_id, compact=True)
        return "\n".join(lines).rstrip() + "\n"

    ordered = selected(items, "page")
    highlights = [it for it in ordered if it.get("_cv")]
    if highlights:
        lines += ["## Selected", "",
                  "The work most relevant to formal verification and to the roles"
                  " described on the [CV](cv.md), linked into the full record below.",
                  ""]
        for it in highlights:
            venue = it.get("container-title-short") or it.get("container-title") or ""
            venue = f", {venue}" if venue else ""
            lines.append(f"- [{it['title']}](#{it['id']}){venue}, {year(it)}")
        lines.append("")

    for group in GROUPS:
        members = [it for it in ordered if group_of(it) == group]
        if not members:
            continue
        lines += [f"## {GROUP_TITLES[group]}", ""]
        for it in members:
            lines += entry_md(it, by_id, compact=False)
    return "\n".join(lines).rstrip() + "\n"


# ── BibTeX ───────────────────────────────────────────────────────────────────

BIBTEX_TYPE = {
    "article-journal": "article",
    "paper-conference": "inproceedings",
    "article": "misc",
    "manuscript": "misc",
    "thesis": "phdthesis",
    "book": "book",
}

#: Characters BibTeX reads as syntax.
BIBTEX_ESCAPES = {
    "\\": r"\textbackslash{}",
    "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
    "_": r"\_", "{": r"\{", "}": r"\}",
}


def bibtex_escape(value: str) -> str:
    """Escape in one pass, never over the output of an earlier replacement.

    Sequential `str.replace` calls cannot do this: `\\` becomes
    `\textbackslash{}`, and the rule for `{` then escapes the braces that
    replacement just introduced.
    """
    return "".join(BIBTEX_ESCAPES.get(char, char) for char in value)


def bibtex_authors(item: dict) -> str:
    names = []
    for author in item.get("author") or []:
        if author.get("literal"):
            names.append(f"{{{bibtex_escape(author['literal'])}}}")
            continue
        family, given = author.get("family", ""), author.get("given", "")
        names.append(
            f"{bibtex_escape(family)}, {bibtex_escape(given)}" if given
            else bibtex_escape(family)
        )
    return " and ".join(names)


def bibtex_entry(item: dict) -> str:
    kind = BIBTEX_TYPE.get(item.get("type"), "misc")
    fields: list[tuple[str, str]] = []

    def put(name, value):
        if value not in (None, "", []):
            fields.append((name, str(value)))

    put("author", bibtex_authors(item))
    # Double braces so a style cannot case-fold "Agda", "Cardano" or "Birkhoff".
    # These titles were checked against the publishers; losing their capitals to
    # a .bst would undo that.
    put("title", f"{{{bibtex_escape(item['title'])}}}")

    venue = bibtex_escape(item.get("container-title") or "")
    if kind == "article":
        put("journal", venue)
    elif kind == "inproceedings":
        put("booktitle", venue)
    elif kind == "phdthesis":
        put("school", bibtex_escape(item.get("publisher") or ""))
    elif kind == "book":
        put("publisher", bibtex_escape(item.get("publisher") or ""))
    elif venue:
        put("howpublished", venue)

    put("series", bibtex_escape(item.get("collection-title") or ""))
    put("volume", item.get("volume"))
    put("number", item.get("issue"))
    put("pages", (item.get("page") or "").replace("-", "--"))
    parts = date_parts(item)
    put("year", parts[0] if parts else None)
    if len(parts) > 1 and 1 <= parts[1] <= 12:
        put("month", MONTHS[parts[1] - 1][:3].lower())
    put("address", bibtex_escape(item.get("event-place") or ""))
    put("doi", item.get("DOI"))

    if item.get("_arxiv"):
        put("eprint", item["_arxiv"])
        put("archivePrefix", "arXiv")
    # A URL that only restates the DOI or the eprint is noise in a .bib.
    url = item.get("URL")
    if url and not (
        (item.get("DOI") and item["DOI"] in url)
        or (item.get("_arxiv") and item["_arxiv"] in url)
    ):
        put("url", url)
    elif url and not item.get("DOI"):
        put("url", url)
    put("note", bibtex_escape(item.get("_note") or ""))

    width = max(len(name) for name, _ in fields)
    body = ",\n".join(f"  {name:<{width}} = {{{value}}}" for name, value in fields)
    return f"@{kind}{{{item['id']},\n{body}\n}}\n"


def render_bibtex(items: list[dict]) -> str:
    return "".join([
        "% Generated from bibliography.json by scripts/python/gen_publications.py.\n",
        "% Do not edit: `make publications` regenerates it.  See ADR-006.\n",
        "%\n",
        "% Encoded in UTF-8, so it wants biber/biblatex or inputenc with utf8.\n",
        "% Titles are double-braced: they were checked against the publishers,\n",
        "% and a .bst case-folding \"Agda\" or \"Birkhoff\" would undo that.\n",
        "\n",
    ] + [f"{bibtex_entry(it)}\n" for it in selected(items, "page")]).rstrip() + "\n"


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

    nothing_to_open = artifactless(items)
    if nothing_to_open:
        print(f"\nnothing for a reader to open ({len(nothing_to_open)}):")
        for entry_id in nothing_to_open:
            print(f"  {entry_id}")

    if review:
        print("\nunresolved, carried from the three-way reconciliation:")
        for it in review:
            print(f"  {it['id']}: {it['_needs_review']}")

    print()
    stale = []
    generated = [(path, render(items, style), len(selected(items, style)))
                 for style, path in OUTPUTS.items()]
    generated.append((BIBTEX, render_bibtex(items), len(items)))
    for path, wanted, count in generated:
        if args.check:
            # The generated files are committed, so "is the file current?" is a
            # real question with a real answer -- and one that was previously
            # claimed rather than asked.  A hand-edit to a generated snippet
            # survives every other check in this repository.
            current = path.read_text() if path.exists() else None
            if current == wanted:
                print(f"  {path.relative_to(REPO_ROOT)}: current ({count} entries)")
            else:
                stale.append(path)
                where = "missing" if current is None else "stale"
                print(f"  {path.relative_to(REPO_ROOT)}: {where}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(wanted)
            print(f"  wrote {path.relative_to(REPO_ROOT)} ({count} entries)")

    if stale:
        print(
            f"\n{len(stale)} generated file(s) do not match bibliography.json.\n"
            "Run `make publications` and commit the result.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
