#!/usr/bin/env python3
"""Prove that no CV entry was lost when four copies were merged into one.

`cv.yml` is the only authoritative CV source (ADR-003).  It was merged from four
copies that disagreed, and the failure that merge could plausibly have committed
is not a wrong date -- a wrong date is visible -- but an entry that quietly
stopped existing.  Ten years of teaching and thirty-odd talks are exactly the
kind of thing nobody notices the absence of.

So this does not check that `cv.yml` is well formed and then assert the rest in
prose.  It reads all four copies and asks, of every entry in every one of them,
whether `cv.yml` still says what that entry said:

  coverage    every entry in every source copy is *covered* -- some `cv.yml`
              entry contains all of its significant words -- or is named in
              `cv.yml`'s `omissions:` list with a reason.  There is no third
              outcome, which is the point.

  omissions   every declared omission names a source entry that exists.  A
              declaration that has stopped matching anything is how "nothing
              was lost" quietly becomes untrue again, so a stale one is a
              failure exactly like an uncovered entry.

  inventory   `import/legacy-cv/inventory.tsv` still matches what the
              extractors produce.  That file is committed, so the entries this
              reads are reviewable in a diff rather than conjured at run time
              -- and an extractor that breaks and starts finding nothing fails
              here rather than reporting a clean run over an empty list.

    python3 scripts/python/check_cv_sources.py [--write] [--explain]

Exit codes follow diff(1): 0 all good, 1 a check failed, 2 could not run.

## What "covered" means, and what it does not

An entry is covered when some `cv.yml` entry's text contains **every**
significant word of it.  Containment, not similarity: there is no partial
credit and no threshold to tune.  "Bounded homomorphisms and fiber products of
lattices" does not cover "Bounded homomorphisms and *finitely generated* fiber
products of lattices", and that is the intended behaviour -- the two copies
really do disagree, and the disagreement should surface here rather than be
smoothed over by a similarity score.

Three things it deliberately cannot see, named here rather than left for
someone to discover:

  URLs are stripped from both sides before comparison.  The copies link the
  same work through gitpitch, gitlab, arxiv and doi.org, at four different
  moments in the life of each of those hosts, and requiring `cv.yml` to carry
  every dead one would make this checker an argument for keeping dead links.
  `cv.yml` carries a URL per entry where a live one exists; that it is the
  *right* URL is not something this can know.

  Word order and grouping are invisible.  Covering text is covering text
  wherever it sits, so an entry filed under the wrong heading still counts as
  covered.  This proves nothing was lost, not that everything landed well.

  A copy this does not read cannot be checked.  The four are listed in SOURCES
  and in ADR-003; a fifth appearing somewhere is a problem for a person.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import unicodedata

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CV = REPO_ROOT / "cv.yml"
BIBLIOGRAPHY = REPO_ROOT / "bibliography.json"
INVENTORY = REPO_ROOT / "import" / "legacy-cv" / "inventory.tsv"

#: Keys in a `cv.yml` entry that are bookkeeping rather than content.  Their
#: values must not count toward covering anything -- `sources` in particular
#: holds the ids of the very entries being checked, so counting it would let
#: every entry cover itself.
BOOKKEEPING = {"sources", "id", "kind"}

#: Words too common to carry information.  A source line reduced to nothing but
#: these is skipped rather than reported: "and", on its own, is not an entry.
#:
#: The second group is hyperlink furniture -- the words that label a link
#: rather than say anything about the entry, as in "(preprint link)" or
#: "([slides](...))" or "Verified Certificate".  URLs are already out of scope
#: (see the module docstring), so these are the last trace of a link, and
#: requiring `cv.yml` to repeat them would be requiring it to describe its own
#: hyperlinks in prose.
STOPWORDS = frozenset("""
a an the of and or in on at for with to from by as is was were be been being
it its this that these those there here he she they we i you his her their our
my your not no nor but if then than so such into over under about after before
during between within without through across per via see also etc vs

