## scripts

This directory contains miscellaneous utility scripts.

The Python utilities live under `scripts/python/`, separated from shell scripts and other scaffolding so that they can be lifted as a self-contained package if and when they become useful outside this repository.  See `scripts/python/_utils/` for the functional-programming primitives (Result monad, command-runner wrappers, file-ops wrappers) shared across the Python scripts.  Tool families get their own subdirectory: `scripts/python/flrp/` is the FLRP certificate emitter (WP-6, issue #457; see its README), tested by `make flrp-test`.

---

### `gh_project_populate`: automating GitHub project creation

This script is used to create a GitHub project, issues, and labels for a repository
from a single markdown file using the GitHub API.

**Prerequisites**.

- Python 3.8+
- `gh` CLI installed and authenticated

**Example Usage**.

The following commands assume the GitHub project/issue generation script is at
`scripts/python/gh_project_populate.py` and the Markdown file containing the
label/project/issue descriptions is `docs/GITHUB_PROJECT.md`.

+  Dry run — see what would be created (from the main project directory).

   ```zsh
   python3 scripts/python/gh_project_populate.py docs/GITHUB_PROJECT.md --repo williamdemeo/williamdemeo.github.io --dry-run
   ```

+  Create everything (will prompt for confirmation).


   ```zsh
   python3 scripts/python/gh_project_populate.py docs/GITHUB_PROJECT.md --repo williamdemeo/williamdemeo.github.io
   ```

+  Or create in stages.

   ```zsh
   python3 scripts/python/gh_project_populate.py docs/GITHUB_PROJECT.md --repo williamdemeo/williamdemeo.github.io --labels-only
   python3 scripts/python/gh_project_populate.py docs/GITHUB_PROJECT.md --repo williamdemeo/williamdemeo.github.io --milestones-only
   python3 scripts/python/gh_project_populate.py docs/GITHUB_PROJECT.md --repo williamdemeo/williamdemeo.github.io --issues-only
   ```

+  Resume if interrupted (e.g., start from issue M1-3).

   ```zsh
   python3 scripts/python/gh_project_populate.py docs/GITHUB_PROJECT.md --repo williamdemeo/williamdemeo.github.io --issues-only --start-from M1-3
   ```

---

### `ci/project-plan-check.sh`: the drift report CI runs

`scripts/ci/project-plan-check.sh` is what the weekly workflow executes.  It
runs the staleness check, classifies the result, and writes a report to
`$GITHUB_STEP_SUMMARY` — or to stdout when that is unset, so running it
locally shows exactly what CI would say:

```zsh
make project-plan-report
```

It is advisory and always exits 0.  Use `make project-plan-check` when you
want the raw exit code.

It lives here rather than in a workflow `run:` block because shell in YAML
cannot be run locally, cannot be linted, and cannot be tested — and because
editing it requires the `workflow` scope to push.  The workflow is now
structure only: when it runs, what it may access, and what it calls.

`scripts/ci/test_project_plan_check.sh` covers all three reporting branches
plus an unexpected exit code, using the `RENDER` seam to stand in for the
render script so no GitHub API access is needed.

---

### `audit_math.mjs`: checking that every expression renders

`scripts/js/audit_math.mjs` renders every `$...$` and `$$...$$` expression in a
content tree with KaTeX and reports what fails.  It loads the bundle the site
ships (`docs/assets/katex/katex.min.js`) and the site's macro table
(`docs/javascripts/katex-macros.js`), so the audit cannot drift from what
visitors actually get, and it needs nothing from npm.

```zsh
make math-audit                         # defaults to import/zola-converted
make math-audit MATH_SRC=docs           # or any other tree
```

Exits non-zero when anything fails to render, so it works as a CI gate once the
mathematical content has moved into `docs/`.

Fenced and inline code are stripped before scanning, so `$PATH` in a shell
example is not mistaken for mathematics.
---

### `gh_project_render`: regenerating GITHUB_PROJECT.md from GitHub

Once the project is bootstrapped, GitHub becomes the source of truth for issue state.  This script pulls live GitHub state and regenerates the issue listings inside `docs/GITHUB_PROJECT.md`, leaving hand-edited prose (milestone descriptions, exit criteria, mermaid graphs) untouched.

The file is treated as a sequence of manual prose segments interleaved with regions delimited by HTML-comment markers:

```markdown
<!-- BEGIN GENERATED: milestone-1 -->
...
<!-- END GENERATED: milestone-1 -->
```

Render preserves manual segments byte-for-byte and rebuilds each generated region from the live GitHub API.  The convention is that a region with id `milestone-N` is rebuilt from issues bearing the `milestone-N-*` label, ordered by their `[MN-k]` ordinal.

**Example Usage**.

+  Regenerate in place:

   ```zsh
   make project-plan
   ```

+  Or run the script directly:

   ```zsh
   python3 scripts/python/gh_project_render.py docs/GITHUB_PROJECT.md --repo williamdemeo/williamdemeo.github.io
   ```

+  Verify staleness without rewriting:

   ```zsh
   make project-plan-check
   ```

   Exit codes follow `diff(1)`, so a caller can tell a stale plan from a
   check that never ran:

   | Code | Meaning |
   | --- | --- |
   | 0 | the file is current |
   | 1 | the file differs from live GitHub state |
   | 2 | the run failed — authentication, API error, bad markers |

   A scheduled CI job runs this weekly and reports drift without failing the
   build: a stale plan is worth knowing about, but it is not a reason to
   block a merge.  It distinguishes 1 from 2, so a broken check is not
   reported as drift.

**Requirements**.

Both targets need an authenticated `gh` on `PATH`; the `Makefile` guards for
it and prints an actionable message rather than a stack trace when it is
missing.  Override the target repository with `make project-plan REPO=owner/name`.

Where authentication comes through `GH_TOKEN` or `GITHUB_TOKEN` rather than a
keychain — GitHub Actions, and some sandboxes — pass `NO_ENV_PREFIX=1`:

```zsh
make project-plan-check NO_ENV_PREFIX=1
```

**A note on `--no-env-prefix`**.

By default the scripts prepend `env -u GH_TOKEN -u GITHUB_TOKEN` to every `gh`
invocation, working around a `gh` quirk where those variables override the
keychain-stored token.  In an environment that authenticates *through* those
variables — some CI runners and sandboxes do — stripping them leaves `gh` with
no credentials at all, and every call fails with exit code 4.  Pass
`--no-env-prefix` there.

**The populate / render symmetry**.

The two scripts cover disjoint phases of the project's life cycle: populate is the one-shot bootstrap from a hand-authored markdown plan to GitHub project state; render is the steady-state inverse, pulling live GitHub state back into the same markdown.  After bootstrap, manual edits to issue bodies should happen on GitHub; the next `make project-plan` propagates them back into `GITHUB_PROJECT.md`.

---

### `check_redirects`: the legacy-URL redirect map

Two dead sites' URLs land on this one: the Octopress paths from
`williamdemeo.github.io`, which is where this site deploys today, and the Zola
paths from `williamdemeo.org`, which M8-1 points here.  147 URLs between them,
with inbound links from published papers, talk slides and `ualib.org`.

`redirects.yml` at the repo root is the only copy of that map.  Each entry
carries one of four dispositions and, where it matters, the reasoning:

| | |
| --- | --- |
| `to:` | redirect here — a `docs/`-relative markdown path or an `http(s)` URL |
| `keep:` | the new site serves this URL itself; no stub, but the page is verified to exist |
| `pending:` | target known, not built yet; the value says what blocks it |
| `none:` | deliberately not redirected; the value says why |

`from` is a URL path, and a trailing `/**` matches everything under a prefix.
Exact matches beat prefix matches and longer prefixes beat shorter ones, so a
specific rule can carve an exception out of a section-wide one.

**A prefix rule cannot carry `to:`,** and the loader rejects it rather than
letting it look like it worked.  `to:` emits exactly one stub, at the prefix
itself, so `/exams/** → …` would redirect `/exams/` and leave the other 47
URLs 404ing with the build reporting success.  Switching a prefix rule on
means either listing its URLs individually, or — for a host move, where each
URL should map onto the matching path under the new host — teaching the hook
prefix rewriting first.  `keep:`, `pending:` and `none:` are fine on a prefix
rule, since none of them emits anything.

**`redirects_hook.py`** emits the stubs at build time, wired in through
mkdocs.yml's `hooks:`.  Only `to:` rules produce output; an active rule whose
target does not resolve aborts the build rather than shipping a stub that
404s.  This deliberately does *not* use the `mkdocs-redirects` plugin, which
as of 1.2.3 hard-depends on `properdocs` — an entire alternative site
generator that installs itself and advertises for a replacement on every
build.  That is a large supply-chain surface, and two more packages to pin in
`flake.nix`, for about forty lines of "write a meta-refresh file".

**`check_redirects.py`** proves the map is trustworthy, in three parts:

```console
$ make redirect-check          # builds the site, then checks against it
  zola        103 urls
  octopress    46 urls
  union       147 urls
  rules: 64
    to         2 rules     2 urls
    keep       3 rules     3 urls
    pending   55 rules   138 urls
    none       4 rules     4 urls
OK -- every legacy URL is accounted for exactly once.
```

- **coverage** — every URL in both inventories is governed by a rule, and every
  rule governs at least one URL.  Several rules may *match* one URL — a
  carve-out inside a prefix rule is exactly that — but precedence picks a
  unique winner, and the tests check that uniqueness exhaustively against the
  real inventories.  A legacy URL nobody thought about is the failure this
  exists to prevent, and it is invisible without the check.
- **`--site DIR`** — what the map claims resolves does resolve: `keep` URLs
  have a real page, active redirects emitted a stub.  Claiming a URL is
  preserved and then not serving it is worse than an honest redirect.
- **`--verify-inventory`** — the Zola URL list still corresponds 1:1 with the
  imported page tree, re-derived rather than taken on trust.  This is what
  turned up that Zola slugifies to lowercase, so `exams/real/1991Nov21.md` is
  served at `/exams/real/1991nov21/` — 43 of the highest-traffic URLs differ
  from their filenames by case alone.

Exit codes follow `diff(1)`: 0 current, 1 a check failed, 2 could not run.
`make redirect-test` runs the rule-matching unit tests.  Both run in CI as
`nix flake check` derivations.

The pending count is printed on every run, grouped by what blocks each group,
so the remainder stays visible instead of being quietly forgotten.  Switching
a redirect on when its target lands is changing `pending:` to `to:` — one
line, one file.

---

### Notes

- The script uses `env -u GH_TOKEN -u GITHUB_TOKEN` by default to work around
  token precedence issues.  Use `--no-env-prefix` to disable this.
- A 1.5-second delay between API calls avoids rate limiting (adjustable with `--delay`).
- Labels and milestones are idempotent — re-running skips existing ones.
- Issue titles are prefixed with `[M0-1]`, `[M1-2]`, etc. for easy identification.

---
