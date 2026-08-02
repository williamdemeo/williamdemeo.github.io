#!/usr/bin/env python3
"""Reconcile the three hand-maintained publication lists that predate ADR-006.

#29's premise is that they disagree.  This finds out where, rather than
assuming, so the authoritative file is built from evidence and the places a
human has to adjudicate are named instead of quietly picked.
"""
import json
import pathlib
import re
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[2]
CV = ROOT / "docs/cv.md"
RESEARCH = ROOT / "import/zola-converted/research/index.md"
ZOTERO = ROOT / "import/legacy-bib-pubs.json"

ARXIV = re.compile(r"(?:arxiv\.org/abs/|arXiv:)(\d{4}\.\d{4,5}|[a-z-]+/\d{7})", re.I)
DOI = re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+")


def year_in(text):
    """A year, ignoring digits that belong to an arXiv id or a DOI.

    `arXiv:2010.04958` is not evidence of the year 2010, and reading it that way
    manufactured two disagreements that did not exist.
    """
    cleaned = ARXIV.sub(" ", text)
    cleaned = DOI.sub(" ", cleaned)
    cleaned = re.sub(r"\d{4}\.\d{4,5}", " ", cleaned)
    m = re.search(r"\b(?:19|20)\d{2}\b", cleaned)
    return int(m.group(0)) if m else None


def as_year(v):
    """Zotero writes date-parts as ints or strings; compare like with like."""
    try:
        return int(str(v)[:4])
    except (TypeError, ValueError):
        return None


def norm(t):
    """Title key: lowercase, alphanumerics only, so hyphenation and '&' vs
    'and' do not read as different papers."""
    t = t.lower().replace("&", "and").replace("\\", "")
    return re.sub(r"[^a-z0-9]+", "", t)


def from_cv():
    out = []
    body = CV.read_text()
    sec = body.split("## Selected publications", 1)[1].split("\nThe complete list", 1)[0]
    for block in re.split(r"\n(?=\d+\.\s)", sec):
        if not block.strip():
            continue
        m = re.search(r"\*\*(.+?)\*\*", block, re.S)
        if not m:
            continue
        title = " ".join(m.group(1).split())
        ax = ARXIV.search(block)
        doi = DOI.search(block)
        out.append({
            "title": title,
            "year": year_in(block),
            "arxiv": ax.group(1) if ax else None,
            "doi": doi.group(0).rstrip(")") if doi else None,
            "raw": " ".join(block.split())[:200],
        })
    return out


def from_research():
    out = []
    for line in RESEARCH.read_text().splitlines():
        if not line.startswith("* ["):
            continue
        m = re.match(r"\*\s*\[(.+?)\]\((.+?)\)", line)
        if not m:
            continue
        title = " ".join(m.group(1).split())
        ax = ARXIV.search(line)
        doi = DOI.search(line)
        out.append({
            "title": title,
            "year": year_in(line),
            "arxiv": ax.group(1) if ax else None,
            "doi": doi.group(0).rstrip(")") if doi else None,
            "raw": " ".join(line.split())[:220],
        })
    return out


def from_zotero():
    d = json.loads(ZOTERO.read_text())
    items = d if isinstance(d, list) else list(d.values())[0]
    out = []
    for it in items:
        issued = it.get("issued", {}).get("date-parts", [[None]])[0][0]
        blob = json.dumps(it)
        ax = ARXIV.search(blob)
        doi = DOI.search(it.get("DOI", "") or blob)
        out.append({
            "title": " ".join(str(it.get("title", "")).split()),
            "year": as_year(issued),
            "arxiv": ax.group(1) if ax else None,
            "doi": doi.group(0).rstrip('"') if doi else None,
            "raw": (it.get("container-title") or it.get("type") or "")[:120],
        })
    return out


sources = {"cv": from_cv(), "research": from_research(), "zotero": from_zotero()}
for name, entries in sources.items():
    print(f"{name:<9} {len(entries)} entries")

# Two entries are the same work if they share an arXiv id OR a normalized
# title.  Keying on one then regrouping by the other loses the link -- that is
# what split "Bounded homomorphisms and fiber products" from "...and finitely
# generated fiber products" into two papers when they share arXiv:1907.08046,
# hiding the very disagreement this script exists to find.
parent = {}


def find(x):
    parent.setdefault(x, x)
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        parent[ra] = rb


records = []
for name, entries in sources.items():
    for e in entries:
        rid = f"{name}:{len(records)}"
        records.append((rid, name, e))
        find(rid)
        union(rid, f"title:{norm(e['title'])}")
        if e["arxiv"]:
            union(rid, f"arxiv:{e['arxiv']}")

by_title = defaultdict(list)
for rid, name, e in records:
    by_title[find(rid)].append((rid, name, e))

print(f"\n{len(by_title)} distinct works across all three lists\n")

print("=" * 78)
print("DISAGREEMENTS")
print("=" * 78)
issues = 0
for t, rows in sorted(by_title.items()):
    seen = {n: e for _k, n, e in rows}
    titles = {n: e["title"] for n, e in seen.items()}
    years = {n: e["year"] for n, e in seen.items() if e["year"]}
    axs = {n: e["arxiv"] for n, e in seen.items() if e["arxiv"]}
    dois = {n: e["doi"] for n, e in seen.items() if e["doi"]}

    problems = []
    if len(set(titles.values())) > 1:
        problems.append(("title", titles))
    if len(set(years.values())) > 1:
        problems.append(("year", years))
    if len(set(axs.values())) > 1:
        problems.append(("arxiv", axs))
    if len(set(dois.values())) > 1:
        problems.append(("doi", dois))
    if problems:
        issues += 1
        print(f"\n  {list(titles.values())[0][:72]}")
        print(f"    in: {', '.join(sorted(seen))}")
        for field, vals in problems:
            print(f"    {field} differs:")
            for n, v in sorted(vals.items()):
                print(f"        {n:<9} {v}")

print(f"\n{issues} work(s) with conflicting metadata\n")

print("=" * 78)
print("COVERAGE")
print("=" * 78)
for t, rows in sorted(by_title.items(), key=lambda kv: -(kv[1][0][2]["year"] or 0)):
    seen = sorted({n for _k, n, _e in rows})
    e = rows[0][2]
    missing = [s for s in ("cv", "research", "zotero") if s not in seen]
    flag = "" if not missing else f"   [absent from: {', '.join(missing)}]"
    print(f"  {e['year'] or '????'}  {e['title'][:58]:<58}{flag}")
