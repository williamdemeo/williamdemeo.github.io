# Contributing

This is a personal website, so this file is mostly a note to self. It exists
because the previous two versions of this site died of workflow friction rather
than of anything wrong with the content, and writing the workflow down is part
of not repeating that.

Corrections and bug reports from anyone are welcome — open an issue.

## The loop

```zsh
make serve          # http://127.0.0.1:8000, live-reloading
```

Edit anything under `docs/`, save, and the browser updates. That is the whole
loop. If it ever needs more than one command to get to a preview, that is a bug
worth fixing rather than working around.

Before pushing:

```zsh
make check          # mkdocs build --strict; fails on any warning
```

CI runs exactly this on every pull request, so a green `make check` locally
means a green pull request.

## Branches and issues

Work is tracked in [`docs/GITHUB_PROJECT.md`](docs/GITHUB_PROJECT.md), which is
populated into GitHub issues by `scripts/python/gh_project_populate.py` and kept
current by `gh_project_render.py`.

Branch names follow the pattern GitHub's "create a branch" button generates from
an issue: `<issue-number>-<slug>`, e.g. `7-m1-6-repository-hygiene`. Reference
the issue in the commit message and let the merge close it.

Issue titles carrying an `[MN-k]` prefix are part of the roadmap. **Do not
remove that prefix when editing a title** — it is the only handle
`gh_project_render.py` has for recognising a planning issue, and without it the
issue silently vanishes from the rendered plan.

## Editing the roadmap

`docs/GITHUB_PROJECT.md` is half hand-written and half generated. Prose outside
the `BEGIN GENERATED` / `END GENERATED` markers is yours to edit; anything
inside them is rebuilt from live GitHub state and your edits there will be
overwritten.

So: to change an issue, edit it on GitHub and re-render. To change a milestone
description or a dependency graph, edit the file.

## Where things live

See the layout table in [`README.md`](README.md). The one non-obvious point is
that `docs/` is both the MkDocs source directory and the home of project
documentation that predates the site; `mkdocs.yml` excludes the latter via
`exclude_docs` rather than moving files and breaking links.

## Licence

Contributions to code are accepted under [MIT](LICENSE); contributions to prose
under [CC BY 4.0](LICENSE-CONTENT). Some files are third-party and under
neither — `LICENSE-CONTENT` lists them.

## Still to come

A dedicated blog authoring workflow — `make post` scaffolding, previewable
drafts that never deploy, one-command publish — is
[#36](https://github.com/williamdemeo/williamdemeo.github.io/issues/36). That
issue is the one that matters most for whether this site stays alive, so this
file will grow a "Writing a post" section when it lands.
