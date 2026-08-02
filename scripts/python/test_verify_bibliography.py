#!/usr/bin/env python3
"""Tests for the bibliography verifier.

Run directly with ``python3 scripts/python/test_verify_bibliography.py`` for
``OK`` and exit 0, or under ``pytest`` if it happens to be installed.  Nothing
here touches the network: every response is a fixture, which is the only way to
test the cases that matter, since they are all about what happens when the
network misbehaves.

Those are the tests worth having.  `verify_bibliography.py` exists to stop a
claim being believed without evidence, so its own central claim -- that it
fails loudly rather than reporting a clean run it did not earn -- is exactly
the thing that must not be taken on trust.  A checker that returns 0 when every
request was refused is worse than no checker, and only a test proves it does
not.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import verify_bibliography as vb  # noqa: E402

CROSSREF_OK = json.dumps(
    {
        "status": "ok",
        "message-type": "work",
        "message": {
            "DOI": "10.1007/s00012-013-0226-3",
            "title": ["Expansions of finite algebras and their congruence lattices"],
            "container-title": ["Algebra universalis"],
            "volume": "69",
            "page": "257-278",
            "issued": {"date-parts": [[2013, 4, 2]]},
            "author": [{"given": "William", "family": "DeMeo"}],
        },
    }
).encode()

ARXIV_OK = b"""<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:arxiv="http://arxiv.org/schemas/atom"
      xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">
  <opensearch:totalResults>1</opensearch:totalResults>
  <entry>
    <id>http://arxiv.org/abs/1205.1106v4</id>
    <title>Expansions of finite algebras and their congruence lattices</title>
    <published>2012-05-05T06:46:40Z</published>
    <author><name>William DeMeo</name></author>
    <arxiv:doi>10.1007/s00012-013-0226-3</arxiv:doi>
  </entry>
</feed>
"""

#: arXiv answers a bad identifier with 200 and an entry pointing at its error
#: vocabulary.  The plainest possible demonstration that a status code is not
#: an answer.
ARXIV_ERROR = b"""<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">
  <opensearch:totalResults>1</opensearch:totalResults>
  <entry>
    <id>http://arxiv.org/api/errors#incorrect_id_format</id>
    <title>Error</title>
  </entry>
