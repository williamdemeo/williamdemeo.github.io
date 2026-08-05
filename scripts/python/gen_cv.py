#!/usr/bin/env python3
"""Render cv.yml to the CV page and to the CV's PDF.

`cv.yml` is the only authoritative CV source (ADR-003) and `bibliography.json`
the only authoritative publication list (ADR-006).  This turns the first into
`docs/cv.md` and `cv/cv.typ`, and takes the publications from the second by way
of the two files `gen_publications.py` renders there -- so the page and the PDF
are two renderings of one pair of files rather than two documents that agree
today.  ADR-010 records the toolchain.

    gen_cv.py                  write the page and the Typst source
    gen_cv.py --pdf            ... and compile the PDF
    gen_cv.py --check          compare the committed files against a fresh render
    gen_cv.py --check --pdf    ... and against a fresh compile of the PDF

Exit codes follow diff(1): 0 fine, 1 a check failed, 2 could not run.

## What decides what

One list of sections is built from `cv.yml`, and two renderers turn it into
Markdown and into Typst.  Neither renderer decides *what the CV says* -- that is
`build()`, once -- so the page and the PDF cannot disagree about a title, a date
or a coauthor.  They differ in what a page is: the web one uses the components
M3-3 built (`timeline`, `talks`), the PDF one a two-column entry with the dates
in the gutter.

## Why the page is checkable

`docs/cv.md` is one of the four copies `check_cv_sources.py` reads, so every
block this emits has to be covered by a single `cv.yml` entry.  That is not a
constraint to work around; it is the thing that makes "the page says only what
the source says" a check rather than a claim.  Two rules follow, and both are
observed below:

  * **A block is never assembled from two entries.**  One rendered block, one
    `cv.yml` entry.
  * **Every word rendered comes from the entry, or from nowhere.**  Link labels
    are the interesting case: "Slides", "Preprint", "PDF", "Certificate" and
    "Link" are in that checker's stopword list precisely because they label a
    hyperlink rather than say anything, so they are free.  A label that is *not*
    free -- the three bare URLs on the Textron entry -- is taken from the words
    of the entry itself, by `label_for`.

Page chrome that says nothing about the career -- the download button, the
pointer to the publications page -- is declared in `cv.yml`'s `omissions:`, as
the page's chrome always has been.
"""

from __future__ import annotations

import argparse
import datetime
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "cv.yml"
PAGE = REPO_ROOT / "docs" / "cv.md"
TYPST = REPO_ROOT / "cv" / "cv.typ"
PDF = REPO_ROOT / "docs" / "assets" / "DeMeo-CV.pdf"

#: What the page's download button points at, relative to `docs/`.  Keeping the
#: name it has always had is what keeps the URL stable: `/assets/DeMeo-CV.pdf`
#: is what the site serves today, so nothing in `redirects.yml` has to move.
PDF_HREF = "assets/DeMeo-CV.pdf"

#: Rendered by `gen_publications.py` from `bibliography.json`, and included
#: rather than re-rendered here: `cv.yml` holds publication ids and no
#: publication metadata, so this file could not render them if it wanted to.
PUBLICATIONS_SNIPPET = "publications-cv.md"
PUBLICATIONS_TYPST = "publications.typ"
PUBLICATIONS_PAGE_URL = "https://williamdemeo.org/publications/"


# ── Runs ─────────────────────────────────────────────────────────────────────
#
# The same idea as `gen_publications.py`'s: a piece of text, the emphasis it
# carries, and where it links.  Everything below builds runs, and the two
# renderers at the bottom are the only code that knows what a link looks like.

Run = tuple[str, str | None, str | None]

EM_DASH, EN_DASH = "—", "–"
MIDDLE_DOT = " · "


def dashes(text: str) -> str:
    """`--` as the source writes it, as the dash it means.

    Three of the four copies were LaTeX or came from it, so `cv.yml` carries
    `25--30 Nov 2024` and `April 12--16, 2021`.  Neither renderer has smart
    substitution turned on -- `smarty` is not among the site's Markdown
    extensions, and Typst never sees these as markup -- so the substitution
    happens here, once, for both.
    """
    return text.replace("---", EM_DASH).replace("--", EN_DASH)


