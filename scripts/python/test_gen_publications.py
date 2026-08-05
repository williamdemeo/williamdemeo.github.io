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


# ── the CV rendering ─────────────────────────────────────────────────────────


def test_the_cv_carries_only_the_entries_marked_for_it():
    items = [dict(PAPER, _cv=True), PREPRINT]
    assert [i["id"] for i in gp.selected(items, "cv")] == ["demeo2022birkhoff"]
    assert len(gp.selected(items, "full")) == 2


def test_both_renderings_are_newest_first():
    older = dict(PAPER, id="older", issued={"date-parts": [[2019]]}, _cv=True)
    order = [i["id"] for i in gp.selected([older, dict(PAPER, _cv=True)], "cv")]
    assert order == ["demeo2022birkhoff", "older"], order


def test_the_cv_abridges_the_date_and_drops_the_doi():
    full = gp.imprint_md(PAPER)
    cv = gp.imprint_md(PAPER, compact=True)
    assert "August 4, 2022" in full and "doi:" in full
    assert "2022" in cv and "August" not in cv and "doi:" not in cv
    # Everything else a citation needs survives the abridgement.
    for kept in ("*TYPES 2021*", "LIPIcs Volume 239", "pages 4:1-4:21"):
        assert kept in cv, (kept, cv)


def test_the_cv_keeps_both_links():
    """The whole point of the CV list is the pair, same as the full one."""
    body = gp.render([dict(PAPER, _cv=True)], "cv")
    assert "[Proceedings](" in body and "[arXiv preprint](" in body, body


def test_the_cv_is_numbered_and_the_page_is_not():
    cv = [l for l in gp.render([dict(PAPER, _cv=True)], "cv").splitlines() if l.strip()]
    page = [l for l in gp.render([PAPER], "page").splitlines() if l.strip()]
    assert any(l.startswith("1. **") for l in cv), cv
    assert any(l.startswith("- **") for l in page), page
    assert not any(l.startswith("1. **") for l in page), page


def test_a_cv_entry_may_borrow_a_link_from_an_entry_the_cv_omits():
    """`_version-of` resolves against the whole file, not the rendered subset."""
    body = gp.render([PAPER, dict(PREPRINT, _cv=True)], "cv")
    assert "[Published version](https://drops.dagstuhl.de/" in body, body


# ── the publications page ────────────────────────────────────────────────────


def test_every_csl_type_in_use_lands_in_a_group():
    """A publications page silently dropping a publication is its worst bug."""
    for kind in ("article-journal", "paper-conference", "article", "manuscript",
                 "thesis", "book"):
        assert gp.group_of({"type": kind}) is not None, kind


def test_an_unknown_type_is_a_validation_failure_not_a_silent_drop():
    assert gp.group_of({"type": "dataset"}) is None
    stray = dict(PAPER, type="dataset")
    assert any("belongs to no group" in p for p in gp.validate([stray])), gp.validate([stray])


def test_the_page_is_grouped_and_the_selected_list_points_into_it():
    body = gp.render([dict(PAPER, _cv=True), PREPRINT], "page")
    assert "## Selected" in body and "## Conference and workshop papers" in body
    assert "## Preprints and unpublished manuscripts" in body
    # The selected link and the entry's anchor have to be the same string, or
    # the page renders a link to nowhere and nothing complains.
    assert "(#demeo2022birkhoff)" in body, body
    assert "{ #demeo2022birkhoff }" in body, body


def test_the_cv_rendering_carries_no_anchors_or_abstracts():
    """Two renderings of one entry must not collide on ids in one page."""
    body = gp.render([dict(PAPER, _cv=True, abstract="x")], "cv")
    assert "{ #" not in body and "???" not in body, body


def test_an_abstract_is_indented_enough_to_stay_inside_its_list_item():
    """At two spaces Python-Markdown ends the list and renders `???` as text."""
    body = gp.render([dict(PAPER, abstract="Some abstract.")], "page")
    assert '\n    ??? quote "Abstract"\n' in body, body
    assert "\n        Some abstract.\n" in body, body


def test_entries_with_nothing_to_open_are_reported():
    assert gp.artifactless([PAPER]) == []
    bare = {"id": "nolink", "type": "paper-conference", "title": "t"}
    assert gp.artifactless([bare]) == ["nolink"]
    # A preprint entry borrows its link, so it is not artifactless.
    assert gp.artifactless([PREPRINT]) == []


# ── BibTeX ───────────────────────────────────────────────────────────────────


def test_bibtex_maps_each_type_to_the_right_entry_kind():
    kinds = {t: gp.BIBTEX_TYPE[t] for t in gp.BIBTEX_TYPE}
    assert kinds["article-journal"] == "article"
    assert kinds["paper-conference"] == "inproceedings"
    assert kinds["thesis"] == "phdthesis"
    assert kinds["manuscript"] == "misc"


def test_bibtex_puts_the_venue_in_the_field_its_type_expects():
    assert field(gp.bibtex_entry(PAPER), "booktitle") == "{TYPES 2021}"
    journal = {"id": "j", "type": "article-journal", "title": "T",
               "author": [{"family": "DeMeo"}], "container-title": "IJAC",
               "issued": {"date-parts": [[2020]]}}
    entry = gp.bibtex_entry(journal)
    assert field(entry, "journal") == "{IJAC}" and not field(entry, "booktitle"), entry


def field(entry: str, name: str) -> str:
    """One field's value, so tests do not depend on the column alignment."""
    for line in entry.splitlines():
        key, _, value = line.partition(" = ")
        if key.strip() == name:
            return value.rstrip(",")
    return ""


def test_bibtex_double_braces_titles():
    """A .bst case-folding "Agda" would undo titles checked against publishers."""
    assert field(gp.bibtex_entry(PAPER), "title").startswith("{{"), gp.bibtex_entry(PAPER)


