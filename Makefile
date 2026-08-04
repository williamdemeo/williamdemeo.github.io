# Makefile for williamdemeo.github.io
#
# The point of this file is that publishing must never be blocked on
# remembering how the tooling works.  `make serve` from a clean checkout gives
# a live-reloading preview in one command, creating the virtualenv if needed.
#
# Inside a Nix dev shell (ADR-004) MkDocs is already on PATH, so the venv
# bootstrap is skipped: rebuilding it there would reinstall from PyPI the
# packages the shell just provided, which is the opposite of the point.  Every
# target below behaves the same either way; only how MkDocs is found differs.

VENV    := .venv
PIP     := $(VENV)/bin/pip
PORT    ?= 8000

# SITE_NIX_SHELL is exported by the devShell in flake.nix, rather than keying
# off IN_NIX_SHELL: that is set inside any nix shell, including ones with no
# MkDocs in them.
ifdef SITE_NIX_SHELL
MKDOCS  := mkdocs
MKDOCS_DEP :=
PYTHON  := python3
else
MKDOCS  := $(VENV)/bin/mkdocs
MKDOCS_DEP := $(VENV)/.stamp
# The venv interpreter, not the system one: the redirect scripts import yaml,
# which arrives as a dependency of MkDocs rather than on its own.
PYTHON  := $(VENV)/bin/python
endif

.DEFAULT_GOAL := help
.PHONY: help install serve build check clean distclean guard-gh

## Create the virtualenv and install pinned dependencies (no-op under Nix)
install: $(MKDOCS_DEP)
ifdef SITE_NIX_SHELL
	@echo "==> nothing to install: $$(mkdocs --version) comes from the dev shell"
endif

# Stamp file rather than the directory: make compares timestamps, and a
# directory's mtime changes on every write inside it, which would rebuild
# the environment constantly.
$(VENV)/.stamp: requirements.txt
	@echo "==> creating $(VENV) and installing pinned dependencies"
	@python3 -m venv $(VENV)
	@$(PIP) install --quiet --upgrade pip
	@$(PIP) install --quiet -r requirements.txt
	@touch $@

## Live-reloading preview (override the port with PORT=8001)
serve: $(MKDOCS_DEP)
	$(MKDOCS) serve --dev-addr 127.0.0.1:$(PORT)

## Build the site into site/
build: $(MKDOCS_DEP)
	$(MKDOCS) build

## Build with --strict; fails on any warning.  This is what CI runs.
check: $(MKDOCS_DEP)
	$(MKDOCS) build --strict

## Remove build output
clean:
	@rm -rf site

## Remove build output and the virtualenv
distclean: clean
	@rm -rf $(VENV)

# ── Worktrees ───────────────────────────────────────────────────────────────
#
# scripts/git/git-wt is the whole tool; these are the two of its commands that
# do not need to change the shell's working directory, and so can be targets
# at all.  Starting work on a branch does need to, which is what the `wt`
# function in scripts/git/wt.sh is for -- one `source` line in ~/.zshrc, and
# then `wt 82-m4-7-mathematics` from anywhere in the repository.  See
# scripts/git/README.md.

WT := scripts/git/git-wt

.PHONY: wt-list wt-clean wt-test

## List every worktree, and what `wt clean` would do to each
wt-list:
	@$(WT) list

## Remove the worktrees whose work has landed.  Dry run unless YES=1
wt-clean:
	@$(WT) clean $(if $(YES),--yes,)

## Unit-test the worktree tooling against throwaway repositories
wt-test:
	@scripts/git/test_git_wt.sh

# ── Project plan ────────────────────────────────────────────────────────────
#
# docs/GITHUB_PROJECT.md is half hand-written prose and half generated from
# live GitHub state.  gh_project_render.py rewrites only the regions between
# the BEGIN/END GENERATED markers and preserves everything else byte for byte,
# so these targets are safe to run against a file with unsaved prose edits.
#
# Both need an authenticated `gh`.  The check is deliberately advisory: a stale
# plan is worth knowing about, but it is not a reason to block a merge.
#
# By default the scripts strip GH_TOKEN and GITHUB_TOKEN before calling gh, to
# stop those variables overriding a keychain-stored token.  Wherever
# authentication comes *through* them instead -- GitHub Actions, and some
# sandboxes -- that leaves gh with no credentials and every call fails.  Set
# NO_ENV_PREFIX=1 there:
#
#     make project-plan-check NO_ENV_PREFIX=1

