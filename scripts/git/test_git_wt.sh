#!/usr/bin/env bash
#
# File: scripts/git/test_git_wt.sh
#
# Regression test for scripts/git/git-wt, against throwaway repositories in a
# temporary directory.  Needs nothing but git: the "remote" is a bare
# repository on disk, so there is no network, no GitHub, and no state outside
# $TMPDIR.
#
# The classification is the part worth testing.  `git wt clean` deletes
# things, and it decides what to delete from four questions -- is the tree
# dirty, are the commits in the base branch, is the remote branch still there,
# is anything unpushed -- whose answers are not visible in the output of any
# one git command.  A wrong answer either loses work or leaves the list as
# cluttered as it was before the tool existed, and both are silent.
#
# Run it with `make wt-test`; `nix flake check` runs it too.

set -uo pipefail

script=$(cd "$(dirname "$0")" && pwd)/git-wt
[ -x "$script" ] || { echo "not executable: $script" >&2; exit 2; }

# The script is executed the way a shell executes it, not handed to bash, so
# its shebang has to resolve.  Where it does not -- a sandbox with no
# /usr/bin/env, which is every Nix builder -- the kernel's ENOENT arrives as
# exit 127 on every single check, and "required file not found" reads like a
# missing script rather than a missing interpreter.  One check up front says
# so once instead of sixty times.
"$script" --help >/dev/null 2>&1
if [ $? -eq 127 ]; then
  printf '%s cannot be executed: its interpreter is missing.\n' "$script" >&2
  printf 'A sandbox with no /usr/bin/env needs patchShebangs first.\n' >&2
  exit 2
fi

# With a template rather than bare `mktemp -d`, which is a GNU extension: the
# BSD mktemp on macOS wants one, and `make wt-test` should work there.
tmp=$(mktemp -d "${TMPDIR:-/tmp}/git-wt-test.XXXXXX")
trap 'rm -rf "$tmp"' EXIT

# Hermetic: no ~/.gitconfig, no /etc/gitconfig, no credential helper, and a
# committer identity that does not depend on one being configured.
export HOME="$tmp"
export GIT_CONFIG_GLOBAL="$tmp/gitconfig"
export GIT_CONFIG_NOSYSTEM=1
export GIT_TERMINAL_PROMPT=0
git config --global user.email 'test@example.invalid'
git config --global user.name 'Worktree Test'
git config --global init.defaultBranch main
git config --global advice.detachedHead false

fail=0
ok()  { printf 'ok   %s\n' "$*"; }
bad() { printf 'FAIL %s\n' "$*"; fail=1; }

is() { # actual expected description
  if [ "$1" = "$2" ]; then ok "$3"; else
    bad "$3"
    printf '       expected: %s\n       got:      %s\n' "$2" "$1"
  fi
}
has() { # haystack needle description
  case "$1" in
    *"$2"*) ok "$3" ;;
    *) bad "$3"; printf '       no %s in: %s\n' "'$2'" "$1" ;;
  esac
}
hasnt() { # haystack needle description
  case "$1" in
    *"$2"*) bad "$3"; printf '       unexpected %s in: %s\n' "'$2'" "$1" ;;
    *) ok "$3" ;;
  esac
}
exists()  { if [ -e "$1" ]; then ok "$2"; else bad "$2"; printf '       missing: %s\n' "$1"; fi; }
absent()  { if [ -e "$1" ]; then bad "$2"; printf '       still there: %s\n' "$1"; else ok "$2"; fi; }

# ── The repositories ────────────────────────────────────────────────────────
#
#   origin.git   the "remote"
#   seed/        a second clone, standing in for everyone else pushing to it
#   proj/main    the main worktree; proj/worktrees/ is where git-wt puts the rest

origin="$tmp/origin.git"
seed="$tmp/seed"
proj="$tmp/proj"
main="$proj/main"
roots="$proj/worktrees"

