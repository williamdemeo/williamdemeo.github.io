#!/usr/bin/env python3
"""Check bibliography.json against the publishers that hold the records.

ADR-006 built bibliography.json by reconciling three hand-maintained lists.
Reconciling makes the copies agree with each other; it does not make them
right.  This asks the publishers instead:

    https://api.crossref.org/works/{DOI}             for every entry with a DOI
    http://export.arxiv.org/api/query?id_list={id}   for every entry with an
                                                     arXiv identifier

and reports every difference between what came back and what the file claims,
across title, authors, container-title, volume, page and year.

Crossref does not index every DOI.  Dagstuhl registers LIPIcs and OASIcs with
DataCite, so a Crossref 404 asks the registration-agency endpoint who owns the
DOI and follows it to

    https://api.datacite.org/dois/{DOI}

when the answer is DataCite.  A DOI no agency claims at all is a defect in the
file, and is reported as one.

Two failure modes it is built to avoid, both learned the hard way in this
repository:

*A blocked network must not read as a clean bill of health.*  Anything that
stops us talking to a service -- DNS, a refused CONNECT, a timeout, a 5xx, a
rate limit -- is a hard error, and so is a partial run: "12 of 15 checked, 3
unreachable" is a failure, not a pass.  A checker that goes green because the
network is blocked is worse than no checker.

*A 200 is not proof of correctness.*  Every response is judged by what it
contains, not by its status line.  Crossref must answer `status: ok` with the
DOI that was asked for; arXiv must return a feed holding one entry whose id is
the one that was asked for.  A 200 carrying a proxy error page is a transport
failure, because it means we never reached the publisher.

Where an entry has both a publisher record and an arXiv posting, the publisher
holds the version of record.  A preprint whose title or author order differs
from the published paper is a fact about the preprint, not an error in the
file, so those differences are reported for information rather than as
something to fix.  Without a publisher record to defer to, they are the best
evidence there is, and are reported as differences.

Exit codes follow diff(1): 0 everything checked agrees, 1 a difference wants a
human, 2 could not run.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "bibliography.json"

CROSSREF = "https://api.crossref.org/works/"
DATACITE = "https://api.datacite.org/dois/"
ARXIV = "http://export.arxiv.org/api/query?id_list="

#: Crossref's "polite pool" wants a contact address and gives better service in
#: return; arXiv asks the same of anything automated.  Both are conditions of
#: use, not decoration.
CONTACT = "williamdemeo@gmail.com"
USER_AGENT = (
    "williamdemeo.github.io-bibliography-verifier/1.0 "
    "(+https://github.com/williamdemeo/williamdemeo.github.io; "
    f"mailto:{CONTACT})"
)

TIMEOUT = 30
#: arXiv asks for roughly three seconds between programmatic requests.
ARXIV_DELAY = 3.0
#: 429 and 503 are the services asking to be tried again, so try again --
#: bounded, and still a hard failure when the last attempt fails too.  Failing
#: loudly means not reporting a pass we did not earn; it does not mean giving
#: up at the first sign of a busy server.
RETRIES = 3
BACKOFF = 2.0
#: Honour Retry-After, but not a value that would leave the run hanging.
MAX_RETRY_AFTER = 30

ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"
OPENSEARCH = "{http://a9.com/-/spec/opensearch/1.1/}"

#: Every level except OK is printed.  Only DIFFERS fails the run: a title that
#: matches apart from the publisher's Title Case is worth seeing and is not
#: worth blocking on, and neither is a field the publisher carries and the file
#: simply does not.
DIFFERS, STYLE, ABSENT, NOTE = "!", "~", "+", "i"


class Unreachable(Exception):
    """We did not get an answer we can attribute to the publisher.

    Raised for transport failures *and* for answers that arrive with a status
    but cannot have come from the service -- a 403 from a filtering proxy, a
    200 whose body is not the document the API returns.  Both mean the same
    thing for the purposes of this script: nothing was verified, so nothing
    may be reported as verified.
    """

    def __init__(self, what: str, reason: str) -> None:
        super().__init__(f"{what}: {reason}")
        self.what = what
        self.reason = reason


# ── talking to the services ─────────────────────────────────────────────────


def retry_after(exc: urllib.error.HTTPError, attempt: int) -> float:
    """How long to wait before trying again, from the header or the backoff."""
    header = (exc.headers or {}).get("Retry-After")
    try:
        return min(float(header), MAX_RETRY_AFTER)
    except (TypeError, ValueError):  # absent, or an HTTP-date we will not parse
        return BACKOFF * attempt


def get(url: str, accept: str) -> tuple[int, bytes]:
    """Fetch `url`, returning (status, body) for answers the service can own.

    404 comes back as an answer -- "no such record" is a fact worth acting on.
    429 and 503 mean "not now", and are retried.  Everything else that is not a
    200 raises Unreachable: a 403 or 407 is a proxy refusing to relay, another
    5xx is the service broken rather than busy.  None of them say anything
    about the bibliography, so none of them may be reported as if they did.

    Only the try-again statuses and timeouts are retried.  A refused connection
    is a host outside an egress allowlist, and asking it three times makes the
    failure slower, not likelier to succeed.
    """
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": accept}
    )
    for attempt in range(1, RETRIES + 1):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return 404, b""
            if exc.code in (429, 503) and attempt < RETRIES:
                time.sleep(retry_after(exc, attempt))
                continue
            hint = ""
            if exc.code in (403, 407):
                hint = " (a proxy refusing to relay looks exactly like this)"
            elif exc.code in (429, 503):
                hint = f" (still, after {RETRIES} attempts)"
            raise Unreachable(url, f"HTTP {exc.code} {exc.reason}{hint}") from exc
        except TimeoutError as exc:
            if attempt < RETRIES:
                time.sleep(BACKOFF * attempt)
                continue
            raise Unreachable(url, f"timed out after {RETRIES} attempts: {exc}") from exc
        except urllib.error.URLError as exc:
            # A timeout while connecting arrives wrapped rather than raw.
            if isinstance(exc.reason, TimeoutError) and attempt < RETRIES:
                time.sleep(BACKOFF * attempt)
                continue
            raise Unreachable(url, f"{exc.reason}") from exc
        except OSError as exc:  # resets, TLS failures
            raise Unreachable(url, f"{type(exc).__name__}: {exc}") from exc
    raise AssertionError("unreachable: the loop above either returns or raises")


def crossref_agency(doi: str) -> str | None:
    """Who registered `doi`, or None if no agency claims it.

    The distinction matters: Crossref 404s a DataCite DOI exactly as it 404s a
    DOI that does not exist, and only one of those is a problem with the file.
    """
    status, body = get(CROSSREF + urllib.parse.quote(doi) + "/agency", "application/json")
    if status == 404:
        return None
    try:
        payload = json.loads(body)
        return payload["message"]["agency"]["label"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise Unreachable(f"crossref agency {doi}", f"unexpected payload: {exc}") from exc


def crossref(doi: str) -> dict | None:
    """The Crossref record for `doi`, or None if Crossref does not index it."""
    status, body = get(CROSSREF + urllib.parse.quote(doi), "application/json")
    if status == 404:
        return None
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        # 200 and not JSON: something between here and Crossref answered for
        # it.  Treating that as an empty record would be the silent pass this
        # script exists to prevent.
        raise Unreachable(f"crossref {doi}", f"200 but not JSON: {exc}") from exc

    if payload.get("status") != "ok" or payload.get("message-type") != "work":
        raise Unreachable(
            f"crossref {doi}",
            f"200 but status={payload.get('status')!r} "
            f"message-type={payload.get('message-type')!r}",
        )
    message = payload.get("message") or {}
    # DOIs are case-insensitive, and Crossref lower-cases some of them on the
    # way out.  A *different* DOI in the reply is not a small thing: it means
    # the answer is about another work.
    if str(message.get("DOI", "")).lower() != doi.lower():
        raise Unreachable(
            f"crossref {doi}", f"answered with a different record: {message.get('DOI')!r}"
        )
    return message


def datacite(doi: str) -> dict | None:
    """The DataCite record for `doi`, or None if DataCite does not hold it."""
    status, body = get(DATACITE + urllib.parse.quote(doi), "application/vnd.api+json")
    if status == 404:
        return None
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise Unreachable(f"datacite {doi}", f"200 but not JSON: {exc}") from exc

    data = payload.get("data") or {}
    if data.get("type") != "dois" or not data.get("attributes"):
        raise Unreachable(f"datacite {doi}", f"200 but not a DOI document: {list(payload)}")
    if str(data.get("id", "")).lower() != doi.lower():
        raise Unreachable(
            f"datacite {doi}", f"answered with a different record: {data.get('id')!r}"
        )
    return data["attributes"]


def arxiv(identifier: str) -> dict | None:
    """The arXiv record for `identifier`, or None if arXiv has no such id."""
    status, body = get(ARXIV + urllib.parse.quote(identifier), "application/atom+xml")
    if status == 404:
        return None
    try:
        feed = ET.fromstring(body)
    except ET.ParseError as exc:
        raise Unreachable(f"arxiv {identifier}", f"200 but not XML: {exc}") from exc
    if not feed.tag.endswith("feed"):
        raise Unreachable(f"arxiv {identifier}", f"200 but root element is {feed.tag!r}")

    entries = feed.findall(f"{ATOM}entry")
    total = feed.findtext(f"{OPENSEARCH}totalResults")
    if not entries or total == "0":
        return None
    if len(entries) > 1:
        raise Unreachable(
            f"arxiv {identifier}", f"asked for one identifier, got {len(entries)} entries"
        )

    entry = entries[0]
    entry_id = entry.findtext(f"{ATOM}id") or ""
    # arXiv reports a bad identifier as a 200 with one entry whose id points at
    # its error vocabulary -- the plainest possible example of why a status
    # code is not an answer.
    if "/api/errors" in entry_id:
        return None
    # `.../abs/2010.04958v2` must be the identifier that was asked for, not a
    # neighbouring paper.
    got = re.sub(r"v\d+$", "", entry_id.rsplit("/abs/", 1)[-1])
    if got.lower() != identifier.lower():
        raise Unreachable(
            f"arxiv {identifier}", f"answered about a different paper: {entry_id!r}"
        )

    def text(tag: str) -> str | None:
        value = entry.findtext(tag)
        return " ".join(value.split()) if value else None

    return {
        "title": text(f"{ATOM}title"),
        "authors": [
            " ".join((author.findtext(f"{ATOM}name") or "").split())
            for author in entry.findall(f"{ATOM}author")
        ],
        "published": text(f"{ATOM}published"),
        "updated": text(f"{ATOM}updated"),
        "summary": text(f"{ATOM}summary"),
        "doi": text(f"{ARXIV_NS}doi"),
        "journal_ref": text(f"{ARXIV_NS}journal_ref"),
        "version": entry_id.rsplit("/abs/", 1)[-1],
    }


# ── comparing ───────────────────────────────────────────────────────────────


def key(value: str) -> str:
    """Fold case, accents and punctuation, so only real differences survive.

    'Ruškuc' and 'Ruskuc' are the same person; 'non-isomorphic' and
    'nonisomorphic' are not the same word, and the caller is told which kind of
    difference it is looking at.
    """
    decomposed = unicodedata.normalize("NFKD", value)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", stripped.lower().replace("&", " and ")).strip()


def loose(value: str) -> str:
    """`key`, with punctuation removed rather than folded to a space.

    This is the one that says 'nonisomorphic' and 'non-isomorphic' match, and
    it is used only to label a difference, never to hide one.
    """
    return key(value).replace(" ", "")


def compare(field: str, ours, theirs) -> tuple[str, str, str, str] | None:
    """One field, as (level, field, ours, theirs), or None when they agree."""
    if theirs in (None, "", []):
        return None
    if ours in (None, "", []):
        return (ABSENT, field, "—", str(theirs))
    ours, theirs = str(ours), str(theirs)
    if ours == theirs:
        return None
    if key(ours) == key(theirs):
        return (STYLE, field, ours, theirs)
    return (DIFFERS, field, ours, theirs)


def compare_pages(ours, theirs):
    """Pages, with 693--710, 693-710 and 693–710 read as one range."""
    dash = re.compile(r"[‐-―]|--")
    return compare(
        "page",
        dash.sub("-", ours) if ours else ours,
        dash.sub("-", theirs) if theirs else theirs,
    )


def compare_volume(ours, theirs):
    """Volumes, which publishers write as '30', 'Vol. 30' or 'Volume 18, Issue 1'.

    A volume is a number.  When the numbers agree the difference is in how the
    publisher writes it down, which is worth seeing once and not worth fixing.
    """
    difference = compare("volume", ours, theirs)
    if difference and difference[0] == DIFFERS:
        ours_digits = re.findall(r"\d+", str(ours))
        theirs_digits = re.findall(r"\d+", str(theirs))
        if ours_digits and theirs_digits and ours_digits[0] == theirs_digits[0]:
            return (STYLE, "volume", str(ours), str(theirs))
    return difference


def compare_issue(ours, theirs):
    """Issues, which publishers zero-pad ("04") and bibliographies do not."""
    difference = compare("issue", ours, theirs)
    if difference and difference[0] == DIFFERS:
        try:
            if int(str(ours)) == int(str(theirs)):
                return (STYLE, "issue", str(ours), str(theirs))
        except (TypeError, ValueError):
            pass
    return difference


def our_authors(item: dict) -> tuple[list[str], bool]:
    """Author display names, and whether the list ends in an 'et al.'."""
    names, abbreviated = [], False
    for author in item.get("author") or []:
        if author.get("literal"):
            if author["literal"].lower().rstrip(".") == "et al":
                abbreviated = True
                continue
            names.append(author["literal"])
            continue
        names.append(" ".join(filter(None, [author.get("given"), author.get("family")])))
    return names, abbreviated


def compare_authors(item: dict, theirs: list[str]):
    """Authors, distinguishing wrong names from a different order or spelling."""
    ours, abbreviated = our_authors(item)
    if not theirs:
        return None
    if abbreviated:
        # "Knispel, DeMeo, et al." claims a prefix, not a list.  Check the
        # prefix, and report the names the file is standing in for.
        prefix = [key(n) for n in theirs[: len(ours)]]
        if [key(n) for n in ours] == prefix:
            return (ABSENT, "author", ", ".join(ours) + ", et al.", ", ".join(theirs))
        return (DIFFERS, "author", ", ".join(ours) + ", et al.", ", ".join(theirs))

    if [n for n in ours] == theirs:
        return None
    if [key(n) for n in ours] == [key(n) for n in theirs]:
        return (STYLE, "author", ", ".join(ours), ", ".join(theirs))

    surnames_ours = [key(n).split()[-1] for n in ours if key(n)]
    surnames_theirs = [key(n).split()[-1] for n in theirs if key(n)]
    if surnames_ours == surnames_theirs:
        # Same people in the same order; the given names are written
        # differently ("William" against "William J.").
        return (STYLE, "author", ", ".join(ours), ", ".join(theirs))
    if sorted(surnames_ours) == sorted(surnames_theirs):
        return (DIFFERS, "author (order)", ", ".join(ours), ", ".join(theirs))
    return (DIFFERS, "author", ", ".join(ours), ", ".join(theirs))


def our_date(item: dict) -> tuple[int, ...]:
    """`issued` as a tuple, to whatever precision the file gives."""
    try:
        parts = item["issued"]["date-parts"][0]
    except (KeyError, IndexError, TypeError):
        return ()
    return tuple(p for p in parts if isinstance(p, int))


def our_year(item: dict):
    parts = our_date(item)
    return parts[0] if parts else None


def crossref_dates(record: dict) -> dict[str, tuple[int, ...]]:
    """Every publication date Crossref offers, keyed by which field it is."""
    dates = {}
    for field in ("issued", "published-print", "published-online", "published"):
        try:
            parts = record[field]["date-parts"][0]
        except (KeyError, IndexError, TypeError):
            continue
        clean = tuple(p for p in parts if isinstance(p, int))
        if clean:
            dates[field] = clean
    return dates


def show_dates(dates: dict[str, tuple[int, ...]]) -> str:
    return ", ".join(
        "-".join(str(p) for p in v) + f" ({k})" for k, v in sorted(dates.items())
    )


def compare_date(ours: tuple[int, ...], theirs: dict[str, tuple[int, ...]]):
    """Our `issued` against every date the publisher offers.

    A date is right if it agrees with any of them as far as we state it: a file
    saying "June 2020" agrees with a record saying 2020-06-15, and says less,
    which is not the same as saying something false.  It is wrong only when it
    matches none of them.
    """
    if not ours or not theirs:
        return None
    if any(candidate[: len(ours)] == ours for candidate in theirs.values()):
        # Agreeing on the year while disagreeing on the month is worth seeing.
        if len(ours) == 1 and any(len(c) > 1 for c in theirs.values()):
            return (NOTE, "issued", "-".join(map(str, ours)), show_dates(theirs))
        return None
    return (DIFFERS, "issued", "-".join(map(str, ours)), show_dates(theirs))


# ── the checks ──────────────────────────────────────────────────────────────


def check_crossref(item: dict, record: dict) -> list[tuple[str, str, str, str]]:
    found = []
    title = " ".join(t for t in (record.get("title") or [])[:1])
    subtitle = " ".join(s for s in (record.get("subtitle") or []) if s)
    if subtitle and loose(subtitle) not in loose(title):
        title = f"{title}: {subtitle}"

    venue = compare(
        "container-title",
        item.get("container-title"),
        (record.get("container-title") or [None])[0],
    )
    # For a conference paper the publisher's container-title is the registered
    # title of the proceedings volume -- "2021 36th Annual ACM/IEEE Symposium on
    # Logic in Computer Science (LICS)" -- and not the name a bibliography calls
    # the venue.  Same distinction DataCite's `container` draws for a series,
    # and handled the same way: shown in full, not reported as something wrong.
    if venue and venue[0] == DIFFERS and record.get("type") == "proceedings-article":
        venue = (NOTE, "proceedings", venue[2], venue[3])

    for difference in (
        compare("title", item.get("title"), title),
        compare_authors(
            item,
            [
                " ".join(filter(None, [a.get("given"), a.get("family") or a.get("name")]))
                for a in record.get("author") or []
            ],
        ),
        venue,
        compare_volume(item.get("volume"), record.get("volume")),
        compare_issue(item.get("issue"), record.get("issue")),
        compare_pages(item.get("page"), record.get("page")),
        compare_date(our_date(item), crossref_dates(record)),
    ):
        if difference:
            found.append(difference)
    return found


def compare_abstract(item: dict, source: str, theirs: str | None):
    """The stored abstract against the service it says it came from.

    Reported as a marker rather than as two walls of text: a difference here is
    a truncation or a hand-edit, and seeing 1,900 characters twice helps nobody
    find it.  Only the service named by `_abstract-source` is checked -- the
    published abstract and the preprint's summary differ legitimately, which is
    the whole reason the field records where it came from.
    """
    ours = item.get("abstract")
    if item.get("_abstract-source") != source:
        return None
    if not theirs:
        return (DIFFERS, "abstract", f"{len(ours or '')} chars, from {source}",
                f"{source} has none")
    if not ours:
        return (ABSENT, "abstract", "—", f"{len(theirs)} chars available")
    if key(ours) == key(theirs):
        return None
    level = STYLE if loose(ours) == loose(theirs) else DIFFERS
    return (level, "abstract", f"{len(ours)} chars: {ours[:60]}…",
            f"{len(theirs)} chars: {theirs[:60]}…")


def datacite_dates(record: dict) -> dict[str, tuple[int, ...]]:
    """Publication dates from DataCite, which writes them as ISO strings.

    `publicationYear` is the year; `dates[]` carries the precise ones, of which
    Issued and Available are the two that mean "published".  Created and
    Copyrighted are about the record, not the work, and are ignored.
    """
    dates = {}
    year = record.get("publicationYear")
    if isinstance(year, int):
        dates["publicationYear"] = (year,)
    for entry in record.get("dates") or []:
        kind = entry.get("dateType")
        if kind not in ("Issued", "Available"):
            continue
        parts = tuple(int(p) for p in re.findall(r"\d+", str(entry.get("date", "")))[:3])
        if parts:
            dates[kind] = parts
    return dates


def check_datacite(item: dict, record: dict) -> list[tuple[str, str, str, str]]:
    found = []
    container = record.get("container") or {}
    pages = "-".join(
        p for p in (container.get("firstPage"), container.get("lastPage")) if p
    )

    for difference in (
        compare("title", item.get("title"), (record.get("titles") or [{}])[0].get("title")),
        compare_authors(
            item,
            [
                " ".join(filter(None, [c.get("givenName"), c.get("familyName")]))
                or c.get("name", "")
                for c in record.get("creators") or []
            ],
        ),
        compare_volume(item.get("volume"), container.get("volume")),
        compare_issue(item.get("issue"), container.get("issue")),
        compare_pages(item.get("page"), pages),
        compare_date(our_date(item), datacite_dates(record)),
    ):
        if difference:
            found.append(difference)

    # DataCite's container for a Dagstuhl paper is the LIPIcs/OASIcs volume --
    # "LIPIcs, Volume 239, TYPES 2021" -- and not the name of the conference,
    # which is what a bibliography calls the venue.  Show it rather than
    # pretend the two fields mean the same thing.
    if container.get("title"):
        found.append((NOTE, "series", str(item.get("container-title") or "—"),
                      container["title"]))

    descriptions = [
        " ".join(str(d.get("description", "")).split())
        for d in record.get("descriptions") or []
        if d.get("descriptionType") in (None, "Abstract")
    ]
    abstract = compare_abstract(item, "datacite", descriptions[0] if descriptions else None)
    if abstract:
        found.append(abstract)
    return found


def check_arxiv(
    item: dict, record: dict, *, has_publisher_record: bool
) -> list[tuple[str, str, str, str]]:
    found = []
    for difference in (
        compare("title", item.get("title"), record["title"]),
        compare_authors(item, record["authors"]),
    ):
        if not difference:
            continue
        if has_publisher_record and difference[0] == DIFFERS:
            # The publisher's record already covers this field, and a preprint
            # is allowed to differ from the paper it became.  "non-isomorphic"
            # on arXiv against "nonisomorphic" in the journal is a fact about
            # the two documents, not a defect to fix.
            difference = (NOTE, difference[1] + " (preprint)", difference[2], difference[3])
        found.append(difference)

    posted = (record.get("published") or "")[:4]
    claimed = (item.get("_preprint") or {}).get("arxiv-year")
    if claimed is not None and posted and int(posted) != claimed:
        found.append((DIFFERS, "_preprint.arxiv-year", str(claimed), posted))
    elif claimed is None and posted and str(our_year(item)) != posted:
        # No _preprint claim to check, but the posting year is not the
        # publication year, and a reader comparing the two should see why.
        found.append((NOTE, "arXiv posted", str(our_year(item)) + " (issued)", posted))

    abstract = compare_abstract(item, "arxiv", record.get("summary"))
    if abstract:
        found.append(abstract)

    if record.get("doi"):
        if not item.get("DOI"):
            found.append((ABSENT, "DOI", "—", record["doi"]))
        elif item["DOI"].lower() != record["doi"].lower():
            found.append((DIFFERS, "DOI", item["DOI"], record["doi"]))

    # journal_ref is free text an author typed, so it is checked by containment
    # and shown in full rather than parsed into fields it does not really have.
    reference = record.get("journal_ref")
    if reference:
        blob = loose(reference)
        missing = [
            f"{name}={value!r}"
            for name, value in (
                ("container-title", item.get("container-title")),
                ("volume", item.get("volume")),
                ("page", item.get("page")),
            )
            if value and loose(str(value)) not in blob
        ]
        if missing:
            found.append((NOTE, "journal_ref", ", ".join(missing) + " not in it", reference))
        else:
            found.append((NOTE, "journal_ref", "—", reference))
    return found


# ── reporting ───────────────────────────────────────────────────────────────


def show(entry_id: str, source: str, differences: list, shown: set) -> None:
    if entry_id not in shown:
        print(f"\n{entry_id}")
        shown.add(entry_id)
    print(f"  {source}")
    for level, field, ours, theirs in differences:
        print(f"    {level} {field}")
        print(f"        ours  {ours}")
        print(f"        them  {theirs}")


def main() -> int:
    global TIMEOUT

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", metavar="ID", help="check one entry by its id")
    parser.add_argument(
        "--timeout", type=int, default=TIMEOUT, metavar="SECONDS",
        help=f"per-request timeout (default {TIMEOUT})",
    )
    arguments = parser.parse_args()
    TIMEOUT = arguments.timeout

    try:
        items = json.loads(SOURCE.read_text())["items"]
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"error: {SOURCE}: {exc}", file=sys.stderr)
        return 2

    if arguments.only:
        items = [i for i in items if i.get("id") == arguments.only]
        if not items:
            print(f"error: no entry with id {arguments.only!r}", file=sys.stderr)
            return 2

    print(f"verifying {len(items)} entr{'y' if len(items) == 1 else 'ies'} against "
          f"api.crossref.org, api.datacite.org and export.arxiv.org")

    shown: set[str] = set()
    unreachable: list[str] = []
    unverifiable: list[str] = []
    substantive = 0
    cosmetic = 0
    checked = 0
    first_arxiv = True

    for item in items:
        entry_id = item.get("id", "?")
        doi, identifier = item.get("DOI"), item.get("_arxiv")

        if not doi and not identifier:
            unverifiable.append(f"{entry_id}: no DOI and no arXiv id")

        verified_by_publisher = False

        if doi:
            try:
                record = crossref(doi)
                if record is not None:
                    checked += 1
                    verified_by_publisher = True
                    differences = check_crossref(item, record)
                    substantive += sum(1 for d in differences if d[0] == DIFFERS)
                    cosmetic += sum(1 for d in differences if d[0] != DIFFERS)
                    if differences:
                        show(entry_id, f"crossref {doi}", differences, shown)
                else:
                    agency = crossref_agency(doi)
                    if agency is None:
                        show(entry_id, f"crossref {doi}",
                             [(DIFFERS, "DOI", doi, "no registration agency claims it")],
                             shown)
                        substantive += 1
                    elif agency.lower() == "datacite":
                        record = datacite(doi)
                        if record is None:
                            # The agency endpoint says DataCite owns it and
                            # DataCite says it does not.  That contradiction is
                            # not something to paper over.
                            show(entry_id, f"datacite {doi}",
                                 [(DIFFERS, "DOI", doi,
                                   "Crossref routes it to DataCite; DataCite has no record")],
                                 shown)
                            substantive += 1
                        else:
                            checked += 1
                            verified_by_publisher = True
                            differences = check_datacite(item, record)
                            substantive += sum(1 for d in differences if d[0] == DIFFERS)
                            cosmetic += sum(1 for d in differences if d[0] != DIFFERS)
                            if differences:
                                show(entry_id, f"datacite {doi}", differences, shown)
                    else:
                        unverifiable.append(
                            f"{entry_id}: DOI {doi} is registered with {agency}, "
                            f"which this script does not query"
                        )
            except Unreachable as exc:
                unreachable.append(f"{entry_id}: {exc}")

        if identifier:
            if not first_arxiv:
                time.sleep(ARXIV_DELAY)
            first_arxiv = False
            try:
                record = arxiv(identifier)
                if record is None:
                    show(entry_id, f"arxiv {identifier}",
                         [(DIFFERS, "_arxiv", identifier, "arXiv has no such identifier")],
                         shown)
                    substantive += 1
                else:
                    checked += 1
                    differences = check_arxiv(
                        item, record, has_publisher_record=verified_by_publisher
                    )
                    substantive += sum(1 for d in differences if d[0] == DIFFERS)
                    cosmetic += sum(1 for d in differences if d[0] != DIFFERS)
                    if differences:
                        show(entry_id, f"arxiv {record['version']}", differences, shown)
            except Unreachable as exc:
                unreachable.append(f"{entry_id}: {exc}")

    print("\n" + "─" * 76)
    print(f"{checked} record(s) fetched and compared")
    print(f"  {DIFFERS} {substantive} difference(s) needing a decision")
    print(f"  {STYLE}/{ABSENT}/{NOTE} {cosmetic} of spelling, of a field only the "
          f"publisher carries, or for information")

    if unverifiable:
        print(f"\nnot verifiable against either service ({len(unverifiable)}):")
        for line in unverifiable:
            print(f"  {line}")

    if unreachable:
        # The whole point.  Anything that stopped us reaching a publisher makes
        # this run worthless as evidence, however much of it succeeded.
        print(f"\nerror: {len(unreachable)} request(s) never reached the service:",
              file=sys.stderr)
        for line in unreachable:
            print(f"  {line}", file=sys.stderr)
        print(
            "\nNothing above is a verification result: a request that does not\n"
            "arrive proves nothing about the entry it was meant to check.\n"
            "A refused CONNECT means the host is outside this environment's\n"
            f"egress allowlist rather than down; a 429 or 503 surviving\n"
            f"{RETRIES} attempts means the service is throttling us, and the\n"
            "run is worth repeating later.",
            file=sys.stderr,
        )
        return 2

    if checked == 0:
        print("\nerror: nothing was actually checked; refusing to report success",
              file=sys.stderr)
        return 2

    return 1 if substantive else 0


if __name__ == "__main__":
    sys.exit(main())