REPO ?= williamdemeo/williamdemeo.github.io

RENDER_FLAGS :=
ifdef NO_ENV_PREFIX
RENDER_FLAGS += --no-env-prefix
endif

RENDER := python3 scripts/python/gh_project_render.py docs/GITHUB_PROJECT.md \
            --repo $(REPO) $(RENDER_FLAGS)

.PHONY: project-plan project-plan-check project-plan-report

## Regenerate the issue listings in docs/GITHUB_PROJECT.md from GitHub
project-plan: guard-gh
	$(RENDER)

## Report whether docs/GITHUB_PROJECT.md is stale; never rewrites it
project-plan-check: guard-gh
	@$(RENDER) --check

## Run the CI drift report locally, exactly as the scheduled job does
project-plan-report: guard-gh
	@NO_ENV_PREFIX=$(if $(NO_ENV_PREFIX),1,) scripts/ci/project-plan-check.sh

guard-gh:
	@command -v gh >/dev/null || { \
	  echo "error: the GitHub CLI (gh) is required for this target."; \
	  echo "       install it, then run: gh auth login"; exit 1; }

# ── Math rendering audit ────────────────────────────────────────────────────
#
# Renders every expression in a content tree with the KaTeX bundle the site
# actually ships, using the site's own macro table, so the audit cannot drift
# from what visitors get.  Needs node; nothing from npm.
#
# It said here for a long time that this "works as a gate once the mathematical
# content reaches docs/".  The content has, and docs/ is now at zero failures,
# so it is one: `nix flake check` runs it.  The default root moved with it --
# auditing the staging tree by default while CI audited docs/ meant a
# contributor could run this, see the exam corpus's failures, and read them as
# a broken build.  Pass MATH_SRC=import/zola-converted to audit that tree
# before migrating it (#56).

MATH_SRC ?= docs

.PHONY: math-audit math-source math-fix

## Render every math expression headlessly and report failures
math-audit:
	@command -v node >/dev/null || { echo "error: node is required for this target"; exit 1; }
	@node scripts/js/audit_math.mjs $(MATH_SRC)

# The audit above renders; the two below read.  They catch disjoint sets of
# defects, which is why both exist: an over-escaped `\{` or a `$ x $` renders
# without raising and so is invisible to the audit, while being wrong on the
# page.
#
# Both default to docs/, which is what ships and what CI gates on.  The
# separate variable is not redundant: these two want different roots at
# different moments, and `make math-fix MATH_ROOT=import/zola-converted`
# before migrating a batch repairs the escaping once, at the source, rather
# than page by page afterwards.

MATH_ROOT ?= docs

## Report math source that arithmatex and KaTeX will silently mis-render
math-source:
	@$(PYTHON) scripts/python/check_math_source.py $(MATH_ROOT)

## Rewrite the mechanical half of what math-source reports, in place
math-fix:
	@$(PYTHON) scripts/python/check_math_source.py --fix $(MATH_ROOT)

# ── Legacy-URL redirects ────────────────────────────────────────────────────
#
# redirects.yml maps every URL the Octopress and Zola sites served to where it
# goes now.  The checker proves the map has no gaps and that what it claims
# resolves really does; the tests cover the rule-matching itself.  See #15.

.PHONY: redirect-check redirect-test

## Check the redirect map against the built site (runs `build` first)
redirect-check: build
	@$(PYTHON) scripts/python/check_redirects.py --verify-inventory --site site

## Unit-test the redirect map's rule matching and config validation
redirect-test: $(MKDOCS_DEP)
	@$(PYTHON) scripts/python/test_redirects.py

# ── Visual system ───────────────────────────────────────────────────────────
#
# `fonts` regenerates docs/assets/fonts/ from upstream sources pinned by
# SHA-256.  Its outputs are committed, so neither an ordinary build nor CI
# needs it, or the network.  Run it when the character repertoire changes.
#
# It deliberately uses the system python rather than $(PYTHON): fonttools and
# brotli are not in requirements.txt, because adding them would oblige
# flake.nix to match their versions (ADR-004's checks.requirements-pins) for a
# generator that runs by hand a few times a year and whose output is committed.
# `pip install 'fonttools[woff]' brotli` is all it needs; the script says so if
# they are missing.  Override with FONT_PYTHON= if they live somewhere else.
#
# The three audits answer the acceptance criteria in #17, and each answers it
# by measuring a rendered page rather than by reading the CSS.  All three need
# node and a Chromium; nothing from npm.  Set CHROME=/path/to/chrome if one is
# not found automatically.  See #17.

