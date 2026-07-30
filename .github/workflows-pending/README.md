# Pending workflows — these replace the files in `.github/workflows/`

These two files are the Nix versions of `ci.yml` and `deploy.yml` (ADR-004,
#55). They are finished, but they are parked here because the session that
wrote them could not write to their real path.

GitHub refuses writes to `.github/workflows/` from a credential lacking the
`workflow` scope. The push was rejected with *"refusing to allow an OAuth App
to create or update workflow `.github/workflows/ci.yml` without `workflow`
scope"* — the same wall M1-4 hit, and the same workaround.

The files still in `.github/workflows/` are the pip-based versions. They keep
working, so CI is not broken in the meantime; it is just not yet running the
flake.

## To activate

```zsh
git mv -f .github/workflows-pending/ci.yml     .github/workflows/ci.yml
git mv -f .github/workflows-pending/deploy.yml .github/workflows/deploy.yml
git rm .github/workflows-pending/README.md
git commit -m "Activate the Nix CI and deployment workflows"
git push
```

The directory should not survive that commit.

## What changes

| File | Before | After |
| --- | --- | --- |
| `ci.yml` | `setup-python`, `pip install -r requirements.txt`, `mkdocs build --strict` | `nix flake check`, then `nix develop --command make check` |
| `deploy.yml` | same pip install, then `mkdocs build --strict` | `nix build`, then stage `result/` into `site/` for Pages |

Triggers, permissions, and concurrency groups are unchanged. `deploy.yml`
still requires **Settings → Pages → Source** set to *GitHub Actions*.

`nix flake check` covers more than the old `mkdocs build --strict` did: the
strict site build, the Cairo/Pango/font probe the social cards need in M3-5,
and the assertion that `requirements.txt` still matches the Nix environment.

## What has and has not been run

The flake itself is verified — `nix build`, `nix flake check`, `nix develop`,
`make serve`, and the `cp -rL` staging step were all executed locally, and
ADR-004 records the results. What has *not* run is these two files on a
GitHub runner, since they have never been at a path Actions reads. The first
real run will be the pull request that activates them.