git init --quiet --bare "$origin"
# `git init` rather than a clone of the empty origin, which warns about it.
git init --quiet "$seed"
git -C "$seed" remote add origin "$origin"
printf 'one\n' >"$seed/file"
git -C "$seed" add file
git -C "$seed" commit --quiet -m 'first'
git -C "$seed" push --quiet -u origin main
git clone --quiet "$origin" "$main"

# A branch pushed to origin and nowhere else, which is the case `git wt
# <branch>` exists for: the branch GitHub made from an issue.
seed_branch() { # name, commit subject
  git -C "$seed" checkout --quiet -b "$1" main
  printf '%s\n' "$2" >"$seed/$1.txt"
  git -C "$seed" add "$1.txt"
  git -C "$seed" commit --quiet -m "$2"
  git -C "$seed" push --quiet -u origin "$1"
  git -C "$seed" checkout --quiet main
}

out=''
rc=0
dest=''
cd_file="$tmp/cd"

run() { # cwd, args...
  local dir=$1
  shift
  : >"$cd_file"
  out=$(cd "$dir" && GIT_WT_CD_FILE="$cd_file" "$script" "$@" 2>&1)
  rc=$?
  dest=$(cat "$cd_file")
}

status_of() { # branch -> the status column `list` gives it
  run "$main" list
  printf '%s\n' "$out" | awk -v b="$1" '$2 == b {print $1; exit}'
}

# ── new ─────────────────────────────────────────────────────────────────────

seed_branch remote-only 'work done elsewhere'

run "$main" remote-only
is "$rc" 0 'new: succeeds for a branch that exists only on the remote'
is "$dest" "$roots/remote-only" 'new: reports the worktree as the destination'
exists "$roots/remote-only/remote-only.txt" 'new: checks the branch out, not the base'
is "$(git -C "$roots/remote-only" rev-parse --abbrev-ref '@{upstream}')" origin/remote-only \
  'new: sets the upstream to the remote branch'

run "$main" remote-only
is "$rc" 0 'new: is idempotent'
has "$out" 'already checked out' 'new: says the worktree already exists'
is "$dest" "$roots/remote-only" 'new: still reports where to go'

run "$roots/remote-only" origin/remote-only
is "$dest" "$roots/remote-only" 'new: accepts a branch name with the remote still on it'

run "$main" brand-new
is "$rc" 0 'new: succeeds for a branch that exists nowhere'
exists "$roots/brand-new" 'new: creates the worktree'
is "$(git -C "$roots/brand-new" rev-parse HEAD)" "$(git -C "$main" rev-parse origin/main)" \
  'new: starts an unknown branch at the base branch'
has "$out" 'git push -u origin brand-new' 'new: says how to publish an unpublished branch'
# Tracking origin/main from a feature branch is what makes `git push` refuse
# and `git pull` merge main in; neither should be inherited from a helper.
is "$(git -C "$roots/brand-new" rev-parse --abbrev-ref '@{upstream}' 2>/dev/null)" '' \
  'new: does not set the upstream to the base branch'

run "$main" claude/nested-name
is "$dest" "$roots/claude/nested-name" 'new: handles a branch name containing a slash'

# The fetch-and-fast-forward half: a commit that lands on origin/main while
# you were away is in the main worktree by the time the next worktree opens.
printf 'two\n' >>"$seed/file"
git -C "$seed" commit --quiet -am 'second'
git -C "$seed" push --quiet origin main
run "$main" ff-check
is "$(git -C "$main" log -1 --format=%s)" 'second' 'new: fast-forwards the base branch first'

run "$roots/remote-only" ''
is "$dest" "$main" 'no argument: goes to the main worktree'
run "$roots/remote-only" main
is "$dest" "$main" 'the base branch resolves to the main worktree, not a new one'

run "$main" path remote-only
is "$out" "$roots/remote-only" 'path: prints an existing worktree'
run "$main" path never-made
is "$out" "$roots/never-made" 'path: prints where one would go'