.PHONY: fonts fonts-check font-audit offline-audit contrast-audit design-audit

FONT_PYTHON ?= python3

## Rebuild the subsetted WOFF2 fonts from their pinned sources (needs network)
fonts:
	@$(FONT_PYTHON) scripts/python/build_fonts.py

## Report whether docs/assets/fonts/ is stale; writes nothing
fonts-check:
	@$(FONT_PYTHON) scripts/python/build_fonts.py --check

## Report every font the browser actually rendered with; fails on a fallback
font-audit: build
	@command -v node >/dev/null || { echo "error: node is required for this target"; exit 1; }
	@node scripts/js/audit_fonts.mjs site

## Fail if any page requests anything from another origin
offline-audit: build
	@command -v node >/dev/null || { echo "error: node is required for this target"; exit 1; }
	@node scripts/js/audit_offline.mjs site

## Measure WCAG contrast on every text element, in both themes
contrast-audit: build
	@command -v node >/dev/null || { echo "error: node is required for this target"; exit 1; }
	@node scripts/js/audit_contrast.mjs site

## Run all three visual-system audits
design-audit: font-audit offline-audit contrast-audit

# ── Publications ────────────────────────────────────────────────────────────
#
# bibliography.json is the only authoritative publication list (ADR-006).  The
# generator renders it into three files -- the publications page's body and the
# CV's selection, as snippets under docs/_snippets/, and docs/publications.bib
# for anyone who wants to cite this work.  Pages include the snippets, so no
# page holds a second copy.
#
# All three are committed, so `publications-check` asks whether they still match
# the bibliography as well as whether the bibliography is sound.  A hand-edit to
# a generated file survives every other check in this repository.  `nix flake
# check` runs it too, since it needs no network.
#
# `publications-check` and `publications-verify` ask different questions and
# neither answers the other's.  The first is offline and asks whether the file
# is internally sound; the second asks the publishers whether it is true, and
# needs api.crossref.org, api.datacite.org and export.arxiv.org.  It exits 2
# rather than 0 when it cannot reach them, so it is not a build gate: CI has no
# network by design (ADR-004), and a check that fails there for a reason
# unrelated to the change would train everyone to ignore it.  Run it when the
# bibliography changes.
#
# Both are stdlib-only -- no dependency in requirements.txt, and so none for
# flake.nix to match under ADR-004's requirements-pins check.

.PHONY: publications publications-check publications-verify publications-test

## Regenerate the publications snippets and BibTeX from bibliography.json
publications: $(MKDOCS_DEP)
	@$(PYTHON) scripts/python/gen_publications.py

## Validate bibliography.json and report stale generated files; writes nothing
publications-check: $(MKDOCS_DEP)
	@$(PYTHON) scripts/python/gen_publications.py --check

## Check bibliography.json against Crossref, DataCite and arXiv (needs network)
publications-verify: $(MKDOCS_DEP)
	@$(PYTHON) scripts/python/verify_bibliography.py

## Unit-test the renderer and the verifier's failure handling (no network)
publications-test: $(MKDOCS_DEP)
	@$(PYTHON) scripts/python/test_gen_publications.py
	@$(PYTHON) scripts/python/test_verify_bibliography.py

## Show this help
help:
	@echo "Targets:"
	@awk '/^## /{doc=substr($$0,4); next} \
	      /^[a-zA-Z_-]+:/{if(doc!=""){split($$1,t,":"); printf "  \033[36m%-20s\033[0m %s\n", t[1], doc; doc=""}}' \
	      $(MAKEFILE_LIST)
	@echo
	@echo "MkDocs comes from:"
ifdef SITE_NIX_SHELL
	@echo "  the Nix dev shell (SITE_NIX_SHELL is set)"
else
	@echo "  $(VENV), created on demand from requirements.txt"
	@echo "  ('nix develop' uses the pinned Nix environment instead -- see ADR-004)"
endif