</feed>
"""

ENTRY = {
    "id": "demeo2013expansions",
    "title": "Expansions of finite algebras and their congruence lattices",
    "author": [{"family": "DeMeo", "given": "William"}],
    "container-title": "Algebra universalis",
    "volume": "69",
    "page": "257-278",
    "issued": {"date-parts": [[2013]]},
    "_arxiv": "1205.1106",
    "DOI": "10.1007/s00012-013-0226-3",
}


def run_main(items, responses, argv=("verify_bibliography.py",)):
    """Run main() over `items` with `responses` standing in for the network.

    `responses` maps a substring of the URL to either (status, body) or an
    exception to raise.  Returns (exit code, stdout, stderr).
    """

    def fake_get(url, accept):
        for fragment, reply in responses.items():
            if fragment in url:
                if isinstance(reply, Exception):
                    raise reply
                return reply
        raise AssertionError(f"test made an unexpected request: {url}")

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump({"items": items}, fh)
        source = Path(fh.name)

    real_get, real_source, real_argv, real_delay = vb.get, vb.SOURCE, sys.argv, vb.ARXIV_DELAY
    out, err = io.StringIO(), io.StringIO()
    try:
        vb.get, vb.SOURCE, sys.argv, vb.ARXIV_DELAY = fake_get, source, list(argv), 0
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = vb.main()
    finally:
        vb.get, vb.SOURCE, sys.argv, vb.ARXIV_DELAY = real_get, real_source, real_argv, real_delay
        source.unlink()
    return code, out.getvalue(), err.getvalue()


# ── the guarantee: a blocked network is never a pass ─────────────────────────


def test_every_request_refused_exits_2():
    code, out, err = run_main(
        [ENTRY],
        {
            "crossref": vb.Unreachable("crossref", "[Errno 111] Connection refused"),
            "arxiv": vb.Unreachable("arxiv", "[Errno 111] Connection refused"),
        },
    )
    assert code == 2, f"a wholly blocked run must exit 2, got {code}"
    assert "never reached the service" in err, err
    assert "0 difference" in out, out


def test_one_refused_request_still_fails_the_run():
    """A partial check is not a pass: "1 of 2 verified" is a failure."""
    code, _out, err = run_main(
        [ENTRY],
        {
            "crossref": (200, CROSSREF_OK),
            "arxiv": vb.Unreachable("arxiv", "timed out"),
        },
    )
    assert code == 2, f"a partial run must exit 2, got {code}"
    assert "1 request(s) never reached the service" in err, err


def test_nothing_to_check_is_not_success():
    """Entries with no identifiers cannot vouch for themselves."""
    bare = {k: v for k, v in ENTRY.items() if k not in ("DOI", "_arxiv")}
    code, out, err = run_main([bare], {})
    assert code == 2, f"a run that checked nothing must exit 2, got {code}"
    assert "refusing to report success" in err, err
    assert "no DOI and no arXiv id" in out, out


def test_clean_run_exits_0():
    code, out, err = run_main([ENTRY], {"crossref": (200, CROSSREF_OK), "arxiv": (200, ARXIV_OK)})
    assert code == 0, f"an entry matching its publishers must exit 0, got {code}\n{out}{err}"
    assert "2 record(s) fetched" in out, out


def test_a_real_difference_exits_1():
    wrong = dict(ENTRY, volume="96")
    code, out, _err = run_main(
        [wrong], {"crossref": (200, CROSSREF_OK), "arxiv": (200, ARXIV_OK)}
    )
    assert code == 1, f"a substantive difference must exit 1, got {code}"
    assert "volume" in out and "96" in out, out


# ── the other guarantee: a 200 is not proof ──────────────────────────────────


def test_crossref_200_that_is_not_json_is_a_transport_failure():
    """A proxy's error page carries a 200 as happily as a record does."""
    code, _out, err = run_main(
        [ENTRY],
        {"crossref": (200, b"<html>Access denied</html>"), "arxiv": (200, ARXIV_OK)},
    )
    assert code == 2, f"a 200 that is not the API's document must exit 2, got {code}"
    assert "not JSON" in err, err


def test_crossref_answering_about_another_doi_is_rejected():
    other = json.loads(CROSSREF_OK)
    other["message"]["DOI"] = "10.1007/somebody-elses-paper"
    code, _out, err = run_main(
        [ENTRY],
        {"crossref": (200, json.dumps(other).encode()), "arxiv": (200, ARXIV_OK)},
    )
    assert code == 2, f"a record for a different DOI must not be compared, got {code}"
    assert "different record" in err, err


def test_crossref_status_not_ok_is_rejected():
    code, _out, err = run_main(
        [ENTRY],
        {
            "crossref": (200, json.dumps({"status": "failed", "message": []}).encode()),
            "arxiv": (200, ARXIV_OK),
        },
    )
    assert code == 2, f"status != ok must exit 2, got {code}"
    assert "status='failed'" in err, err


def test_arxiv_error_entry_is_a_missing_identifier_not_a_pass():
    code, out, _err = run_main(
        [ENTRY], {"crossref": (200, CROSSREF_OK), "arxiv": (200, ARXIV_ERROR)}
    )
    assert code == 1, f"an unknown arXiv id is a difference, got {code}"
    assert "no such identifier" in out, out


def test_arxiv_answering_about_another_paper_is_rejected():
    code, _out, err = run_main(
        [ENTRY],
        {
            "crossref": (200, CROSSREF_OK),
            "arxiv": (200, ARXIV_OK.replace(b"1205.1106v4", b"9999.99999v1")),
        },
    )
    assert code == 2, f"a feed about another paper must exit 2, got {code}"
    assert "different paper" in err, err


def test_a_404_from_the_registrar_route_is_a_bad_doi_not_a_pass():
    """No agency claims the DOI: that is a defect in the file, not a hiccup."""
    code, out, _err = run_main(
        [dict(ENTRY, DOI="10.9999/nope")],
        {"/agency": (404, b""), "crossref": (404, b""), "arxiv": (200, ARXIV_OK)},
    )
    assert code == 1, f"an unclaimed DOI must be reported, got {code}"
    assert "no registration agency" in out, out