link links slides preprint pdf html docs doi url verified certificate abstract
available
""".split())

#: Abbreviations expanded before comparison, on both sides.  This is
#: canonicalisation, not matching: the copies write the same venue as
#: "Intl. J. of Algebra and Computation" and "International Journal of Algebra
#: and Computation", and the same employer as "New Jersey Inst of Tech" and
#: "New Jersey Inst. of Technology".  Without this every such pair would be an
#: omission to declare, and a hundred declared non-omissions would bury the
#: handful that are real.
ABBREVIATIONS = {
    "intl": "international", "int": "international", "natl": "national",
    "conf": "conference", "proc": "proceedings", "symp": "symposium",
    "univ": "university", "dept": "department", "inst": "institute",
    "tech": "technology", "sci": "science", "assoc": "association",
    "amer": "american", "prof": "professor", "comp": "computer",
    "mt": "mountain", "pp": "pages", "page": "pages",
    # Months.  The copies write the same week as "April 14--18, 2019" and
    # "14--18 Apr 2019", and a summer school is not a different summer school
    # for being written the other way round.
    "jan": "january", "feb": "february", "mar": "march", "apr": "april",
    "jun": "june", "jul": "july", "aug": "august", "sep": "september",
    "sept": "september", "oct": "october", "nov": "november", "dec": "december",
}

#: Markup that carries no words: Markdown emphasis and link syntax, LaTeX
#: escapes, PDF-extract artifacts.  Stripped before tokenizing so `**Editor**`
#: and `Editor` are the same word.
MARKUP = re.compile(r"[*_`~\\{}\[\]()<>|#]+")
URL = re.compile(r"(?:https?://|www\.|mailto:)\S+", re.I)
MD_LINK = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")


def fold(text: str) -> str:
    """Lowercase, and strip diacritics so Ruškuc and Ruskuc are one name."""
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def tokens(text: str) -> set[str]:
    """The significant words of a piece of text.

    URLs go first and whole: tokenizing them yields `https`, `github`, `com`
    and a scatter of path fragments, which are either noise or -- worse -- a
    coincidental match.

    A link contributes both halves, and the URL rule then decides the target's
    fate.  Dropping every target instead would have been simpler and wrong: the
    Zola copy writes its referees as `[Clifford Bergman](cbergman@iastate.edu)`,
    with a bare address and no `mailto:`, so the whole email would have been
    invisible to the check and `cv.yml` could have dropped it silently.
    """
    text = MD_LINK.sub(r" \1 \2 ", text)
    text = URL.sub(" ", text)
    text = MARKUP.sub(" ", fold(text))
    words = (ABBREVIATIONS.get(w, w) for w in re.findall(r"[a-z0-9]+", text))
    return {w for w in words if w not in STOPWORDS and (len(w) > 1 or w.isdigit())}


def slug(text: str, limit: int = 44) -> str:
    words = re.findall(r"[a-z0-9]+", MARKUP.sub(" ", fold(URL.sub(" ", text))))
    out = "-".join(words)[:limit].strip("-")
    return out or "x"


# ── Reading the four copies ─────────────────────────────────────────────────
#
# Each copy is a different shape, so each gets its own reader.  They all return
# the same thing: a list of (section, text) pairs, in document order.
#
# Every reader errs toward *over*-extraction.  A spurious entry costs one line
# in `omissions:` and is obvious in review; a missed one is invisible, and is
# the entire failure this file exists to prevent.


DASH_RULE = re.compile(r"^-{3,}$")
LIST_MARKER = re.compile(r"^\s*(?:[-+*]|\d+[.)])\s+")
HARD_BREAK = re.compile(r"(?:\\|  )$")


def to_atx(text: str) -> str:
    """Rewrite setext headings as `# heading`, and drop horizontal rules.

    Both are a run of dashes on their own line, and what tells them apart is
    the line above: a heading underlines text, a rule follows a blank line.
    The Zola copy uses both, several times each.
    """
    lines = text.split("\n")
    out: list[str] = []
    for i, line in enumerate(lines):
        if not DASH_RULE.match(line.strip()):
            out.append(line)
            continue
        if i and lines[i - 1].strip() and out:
            out[-1] = f"# {out[-1].strip()}"
        # Either way the dash run itself is not content.
    return "\n".join(out)


def markdown_entries(text: str, heading: re.Pattern, *, setext: bool = False):
    """Blocks of a Markdown copy, filed under the heading above them.

    An entry is a run of non-blank lines, split further at list markers so a
    twelve-item numbered list is twelve entries rather than one.
    """
    if setext:
        text = to_atx(text)
    section, entries, current = "(preamble)", [], []

    def flush():
        # The bullet or ordinal a block opens with is enumeration, not content.
        # Left in, "7." makes `7` a word the entry is required to contain, and
        # the Zola copy's talks are numbered 1 to 34.
        body = LIST_MARKER.sub("", "\n".join(current).strip(), count=1).strip()
        if body:
            entries.append((section, body))
        current.clear()

    for line in text.split("\n"):
        found = heading.match(line)
        if found:
            flush()
            section = found.group(1).strip()
            continue
        if not line.strip():
            flush()
            continue
        if LIST_MARKER.match(line):
            flush()
        current.append(line)
        # A Markdown hard break -- a trailing backslash, or two spaces -- ends
        # a unit too.  Three of the copies use one to separate list entries
        # that have no blank line between them, and the `williamdemeo/cv`
        # Synergistic Activities section is five separate roles written as one
        # block that way.  Splitting here can only make units smaller, and a
        # smaller unit is a stricter thing to have to cover, not a looser one.
        if HARD_BREAK.search(line):
            flush()

    flush()
    return entries


def read_cv_repo(path: pathlib.Path):
    """`github.com/williamdemeo/cv`, README.md -- ATX headings, mixed lists."""
    return markdown_entries(path.read_text(encoding="utf-8"),
                            re.compile(r"^#\s+(.*)$"))


FRONT_MATTER = re.compile(r"\A\+\+\+.*?\+\+\+\n", re.S)


def read_zola(path: pathlib.Path):
    """The Zola site's `cv/index.md` -- TOML front matter, setext headings."""
    text = FRONT_MATTER.sub("", path.read_text(encoding="utf-8"))
    return markdown_entries(text, re.compile(r"^#\s+(.*)$"), setext=True)


