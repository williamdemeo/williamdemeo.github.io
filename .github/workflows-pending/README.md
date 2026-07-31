# Pending workflow update — replaces the live `project-plan-check.yml`

```zsh
git mv -f .github/workflows-pending/project-plan-check.yml .github/workflows/project-plan-check.yml
git rm .github/workflows-pending/README.md
git commit -m "Reduce the staleness workflow to structure only"
```

**This should be the last time this file needs the dance.** That is the point
of the change: the workflow drops from 87 lines to 39, and from 37 lines of
shell to 1. All of the logic moved to `scripts/ci/project-plan-check.sh`,
which pushes without the `workflow` scope — so future edits to *what the check
does* touch only the script.

The YAML now holds what genuinely has to be there: the schedule, the
permissions, and the two environment variables the script reads. It should
change only when the *shape* of CI changes, which is exactly when you would
want to review it anyway.

## Why bother

Shell inside a `run:` block cannot be run locally, cannot be linted, and
cannot be tested. The only way to exercise the old version was to wait for a
scheduled job — and even then, only the branch that happened to be taken.

`scripts/ci/test_project_plan_check.sh` now covers all three reporting
branches, an unexpected exit code, and the captured error reaching the report.
`make project-plan-report` shows what CI will say, before you commit.

No `${{ }}` interpolation is left inside a shell body, which removes the
expression-injection surface rather than relying on quoting.
