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

### Notes

- The script uses `env -u GH_TOKEN -u GITHUB_TOKEN` by default to work around
  token precedence issues.  Use `--no-env-prefix` to disable this.
- A 1.5-second delay between API calls avoids rate limiting (adjustable with `--delay`).
- Labels and milestones are idempotent — re-running skips existing ones.
- Issue titles are prefixed with `[M0-1]`, `[M1-2]`, etc. for easy identification.

---