def t(text, style: str | None = None, url: str | None = None) -> Run:
    return (dashes(str(text)), style, url)


def join(parts: list[list[Run]], separator: str = ", ") -> list[Run]:
    """Runs joined by a separator, skipping the parts that are empty."""
    out: list[Run] = []
    for part in [p for p in parts if p]:
        if out:
            out.append(t(separator))
        out += part
    return out


class Entry:
    """One thing that happened: a date, what it was, and the detail beneath.

    `term` is the date gutter; `head` the first line; `body` the lines under it;
    `items` the entries nested inside it, which only teaching and the summer
    schools have.  Every one of them is optional, and a renderer that meets an
    entry without a date or without a body leaves the space out rather than
    leaving it empty (the M3-3 rule -- see docs/design/style.md).
    """

    def __init__(self, term: str = "", head=(), body=(), items=()):
        self.term = dashes(term)
        self.head: list[Run] = list(head)
        self.body: list[list[Run]] = [list(line) for line in body if line]
        self.items: list[Entry] = list(items)


class Section:
    def __init__(self, title: str, kind: str, entries=(), note=()):
        self.title = title
        self.kind = kind
        self.entries: list[Entry] = list(entries)
        self.note: list[Run] = list(note)


# ── Reading cv.yml ───────────────────────────────────────────────────────────


def text_of(value) -> str:
    """A YAML scalar as one line.

    Folded block scalars arrive already folded, so this is only about the ones
    that were not.  Runs of spaces *inside* a line are left alone: the house
    style puts two after a full stop, and neither renderer shows the difference.
    """
    return re.sub(r"\s*\n\s*", " ", str(value)).strip()


def sentence_case(text: str) -> str:
    """Capitalise the first letter and nothing else.

    Not `str.capitalize`, which lowercases the rest -- and so turned "univalent
    type theory in Agda" into "... in agda", which is a different thing.
    """
    return text[:1].upper() + text[1:] if text else text


def strip_scheme(url: str) -> str:
    return re.sub(r"^https?://", "", url).rstrip("/")


WORD = re.compile(r"[A-Za-z0-9]+")


def label_for(url: str, source: str) -> str:
    """A bare URL's label, taken from the words of the entry it sits on.

    Three links on the Textron entry are URLs and nothing else -- AFOSR, the
    Haleakala Observatories, the MHPCC supercomputer -- and all three are named
    in the entry's own note.  Matching the URL against the phrases of that note
    labels them the way a person would, and it cannot introduce a word the entry
    does not have, which is what `check_cv_sources.py` requires of this page.

    Falls back to "Link", which that checker treats as hyperlink furniture and
    so requires nothing of.
    """
    target = "".join(WORD.findall(url.lower()))
    words = WORD.findall(source)
    best = ""
    for size in range(4, 0, -1):
        for i in range(len(words) - size + 1):
            phrase = words[i:i + size]
            if "".join(phrase).lower() in target and len(" ".join(phrase)) > len(best):
                best = " ".join(phrase)
        if best:
            return best
    return "Link"


def linked(label: str, url: str | None, style: str | None = None) -> list[Run]:
    return [t(label, style, url)] if url else [t(label, style)]


def years(item: dict) -> str:
    """The date gutter: a range, an open range, or a single year."""
    start, end = item.get("start"), item.get("end")
    if start and end:
        # "present" is not a year, and a range with nothing after the dash is
        # how the timeline component writes an open one (docs/design/style.md).
        return f"{start}{EN_DASH}" if str(end) == "present" else f"{start}{EN_DASH}{end}"
    for key in ("year", "start", "completed", "earned"):
        if item.get(key):
            return str(item[key]).split()[-1]
    return EN_DASH


# ── The sections, in the order cv.yml declares them ──────────────────────────