YAML_FRONT_MATTER = re.compile(r"\A---\n.*?\n---\n", re.S)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)

#: A line that is one HTML tag and nothing else: `<div class="timeline"
#: markdown>` and the `</div>` closing it.  These wrap the M3-3 components the
#: page is built from (docs/design/style.md), and they are markup in the same
#: sense the Markdown emphasis `MARKUP` strips is -- a `</div>` is not an entry,
#: and reading it as one would ask `cv.yml` to contain the word "div".
HTML_BLOCK = re.compile(r"^\s*</?[a-z][^>]*>\s*$", re.I | re.M)


def read_site(path: pathlib.Path):
    """`docs/cv.md`, the page as it stands.

    Since #41 the page is generated from `cv.yml`, so what this reads back is a
    rendering of the source rather than a fourth opinion about it (ADR-003) --
    and the coverage check is what holds the renderer to saying only what the
    source says.

    The `--8<--` include is dropped rather than read: what it pulls in is
    generated from bibliography.json, so treating it as CV source would have
    this file re-checking ADR-006's output against itself.
    """
    text = HTML_COMMENT.sub("", YAML_FRONT_MATTER.sub("", path.read_text(encoding="utf-8")))
    text = re.sub(r"^--8<--.*$", "", text, flags=re.M)
    text = HTML_BLOCK.sub("", text)
    return markdown_entries(text, re.compile(r"^#{1,6}\s+(.*)$"))


