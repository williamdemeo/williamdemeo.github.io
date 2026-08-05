<!-- File: docs/adr/004-nix-environment.md -->

# ADR-004: Adopt Nix for the development environment and CI

**Status**: Accepted

**Date**: 2026-07-30

**Deciders**: William DeMeo

**Related**: [#55](https://github.com/williamdemeo/williamdemeo.github.io/issues/55) (M1-9), [#5](https://github.com/williamdemeo/williamdemeo.github.io/issues/5) (M1-4), [#6](https://github.com/williamdemeo/williamdemeo.github.io/issues/6) (M1-5), M3-5 (social cards)

---

## Context

M1-4 established the local build loop: a `Makefile` that creates `.venv` from a pinned `requirements.txt`, and `make check` running `mkdocs build --strict`. M1-5 wired the same two commands into GitHub Actions. Both work today.

Both stop working at M3-5. The Material `social` plugin generates Open Graph card images through Pillow and CairoSVG, and those reach libcairo, Pango, FreeType and fontconfig through cffi and `ctypes` at run time rather than through a link-time dependency that pip could see. `pip install` cannot install them, cannot pin them, and cannot detect their absence — the failure surfaces as a `dlopen` error or a card with no glyphs on it, at build time, on whichever machine happens to lack the library. The pip-side workaround is an `apt-get install` line in the workflow that drifts from whatever the developer has installed locally, which is the textbook works-locally-fails-in-CI shape.

`requirements.txt` pins the Python packages. It does not pin Python, libcairo, Pango, or a single font. The site whose replacement this project is undertaking makes the argument better than any hypothetical: the Zola source is pinned to v0.5.0 from 2018 and cannot be built with any current release (ADR-001). Pinning the Python layer and leaving the layer underneath it floating reproduces that failure one level down.

There is also a consistency argument. `agda-algebras` and `agda-native-air` are both Nix projects. One mental model across all three means `nix develop` is the answer everywhere, with no context-switch cost when moving between them in the same evening. For a site whose premise is removing friction from the publishing loop (M6-2), that matters more than it would on a repository touched daily.

## Decision

**Adopt Nix as the primary development and CI environment, with `requirements.txt` retained as a supported fallback.**

`flake.nix` provides:

| Output | What it is |
| --- | --- |
| `devShells.default` | Python 3.12, MkDocs, Material, Pillow, CairoSVG, Cairo, Pango, gdk-pixbuf, FreeType, fontconfig, libffi, Roboto and DejaVu, GNU make |
| `packages.default` | The site, built by `mkdocs build --strict` into the store |
| `checks.site` | The same derivation as `packages.default` |
| `checks.native-deps` | Renders text through CairoSVG and loads a TrueType face through Pillow |
| `checks.requirements-pins` | Fails if `requirements.txt` and the Nix environment disagree on a version |
| `apps.serve` | `nix run .#serve` — the live-reloading preview, no shell needed |

`.envrc` contains `use flake` for direnv users. Both CI workflows install Nix and run the flake. `requirements.txt` and the `.venv` path continue to work unchanged on a machine without Nix.

## What was verified

Claiming native-dependency reproducibility on the strength of a flake that was never run would be self-defeating, so each of these was executed rather than reasoned about:

- `nix build` produces the site: 49 files, 2.6 MB, `index.html` correct.
- `nix flake check` passes all three checks. `checks.native-deps` reports `fc-match Roboto -> .../roboto-3.011/share/fonts/truetype/Roboto-Regular.ttf`, CairoSVG rendering antialiased text in 218 shades of grey, and Pillow measuring a 187.3 px string in Roboto Regular.
- `nix develop` gives a shell with `mkdocs 1.6.1`, `cairosvg 2.7.1`, `pillow 11.2.1`, and `fc-match` resolving Roboto.
- Inside that shell, from a tree with no `.venv`: `make install` is a no-op, `make check` and `make build` succeed, `make serve` answers HTTP 200 with the right `<title>`, and no `.venv` is created.
- Outside the shell, from a tree with no `.venv`: `make check` creates the virtualenv, installs MkDocs 1.6.1 and Material 9.5.49 from PyPI, and builds. The fallback path is not theoretical.
- `nix run .#serve` answers HTTP 200.
- The Pages staging step (`cp -rL --no-preserve=mode,ownership result site`) produces a writable directory with no dangling symlinks, which is what `upload-pages-artifact` needs.

## Rationale

### `nixpkgs` is pinned to a channel tarball, not a `github:` ref

`inputs.nixpkgs.url` is `https://channels.nixos.org/nixos-25.05/nixexprs.tar.xz` rather than the more familiar `github:NixOS/nixpkgs/nixos-25.05`.

This is not a weaker pin. `channels.nixos.org` redirects to an immutable `releases.nixos.org/nixos/25.05/nixos-25.05.<build>` path, and `flake.lock` records that resolved URL together with the revision and a `narHash` — `nixos-25.05.813814.ac62194c3917`, `sha256-3zSML8xJhOT2kRBCNUpniZSCeCBCPA3KGsRYh+KdtbU=`. It is pinned exactly as tightly.

It has two advantages over the `github:` form. The build it names is a *channel* build, meaning it passed the nixpkgs test suite and is fully populated in `cache.nixos.org`, so CI substitutes binaries instead of compiling Cairo from source. And it never touches the GitHub API, which rate-limits unauthenticated Actions runners.

Switching to `github:NixOS/nixpkgs/nixos-25.05` is a one-line change and costs nothing but a re-lock.

### Material is held at 9.5.49 rather than following nixpkgs

nixpkgs 25.05 ships `mkdocs-material` 9.6.4; `requirements.txt` pins 9.5.49. Two supported paths on two different theme versions would make "it builds for me" mean nothing, so they are held together.

Holding them at 9.5.49 rather than bumping `requirements.txt` to 9.6.4 keeps a theme upgrade out of an infrastructure change. A minor Material release moves rendered output, and if something shifts in the site it should be attributable to the change that asked for it. The override fetches the PyPI sdist — which carries the same prebuilt `material/` tree plus the `requirements.txt` and `package.json` its hatch build hooks read — and is a pure-Python build of a few seconds.

`checks.requirements-pins` is what makes this safe. It parses every `name==version` line in `requirements.txt`, resolves the same distribution from the Nix environment, and fails on any mismatch, on a missing package, or on a requirement too loose to compare. Drift becomes a red build rather than a discovery.

### Not `uv2nix` or `poetry2nix`, yet

Either would derive the Nix environment from the Python lockfile and restore a single source of truth, removing the version-override maintenance described above. Neither is worth it for two pinned direct dependencies, and both add an input whose own upgrade cadence has to be tracked. Worth revisiting when the dependency set grows — M3-5 and M6-1 add plugins — or the first time `checks.requirements-pins` is annoying rather than useful.

### `cache-nix-action` rather than Magic Nix Cache

Issue #55 suggested `DeterminateSystems/magic-nix-cache-action`. The installer recommendation is taken; the cache one is not.

Magic Nix Cache's free tier reached end of life in February 2025 when GitHub shut down the Actions cache API it was built on. It was [brought back in June 2025](https://determinate.systems/blog/bringing-back-magic-nix-cache-action/) on top of a reverse-engineered implementation of GitHub's replacement API, which Determinate Systems describe in the same post as guesswork that could stop working whenever the undocumented API changes. It also defaults to `use-flakehub: true`, uploading build results to a third-party cache in private beta.

`nix-community/cache-nix-action` is a fork of `actions/cache` specialised for `/nix/store`. It goes through the documented Actions cache toolkit, needs no secrets, and involves no third party. For this repository the difference is modest either way — the dev shell closure is about 450 MiB and nearly all of it comes from `cache.nixos.org` regardless — so the tiebreaker is which one is less likely to need attention.

The cache is written only by the deploy workflow, on pushes to `main`. A cache saved on a pull-request ref is readable only by that pull request, so writing one there would upload hundreds of megabytes nothing else can use. Pull requests restore from the `main` cache and set `save: false`. `gc-max-store-size-linux: 2G` bounds the upload, well under GitHub's 10 GB per-repository limit; stale entries are left to GitHub's own eviction rather than purged, which would need `actions: write` and fail on forks.

### The `Makefile` keys on `SITE_NIX_SHELL`, not `IN_NIX_SHELL`

Inside the dev shell the `Makefile` uses the MkDocs on `PATH` and skips the virtualenv, because rebuilding a venv to reinstall from PyPI what the shell already provides is the opposite of the point — and needs network besides.

The marker is `SITE_NIX_SHELL`, exported by the devShell, rather than `IN_NIX_SHELL`, which `nix develop` does set but which is equally set by any unrelated `nix-shell`. Under `nix-shell -p jq` the Makefile would conclude MkDocs was on `PATH` when it is not. A project-specific marker says the thing actually meant.

Target names and behaviour are identical in both environments; only how MkDocs is found differs. `make help` reports which of the two is in effect.

### CI builds the same derivation twice, deliberately

`nix flake check` on a pull request and `nix build` on the deploy run resolve to one derivation. What deploys is bit-for-bit what was reviewed, out of the same cache, rather than a second build that happens to agree with the first. This is the property the pip workflows could not offer, since `pip install -r requirements.txt` on two runners a month apart is two different environments.

The build workflow additionally runs `nix develop --command make check`. `nix flake check` would not catch a devShell that builds but has a broken `Makefile` interaction, and the promise that `make serve` works in a fresh shell with no further setup is exactly the sort of thing that breaks quietly.

## Consequences

### Positive

- Cairo, Pango, FreeType, fontconfig and fonts are declared and identical locally and in CI. The dependency M3-5 needs is a locked input rather than an `apt-get` line.
- `flake.lock` pins Python itself, the C libraries, and the fonts — not just the Python packages. This is the difference between a site that still builds in 2031 and one that does not.
- One command, `nix develop`, matches `agda-algebras` and `agda-native-air`.
- `nix run .#serve` previews the site with no shell and no checkout-local state.
- `checks.native-deps` turns "the native libraries are present and working" from an assumption into a build failure when it stops being true.
- A contributor without Nix is unaffected: `make serve` still works from `requirements.txt`.

### Costs accepted

- **Two dependency sets.** `requirements.txt` and `flake.nix` both name versions, and the Material override has to be bumped alongside `requirements.txt`. `checks.requirements-pins` makes drift loud, but it does not make it impossible. This is the real price of keeping the non-Nix path, and it is the first thing to revisit (with `uv2nix`) if it starts to chafe.
- **Cold-start cost in CI.** A cache miss fetches roughly 450 MiB before MkDocs runs, against a few seconds for `pip install` of two wheels. The GitHub Actions store cache recovers most of it after the first push to `main`, but the floor is higher than the pip path's.
- **Nix is a prerequisite for the primary path.** Anyone without it takes the fallback and gets a less reproducible environment. On this repository, with one maintainer who already runs Nix, that asymmetry costs nothing; on a project with drive-by contributors it would be a real barrier.
- **`nix flake check` covers the host system only.** The flake declares four systems; CI checks `x86_64-linux`. A Darwin-specific break would surface on a laptop rather than in CI.

### Neutral

- `nix/native-deps-check.py` and `nix/requirements-pins-check.py` are the flake's checks kept as readable files rather than strings embedded in Nix, which cannot be run or linted on their own.
- `packages.default` builds from a `lib.fileset` covering `mkdocs.yml`, `docs/` and `scripts/python/`. `csp/`, `archive/`, the CV and git history stay out of the store, so editing them cannot invalidate a build that could not depend on them.
- `result`, `result-*` and `.direnv/` are added to `.gitignore`.
- The dev shell does not export `LD_LIBRARY_PATH`. nixpkgs patches `cairocffi` to `dlopen` an absolute store path, so the Nix path does not need it, and exporting it into an interactive shell is a reliable way to break unrelated host tools.

## What this does not solve: social-card fonts

The native half of M3-5 is handled. The offline half is not, and the distinction is worth recording precisely so it is not rediscovered later.

`material/plugins/social/plugin.py` resolves fonts in `_resolve_font` by looking for `<cache_dir>/fonts/<family>/Regular.ttf` and `Bold.ttf`, where `cache_dir` defaults to `.cache/plugin/social`. If that directory is absent it downloads the family from `fonts.google.com`. It never consults fontconfig, so the Roboto in this flake's closure — the font `checks.native-deps` resolves and renders with — is not where the plugin looks.

A sandboxed `nix build` has no network, so enabling the plugin as-is will fail. M3-5 needs to seed `<cache_dir>/fonts/<family>/{Regular,Bold}.ttf` from the font packages the flake already provides, as a build step ahead of `mkdocs build`. That is deliberately left to M3-5 rather than done here: the font family is a decision belonging to the visual system in M3-1, and seeding a family nobody has chosen yet would be dead code that rots before it is used.

**Resolved by M3-5 (#21)**, with one refinement over the sketch above: the seed
is not the flake's Roboto but the visual system's own faces — static TTF
instances of Inter 400 and Space Grotesk 600, emitted by `build_fonts.py` from
the same pinned sources as the WOFF2 and committed under
`docs/assets/fonts/cards/`.  `scripts/python/social_fonts_hook.py` copies them
into the plugin's cache ahead of its `on_config`, an mkdocs hook rather than a
build step so that every way of building seeds identically.  The flake needed
no change for it; `checks.native-deps` had already proven the rasterisation
path.

## Implementation status

| Task | Status |
| --- | --- |
| `flake.nix` with a devShell covering Python, MkDocs and the social-card native dependencies | Done |
| `packages.default` building the site with `mkdocs build --strict` | Done |
| `nix flake check` wired to the strict build | Done |
| `.envrc` with `use flake` | Done |
| `Makefile` targets working identically inside and outside the dev shell | Done |
| CI workflows switched to the flake, with a binary cache | Written; parked in `.github/workflows-pending/` |
| Social-card *native* dependencies verified in CI | Done, via `checks.native-deps` |
| Social-card *generation* verified in CI | Deferred to M3-5; see above |
| `requirements.txt` kept and documented as the non-Nix path | Done |
| This ADR | Done |

## Notes

M1-4's optional `flake.nix` sub-task is superseded by this decision.

The two Nix workflows are parked in `.github/workflows-pending/` rather than replacing the pip-based ones, because GitHub rejects a push touching `.github/workflows/` from a credential without the `workflow` scope — the same wall M1-4 hit, with the same two-line `git mv` to clear it, documented in that directory's README. The pip workflows stay live until then, so CI is not broken in the meantime; it is simply not yet running the flake. Everything in [What was verified](#what-was-verified) was run locally and holds regardless, but neither workflow file has executed on a GitHub runner.

`nix flake update` advances `nixpkgs` to the current `nixos-25.05` channel build; moving to a later NixOS release is an edit to `flake.nix`. Either will fail `checks.requirements-pins` if it moves Material off 9.5.49, which is the intended behaviour rather than an inconvenience.
