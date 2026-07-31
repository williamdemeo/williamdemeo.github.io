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
else
MKDOCS  := $(VENV)/bin/mkdocs
MKDOCS_DEP := $(VENV)/.stamp
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

.PHONY: project-plan project-plan-check

## Regenerate the issue listings in docs/GITHUB_PROJECT.md from GitHub
project-plan: guard-gh
	$(RENDER)

## Report whether docs/GITHUB_PROJECT.md is stale; never rewrites it
project-plan-check: guard-gh
	@$(RENDER) --check

guard-gh:
	@command -v gh >/dev/null || { \
	  echo "error: the GitHub CLI (gh) is required for this target."; \
	  echo "       install it, then run: gh auth login"; exit 1; }

## Show this help
help:
	@echo "Targets:"
	@awk '/^## /{doc=substr($$0,4); next} \
	      /^[a-zA-Z_-]+:/{if(doc!=""){split($$1,t,":"); printf "  \033[36m%-19s\033[0m %s\n", t[1], doc; doc=""}}' \
	      $(MAKEFILE_LIST)
	@echo
	@echo "MkDocs comes from:"
ifdef SITE_NIX_SHELL
	@echo "  the Nix dev shell (SITE_NIX_SHELL is set)"
else
	@echo "  $(VENV), created on demand from requirements.txt"
	@echo "  ('nix develop' uses the pinned Nix environment instead -- see ADR-004)"
endif