# `new` is the default subcommand, so its options have to reach it unspelled.
run "$main" --no-fetch remote-only
is "$rc" 0 'an option works without the `new` subcommand'
run "$main" --bogus
is "$rc" 1 'an unknown option fails'
has "$out" 'unknown option: --bogus' 'an unknown option is named, not answered with usage'
run "$main" --help
is "$rc" 0 '--help exits 0'
has "$out" 'usage:' '--help prints the usage'

# ── The four states clean has to tell apart ─────────────────────────────────

# merged: pushed, and its commits are now in origin/main.
seed_branch merged-work 'a merged change'
run "$main" merged-work
git -C "$seed" merge --quiet --no-ff -m 'merge merged-work' merged-work
git -C "$seed" push --quiet origin main

# gone: pushed, merged by a squash so its commits are ancestors of nothing,
# and deleted on the remote afterwards.  This is what a merged pull request
# leaves behind with GitHub's "delete branch on merge" set.
seed_branch squashed-work 'a squashed change'
run "$main" squashed-work
git -C "$seed" push --quiet origin --delete squashed-work

# dirty: uncommitted changes.
seed_branch in-progress 'work in progress'
run "$main" in-progress
printf 'scratch\n' >"$roots/in-progress/scratch.txt"

# unpushed: a commit that exists nowhere else.
seed_branch not-pushed-yet 'committed but not pushed'
run "$main" not-pushed-yet
printf 'more\n' >>"$roots/not-pushed-yet/not-pushed-yet.txt"
git -C "$roots/not-pushed-yet" commit --quiet -am 'local only'

# active: pushed, up to date with its remote branch, not merged anywhere.
seed_branch still-going 'ongoing work'
run "$main" still-going

is "$(status_of merged-work)"    merged   'list: a branch whose commits are in the base is merged'
is "$(status_of squashed-work)"  gone     'list: a branch deleted on the remote is gone'
is "$(status_of in-progress)"    dirty    'list: uncommitted changes win over everything else'
is "$(status_of not-pushed-yet)" unpushed 'list: a commit that exists nowhere else is unpushed'
is "$(status_of still-going)"    active   'list: a live branch is active'
is "$(status_of brand-new)"      fresh    'list: a worktree with no commits of its own is fresh'
is "$(status_of main)"           main     'list: the main worktree is never a candidate'

run "$main" list
has "$out" 'would remove 2' 'list: counts the ones clean would take'

# ── clean ───────────────────────────────────────────────────────────────────

run "$main" clean
is "$rc" 0 'clean: exits 0 with nothing to do'
has "$out" 'would remove' 'clean: says what it would remove'
has "$out" 'nothing was removed' 'clean: says it removed nothing'
exists "$roots/merged-work" 'clean: is a dry run without --yes'

run "$main" clean --yes
absent "$roots/merged-work"   'clean --yes: removes a merged worktree'
absent "$roots/squashed-work" 'clean --yes: removes a worktree whose branch is gone'
exists "$roots/in-progress"   'clean --yes: keeps uncommitted changes'
exists "$roots/not-pushed-yet" 'clean --yes: keeps unpushed commits'
exists "$roots/still-going"   'clean --yes: keeps live work'
exists "$roots/brand-new"     'clean --yes: keeps a worktree with no commits yet'
exists "$main"                'clean --yes: never touches the main worktree'

is "$(git -C "$main" branch --list merged-work)" '' 'clean --yes: deletes the merged branch'
is "$(git -C "$main" branch --list squashed-work)" '' 'clean --yes: deletes the branch that is gone'
has "$out" 'git branch squashed-work' 'clean --yes: says how to restore an unmerged branch it deleted'
is "$(git -C "$main" branch --list in-progress | tr -d ' *+')" in-progress \
  'clean --yes: keeps the branch of a worktree it kept'

# A worktree whose directory was deleted by hand leaves a record behind that
# only `git worktree prune` clears -- the state every stale list ends up in.
rm -rf "$roots/still-going"
run "$main" list
is "$(status_of still-going)" missing 'list: a deleted directory shows as missing'
run "$main" clean --yes
hasnt "$(git -C "$main" worktree list)" still-going 'clean --yes: prunes the record of a deleted directory'