def test_a_datacite_doi_is_followed_to_datacite():
    agency = json.dumps(
        {"message": {"DOI": "10.4230/x", "agency": {"id": "datacite", "label": "DataCite"}}}
    ).encode()
    record = json.dumps(
        {
            "data": {
                "id": "10.4230/x",
                "type": "dois",
                "attributes": {
                    "titles": [{"title": "A paper"}],
                    "creators": [{"givenName": "William", "familyName": "DeMeo"}],
                    "publicationYear": 2024,
                    "container": {"volume": "118", "firstPage": "2:1", "lastPage": "2:18"},
                },
            }
        }
    ).encode()
    item = {
        "id": "x",
        "title": "A paper",
        "author": [{"family": "DeMeo", "given": "William"}],
        "volume": "118",
        "page": "2:1-2:18",
        "issued": {"date-parts": [[2024]]},
        "DOI": "10.4230/x",
    }
    code, out, err = run_main(
        [item],
        {"/agency": (200, agency), "api.datacite.org": (200, record), "crossref": (404, b"")},
    )
    assert code == 0, f"a matching DataCite record must pass, got {code}\n{out}{err}"
    assert "1 record(s) fetched" in out, out


# ── retrying, which is the other half of not giving up too early ─────────────


class FakeResponse:
    """Just enough of an HTTPResponse for `get` to read."""

    def __init__(self, body: bytes) -> None:
        self.status, self._body = 200, body

    def read(self) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False


def run_get(replies, url="https://api.crossref.org/works/10.1/x"):
    """Call `get` against a scripted sequence of urlopen outcomes."""
    attempts = []

    def fake_urlopen(request, timeout=None):
        outcome = replies[min(len(attempts), len(replies) - 1)]
        attempts.append(request.full_url)
        if isinstance(outcome, Exception):
            raise outcome
        return FakeResponse(outcome)

    real_urlopen, real_backoff, real_sleep = (
        vb.urllib.request.urlopen, vb.BACKOFF, vb.time.sleep
    )
    slept = []
    try:
        vb.urllib.request.urlopen = fake_urlopen
        vb.BACKOFF = 0.0
        vb.time.sleep = slept.append
        try:
            return vb.get(url, "application/json"), attempts, slept
        except vb.Unreachable as exc:
            return exc, attempts, slept
    finally:
        vb.urllib.request.urlopen = real_urlopen
        vb.BACKOFF = real_backoff
        vb.time.sleep = real_sleep


def http_error(code, reason="Service Unavailable", headers=None):
    return urllib.error.HTTPError("http://x", code, reason, headers or {}, None)


def test_a_503_is_retried_and_then_succeeds():
    result, attempts, _slept = run_get([http_error(503), b'{"ok": true}'])
    assert len(attempts) == 2, attempts
    assert result == (200, b'{"ok": true}'), result


def test_a_persistent_503_fails_rather_than_passing_quietly():
    result, attempts, _slept = run_get([http_error(503)])
    assert isinstance(result, vb.Unreachable), result
    assert len(attempts) == vb.RETRIES, attempts
    assert f"{vb.RETRIES} attempts" in str(result), result


def test_retry_after_is_honoured_but_capped():
    _result, _attempts, slept = run_get([http_error(429, "Too Many Requests",
                                                    {"Retry-After": "9999"})])
    assert slept and max(slept) == vb.MAX_RETRY_AFTER, slept


def test_a_refused_connection_is_not_retried():
    """A host outside an allowlist will not relent; asking again just costs time."""
    result, attempts, _slept = run_get(
        [urllib.error.URLError(ConnectionRefusedError(111, "Connection refused"))]
    )
    assert isinstance(result, vb.Unreachable), result
    assert len(attempts) == 1, attempts


def test_a_404_is_an_answer_not_a_failure():
    result, attempts, _slept = run_get([http_error(404, "Not Found")])
    assert result == (404, b""), result
    assert len(attempts) == 1, attempts


# ── comparison semantics ─────────────────────────────────────────────────────


def test_accents_fold_but_hyphens_do_not():
    assert vb.key("Ruškuc") == vb.key("Ruskuc")
    assert vb.key("nonisomorphic") != vb.key("non-isomorphic")


