# williamdemeo.github.io

Source for my personal website and blog — mathematics, formal verification in
Agda, and AI tooling for interactive theorem proving.

Built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) and
deployed to GitHub Pages by GitHub Actions on every push to `main`.

- **Live:** <https://williamdemeo.github.io>
- **Roadmap:** [`docs/GITHUB_PROJECT.md`](docs/GITHUB_PROJECT.md) and the
  [issue tracker](https://github.com/williamdemeo/williamdemeo.github.io/issues)

## Quick start

```zsh
git clone https://github.com/williamdemeo/williamdemeo.github.io
cd williamdemeo.github.io
make serve          # http://127.0.0.1:8000, live-reloading
```

`make serve` creates the virtualenv and installs pinned dependencies on first
run. Nothing else to set up. Run `make` on its own to list every target.

| Target | What it does |
| --- | --- |
| `make serve` | Live-reloading preview (override with `PORT=8001`) |
| `make build` | Build into `site/` |
| `make check` | Build with `--strict`; fails on any warning. This is what CI runs. |
| `make clean` | Remove build output |
| `make distclean` | Also remove the virtualenv |

## Layout

| Path | Contents |
| --- | --- |
| `docs/` | Site content. Everything here is published except the exclusions in `mkdocs.yml`. |
| `docs/blog/posts/` | Blog posts, one file per post. URL scheme and front matter: `docs/adr/007-blog-url-scheme.md`. |
| `docs/adr/` | Architecture decision records. Not published. |
| `docs/GITHUB_PROJECT.md` | Project roadmap, partly generated from GitHub. Not published. |
| `archive/` | Preserved content from the retired Octopress site. Not published. |
| `scripts/python/` | Project tooling — issue population, plan rendering, migration helpers. |
| `scripts/git/` | Worktree tooling: `wt <branch>` to start work, `wt clean` to tidy up after a merge. See its README. |
| `.github/workflows/` | Strict build on pull requests; build and deploy on `main`. |

## Publishing

Push to `main`. The deploy workflow builds with `--strict` and publishes to
GitHub Pages; the site is live in a couple of minutes. Pull requests get the
same strict build, so a broken internal link fails review rather than shipping.

A dedicated blog authoring workflow — `make post`, drafts, one-command publish —
is coming in [#36](https://github.com/williamdemeo/williamdemeo.github.io/issues/36).

## Licence

This repository mixes code and prose, which want different terms.

- **Code** — build configuration, `scripts/`, `Makefile`, CSS:
  [MIT](LICENSE).
- **Prose** — everything under `docs/`: posts, pages, research writing, ADRs:
  [CC BY 4.0](LICENSE-CONTENT).

Some files are **neither**, because they are not mine. `LICENSE-CONTENT` lists
them explicitly — third-party papers under `csp/` and one archived post written
by someone else. Check there before reusing anything from `archive/` or `csp/`.
