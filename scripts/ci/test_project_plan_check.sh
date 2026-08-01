#!/usr/bin/env bash
#
# File: scripts/ci/test_project_plan_check.sh
#
# Regression test for project-plan-check.sh.  Exercises all three reporting
# branches through the RENDER seam, without touching the GitHub API.
#
# This test is the point of moving the logic out of the workflow: while it
# lived in a `run:` block there was no way to run it except by waiting for a
# scheduled job, and no way to check the branch you were not currently in.

set -uo pipefail
cd "$(dirname "$0")/../.."

stub="$(mktemp)"; trap 'rm -f "$stub"' EXIT
cat > "$stub" <<'STUB'
#!/usr/bin/env bash
printf 'stub output for exit %s\n' "$STUB_CODE"
exit "$STUB_CODE"
STUB
chmod +x "$stub"

fail=0
check() { # code, expected substring
  local out
  out="$(STUB_CODE="$1" RENDER="$stub" ./scripts/ci/project-plan-check.sh 2>&1)"
  local rc=$?
  if [ "$rc" -ne 0 ]; then
    printf 'FAIL exit %s: reporter returned %s, must always be 0\n' "$1" "$rc"; fail=1; return
  fi
  case "$out" in
    *"$2"*) printf 'ok   exit %s -> %s\n' "$1" "$2" ;;
    *) printf 'FAIL exit %s: expected %s\n     got: %s\n' "$1" "$2" "$out"; fail=1 ;;
  esac
}

check 0 'is current'
check 1 'has drifted'
check 2 'could not run'
# Anything unexpected must fall through to the failure branch rather than
# being silently reported as drift.
check 4 'could not run'
# The captured render output has to reach the report, or a failed check gives
# no clue what went wrong.
check 2 'stub output for exit 2'

[ "$fail" -eq 0 ] && echo 'all reporting branches ok' || echo 'FAILURES'
exit "$fail"
