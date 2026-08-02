#!/usr/bin/env python3
"""Verify the legacy-URL redirect map.

Three independent checks, each of which can be run on its own:

  coverage    every URL both legacy sites served is governed by a rule in
              redirects.yml, and every rule governs at least one URL.  Several
              rules may *match* one URL -- an exact carve-out inside a prefix
              rule is the point -- but precedence picks a unique winner, and
              that winner is what is reported.  A legacy URL nobody thought
              about is the failure this exists to prevent, and it is invisible
              without this check.

  --site DIR  every URL the map claims resolves actually resolves in the built
              site: `keep` URLs have a real page, and active redirects emitted
              a stub.  Claiming a URL is preserved and then not serving it is
              worse than an honest redirect.

  --verify-inventory
              the Zola URL list still corresponds 1:1 with the imported page
              tree.  That correspondence is the evidence the list is complete;
              this re-derives it rather than trusting the header comment.

Exit codes follow diff(1): 0 all good, 1 a check failed, 2 could not run.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from _redirects_lib import (  # noqa: E402
    CONFIG,
    REPO_ROOT,
    ConfigError,
    is_stubbable,
    load,
    match,
    read_inventory,
)

DOCS = REPO_ROOT / "docs"
TREE = REPO_ROOT / "import" / "zola-converted"
SRC = REPO_ROOT / "import" / "zola-content"

DATED = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-(.+)$")


def check_coverage(rules, inventories) -> list[str]:
    problems = []
    urls = set()
    for name, path in inventories.items():
        if not path.exists():
            problems.append(f"inventory {name}: {path} does not exist")
            continue
        found = read_inventory(path)
        print(f"  {name:<10} {len(found):>4} urls  ({path.relative_to(REPO_ROOT)})")
        urls |= set(found)

    print(f"  {'union':<10} {len(urls):>4} urls")

    for url in sorted(urls):
        rule = match(url, rules)
        if rule is None:
            problems.append(f"no rule covers {url}")
        else:
            rule.matched.append(url)

    # A rule matching nothing is either a typo or a URL that quietly vanished
    # from the inventory.  Both are worth surfacing.
    for rule in rules:
        if not rule.matched:
            problems.append(f"rule {rule.frm!r} matches no URL in any inventory")

    # A stub is an HTML page; serving one where a feed or a text file was
    # requested breaks the client more thoroughly than a 404 would.
    for rule in rules:
        if rule.active and not is_stubbable(rule.frm):
            problems.append(
                f"{rule.frm}: an HTML stub is the wrong response for a non-HTML URL"
            )

    # A `to:` rule whose *source* URL is also a real page is always a bug: the
    # hook writes stubs after the build, so the stub replaces the page -- and
    # when the rule points at that same page, the result is a stub redirecting
    # to itself.  The hook refuses to do it; this reports it before the build
    # runs, and names the fix.
    for rule in rules:
        if not rule.active:
            continue
        stripped = rule.frm.strip("/")
        for candidate in (f"{stripped}/index.md", f"{stripped}.md") if stripped else ("index.md",):
            if (DOCS / candidate).exists():
                problems.append(
                    f"{rule.frm}: the site serves this URL itself "
                    f"(docs/{candidate}); use `keep: true`, not `to:`"
                )
                break

    # An internal target must exist as a source file, or the hook aborts the
    # build.  Catching it here reports every bad target at once, rather than
    # one per build.
    for rule in rules:
        if rule.active:
            target = str(rule.value)
            if not target.lower().startswith(("http://", "https://")):
                if not (DOCS / target).exists():
                    problems.append(f"{rule.frm} -> {target}: no such file under docs/")

    by_form = {}
    for rule in rules:
        by_form.setdefault(rule.form, []).append(rule)
    print()
    print(f"  rules: {len(rules)}")
    for form in ("to", "keep", "pending", "none"):
        got = by_form.get(form, [])
        n_urls = sum(len(r.matched) for r in got)
        print(f"    {form:<8} {len(got):>3} rules  {n_urls:>4} urls")
    return problems


def check_site(rules, site: pathlib.Path) -> list[str]:
    problems = []
    if not site.exists():
        return [f"{site} does not exist -- run `make build` first"]

    def served(url: str) -> bool:
        rel = url.strip("/")
        candidates = [site / rel / "index.html"] if rel else [site / "index.html"]
        if rel and re.search(r"\.[A-Za-z0-9]+$", rel):
            candidates = [site / rel]
        return any(c.exists() for c in candidates)

    kept = emitted = 0
    for rule in rules:
        if rule.form == "keep":
            for url in rule.matched:
                if served(url):
                    kept += 1
                else:
                    problems.append(f"{url}: declared `keep` but the built site has no page there")
        elif rule.active:
            for url in rule.matched:
                if served(url):
                    emitted += 1
                else:
                    problems.append(f"{url}: active redirect, but no stub in the built site")

    print(f"  preserved urls serving a page : {kept}")
    print(f"  redirect stubs emitted        : {emitted}")
    return problems


def check_inventory(inventories) -> list[str]:
    """Re-derive the Zola URLs from the imported tree and compare."""
    if not TREE.exists():
        return [f"{TREE} does not exist"]
    listed = set(read_inventory(inventories["zola"]))

    def front_matter(page: str) -> dict:
        src = SRC / page
        if not src.exists():
            return {}
        m = re.match(r"\+\+\+\n(.*?)\n\+\+\+", src.read_text(errors="replace"), re.S)
        if not m:
            return {}
        return dict(re.findall(r'^\s*(\w+)\s*=\s*"(.*?)"', m.group(1), re.M))

    def url_for(page: str) -> str:
        fm = front_matter(page)
        if "path" in fm:
            p = fm["path"].strip("/")
            return f"/{p}/" if p else "/"
        stem = page.removesuffix(".md")
        if stem in ("index", "_index"):
            return "/"
        if stem.endswith("/index") or stem.endswith("/_index"):
            stem = stem.rsplit("/", 1)[0]
        parts = stem.split("/")
        if "slug" in fm:
            parts[-1] = fm["slug"]
        else:
            m = DATED.match(parts[-1])
            if m:
                parts[-1] = m.group(4)
        # Zola slugifies to lowercase: `exams/real/1991Nov21.md` is served at
        # /exams/real/1991nov21/.  Every exam URL differs from its filename by
        # case alone, which is exactly the kind of thing that 404s quietly.
        return "/" + "/".join(p.lower() for p in parts) + "/"

    pages = sorted(p.relative_to(TREE).as_posix() for p in TREE.rglob("*.md"))
    derived = {}
    for page in pages:
        derived.setdefault(url_for(page), []).append(page)

    problems = []
    for url in sorted(listed - set(derived)):
        problems.append(f"{url}: listed as served, but no imported page derives it")
    for url in sorted(set(derived) - listed):
        problems.append(f"{url}: derived from {derived[url][0]}, but not in the inventory")
    for url, ps in derived.items():
        if len(ps) > 1:
            problems.append(f"{url}: derived from {len(ps)} pages ({', '.join(ps)})")

    print(f"  imported pages : {len(pages)}")
    print(f"  listed urls    : {len(listed)}")
    print(f"  matched        : {len(listed & set(derived))}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--site", type=pathlib.Path, help="built site to verify against")
    ap.add_argument(
        "--verify-inventory",
        action="store_true",
        help="re-derive the Zola URL list from the imported tree",
    )
    ap.add_argument("--config", type=pathlib.Path, default=CONFIG)
    args = ap.parse_args()

    try:
        rules, inventories = load(args.config)
    except (ConfigError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"redirect map: {args.config.relative_to(REPO_ROOT)}")
    problems = check_coverage(rules, inventories)

    if args.verify_inventory:
        print("\ninventory provenance:")
        problems += check_inventory(inventories)

    if args.site:
        print(f"\nbuilt site: {args.site}")
        problems += check_site(rules, args.site)

    print()
    if problems:
        print(f"{len(problems)} problem(s):", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1

    pending = [r for r in rules if r.form == "pending"]
    n = sum(len(r.matched) for r in pending)
    print("OK -- every legacy URL is governed by exactly one rule.")
    if pending:
        print(f"{n} url(s) across {len(pending)} rule(s) are still pending a target:")
        blockers = {}
        for r in pending:
            blockers.setdefault(str(r.value), 0)
            blockers[str(r.value)] += len(r.matched)
        for reason, count in sorted(blockers.items(), key=lambda kv: -kv[1]):
            print(f"  {count:>4}  {reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