def education(data) -> Section:
    entries = []
    for item in data["education"]:
        head = [t(item["degree"], "strong"), t(" " + EM_DASH + " ")]
        head += linked(item["institution"], item.get("institution_url"))
        if item.get("place"):
            head += [t(", " + item["place"])]
        body = []
        if item.get("thesis"):
            line = [t("Thesis: ")] + linked(item["thesis"], item.get("thesis_url"))
            body.append(line + [t(".")])
        if item.get("advisor"):
            body.append([t("Advisor: ")] + linked(item["advisor"], item.get("advisor_url")) + [t(".")])
        entries.append(Entry(term=years(item), head=head, body=body))
    return Section("Education", "timeline", entries)


def appointments(data) -> Section:
    entries = []
    for item in data["appointments"]:
        head = [t(item["role"], "strong")]
        where = item.get("department") or item.get("team")
        if where:
            head += [t(", " + where)]
        head += [t(" " + EM_DASH + " ")] + linked(item["institution"], item.get("url"))
        if item.get("place"):
            head += [t(", " + item["place"])]

        body = []
        if item.get("note"):
            body.append([t(text_of(item["note"]))])
        links = []
        if item.get("project_url"):
            links.append(linked("Project", item["project_url"]))
        for url in item.get("links") or []:
            links.append(linked(label_for(url, text_of(item.get("note", ""))), url))
        if links:
            body.append(join(links, MIDDLE_DOT))
        entries.append(Entry(term=years(item), head=head, body=body))
    return Section("Appointments", "timeline", entries)


def grants(data) -> Section:
    entries = []
    for item in data["grants_and_awards"]:
        head = [t(item["title"], "strong")]
        if item.get("number"):
            head += [t(" " + item["number"])]
        if item.get("for"):
            # One award writes "for Outstanding Research in Mathematics" and the
            # other names the symposium outright, so the separator depends on
            # which of the two this is rather than being fixed.
            award_for = item["for"]
            head += [t((" " if award_for.lower().startswith("for ") else ", ") + award_for)]
        if item.get("place"):
            head += [t(", " + item["place"])]
        body = []
        if item.get("project_title"):
            body.append(linked(item["project_title"], item.get("url"), "em") + [t(".")])
        elif item.get("url"):
            body.append(linked(label_for(item["url"], text_of(item.get("description", ""))),
                               item["url"]))
        for key in ("role", "description"):
            if item.get(key):
                line = text_of(item[key])
                # `description` is where the Magellan entry says "See
                # soundmath.github.io/...", which the line above has already
                # rendered as a link on the project title.
                if key == "description" and item.get("url") and line.lower().startswith("see "):
                    continue
                body.append([t(line + ("." if not line.endswith(".") else ""))])
        entries.append(Entry(term=years(item), head=head, body=body))
    return Section("Grants and awards", "timeline", entries)


def publications(data) -> Section:
    return Section(
        "Selected publications", "publications",
        note=[t("The complete record, with abstracts, is on the ")]
        + linked("publications page", PUBLICATIONS_PAGE_URL)
        + [t(".")],
    )


def projects(data) -> Section:
    entries = []
    for item in data["projects"]:
        head = linked(item["title"], item.get("url"), "strong")
        body = []
        if item.get("with"):
            names = item["with"]
            with_whom = (names[0] if len(names) == 1
                         else ", ".join(names[:-1]) + " and " + names[-1])
            body.append([t(f"With {with_whom}.")])
        if item.get("status"):
            body.append([t(sentence_case(item["status"]) + ".")])
        # `note:` is deliberately not rendered here.  In `appointments:` it is
        # what the post involved; in `projects:` it is a note to whoever edits
        # the file -- which ADR it answers to, which issue decides its home.
        entries.append(Entry(head=head, body=body))
    return Section("Projects", "list", entries)


def teaching(data) -> Section:
    entries = []
    for group in data["teaching"]:
        head = [t(group["institution"], "strong")]
        if group.get("as"):
            head += [t(" " + EM_DASH + " " + group["as"])]
        courses = []
        for course in group["courses"]:
            line = linked(course["code"], course.get("url"), "strong")
            line += [t(" " + course["title"])]
            tail = [x for x in (course.get("level"), course.get("note"), course.get("term")) if x]
            if tail:
                line += [t(" " + EM_DASH + " " + ", ".join(tail))]
            courses.append(Entry(head=line))
        entries.append(Entry(head=head, items=courses))
    return Section("Teaching", "groups", entries)


