# Pending workflows — move these into `.github/workflows/`

These two files are finished and validated, but they are parked here because
the session that wrote them could not place them at their real path.

GitHub refuses writes to `.github/workflows/` from a credential lacking the
`workflow` scope. Both available routes hit that wall: `git push` was rejected
with *"refusing to allow an OAuth App to create or update workflow
`.github/workflows/ci.yml` without `workflow` scope"*, and the Contents API
returned `404 Not Found`, which is what GitHub sends when the token may not
touch that path.

## To activate

```zsh
git mv .github/workflows-pending/ci.yml     .github/workflows/ci.yml
git mv .github/workflows-pending/deploy.yml .github/workflows/deploy.yml
git rm .github/workflows-pending/README.md
git commit -m "Activate CI and Pages deployment workflows"
git push
```

The directory should not survive that commit.

## What they do

| File | Trigger | Purpose |
| --- | --- | --- |
| `ci.yml` | pull requests | `mkdocs build --strict`; a broken internal link fails review |
| `deploy.yml` | push to `main` | strict build, then publish to GitHub Pages |

`deploy.yml` requires **Settings → Pages → Source** set to *GitHub Actions*,
which is already configured (M1-1, #2).

Neither workflow has executed yet. The YAML parses and the job graphs and
triggers were checked, but the first real run will be the pull request that
activates them.
