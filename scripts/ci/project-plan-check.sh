#!/usr/bin/env bash
#
# File: scripts/ci/project-plan-check.sh
#
# Report whether docs/GITHUB_PROJECT.md has drifted from live GitHub state.
#
# This lives here rather than inside a workflow `run:` block for three
# reasons: shell in YAML cannot be run locally, cannot be linted, and cannot
# be tested; and every edit to it needs the `workflow` scope to push.  The
# workflow is now four lines of structure that call this.
#
# Advisory by design: always exits 0.  A stale plan is worth surfacing -- it
# is the failure mode this project exists to avoid -- but it is not a reason
# to fail a build.  Use `make project-plan-check` when you want the raw exit
# code.
#
# The distinction that matters is drift versus a check that never ran.
# gh_project_render.py follows diff(1) -- 0 current, 1 differs, 2 failed --
# and reporting "the plan has drifted" when the real problem was an expired
# token sends you to fix the wrong thing.
#
# Environment:
#   REPO            owner/name to check against  (default: this repository)
#   PLAN            path to the plan file        (default: docs/GITHUB_PROJECT.md)
#   NO_ENV_PREFIX   set to pass --no-env-prefix; required wherever gh
#                   authenticates through GH_TOKEN/GITHUB_TOKEN, GitHub
#                   Actions included
#   RENDER          the render command, overridable so the reporting logic
#                   can be tested without reaching the GitHub API
#
# Writes to $GITHUB_STEP_SUMMARY when set, otherwise to stdout, so running it
# locally shows exactly what CI would report.

set -uo pipefail

REPO="${REPO:-${GITHUB_REPOSITORY:-williamdemeo/williamdemeo.github.io}}"
PLAN="${PLAN:-docs/GITHUB_PROJECT.md}"
RENDER="${RENDER:-python3 scripts/python/gh_project_render.py}"
SUMMARY="${GITHUB_STEP_SUMMARY:-/dev/stdout}"

flags=()
[ -n "${NO_ENV_PREFIX:-}" ] && flags+=(--no-env-prefix)

# ${flags[@]+...} guards the empty-array expansion under `set -u`, which is
# an error on bash before 4.4 (still the system bash on macOS).
out="$($RENDER "$PLAN" --repo "$REPO" --check ${flags[@]+"${flags[@]}"} 2>&1)"
code=$?

case "$code" in
  0)
    printf '`%s` is current.\n' "$PLAN" >> "$SUMMARY"
    ;;
  1)
    {
      printf '### `%s` has drifted\n\n' "$PLAN"
      printf 'Run `make project-plan` locally and commit the result.\n'
    } >> "$SUMMARY"
    ;;
  *)
    {
      printf '### The staleness check could not run\n\n'
      printf 'This is **not** drift: the check itself failed with exit code'
      printf ' %s, so whether the plan is current is unknown.\n' "$code"
      printf 'Usually authentication or a GitHub API error.\n\n'
      printf '```\n%s\n```\n' "$out"
    } >> "$SUMMARY"
    ;;
esac

exit 0