def talks(data) -> Section:
    entries = []
    for item in data["talks"]:
        # "The slides link goes on the title rather than in a row of its own, so
        # a talk with no slides is simply a title that is not a link" -- the
        # talk component, docs/design/style.md.  Most of these have slides and
        # no event page, so following it saves a line on two thirds of them.
        primary = "url" if item.get("url") else "slides"
        head = linked(item["title"], item.get(primary), "strong")
        venue = [x for x in (item.get("venue"), item.get("place"), str(item.get("year") or ""))
                 if x]
        line = [t(", ".join(venue))]
        if item.get("note"):
            line += [t(MIDDLE_DOT + item["note"])]
        extra = []
        for label, key in (("Slides", "slides"), ("Preprint", "preprint"),
                           ("Abstract", "abstract_url"), ("Docs", "docs")):
            if item.get(key) and key != primary:
                extra.append(linked(label, item[key]))
        body = [line] + ([join(extra, MIDDLE_DOT)] if extra else [])
        entries.append(Entry(head=head, body=body))
    return Section("Talks", "talks", entries)


def service(data) -> Section:
    entries = []
    for item in data["service"]:
        head = [t(item["role"], "strong")]
        if item.get("what"):
            head += [t(", ")] + linked(item["what"], item.get("url"))
        if item.get("note"):
            head += [t(", " + item["note"])]
        if item.get("institution"):
            head += [t(" " + EM_DASH + " " + item["institution"])]
        span = years(item) if (item.get("year") or item.get("start")) else ""
        where = ", ".join(x for x in (item.get("place"), span) if x)
        if where:
            head += [t(", " + where)]
        body = [[t(text_of(item["description"]))]] if item.get("description") else []
        entries.append(Entry(head=head, body=body))
    return Section("Service", "list", entries)


def advising(data) -> Section:
    entries = []
    for item in data["advising"]:
        head = [t(item["institution"], "strong")]
        body = [[t(text_of(item["what"]))]]
        if item.get("url"):
            body.append(linked("Link", item["url"]))
        entries.append(Entry(head=head, body=body))
    return Section("Advising and mentoring", "list", entries)


def certifications(data) -> Section:
    entries = []
    for item in data["certifications"]:
        head = [t(item["title"], "strong")]
        detail = [x for x in (item.get("provider"), item.get("length"),
                              item.get("grade"), item.get("earned")) if x]
        line = [t(", ".join(detail))]
        if item.get("certificate"):
            line += [t(MIDDLE_DOT)] + linked("Certificate", item["certificate"])
        entries.append(Entry(head=head, body=[line]))
    return Section("Certifications", "list", entries)


def summer_schools(data) -> Section:
    entries = []
    for item in data["summer_schools"]:
        head = linked(item["title"], item.get("url"), "strong")
        where = [x for x in (item.get("institution"), item.get("place")) if x]
        dates = item.get("dates") or (str(item["year"]) if item.get("year") else "")
        first = ", ".join(where + ([dates] if dates else []))
        body = [[t(first)]] if first else []
        if item.get("topics"):
            body.append([t(sentence_case(text_of(item["topics"])) + ".")])
        nested = []
        for visit in item.get("attended") or []:
            line = [x for x in (visit.get("institution"), visit.get("note"),
                                visit.get("dates")) if x]
            nested.append(Entry(head=linked(", ".join(line), visit.get("url"))))
        entries.append(Entry(head=head, body=body, items=nested))
    return Section("Summer schools and short courses", "list", entries)