def test_case_only_difference_is_style_not_a_mismatch():
    level, *_ = vb.compare("title", "A study of things", "A Study of Things")
    assert level == vb.STYLE, level


def test_hyphenation_difference_is_substantive():
    level, *_ = vb.compare("title", "nonisomorphic lattices", "non-isomorphic lattices")
    assert level == vb.DIFFERS, level


def test_a_field_only_the_publisher_has_is_absent_not_wrong():
    level, *_ = vb.compare("volume", None, "118")
    assert level == vb.ABSENT, level


def test_publisher_silence_is_never_a_difference():
    assert vb.compare("volume", "30", None) is None


def test_volume_written_differently_is_style():
    level, *_ = vb.compare_volume("18", "Volume 18, Issue 1")
    assert level == vb.STYLE, level
    assert vb.compare_volume("18", "Volume 19, Issue 1")[0] == vb.DIFFERS


def test_page_dashes_normalise():
    assert vb.compare_pages("693-710", "693--710") is None
    assert vb.compare_pages("693-710", "693–710") is None
    assert vb.compare_pages("693-710", "693-711")[0] == vb.DIFFERS


def test_author_order_is_substantive():
    item = {"author": [{"family": "Carette", "given": "Jacques"},
                       {"family": "DeMeo", "given": "William"}]}
    level, field, *_ = vb.compare_authors(item, ["William DeMeo", "Jacques Carette"])
    assert level == vb.DIFFERS and "order" in field, (level, field)


def test_initials_are_style_not_a_different_person():
    item = {"author": [{"family": "DeMeo", "given": "William J."}]}
    level, *_ = vb.compare_authors(item, ["William DeMeo"])
    assert level == vb.STYLE, level


def test_et_al_checks_the_prefix_and_reports_the_rest():
    item = {"author": [{"family": "Knispel", "given": "Andre"},
                       {"family": "DeMeo", "given": "William"},
                       {"literal": "et al."}]}
    level, _field, _ours, theirs = vb.compare_authors(
        item, ["Andre Knispel", "William DeMeo", "Ulf Norell"]
    )
    assert level == vb.ABSENT, level
    assert "Ulf Norell" in theirs, theirs


def test_et_al_over_a_wrong_prefix_is_a_difference():
    item = {"author": [{"family": "Knispel", "given": "Andre"},
                       {"literal": "et al."}]}
    level, *_ = vb.compare_authors(item, ["Orestis Melkonian", "Andre Knispel"])
    assert level == vb.DIFFERS, level


def test_a_proceedings_volume_title_is_not_the_venue_name():
    """IEEE registers the volume; a bibliography names the conference."""
    item = {"container-title": "36th ACM/IEEE Symposium on Logic in Computer Science (LICS 2021)"}
    volume_title = "2021 36th Annual ACM/IEEE Symposium on Logic in Computer Science (LICS)"
    proceedings = vb.check_crossref(
        item, {"type": "proceedings-article", "container-title": [volume_title]}
    )
    assert [d[0] for d in proceedings] == [vb.NOTE], proceedings
    assert proceedings[0][3] == volume_title, proceedings

    # A journal's container-title *is* the journal, so a difference there stays
    # a difference.
    journal = vb.check_crossref(
        item, {"type": "journal-article", "container-title": ["Some Other Journal"]}
    )
    assert [d[0] for d in journal] == [vb.DIFFERS], journal


def test_preprint_differences_defer_to_the_publisher():
    """arXiv holds the preprint; the journal holds the version of record."""
    item = dict(ENTRY, title="Isotopic algebras with nonisomorphic congruence lattices")
    record = {"title": "Isotopic algebras with non-isomorphic congruence lattices",
              "authors": ["William DeMeo"], "published": "2013-01-31T00:31:29Z"}
    with_publisher = vb.check_arxiv(item, record, has_publisher_record=True)
    alone = vb.check_arxiv(item, record, has_publisher_record=False)
    assert [d[0] for d in with_publisher] == [vb.NOTE], with_publisher
    assert [d[0] for d in alone] == [vb.DIFFERS], alone


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