# ── rm ──────────────────────────────────────────────────────────────────────

run "$main" rm in-progress
is "$rc" 1 'rm: refuses a worktree with uncommitted changes'
exists "$roots/in-progress" 'rm: leaves it alone'
has "$out" '--force' 'rm: says which flag would override it'

run "$main" rm --force in-progress
is "$rc" 0 'rm --force: removes it anyway'
absent "$roots/in-progress" 'rm --force: the worktree is gone'

run "$main" rm not-pushed-yet
is "$rc" 0 'rm: removes a clean worktree with unpushed commits'
has "$out" 'kept branch not-pushed-yet' 'rm: keeps the branch when the commits are only there'
is "$(git -C "$main" branch --list not-pushed-yet | tr -d ' *+')" not-pushed-yet \
  'rm: the branch is still there to check out again'

run "$main" rm "$main"
is "$rc" 1 'rm: refuses the main worktree'
has "$out" 'main worktree' 'rm: says why'

run "$main" rm nonexistent-branch
is "$rc" 1 'rm: reports a branch with no worktree'

# Removing the worktree you are standing in has to leave the shell somewhere,
# and the main worktree is the only place guaranteed to exist.
run "$roots/brand-new" rm
is "$rc" 0 'rm: removes the worktree it is run from'
is "$dest" "$main" 'rm: sends the shell to the main worktree afterwards'

# ── The shell wrapper ───────────────────────────────────────────────────────
#
# The cd is the whole point of scripts/git/wt.sh, and it is the one thing a
# test of git-wt alone cannot see: it happens in the shell that sourced it.
# Exercised here in bash; the zsh-only lines in that file are the two that
# find its own path and hook up completion.

wrapper=$(cd "$(dirname "$0")" && pwd)/wt.sh

landed=$(cd "$main" && . "$wrapper" && wt remote-only >/dev/null 2>&1 && pwd)
is "$landed" "$roots/remote-only" 'wt.sh: the shell lands in the worktree'

landed=$(cd "$roots/remote-only" && . "$wrapper" && wt >/dev/null 2>&1 && pwd)
is "$landed" "$main" 'wt.sh: no argument lands in the main worktree'

landed=$(cd "$main" && . "$wrapper" && wt list >/dev/null 2>&1 && pwd)
is "$landed" "$main" 'wt.sh: a command with no destination does not move the shell'

# ── Configuration ───────────────────────────────────────────────────────────

git -C "$main" config wt.root "$tmp/elsewhere"
run "$main" configured-root
is "$dest" "$tmp/elsewhere/configured-root" 'wt.root: relocates the worktree root'
GIT_WT_ROOT="$tmp/override" run "$main" env-root
is "$dest" "$tmp/override/env-root" 'GIT_WT_ROOT: overrides wt.root'
git -C "$main" config --unset wt.root

# $tmp holds the repositories but is not one, which is the situation a fresh
# terminal in $HOME is in.
run "$tmp" list
is "$rc" 1 'outside a repository: fails without GIT_WT_HOME'
has "$out" 'GIT_WT_HOME' 'outside a repository: says what would fix it'
GIT_WT_HOME="$main" run "$tmp" path remote-only
is "$out" "$roots/remote-only" 'GIT_WT_HOME: works on that repository from outside any'
GIT_WT_HOME="$tmp/not-a-repo" run "$tmp" list
is "$rc" 1 'GIT_WT_HOME: a path that is not a repository fails'

# ── Paths with spaces ───────────────────────────────────────────────────────
#
# Arguments reach the option scan as ${@+"$@"} and the rm targets as
# ${arr[@]+"${arr[@]}"}.  Those guards exist for bash 3.2, which treats an
# empty array under `set -u` as an unbound variable; the inner quotes are what
# stop the arguments being split on whitespace and glob-expanded on the way
# through.  A worktree root with a space in it exercises both -- and a
# regression here is silent, because everything without a space keeps working.

spaced="$tmp/work trees"