def test_bibtex_escapes_characters_that_are_syntax():
    assert gp.bibtex_escape("a & b") == r"a \& b"
    assert gp.bibtex_escape("100%") == r"100\%"
    assert gp.bibtex_escape("a_b") == r"a\_b"
    # The backslash has to be replaced first or it escapes the new escapes.
    assert gp.bibtex_escape(r"a\b") == r"a\textbackslash{}b"


def test_bibtex_writes_authors_family_first_and_joined_with_and():
    item = {"author": [{"family": "Bergman", "given": "Clifford"},
                       {"family": "DeMeo", "given": "William"}]}
    assert gp.bibtex_authors(item) == "Bergman, Clifford and DeMeo, William"


def test_bibtex_braces_a_literal_author_so_it_is_not_split():
    item = {"author": [{"literal": "The Agda Team"}]}
    assert gp.bibtex_authors(item) == "{The Agda Team}"


def test_bibtex_uses_en_dash_page_ranges():
    assert field(gp.bibtex_entry(PAPER), "pages") == "{4:1--4:21}"


def test_bibtex_omits_a_url_that_only_restates_the_eprint():
    """`eprint` already is that link; repeating it as `url` is noise."""
    assert not field(gp.bibtex_entry(PREPRINT), "url"), gp.bibtex_entry(PREPRINT)
    assert field(gp.bibtex_entry(PREPRINT), "eprint") == "{2101.10166}"


def test_bibtex_omits_a_url_that_only_restates_the_doi():
    item = {"id": "x", "type": "article-journal", "title": "T",
            "author": [{"family": "DeMeo"}], "issued": {"date-parts": [[2020]]},
            "DOI": "10.1/abc", "URL": "https://doi.org/10.1/abc"}
    assert not field(gp.bibtex_entry(item), "url"), gp.bibtex_entry(item)


def test_bibtex_keeps_a_url_that_is_the_only_link():
    item = {"id": "x", "type": "paper-conference", "title": "T",
            "author": [{"family": "DeMeo"}], "issued": {"date-parts": [[2004]]},
            "URL": "https://example.org/paper.pdf"}
    assert field(gp.bibtex_entry(item), "url") == "{https://example.org/paper.pdf}"


def test_bibtex_keeps_a_url_pointing_somewhere_the_identifiers_do_not():
    """LMCS has an article page that is neither the DOI nor the arXiv abstract."""
    item = {"id": "x", "type": "article-journal", "title": "T",
            "author": [{"family": "DeMeo"}], "issued": {"date-parts": [[2022]]},
            "DOI": "10.46298/lmcs-18(1:12)2022", "_arxiv": "1611.02867",
            "URL": "https://lmcs.episciences.org/8975"}
    assert field(gp.bibtex_entry(item), "url") == "{https://lmcs.episciences.org/8975}"


def test_bibtex_carries_the_arxiv_eprint():
    entry = gp.bibtex_entry(PAPER)
    assert field(entry, "eprint") == "{2101.10166}"
    assert field(entry, "archivePrefix") == "{arXiv}"


# ── Typst ────────────────────────────────────────────────────────────────────
#
# The PDF's copy of the CV selection (ADR-010).  What matters here is not that
# it is well formed -- `typst compile` says that, and `nix flake check` runs it
# -- but that it says the same words as the Markdown snippet beside it.  Both
# come from the same runs, and these are the tests that keep it that way.


def typst_field(entry: str, name: str) -> str:
    for line in entry.splitlines():
        if line.strip().startswith(f"{name}:"):
            return line.strip().removeprefix(f"{name}:").strip().rstrip(",")
    return ""


def test_the_typst_data_says_what_the_cv_snippet_says():
    item = dict(PAPER, _cv=True)
    entry = "\n".join(gp.typst_entry(item, {item["id"]: item}))
    snippet = gp.render([item], "cv")
    # Every word of the byline and the imprint, in order, in both renderings.
    for runs in (gp.byline_runs(item), gp.imprint_runs(item, compact=True)):
        for text, _ in runs:
            assert gp.typst_string(text)[1:-1] in entry, text
            assert text in snippet, text


def test_the_typst_data_marks_the_author_the_snippet_emphasises():
    item = {"id": "x", "type": "article-journal", "title": "T",
            "author": [{"family": "Bergman", "given": "Clifford"},
                       {"family": "DeMeo", "given": "William"}],
            "issued": {"date-parts": [[2022]]}}
    entry = "\n".join(gp.typst_entry(item, {}))
    assert '("William DeMeo", "strong")' in entry
    assert '("Clifford Bergman", none)' in entry


def test_a_typst_string_escapes_what_is_syntax_inside_one():
    assert gp.typst_string(r'a "b" \c') == r'"a \"b\" \\c"'


def test_typst_markup_characters_cross_as_text_not_as_markup():
    """A title is data.  `#`, `*` and `_` in one must not become formatting."""
    assert gp.typst_string("#set _x_ *y*") == '"#set _x_ *y*"'


def test_a_one_element_typst_array_keeps_its_trailing_comma():
    """`(x)` is x in parentheses; `(x,)` is a one-element array."""
    assert gp.typst_array(["1"]) == "(1,)"
    assert gp.typst_array(["1", "2"]) == "(1, 2)"
    assert gp.typst_array([]) == "()"


def test_the_typst_rendering_covers_the_same_entries_as_the_cv_snippet():
    items = [dict(PAPER, _cv=True), PREPRINT]
    body = gp.render_typst(items)
    assert body.count("    id: ") == len(gp.selected(items, "cv"))
    assert '"demeo2022birkhoff"' in body
    assert '"demeo2021birkhoff"' not in body


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