#: The GitLab PDF's sidebar section labels, which the extract puts on their own
#: lines -- sometimes two, since the sidebar wraps.  A frozen snapshot, so a
#: fixed list is honest; `test_cv_sources.py` checks every one still matches.
PDF_SECTIONS = [
    ("Contact", "Information"), ("Research", "Interests"), ("Education",),
    ("Academic", "Appointments"), ("Industry", "Experience"), ("Publications",),
    ("Grants &", "Awards"), ("Synergistic", "Activities"),
    ("Data Science", "Certificates"), ("Summer Schools", "Attended"),
    ("Teaching", "Experience"), ("Talks",), ("Talks (cont.)",), ("References",),
]

#: Running heads.  Five of them, one per page, and each is the only line on
#: which the site URL and the email address appear together.
PDF_FURNITURE = re.compile(r"^williamdemeo\.org Page \d+ of \d+ williamdemeo@gmail\.com$")

#: The title block, which is typography rather than an entry.
PDF_TITLE = re.compile(r"^(William DeMeo|Curriculum Vitae)$")


def read_pdf_text(path: pathlib.Path):
    """`cv/demeo_cv.pdf` from the GitLab job-app repository, as text.

    One entry per line.  The extract has no blank lines to group by -- a PDF
    has no paragraphs, only positioned text -- so grouping would mean guessing
    where entries begin.  Line granularity guesses nothing: a wrapped entry
    arrives as several one-line entries, each of which has to be covered, which
    is a stricter requirement than covering them jointly rather than a weaker
    one.
    """
    lines = [l.rstrip() for l in path.read_text(encoding="utf-8").split("\n")]
    section, entries, i = "(preamble)", [], 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or PDF_FURNITURE.match(line) or PDF_TITLE.match(line):
            i += 1
            continue
        matched = next(
            (h for h in PDF_SECTIONS
             if [l.strip() for l in lines[i:i + len(h)]] == list(h)), None)
        if matched:
            section = " ".join(matched)
            i += len(matched)
            continue
        entries.append((section, LIST_MARKER.sub("", line).strip()))
        i += 1
    return entries


#: The four copies, in the order ADR-003 lists them.  A copy that is not here
#: is a copy nothing checks.
SOURCES = {
    "cvrepo": (REPO_ROOT / "import" / "legacy-cv" / "cv-repo-README.md", read_cv_repo),
    "zola": (REPO_ROOT / "import" / "zola-content" / "cv" / "index.md", read_zola),
    "jobapp": (REPO_ROOT / "import" / "legacy-cv" / "demeo_cv-2022.txt", read_pdf_text),
    "site": (REPO_ROOT / "docs" / "cv.md", read_site),
}


def extract() -> list[tuple[str, str, str]]:
    """Every entry of every copy, as (id, section, text).

    Ids are content-derived rather than positional, so reordering a copy does
    not renumber every declaration that refers to it.  A repeated line -- and
    "Math 122: Calculus for Business and Social Sciences" is there three times
    -- gets a numeric suffix.
    """
    rows, seen = [], {}
    for name, (path, reader) in SOURCES.items():
        if not path.exists():
            raise FileNotFoundError(path)
        for section, text in reader(path):
            if not tokens(text):
                continue
            base = f"{name}:{slug(section, 24)}:{slug(text)}"
            seen[base] = seen.get(base, 0) + 1
            entry_id = base if seen[base] == 1 else f"{base}~{seen[base]}"
            rows.append((entry_id, section, " ".join(text.split())))
    return rows


def write_inventory(rows) -> None:
    body = "".join(f"{i}\t{s}\t{t}\n" for i, s, t in rows)
    INVENTORY.parent.mkdir(parents=True, exist_ok=True)
    INVENTORY.write_text(HEADER + body, encoding="utf-8")