def references(data) -> Section:
    entries = []
    for item in data["references"]:
        head = [t(item["name"], "strong")]
        detail = [x for x in (item.get("title"), item.get("institution")) if x]
        if detail:
            head += [t(", " + ", ".join(detail))]
        if item.get("teaching_reference"):
            head += [t(" (teaching reference)")]
        entries.append(Entry(head=head))
    # The addresses are in cv.yml and are deliberately not rendered.  ADR-003
    # dropped the referees' office addresses and telephone numbers from the
    # merge on the grounds that a CV published on a website is not a CV mailed
    # to a search committee; an email address is the same thing, and it is
    # their exposure rather than William's.
    return Section("References", "list", entries)


def build(data) -> list[Section]:
    interests = data["research_interests"][0]
    return [
        Section("Research interests", "prose", [
            Entry(body=[[t(text_of(interests["summary"]))]]),
            Entry(body=[[t("Theory", "strong"), t(". " + text_of(interests["theory"]))]]),
            Entry(body=[[t("Practice", "strong"), t(". " + text_of(interests["practice"]))]]),
        ]),
        education(data),
        appointments(data),
        grants(data),
        publications(data),
        projects(data),
        teaching(data),
        talks(data),
        service(data),
        advising(data),
        certifications(data),
        summer_schools(data),
        references(data),
    ]


# ── The page ─────────────────────────────────────────────────────────────────

MD_MARKUP = {"strong": "**{}**", "em": "*{}*"}
MD_ESCAPE = re.compile(r"([\\*_`\[\]])")

PAGE_HEADER = """---
title: CV
description: >-
  Curriculum vitae of William DeMeo: research interests, education,
  appointments, publications, teaching, talks and service.
---

<!-- Generated from cv.yml by scripts/python/gen_cv.py.
     Do not edit: `make cv` regenerates it, and `make cv-render-check` fails
     when it is stale.  The publications below are the include on its own
     line, rendered from bibliography.json.  See ADR-003, ADR-006, ADR-010. -->

# Curriculum vitae
"""


def md_runs(runs: list[Run]) -> str:
    out = []
    for text, style, url in runs:
        piece = MD_ESCAPE.sub(r"\\\1", text)
        # `**[title](url)**`, the way docs/design/style.md writes a talk: the
        # emphasis is the entry's, and the link sits inside it.
        piece = f"[{piece}]({url})" if url else piece
        out.append(MD_MARKUP.get(style, "{}").format(piece))
    return "".join(out)


def md_entry(entry: Entry, kind: str) -> list[str]:
    """One entry, as the block the checker will read it back as.

    Every line but the last carries a Markdown hard break, which is what holds
    a multi-line entry together on the page -- and what splits it into one
    checked unit per line, each of which has to be covered on its own.
    """
    lines = []
    if kind == "timeline":
        lines.append(entry.term)
        lines.append(f":   {md_runs(entry.head)}")
        lines += [f"    {md_runs(line)}" for line in entry.body]
    else:
        lines.append(f"- {md_runs(entry.head)}" if entry.head else "-")
        lines += [f"  {md_runs(line)}" for line in entry.body]
    body = [f"{line}  " for line in lines[:-1]] + [lines[-1]]
    for item in entry.items:
        body += [f"    - {md_runs(item.head)}"]
    return body


def render_page(sections: list[Section], data: dict) -> str:
    contact = data["contact"]
    out = [PAGE_HEADER.rstrip(), ""]
    out += [f"[:material-file-download: Download PDF]({PDF_HREF})" + "{ .md-button }", ""]
    out += [md_runs([t(contact["email"], None, f"mailto:{contact['email']}"),
                     t(MIDDLE_DOT)]
                    + linked(strip_scheme(contact["url"]), contact["url"])), ""]

    for section in sections:
        out += [f"## {section.title}", ""]
        if section.kind == "publications":
            out += [f'--8<-- "{PUBLICATIONS_SNIPPET}"', ""]
        elif section.kind == "prose":
            for entry in section.entries:
                out += [md_runs(line) for line in entry.body] + [""]
        elif section.kind == "groups":
            for entry in section.entries:
                out += [md_runs(entry.head), ""]
                out += [f"- {md_runs(item.head)}" for item in entry.items] + [""]
        else:
            wrapper = {"timeline": "timeline", "talks": "talks"}.get(section.kind)
            if wrapper:
                out += [f'<div class="{wrapper}" markdown>', ""]
            for entry in section.entries:
                out += md_entry(entry, section.kind) + [""]
            if wrapper:
                out += ["</div>", ""]
        if section.note:
            out += [md_runs(section.note), ""]

    return "\n".join(out).rstrip() + "\n"


