# Pending workflow — move into `.github/workflows/`

`project-plan-check.yml` is finished and validated but parked here, because
GitHub refuses writes to `.github/workflows/` from a credential lacking the
`workflow` scope, which the session that wrote it does not have.

```zsh
git mv .github/workflows-pending/project-plan-check.yml .github/workflows/
git rm .github/workflows-pending/README.md
git commit -m "Activate the project-plan staleness check"
```

The directory should not survive that commit.

## What it does

Runs `gh_project_render.py --check` weekly and writes the result to the job
summary. It is **advisory**: the check step carries `continue-on-error`, so
drift is reported without failing anything. A stale plan is worth knowing
about; it is not a reason to block a merge.

It passes `--no-env-prefix`, because Actions authenticates through `GH_TOKEN`
and the scripts' default is to strip exactly that variable.
