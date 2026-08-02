#!/usr/bin/env python3
"""Tests for the redirect-map library.

Needs PyYAML, which arrives as a MkDocs dependency rather than on its own, so
``make redirect-test`` runs these against the virtualenv (or the Nix dev shell)
rather than the system interpreter.  Nothing else is required: run directly
with ``python3 scripts/python/test_redirects.py`` for ``OK`` and exit 0, or
under ``pytest`` if it happens to be installed.

The rule-matching tests are the ones that matter.  `check_redirects.py` proves
every legacy URL is covered by *some* rule, but "covered" is only meaningful if
the rule that wins is the one a reader would expect.  A section-wide rule
quietly swallowing the exception carved out of it would still report full
coverage while sending the URL somewhere wrong.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _redirects_lib as rl  # noqa: E402


def rules(*specs) -> list[rl.Rule]:
    """Build rules from `(from, form, value)` triples, as `load` would."""
    out = []
    for frm, form, value in specs:
        prefix = frm.endswith("/**")
        out.append(
            rl.Rule(frm=frm[:-2] if prefix else frm, form=form, value=value, prefix=prefix)
        )
    return out


def load_text(text: str):
    with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as fh:
        fh.write(text)
        path = Path(fh.name)
    try:
        return rl.load(path)
    finally:
        path.unlink()


def test_exact_beats_prefix():
    rs = rules(("/computing/**", "pending", "x"), ("/computing/coq/", "to", "a.md"))
    assert rl.match("/computing/coq/", rs).form == "to"
    assert rl.match("/computing/other/", rs).form == "pending"


def test_longer_prefix_wins():
    rs = rules(("/research/**", "pending", "x"), ("/research/csp/**", "to", "a.md"))
    assert rl.match("/research/csp/oldnotes/", rs).form == "to"
    assert rl.match("/research/index/", rs).form == "pending"


def test_prefix_matches_its_own_root():
    """`/exams/**` has to cover `/exams/` itself, or the section index is a gap."""
    rs = rules(("/exams/**", "pending", "x"))
    assert rl.match("/exams/", rs) is not None
    assert rl.match("/exams/real/1991nov21/", rs) is not None


def test_unmatched_url_is_none():
    assert rl.match("/nowhere/", rules(("/exams/**", "pending", "x"))) is None


def test_prefix_does_not_match_sibling():
    """`/talks/**` must not swallow `/talksomething/`."""
    rs = rules(("/talks/**", "pending", "x"))
    assert rl.match("/talksomething/", rs) is None


def test_output_path():
    assert rl.output_path("/") == "index.html"
    assert rl.output_path("/about/") == "about/index.html"
    assert rl.output_path("/exams/real/1991nov21/") == "exams/real/1991nov21/index.html"
    # A URL naming a file maps to itself rather than gaining an index.html.
    assert rl.output_path("/atom.xml") == "atom.xml"


def test_is_stubbable():
    assert rl.is_stubbable("/about/")
    assert rl.is_stubbable("/")
    assert not rl.is_stubbable("/atom.xml")
    assert not rl.is_stubbable("/robots.txt")


def test_active_rules_are_only_to():
    rs = rules(
        ("/a/", "to", "x.md"),
        ("/b/", "keep", True),
        ("/c/", "pending", "later"),
        ("/d/", "none", "never"),
    )
    assert [r.frm for r in rl.active_rules(rs)] == ["/a/"]


def test_load_rejects_two_forms():
    try:
        load_text("rules:\n  - from: /a/\n    to: x.md\n    keep: true\n")
    except rl.ConfigError as exc:
        assert "expected exactly one" in str(exc)
    else:
        raise AssertionError("a rule with two dispositions should not load")


def test_load_rejects_no_form():
    try:
        load_text("rules:\n  - from: /a/\n")
    except rl.ConfigError as exc:
        assert "expected exactly one" in str(exc)
    else:
        raise AssertionError("a rule with no disposition should not load")


def test_load_rejects_duplicate_from():
    try:
        load_text("rules:\n  - from: /a/\n    keep: true\n  - from: /a/\n    keep: true\n")
    except rl.ConfigError as exc:
        assert "duplicate" in str(exc)
    else:
        raise AssertionError("two rules for one URL should not load")


def test_load_rejects_missing_from():
    try:
        load_text("rules:\n  - keep: true\n")
    except rl.ConfigError as exc:
        assert "no `from`" in str(exc)
    else:
        raise AssertionError("a rule without `from` should not load")


def test_load_strips_prefix_marker():
    rs, _ = load_text("rules:\n  - from: /exams/**\n    pending: later\n")
    assert rs[0].prefix and rs[0].frm == "/exams/"


def test_read_inventory_skips_comments():
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
        fh.write("# a header\n\n/a/\n/b/   # trailing\n")
        path = Path(fh.name)
    try:
        assert rl.read_inventory(path) == ["/a/", "/b/"]
    finally:
        path.unlink()


def test_load_rejects_prefix_with_to():
    """`to:` emits one stub; a prefix rule names many URLs.

    Verified before this guard existed: `/exams/** -> https://…` wrote a single
    stub, at `/exams/`, and the build reported success -- leaving 47 of the
    site's highest-traffic URLs 404ing.
    """
    try:
        load_text("rules:\n  - from: /exams/**\n    to: https://example.com/exams/\n")
    except rl.ConfigError as exc:
        assert "prefix rule with `to:`" in str(exc)
    else:
        raise AssertionError("a prefix rule with `to:` should not load")


def test_load_allows_prefix_with_non_emitting_forms():
    """`keep`, `pending` and `none` emit nothing, so a prefix is fine."""
    for form, value in (("keep", "true"), ("pending", "later"), ("none", "never")):
        rs, _ = load_text(f"rules:\n  - from: /exams/**\n    {form}: {value}\n")
        assert rs[0].prefix and rs[0].form == form


def test_winner_is_unique_for_every_real_url():
    """No URL in either inventory has two rules tied for most specific.

    Coverage is only meaningful if the rule that wins is the one a reader would
    predict.  The uniqueness argument is short -- exact outranks prefix, at most
    one exact rule can equal a URL, and two equal-length prefixes matching the
    same URL would be identical and rejected as duplicates -- but an argument is
    not a check, so this runs it over every URL the two legacy sites served.
    """
    rules, inventories = rl.load()
    urls = set()
    for path in inventories.values():
        urls |= set(rl.read_inventory(path))
    assert urls, "no URLs read from the inventories"

    for url in sorted(urls):
        hits = [r for r in rules if r.matches(url)]
        assert hits, f"{url} is matched by no rule"
        best = max(h.specificity for h in hits)
        tied = [h for h in hits if h.specificity == best]
        assert len(tied) == 1, f"{url} has {len(tied)} rules tied at specificity {best}"
        assert rl.match(url, rules) is tied[0]


def test_real_config_loads_and_covers_its_inventories():
    """The shipped redirects.yml parses, and its inventories exist."""
    rs, inventories = rl.load()
    assert rs, "redirects.yml defines no rules"
    assert set(inventories) == {"zola", "octopress"}
    for name, path in inventories.items():
        assert path.exists(), f"{name} inventory missing: {path}"


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
