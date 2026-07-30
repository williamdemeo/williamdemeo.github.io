# Makefile for williamdemeo.github.io
#
# The point of this file is that publishing must never be blocked on
# remembering how the tooling works.  `make serve` from a clean checkout gives
# a live-reloading preview in one command, creating the virtualenv if needed.
#
# Inside a Nix dev shell (M1-9, #55) the venv bootstrap is redundant but
# harmless; every target below works either way.

VENV    := .venv
PIP     := $(VENV)/bin/pip
MKDOCS  := $(VENV)/bin/mkdocs
PORT    ?= 8000

.DEFAULT_GOAL := help
.PHONY: help install serve build check clean distclean

## Create the virtualenv and install pinned dependencies
install: $(VENV)/.stamp

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
serve: $(VENV)/.stamp
	$(MKDOCS) serve --dev-addr 127.0.0.1:$(PORT)

## Build the site into site/
build: $(VENV)/.stamp
	$(MKDOCS) build

## Build with --strict; fails on any warning.  This is what CI runs.
check: $(VENV)/.stamp
	$(MKDOCS) build --strict

## Remove build output
clean:
	@rm -rf site

## Remove build output and the virtualenv
distclean: clean
	@rm -rf $(VENV)

## Show this help
help:
	@echo "Targets:"
	@awk '/^## /{doc=substr($$0,4); next} \
	      /^[a-zA-Z_-]+:/{if(doc!=""){split($$1,t,":"); printf "  \033[36m%-10s\033[0m %s\n", t[1], doc; doc=""}}' \
	      $(MAKEFILE_LIST)