# ── The Typst source ─────────────────────────────────────────────────────────
#
# Data, not layout: `cv/template.typ` decides how a page of this looks, and is
# hand-written Typst.  Keeping the generated half free of layout is what makes
# its diff readable when `cv.yml` changes -- and the PDF check compiles the two
# together, so an edit to either without a rebuild fails.


def typst_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def typst_array(items: list[str]) -> str:
    if not items:
        return "()"
    if len(items) == 1:
        return f"({items[0]},)"
    return "(" + ", ".join(items) + ")"


def typst_runs(runs: list[Run]) -> str:
    return typst_array([
        f"({typst_string(text)}, {typst_string(style) if style else 'none'}, "
        f"{typst_string(url) if url else 'none'})"
        for text, style, url in runs
    ])


def typst_entry(entry: Entry, indent: str) -> list[str]:
    lines = [f"{indent}("]
    if entry.term:
        lines.append(f"{indent}  term: {typst_string(entry.term)},")
    if entry.head:
        lines.append(f"{indent}  head: {typst_runs(entry.head)},")
    if entry.body:
        lines.append(f"{indent}  body: (")
        lines += [f"{indent}    {typst_runs(line)}," for line in entry.body]
        lines.append(f"{indent}  ),")
    if entry.items:
        lines.append(f"{indent}  items: (")
        for item in entry.items:
            lines += typst_entry(item, indent + "    ")
        lines.append(f"{indent}  ),")
    lines.append(f"{indent}),")
    return lines


def render_typst(sections: list[Section], data: dict, built: datetime.date) -> str:
    contact = data["contact"]
    meta = data["meta"]
    out = [
        "// Generated from cv.yml by scripts/python/gen_cv.py.",
        "// Do not edit: `make cv` regenerates it.  See ADR-003, ADR-010.",
        "//",
        "// Data only.  cv/template.typ is the layout, and is written by hand.",
        "//",
        "// `built` is the date this file was generated, and is what the footer",
        "// prints.  It is here rather than taken from the clock at compile time so",
        "// that the PDF is a function of files in the repository: `gen_cv.py",
        "// --check --pdf` recompiles with this date and compares the bytes, which",
        "// it could not do against a date that changed on every build.",
        "",
        '#import "template.typ": cv-document, render-sections',
        f'#import "{PUBLICATIONS_TYPST}": publications',
        "",
        f"#let built = datetime(year: {built.year}, month: {built.month}, day: {built.day})",
        "",
        "#show: cv-document.with(",
        f"  name: {typst_string(meta['name'])},",
        f"  title: {typst_string(meta['title'])},",
        f"  email: {typst_string(contact['email'])},",
        f"  url: {typst_string(contact['url'])},",
        "  built: built,",
        ")",
        "",
        "#let sections = (",
    ]
    for section in sections:
        out.append("  (")
        out.append(f"    title: {typst_string(section.title)},")
        out.append(f"    kind: {typst_string(section.kind)},")
        if section.kind == "publications":
            out.append("    publications: publications,")
        if section.note:
            out.append(f"    note: {typst_runs(section.note)},")
        out.append("    entries: (")
        for entry in section.entries:
            out += typst_entry(entry, "      ")
        out.append("    ),")
        out.append("  ),")
    out += [")", "", "#render-sections(sections)"]
    return "\n".join(out) + "\n"


BUILT = re.compile(r"^#let built = datetime\(year: (\d+), month: (\d+), day: (\d+)\)$", re.M)


def built_date(source: str) -> datetime.date | None:
    found = BUILT.search(source)
    return datetime.date(*(int(g) for g in found.groups())) if found else None


# ── The PDF ──────────────────────────────────────────────────────────────────


