# Pending workflow update — replaces the live `project-plan-check.yml`

This is an **updated** version of `.github/workflows/project-plan-check.yml`,
not a new workflow. It is parked here because GitHub refuses writes to
`.github/workflows/` from a credential lacking the `workflow` scope, which the
session that wrote it does not have.

```zsh
git mv -f .github/workflows-pending/project-plan-check.yml .github/workflows/project-plan-check.yml
git rm .github/workflows-pending/README.md
git commit -m "Apply the drift/failure distinction to the staleness check"
```

The directory should not survive that commit.

## What changed, and why

The live version reports **"docs/GITHUB_PROJECT.md has drifted"** on any
non-zero exit. But `gh_project_render.py` also exits non-zero when the check
*fails* — an expired token, an API error — so a broken check was being
reported as a stale plan, sending you to fix the wrong thing.

`gh_project_render.py` now follows `diff(1)`: **0** current, **1** differs,
**2** the run failed. This version captures the code rather than letting the
step fail, and reports all three outcomes. A failed check now says so, quotes
the error, and states that the plan's freshness is unknown.

Rewriting it also moved the two `${{ }}` interpolations out of the shell body
and into `env:`, which removes the usual expression-injection footgun.

Raised by Copilot review on #63.
