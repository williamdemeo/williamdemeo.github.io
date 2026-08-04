"""Count the evidence-strip numbers from an agda-algebras checkout.

The home page's evidence strip (M3-2c, #95) shows a small number of measures,
and ADR-009's third principle binds them: every figure on screen is a count a
script produced, never copy.  This is that script.  Its output is committed as
`docs/assets/evidence.json`, so the site build needs no network and no
checkout; regenerating is a deliberate act, and the JSON records the commit it
was counted from.

## What is counted, and what deliberately is not

* **Agda modules** -- the `*.lagda.md` files under `src/`.
* **Lines of Agda** -- lines *inside* ```agda fences only.  A literate module
  is mostly prose, and counting prose as code would be exactly the inflated
  claim the strip exists to avoid.
* **Postulates** -- occurrences of a line-leading `postulate` keyword inside
  those fences.  Zero is the expected value: every module carries `--safe`,
  under which Agda rejects postulates, and the module count of that pragma is
  recorded alongside as corroboration.
* **Definitions and theorems are not counted.**  A grep cannot distinguish a
  theorem from a helper from a re-export, and a number that cannot be defended
  is worse than no number.  If a typechecker-backed count (from `.agdai`
  interfaces) lands later, it can join the strip; see #95.

Usage:

    python3 scripts/python/count_evidence.py /path/to/agda-algebras \
        > docs/assets/evidence.json

The path must be a git checkout; the commit hash and date are read from it and
shipped in the JSON, so a reader of the strip can check the numbers against
exactly the tree they were counted from.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

#: Matches a line-leading `postulate`, allowing indentation.  Agda's layout
#: rules mean a postulate block opens with the keyword at the start of its
#: (possibly indented) line; an identifier merely *containing* the word, like
#: `postulateFree`, does not match because of the word boundary.
POSTULATE = re.compile(r"^\s*postulate\b")

SAFE_PRAGMA = re.compile(r"OPTIONS.*--safe")


def agda_lines(path: Path):
    """The lines inside ```agda fences of one literate module."""
    lines, in_fence = [], False
    for line in path.read_text(encoding="utf-8").splitlines():
        if in_fence:
            if line.startswith("```"):
                in_fence = False
            else:
                lines.append(line)
        elif line.startswith("```agda"):
            in_fence = True
    return lines


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__.split("Usage:")[1].strip())
    repo = Path(sys.argv[1])
    src = repo / "src"
    if not src.is_dir():
        sys.exit(f"{src} is not a directory; pass an agda-algebras checkout")

    modules = sorted(src.rglob("*.lagda.md"))
    code = []
    for module in modules:
        code.extend(agda_lines(module))
    safe = sum(
        1 for m in modules if SAFE_PRAGMA.search(m.read_text(encoding="utf-8"))
    )
    postulates = sum(1 for line in code if POSTULATE.match(line))

    out = {
        "generated_by": "scripts/python/count_evidence.py",
        "source": {
            "repo": "https://github.com/ualib/agda-algebras",
            "commit": git(repo, "rev-parse", "HEAD"),
            "commit_date": git(repo, "log", "-1", "--format=%cs"),
        },
        "measures": [
            {
                "id": "modules",
                "value": len(modules),
                "label": "Agda modules",
                "detail": f"{safe} of {len(modules)} carry --safe",
                "command": "find src -name '*.lagda.md' | wc -l",
                "href": "https://github.com/ualib/agda-algebras",
            },
            {
                "id": "lines",
                "value": len(code),
                "label": "lines of Agda",
                "detail": "code fences only; prose not counted",
                "command": "awk fence-extraction over src/**/*.lagda.md",
                "href": "https://github.com/ualib/agda-algebras",
            },
            {
                "id": "postulates",
                "value": postulates,
                "label": "postulates",
                "detail": "--safe rejects them; counted anyway",
                "command": r"grep -cE '^\s*postulate\b' over the fenced code",
                "href": "https://github.com/ualib/agda-algebras",
                "emphasis": True,
            },
            {
                "id": "requests",
                "value": 0,
                "label": "third-party requests",
                "detail": "on every page of this site",
                "command": "make offline-audit",
                "href": "design/style.md#checks",
                "emphasis": True,
            },
        ],
    }
    json.dump(out, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