def compile_pdf(destination: pathlib.Path) -> None:
    """Compile `cv/cv.typ`, using Typst's own fonts and nothing else.

    `--ignore-system-fonts` is what makes the result the same file everywhere:
    with it the only inputs are the Typst binary, the two `.typ` files and the
    date inside one of them, so the same nixpkgs `typst` gives the same bytes on
    a laptop and on a CI runner.  Verified: identical output from a different
    directory, timezone and locale.
    """
    typst = shutil.which("typst")
    if typst is None:
        raise FileNotFoundError(
            "typst is not on PATH.  It is in the dev shell: `nix develop`, or "
            "`nix run nixpkgs#typst`.  See ADR-010."
        )
    subprocess.run(
        [typst, "compile", "--ignore-system-fonts", "--root", str(REPO_ROOT),
         str(TYPST), str(destination)],
        check=True,
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="compare the committed files against a fresh render")
    ap.add_argument("--pdf", action="store_true", help="also build (or check) the PDF")
    ap.add_argument("--date", help="the build date to stamp, as YYYY-MM-DD")
    args = ap.parse_args(argv)

    try:
        data = yaml.safe_load(SOURCE.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        print(f"error: {SOURCE}: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print(f"error: {SOURCE}: expected a mapping at the top level", file=sys.stderr)
        return 2

    committed = TYPST.read_text(encoding="utf-8") if TYPST.exists() else ""
    if args.date:
        built = datetime.date.fromisoformat(args.date)
    elif args.check:
        # The one thing a fresh render cannot know.  Taking it from the file
        # being checked is what keeps the comparison exact everywhere else: a
        # date read from the clock would differ every day and the check would
        # have to forgive a difference, which is how a check stops catching
        # things.  A file with no date in it fails below rather than passing.
        built = built_date(committed) or datetime.date.today()
    else:
        built = datetime.date.today()

    sections = build(data)
    outputs = [(PAGE, render_page(sections, data)),
               (TYPST, render_typst(sections, data, built))]

    entries = sum(len(s.entries) for s in sections)
    print(f"cv.yml: {len(sections)} section(s), {entries} entries, built {built}")

    stale = []
    for path, wanted in outputs:
        if args.check:
            current = path.read_text(encoding="utf-8") if path.exists() else None
            if current == wanted:
                print(f"  {path.relative_to(REPO_ROOT)}: current")
            else:
                stale.append(path)
                print(f"  {path.relative_to(REPO_ROOT)}: "
                      f"{'missing' if current is None else 'stale'}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(wanted, encoding="utf-8")
            print(f"  wrote {path.relative_to(REPO_ROOT)}")

    if args.check and built_date(committed) is None and TYPST not in stale:
        # The date is the one thing `--check` takes from the file it is checking,
        # so a file without one would otherwise be compared against today's and
        # pass on the day it was written.
        print(f"  {TYPST.relative_to(REPO_ROOT)}: no build date in it", file=sys.stderr)
        stale.append(TYPST)

    if args.pdf and not stale:
        try:
            if args.check:
                # Somewhere writable.  Under `nix flake check` the source is a
                # store path, and a check that has to write next to the file it
                # is checking is a check that cannot run in a sandbox.
                with tempfile.TemporaryDirectory() as tmp:
                    fresh = pathlib.Path(tmp) / PDF.name
                    compile_pdf(fresh)
                    same = PDF.exists() and fresh.read_bytes() == PDF.read_bytes()
                print(f"  {PDF.relative_to(REPO_ROOT)}: "
                      f"{'current' if same else 'stale'} ({built})")
                if not same:
                    stale.append(PDF)
            else:
                compile_pdf(PDF)
                print(f"  wrote {PDF.relative_to(REPO_ROOT)} ({PDF.stat().st_size:,} bytes)")
        except (FileNotFoundError, subprocess.CalledProcessError) as exc:
            print(f"error: compiling the PDF: {exc}", file=sys.stderr)
            return 2

    if stale:
        print(
            f"\n{len(stale)} file(s) do not match cv.yml.\n"
            "Run `make cv` (and `make cv-pdf`) and commit the result.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
