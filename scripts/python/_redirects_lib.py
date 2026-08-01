"""Shared logic for the legacy-URL redirect map.

`redirects.yml` is the single source of truth.  Two things read it:

    redirects_hook.py   emits a stub for each active rule at build time
    check_redirects.py  proves the file covers every legacy URL, and that the
                        targets resolve

Keeping the matching in one place is what lets those two agree.  If the hook
and the checker disagreed about which rule wins for a URL, the checker would be
verifying something other than what gets built.
"""

from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass, field

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CONFIG = REPO_ROOT / "redirects.yml"

#: The four mutually exclusive dispositions a rule can carry.
FORMS = ("to", "keep", "pending", "none")


@dataclass
class Rule:
    frm: str
    form: str
    value: object
    #: Set for `from: /foo/**`; then `frm` is the bare prefix `/foo/`.
    prefix: bool = False
    matched: list[str] = field(default_factory=list)

    @property
    def active(self) -> bool:
        return self.form == "to"

    def matches(self, url: str) -> bool:
        return url.startswith(self.frm) if self.prefix else url == self.frm

    @property
    def specificity(self) -> int:
        """Exact beats prefix; a longer prefix beats a shorter one.

        Without this a section-wide rule would swallow the exceptions carved
        out of it, silently -- the URL would still be "covered", just by the
        wrong rule, which is the failure mode hardest to notice.
        """
        return 10_000 if not self.prefix else len(self.frm)


class ConfigError(Exception):
    pass


def load(path: pathlib.Path = CONFIG) -> tuple[list[Rule], dict[str, pathlib.Path]]:
    raw = yaml.safe_load(path.read_text())
    if not isinstance(raw, dict) or "rules" not in raw:
        raise ConfigError(f"{path}: expected a mapping with a `rules` key")

    rules: list[Rule] = []
    seen: set[str] = set()
    for i, entry in enumerate(raw["rules"], start=1):
        if not isinstance(entry, dict) or "from" not in entry:
            raise ConfigError(f"{path}: rule {i} has no `from`")
        frm = str(entry["from"])
        forms = [f for f in FORMS if f in entry]
        if len(forms) != 1:
            raise ConfigError(
                f"{path}: rule {i} ({frm}) has {len(forms)} of {FORMS}; expected exactly one"
            )
        prefix = frm.endswith("/**")
        if prefix:
            frm = frm[: -len("**")]
        if frm in seen:
            raise ConfigError(f"{path}: duplicate rule for {frm!r}")
        seen.add(frm)
        rules.append(Rule(frm=frm, form=forms[0], value=entry[forms[0]], prefix=prefix))

    inventories = {
        name: REPO_ROOT / rel for name, rel in (raw.get("inventories") or {}).items()
    }
    return rules, inventories


def read_inventory(path: pathlib.Path) -> list[str]:
    """URL list, one per line; `#` comments and blank lines skipped."""
    out = []
    for line in path.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            out.append(line)
    return out


def match(url: str, rules: list[Rule]) -> Rule | None:
    """The single rule that governs `url`, or None."""
    hits = [r for r in rules if r.matches(url)]
    if not hits:
        return None
    return max(hits, key=lambda r: r.specificity)


def output_path(url: str) -> str:
    """Where in the built site the stub for `url` goes.

    `/a/b/` is served by `a/b/index.html`, so that is what gets written.  A URL
    that already names a file (`/atom.xml`) maps to itself -- though see
    `is_stubbable`: those should not be redirected with an HTML stub at all.
    """
    stripped = url.strip("/")
    if not stripped:
        return "index.html"
    if re.search(r"\.[A-Za-z0-9]+$", stripped):
        return stripped
    return f"{stripped}/index.html"


def is_stubbable(url: str) -> bool:
    """Whether an HTML meta-refresh stub is a sane thing to serve here.

    A URL that names a non-HTML file (`/atom.xml`) is requested by something
    that wants that format.  Handing a feed reader an HTML page is worse than
    leaving the URL alone, so those need a real file, not a redirect.
    """
    return not re.search(r"\.[A-Za-z0-9]+$", url.rstrip("/"))


def active_rules(rules: list[Rule]) -> list[Rule]:
    """The rules that produce a stub, in file order."""
    return [r for r in rules if r.active]
