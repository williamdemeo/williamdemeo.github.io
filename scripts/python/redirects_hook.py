"""Emit redirect stubs for the legacy URLs listed in redirects.yml.

Only the `to:` rules produce output.  `keep`, `pending` and `none` rules emit
nothing by design -- see redirects.yml for what each means.

## Why this is not the mkdocs-redirects plugin

As of 1.2.3 that plugin takes a *hard* dependency on `properdocs`, a fork of
MkDocs which installs itself alongside and prints an advertisement for itself
on every build.  Pulling an entire alternative site generator into the
dependency tree -- and pinning two more packages in flake.nix to keep
`checks.requirements-pins` honest -- is a poor trade for what the plugin
actually does, which is write a meta-refresh HTML file at a computed path.

So that is what this does, in about forty lines, with no new dependency.  The
stub is the same shape as the plugin's: a `<meta http-equiv="refresh">` for
everyone, a `<link rel="canonical">` so search engines consolidate on the new
URL rather than indexing the stub, and a line of script that carries any
fragment across, since a refresh drops it.

## Correctness

An active rule whose target does not resolve fails the build rather than
emitting a stub that 404s.  A redirect that silently points nowhere is worse
than no redirect: it looks handled.
"""

from __future__ import annotations

import logging
import pathlib
import posixpath
import sys

log = logging.getLogger("mkdocs.plugins.redirects")

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from _redirects_lib import ConfigError, active_rules, load, output_path  # noqa: E402

STUB = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Redirecting&hellip;</title>
<link rel="canonical" href="{url}">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={url}">
<script>var h=window.location.hash;location.replace("{url}"+h)</script>
</head>
<body>
<p>This page has moved to <a href="{url}">{url}</a>.</p>
</body>
</html>
"""

#: Populated in on_files, consumed in on_post_build.
_pages: dict[str, str] = {}


def on_files(files, config):
    """Record where every source page ended up, to resolve internal targets."""
    _pages.clear()
    for f in files.documentation_pages():
        _pages[f.src_path.replace("\\", "/")] = f.url
    return files


def on_post_build(config, **kwargs):
    try:
        rules, _ = load()
    except (ConfigError, OSError) as exc:
        raise SystemExit(f"redirects.yml: {exc}")

    site_dir = pathlib.Path(config["site_dir"])
    written = 0

    for rule in active_rules(rules):
        target = str(rule.value)

        if target.lower().startswith(("http://", "https://")):
            url = target
        elif target in _pages:
            # Relative, not root-absolute, so the stubs keep working if the
            # site is ever served from a subdirectory.
            here = posixpath.dirname(output_path(rule.frm))
            url = posixpath.relpath(_pages[target], start=here or ".")
            if not url.endswith("/"):
                url += "/"
        else:
            raise SystemExit(
                f"redirects.yml: {rule.frm} -> {target}: no such page.\n"
                f"  Internal targets are docs/-relative markdown paths, e.g. `about.md`.\n"
                f"  Use `pending:` until the target exists."
            )

        dest = site_dir / output_path(rule.frm)

        # MkDocs cleans site_dir before building, so anything already here was
        # written by this build: a real page.  Overwriting it would delete the
        # page and, when the rule points at that same page, leave a stub
        # redirecting to itself.  That is not hypothetical -- it is what
        # `/archive/ -> archive/index.md` did to the archive index, and no
        # check caught it, because a stub *is* a file at the expected URL.
        if dest.exists():
            raise SystemExit(
                f"redirects.yml: {rule.frm} would overwrite a page the site "
                f"already builds at that URL.\n"
                f"  The site serves {rule.frm} itself, so this should be "
                f"`keep: true`, not a redirect."
            )

        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(STUB.format(url=url), encoding="utf-8")
        log.debug("redirect %s -> %s", rule.frm, url)
        written += 1

    pending = sum(1 for r in rules if r.form == "pending")
    log.info(
        "↪️  %d redirect stub(s) from redirects.yml; %d rule(s) still pending a target",
        written,
        pending,
    )