HEADER = (
    "# Every entry in the four CV copies ADR-003 merged, as extracted by\n"
    "# scripts/python/check_cv_sources.py.  Regenerate with `make cv-inventory`;\n"
    "# `make cv-check` fails when this file and the copies disagree.\n"
    "#\n"
    "# Committed so that what the checker reads is reviewable in a diff, and so\n"
    "# that an extractor which breaks and finds nothing fails a check instead of\n"
    "# reporting a clean run over an empty list.  Do not edit by hand.\n"
    "#\n"
    "# id\tsection\ttext\n"
)


def read_inventory() -> list[tuple[str, str, str]]:
    rows = []
    for line in INVENTORY.read_text(encoding="utf-8").split("\n"):
        if not line or line.startswith("#"):
            continue
        entry_id, section, text = line.split("\t")
        rows.append((entry_id, section, text))
    return rows


# ── cv.yml ──────────────────────────────────────────────────────────────────


def walk(node, into: list[str]) -> None:
    """Every string anywhere under `node`, bookkeeping keys excluded.

    Field *names* count as well as values.  A name is part of what an entry
    says -- `project_title:` is how this file writes the label the GitLab PDF
    prints as *Project Title:*, and `advisor:` the one the Zola copy writes as
    *Advisor:* -- so leaving names out would make every such label an entry
    with nothing to cover it.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            if key not in BOOKKEEPING:
                into.append(str(key).replace("_", " "))
                walk(value, into)
    elif isinstance(node, list):
        for item in node:
            walk(item, into)
    elif node is not None:
        into.append(str(node))


def cv_entries(data: dict) -> list[tuple[str, set[str]]]:
    """(label, token set) for every entry in cv.yml, omissions excluded."""
    out = []
    for section, value in data.items():
        if section in ("omissions", "meta"):
            continue
        items = value if isinstance(value, list) else [value]
        for i, item in enumerate(items):
            strings: list[str] = [str(section).replace("_", " ")]
            walk(item, strings)
            label = f"{section}[{i}]"
            if isinstance(item, dict):
                for key in ("title", "role", "name", "course", "degree", "ref"):
                    if item.get(key):
                        label = f"{section}: {item[key]}"
                        break
            out.append((label, tokens(" ".join(strings))))
    return out


def bibliography_entries() -> list[tuple[str, set[str]]]:
    """(label, token set) for every entry in bibliography.json.

    The legacy copies all carried a publication list, and none of those lists
    is reproduced in `cv.yml`: ADR-006 made `bibliography.json` the only
    authoritative one, and #16 must not undo that by giving publications a
    second home.  So publication entries are covered from *there*, which turns
    the boundary between the two files into something this can check rather
    than something the ADR merely asserts.

    Abstracts are excluded.  They are long enough to contain, by accident, all
    the words of some unrelated one-line entry, and covering an entry by
    accident is the one outcome worse than not covering it.
    """
    data = json.loads(BIBLIOGRAPHY.read_text(encoding="utf-8"))
    out = []
    for item in data["items"]:
        strings: list[str] = []
        walk({k: v for k, v in item.items() if k != "abstract"}, strings)
        out.append((f"bibliography.json: {item.get('id')}", tokens(" ".join(strings))))
    return out


def check(rows, data, *, explain: bool) -> tuple[list[str], int, int]:
    entries = cv_entries(data) + bibliography_entries()
    declared = {}
    for i, item in enumerate(data.get("omissions") or []):
        if not isinstance(item, dict) or not item.get("id") or not item.get("reason"):
            return [f"omissions[{i}]: needs both an `id` and a `reason`"], 0, 0
        declared[item["id"]] = item["reason"]

    anywhere: set[str] = set().union(*(have for _, have in entries)) if entries else set()

    problems, covered, omitted, seen = [], 0, set(), set()
    for entry_id, section, text in rows:
        want = tokens(text)
        by = next((label for label, have in entries if want <= have), None)
        if by is not None:
            covered += 1
            if explain:
                print(f"  ok   {entry_id}\n         <- {by}")
            if entry_id in declared:
                # Accounted for either way, so the stale-declaration sweep
                # below must not also report it.  One confused declaration is
                # one problem, not two.
                seen.add(entry_id)
                problems.append(
                    f"{entry_id}: declared an omission, but cv.yml covers it "
                    f"({by}).  Drop the declaration."
                )
            continue
        if entry_id in declared:
            seen.add(entry_id)
            omitted.add(entry_id)
            if explain:
                print(f"  drop {entry_id}\n         <- {declared[entry_id]}")
            continue
        # Two different failures, and the repair differs.  Words cv.yml does
        # not have anywhere are missing content; words it has, but scattered
        # across entries, mean the entry was split or filed in pieces.
        absent = sorted(want - anywhere)
        why = (f"cv.yml does not contain: {' '.join(absent)[:72]}" if absent else
               "every word is in cv.yml, but no single entry has them all")
        problems.append(
            f"{entry_id}\n      {section}: {text[:96]}\n      {why}"
        )

    for entry_id in declared:
        if entry_id not in seen:
            problems.append(
                f"{entry_id}: declared an omission, but no source entry has that id"
            )

    # `publications.carried` is documentation, and documentation that names a
    # publication which is not in bibliography.json is worse than none: it is
    # the CV claiming a paper the authoritative list does not have.
    known = {item.get("id") for item in
             json.loads(BIBLIOGRAPHY.read_text(encoding="utf-8"))["items"]}
    for ref in (data.get("publications") or {}).get("carried") or []:
        if ref not in known:
            problems.append(f"publications.carried: {ref!r} is not in bibliography.json")

    return problems, covered, len(omitted)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true",
                    help="regenerate the inventory from the copies; check nothing")
    ap.add_argument("--explain", action="store_true",
                    help="print what covers each source entry")
    args = ap.parse_args(argv)

    try:
        rows = extract()
    except (OSError, ValueError) as exc:
        print(f"error: reading the CV copies: {exc}", file=sys.stderr)
        return 2

    for name in SOURCES:
        print(f"  {name:<8} {sum(1 for r in rows if r[0].startswith(name + ':')):>4} entries")
    print(f"  {'total':<8} {len(rows):>4}")

    if args.write:
        write_inventory(rows)
        print(f"\nwrote {INVENTORY.relative_to(REPO_ROOT)} ({len(rows)} entries)")
        return 0

    try:
        committed = read_inventory()
    except (OSError, ValueError) as exc:
        print(f"error: {INVENTORY}: {exc}\nRun `make cv-inventory`.", file=sys.stderr)
        return 2
    if committed != rows:
        stale = {r[0] for r in rows} ^ {r[0] for r in committed}
        print(f"\nerror: {INVENTORY.relative_to(REPO_ROOT)} does not match the copies "
              f"({len(stale)} id(s) differ).\nRun `make cv-inventory` and review the "
              f"diff before committing it.", file=sys.stderr)
        return 1

    try:
        data = yaml.safe_load(CV.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        print(f"error: {CV}: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print(f"error: {CV}: expected a mapping at the top level", file=sys.stderr)
        return 2

    print()
    problems, covered, omitted = check(rows, data, explain=args.explain)
    print(f"  covered  {covered}")
    print(f"  omitted  {omitted} (declared, with reasons)")
    if problems:
        print(f"\n{len(problems)} problem(s):\n", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}\n", file=sys.stderr)
        print(
            "Every entry in every copy has to survive into cv.yml or be dropped on\n"
            "purpose.  Add it to cv.yml, or add its id to `omissions:` with the\n"
            "reason it is not being carried forward.  See ADR-003.",
            file=sys.stderr,
        )
        return 1

    print("\n✓ every entry in all four CV copies is carried or declared.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
