#!/usr/bin/env python3
"""Tests for the publications renderer and its validation.

Run directly with ``python3 scripts/python/test_gen_publications.py`` for ``OK``
and exit 0, or under ``pytest`` if it happens to be installed.  Nothing here
reads bibliography.json: every case is a literal, so a test failing means the
renderer changed rather than the bibliography did.

The validation tests matter most.  Splitting the Birkhoff entry meant
*relaxing* the rule that an arXiv id appears once, and a relaxed check is worth
more scrutiny than a strict one: it has to keep catching the duplicate it was
written for while allowing the preprint pair it was relaxed for.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gen_publications as gp  # noqa: E402

PAPER = {
    "id": "demeo2022birkhoff",
    "type": "paper-conference",
    "title": "A machine-checked proof of Birkhoff's variety theorem",
    "author": [{"family": "DeMeo", "given": "William"}],
    "container-title": "TYPES 2021",
    "collection-title": "LIPIcs",
    "volume": "239",
    "page": "4:1-4:21",
    "issued": {"date-parts": [[2022, 8, 4]]},
    "DOI": "10.4230/LIPIcs.TYPES.2021.4",
    "URL": "https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.TYPES.2021.4",
    "_arxiv": "2101.10166",
}

PREPRINT = {
    "id": "demeo2021birkhoff",
    "type": "article",
    "title": "A machine-checked proof of Birkhoff's variety theorem",
    "author": [{"family": "DeMeo", "given": "William"}],
    "issued": {"date-parts": [[2021, 1, 25]]},
    "_arxiv": "2101.10166",
    "URL": "https://arxiv.org/abs/2101.10166",
    "_version-of": "demeo2022birkhoff",
}


# ── validation ───────────────────────────────────────────────────────────────


def test_a_preprint_may_share_its_arxiv_id_with_the_paper():
    assert gp.validate([PAPER, PREPRINT]) == []


def test_two_unrelated_entries_may_not_share_an_arxiv_id():
    impostor = dict(PREPRINT, id="somethingelse")
    del impostor["_version-of"]
    problems = gp.validate([PAPER, impostor])
    assert any("also on" in p for p in problems), problems


def test_version_of_must_name_an_entry_that_exists():
    problems = gp.validate([dict(PREPRINT, **{"_version-of": "nope"})])
    assert any("_version-of names no entry" in p for p in problems), problems


def test_a_duplicate_id_is_still_caught():
    problems = gp.validate([PAPER, dict(PAPER, _arxiv=None)])
    assert any("duplicate id" in p for p in problems), problems


# ── dates ────────────────────────────────────────────────────────────────────


def test_dates_render_to_the_precision_given_and_no_further():
    assert gp.issued_text({"issued": {"date-parts": [[2004]]}}) == "2004"
    assert gp.issued_text({"issued": {"date-parts": [[2020, 6]]}}) == "June 2020"
    assert gp.issued_text({"issued": {"date-parts": [[2022, 1, 19]]}}) == "January 19, 2022"


def test_a_missing_or_nonsense_date_does_not_crash():
    assert gp.issued_text({}) == ""
    assert gp.issued_text({"issued": {"date-parts": [[2020, 13]]}}) == "2020"


# ── the imprint line ─────────────────────────────────────────────────────────


def test_the_imprint_carries_everything_the_record_supports():
    line = gp.imprint_md(PAPER)
    for expected in ("*TYPES 2021*", "LIPIcs Volume 239", "August 4, 2022",
                     "pages 4:1-4:21", "doi:10.4230/LIPIcs.TYPES.2021.4"):
        assert expected in line, (expected, line)


def test_the_imprint_omits_what_the_record_does_not_have():
    line = gp.imprint_md({"container-title": "ISMA 2004", "issued": {"date-parts": [[2004]]}})
    assert line == "*ISMA 2004*, 2004.", line
    assert "Issue" not in line and "pages" not in line and "doi" not in line


def test_a_journal_shows_its_abbreviation_when_it_has_one():
    line = gp.imprint_md({
        "container-title": "Logical Methods in Computer Science",
        "container-title-short": "LMCS", "volume": "18", "issue": "1",
        "issued": {"date-parts": [[2022, 1, 19]]},
    })
    assert "*Logical Methods in Computer Science* (LMCS), Volume 18, Issue 1" in line, line


def test_a_conference_shows_where_it_was_held():
    line = gp.imprint_md({
        "container-title": "ISMA 2004", "event-place": "Nara, Japan",
        "issued": {"date-parts": [[2004]]},
    })
    assert line == "*ISMA 2004*, Nara, Japan, 2004.", line


def test_a_bare_preprint_says_so():
    line = gp.imprint_md(PREPRINT)
    assert line.startswith("arXiv preprint arXiv:2101.10166, January 25, 2021"), line


# ── the link row ─────────────────────────────────────────────────────────────


def by_id(*items):
    return {i["id"]: i for i in items}


def test_the_published_version_and_the_preprint_sit_side_by_side():
    links = gp.links_md(PAPER, by_id(PAPER, PREPRINT))
    assert links == [
        "[Proceedings](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.TYPES.2021.4)",
        "[arXiv preprint](https://arxiv.org/abs/2101.10166)",
    ], links


def test_a_preprint_borrows_the_published_link_from_the_paper():
    links = gp.links_md(PREPRINT, by_id(PAPER, PREPRINT))
    assert links[0].startswith("[Published version](https://drops.dagstuhl.de/"), links
    assert links[1] == "[arXiv preprint](https://arxiv.org/abs/2101.10166)", links


def test_an_entry_with_only_a_doi_links_through_doi_org():
    item = {"type": "article-journal", "DOI": "10.1142/S0218196720500174"}
    assert gp.links_md(item, {}) == [
        "[Journal](https://doi.org/10.1142/S0218196720500174)"
    ], gp.links_md(item, {})


def test_a_bare_url_is_not_called_a_journal():
    """Nothing vouches for an author-hosted PDF being the version of record."""
    pdf = {"type": "paper-conference", "URL": "https://example.org/paper.pdf"}
    page = {"type": "paper-conference", "URL": "https://example.org/paper"}
    assert gp.links_md(pdf, {}) == ["[PDF](https://example.org/paper.pdf)"]
    assert gp.links_md(page, {}) == ["[Link](https://example.org/paper)"]


def test_an_arxiv_url_is_never_the_published_version():
    preprint_only = {"type": "manuscript", "URL": "https://arxiv.org/abs/1301.6788",
                     "_arxiv": "1301.6788"}
    assert gp.links_md(preprint_only, {}) == [
        "[arXiv preprint](https://arxiv.org/abs/1301.6788)"
    ], gp.links_md(preprint_only, {})


def test_an_entry_with_nothing_to_link_gets_no_links():
    assert gp.links_md({"type": "book", "title": "x"}, {}) == []


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
        except AssertionError as exc:
            failed += 1
            print(f"FAIL {t.__name__}: {exc}", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"ERROR {t.__name__}: {exc!r}", file=sys.stderr)
    if failed:
        print(f"\n{failed} of {len(tests)} tests failed", file=sys.stderr)
        return 1
    print(f"OK ({len(tests)} tests)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
