"""Re-run the hero's hole-filling sessions and emit their transcript as JSON.

The home page's terminal (M3-2d, #96) replays Agda sessions, and ADR-009's
third principle binds it: anything replayed is a replay of something real.
This script is where the something real happens.  For each module listed in
`MODULES` -- one per tab of the terminal, in tab order -- it reads the replay
block, derives the hole variant (the last line's right-hand side becomes
`{! !}`), and drives a real Agda through the session an editor would have:
load the file, read the goal, give the fill, watch the goal count reach
zero.  It then batch-checks the committed file as written.  Everything the
terminal shows is taken from what Agda answered here -- the goal text, the
goal count, the version on the `✓` line -- never typed by hand.

The output is committed as `docs/assets/proof.json`, so the site build needs
no Agda and no re-run; regenerating is a deliberate act (`make proof`), and
each session records the SHA-256 of the module it ran over, so a transcript
that has gone stale is at least *detectably* stale -- compare the hash
against the checked-out file.  (A git commit would be the evidence-strip
precedent, but this transcript lives in the same repository as its source,
and a commit recorded inside a tree cannot name that tree; the content hash
can.)

Usage:

    python3 scripts/python/gen_proof.py [--agda /path/to/agda] \
        > docs/assets/proof.json

The Agda need not know any library: the modules are self-contained by
design (no imports), and every run passes `--no-libraries` so the machine's
default libraries cannot leak in -- without it, a module named `Induction`
is ambiguous against agda-stdlib on any machine whose defaults include it.

## Output fields

* `agda`     -- the version string parsed from `agda --version`, shared by
               every session below.
* `sessions` -- one entry per module, in tab order:
    * `label`  -- the definiendum of the filled line; the terminal's tab
                 label, so the tab bar never invents a name either.
    * `source` -- the module's repo path, its SHA-256, the run date, and
                 the command that regenerates this file.
    * `lines`  -- the replay block's lines above the one that gets the hole.
    * `hole`   -- the derived hole line, as loaded.
    * `goals`  -- what Agda reported for it: interaction-point id and goal
                 type.
    * `fill`   -- the real last line, whose right-hand side was given.
    * `names`  -- the identifiers the renderer may colour as definitions:
                 the replay block's own definienda, listed so the hook
                 never guesses at what is a name.  Deliberately nothing
                 else -- a terminal where every known identifier is
                 coloured is one where the definiendum no longer stands
                 out.
    * `check`  -- the `✓` line, composed here from the version of the Agda
                 that actually accepted the file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

#: The replayed modules, relative to the repository root, in tab order --
#: the research signature first.  The markers inside each delimit its
#: replay block; see the prose there.
MODULES = [
    "agda/Free.lagda.md",
    "agda/Induction.lagda.md",
    "agda/Absurd.lagda.md",
    "agda/DoubleNegation.lagda.md",
    "agda/Absorption.lagda.md",
]

MARKED = re.compile(
    r"<!-- replay-begin -->\n```agda\n(.*?)\n```\n<!-- replay-end -->",
    re.DOTALL,
)

#: A definiendum: `name : ...` opening a declaration, at any indent (a
#: replay block may live inside an anonymous module).  Mixfix names
#: containing `_` are excluded -- their occurrences (`𝕌[ 𝑨 ]`) are not the
#: token the declaration names, so a renderer could not match them anyway.
DEFINIENDUM = re.compile(
    r"^\s*([^\s_(){}\[\];.\"@-][^\s_(){}\[\];.\"@]*)\s+:\s", re.MULTILINE)


def fail(msg: str) -> None:
    sys.exit(f"gen_proof: {msg}")


def replay_block(module: str, text: str) -> list[str]:
    found = MARKED.findall(text)
    if len(found) != 1:
        fail(f"{module} must contain exactly one marked replay block; "
             f"found {len(found)}")
    lines = found[0].split("\n")
    if len(lines) < 2 or " = " not in lines[-1]:
        fail(f"{module}'s replay block must end in a `lhs = rhs` line to "
             "put the hole in")
    return lines


def interact(agda: str, cwd: Path, commands: list[str]) -> list[dict]:
    """Run one `--interaction-json` session; return the parsed responses.

    Responses arrive one JSON object per line, interleaved with `JSON> `
    prompts; the prompt is stripped wherever it lands.
    """
    proc = subprocess.run(
        [agda, "--interaction-json", "--no-libraries"],
        input="".join(c + "\n" for c in commands),
        capture_output=True, text=True, cwd=cwd,
    )
    responses = []
    for line in proc.stdout.splitlines():
        line = line.removeprefix("JSON> ").strip()
        if line:
            responses.append(json.loads(line))
    if proc.returncode != 0:
        fail(f"agda --interaction-json exited {proc.returncode}:\n"
             f"{proc.stderr}")
    for r in responses:
        info = r.get("info", {})
        if "Error" in str(r.get("kind", "")) or "Error" in str(info.get("kind", "")):
            fail(f"Agda reported an error:\n{json.dumps(r, indent=2)}")
        if info.get("kind") == "AllGoalsWarnings" and info.get("errors"):
            fail(f"Agda reported errors:\n{json.dumps(info['errors'], indent=2)}")
    return responses


def haskell_string(s: str) -> str:
    """A Haskell string literal, for splicing into an IOTCM command."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def session(agda: str, version: str, module: str) -> dict:
    """Run one module's hole-filling session; return its transcript entry."""
    src_path = ROOT / module
    text = src_path.read_text(encoding="utf-8")
    lines = replay_block(module, text)
    fill = lines[-1]
    lhs = fill.split(" = ", 1)[0]
    hole = f"{lhs} = {{! !}}"
    rhs = fill.split(" = ", 1)[1]
    label = lhs.strip().split()[0]

    names = sorted(set(DEFINIENDUM.findall("\n".join(lines))))

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        name = src_path.name

        # The session: load the hole variant, then give the fill into ?0.
        # `Indirect` matters -- it is what agda-mode sends, and it keeps large
        # highlighting payloads out of the response stream.
        (tmp / name).write_text(
            text.replace(fill, hole), encoding="utf-8")
        responses = interact(agda, tmp, [
            f"IOTCM {haskell_string(name)} NonInteractive Indirect "
            f"(Cmd_load {haskell_string(name)} [])",
            f"IOTCM {haskell_string(name)} NonInteractive Indirect "
            f"(Cmd_give WithoutForce 0 noRange {haskell_string(rhs)})",
        ])

        goal_states = [r["info"] for r in responses
                       if r.get("info", {}).get("kind") == "AllGoalsWarnings"]
        if len(goal_states) < 2:
            fail(f"{module}: expected goal reports after the load and after "
                 "the give")
        open_goals = goal_states[0]["visibleGoals"]
        if len(open_goals) != 1 or open_goals[0].get("kind") != "OfType":
            fail(f"{module}: expected exactly one typed goal after loading "
                 f"the hole variant; got {json.dumps(open_goals)}")
        gave = [r for r in responses if r.get("kind") == "GiveAction"]
        if not gave:
            fail(f"{module}: Agda did not accept the fill (no GiveAction "
                 "in responses)")
        if goal_states[-1]["visibleGoals"]:
            fail(f"{module}: goals remain after the give; the transcript "
                 "would be a lie")

        # The `✓` line's claim is about the committed file, so the committed
        # bytes are what the final batch check runs over.
        (tmp / name).write_text(text, encoding="utf-8")
        batch = subprocess.run([agda, "--no-libraries", name],
                               capture_output=True, text=True, cwd=tmp)
        if batch.returncode != 0:
            fail(f"{module} failed to type-check as committed:\n"
                 f"{batch.stdout}{batch.stderr}")

    return {
        "label": label,
        "source": {
            "file": module,
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "date": date.today().isoformat(),
            "command": "make proof",
        },
        "lines": lines[:-1],
        "hole": hole,
        "goals": [
            {"id": g["constraintObj"]["id"], "type": g["type"]}
            for g in open_goals
        ],
        "fill": fill,
        "names": names,
        "check": f"✓ type-checked · Agda {version}",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--agda", default="agda",
                    help="the Agda to run the sessions with (default: agda)")
    args = ap.parse_args()

    if shutil.which(args.agda) is None:
        fail(f"`{args.agda}` is not executable; pass --agda /path/to/agda "
             "(the Makefile forwards AGDA=... here)")

    version_out = subprocess.run(
        [args.agda, "--version"], capture_output=True, text=True, check=True
    ).stdout
    m = re.search(r"Agda version (\S+)", version_out)
    if not m:
        fail(f"could not parse `{args.agda} --version`:\n{version_out}")
    version = m.group(1)

    out = {
        "generated_by": "scripts/python/gen_proof.py",
        "agda": version,
        "sessions": [session(args.agda, version, module)
                     for module in MODULES],
    }
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