GIT_WT_ROOT="$spaced" run "$main" spaced-branch
is "$dest" "$spaced/spaced-branch" 'spaces: a worktree root containing a space works'
exists "$spaced/spaced-branch" 'spaces: the worktree is really there'

GIT_WT_ROOT="$spaced" run "$main" list
has "$out" 'spaced-branch' 'spaces: list reports it'

GIT_WT_ROOT="$spaced" run "$main" rm "$spaced/spaced-branch"
is "$rc" 0 'spaces: rm accepts a path containing spaces'
absent "$spaced/spaced-branch" 'spaces: and removes exactly it'

# `clean` accepts --yes, and nothing else that quietly means the same thing.
run "$main" clean --force
is "$rc" 1 'clean: --force is not a synonym for --yes'
has "$out" 'unknown option: --force' 'clean: and says so rather than removing anything'

# ── Several projects ────────────────────────────────────────────────────────
#
# GIT_WT_PROJECTS lists directories that *contain* projects, so this is a
# container holding three of them, each laid out as <project>/main.  One is
# named after a branch that exists in the first repository, which is the
# collision the precedence rule has to survive.

hub="$tmp/hub"
git clone --quiet "$origin" "$hub/alpha/main"
git clone --quiet "$origin" "$hub/beta/main"
git clone --quiet "$origin" "$hub/remote-only/main"

# From outside any repository, one argument is a project name.
GIT_WT_PROJECTS="$hub" run "$tmp" alpha
is "$dest" "$hub/alpha/main" 'projects: a name on the search path is a project'

# Two arguments are always project-then-something, even standing in another
# repository -- and the destination survives the re-exec into it.
GIT_WT_PROJECTS="$hub" run "$main" alpha merged-work
is "$dest" "$hub/alpha/worktrees/merged-work" 'projects: <project> <branch> works from another repository'
exists "$hub/alpha/worktrees/merged-work" 'projects: and really makes the worktree there'

GIT_WT_PROJECTS="$hub" run "$main" beta list
has "$out" "hub/beta/main" 'projects: <project> <command> runs the command over there'

GIT_WT_PROJECTS="$hub" run "$tmp" "$hub/alpha" path some-branch
is "$out" "$hub/alpha/worktrees/some-branch" 'projects: a path names a project too'

# The repository you are standing in always wins for a single argument, even
# when a project has the same name as the branch.
GIT_WT_PROJECTS="$hub" run "$main" remote-only
is "$dest" "$roots/remote-only" 'projects: one argument is a branch here, not a project elsewhere'

GIT_WT_PROJECTS="$hub" run "$tmp" no-such-project
is "$rc" 1 'projects: an unknown name outside a repository fails'

# ── clean --all ─────────────────────────────────────────────────────────────

GIT_WT_PROJECTS="$hub" run "$tmp" clean --all
is "$rc" 0 'clean --all: exits 0'
has "$out" "hub/alpha/main" 'clean --all: reaches the first project'
has "$out" "hub/beta/main" 'clean --all: reaches the second'
exists "$hub/alpha/worktrees/merged-work" 'clean --all: is still a dry run'

GIT_WT_PROJECTS="$hub" run "$tmp" clean --all --yes
absent "$hub/alpha/worktrees/merged-work" 'clean --all --yes: removes across projects'
is "$(git -C "$hub/alpha/main" branch --list merged-work)" '' 'clean --all --yes: and their branches'
exists "$main" 'clean --all --yes: leaves main worktrees alone'

GIT_WT_PROJECTS="$hub" run "$tmp" list --all
has "$out" "hub/beta/main" 'list --all: reports every project'

run "$main" clean --all
is "$rc" 1 'clean --all: fails when GIT_WT_PROJECTS is not set'
has "$out" 'GIT_WT_PROJECTS' 'clean --all: says what is missing'

# ── ─────────────────────────────────────────────────────────────────────────

if [ "$fail" -eq 0 ]; then echo 'all worktree tooling checks ok'; else echo 'FAILURES'; fi
exit "$fail"
