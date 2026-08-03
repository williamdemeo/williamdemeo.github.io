# File: scripts/git/wt.sh
#
# `wt` -- scripts/git/git-wt plus the one thing no program can do for the
# shell that ran it: change its directory.  git-wt writes where it ended up
# to the file named by GIT_WT_CD_FILE; this function reads it and cd's there.
#
# Works in zsh and bash.  Add to ~/.zshrc:
#
#     source ~/git/williamdemeo/MKDOCS/williamdemeo.github.io/main/scripts/git/wt.sh
#
# and then, from anywhere inside the repository:
#
#     wt 82-m4-7-mathematics     fetch, fast-forward main, create the worktree, cd there
#     wt                         cd to the main worktree
#     wt list                    every worktree and whether it is finished
#     wt clean                   what `wt clean --yes` would remove
#     wt rm                      remove the worktree you are standing in, and cd out
#
# Putting scripts/git on PATH as well makes the same tool available as the git
# subcommand `git wt`, which is the right spelling everywhere the cd does not
# matter -- inside scripts, and in another repository.

if [ -n "${ZSH_VERSION:-}" ]; then
  # %x is the file being sourced, and (%) asks for prompt escapes to be
  # expanded in it.  Wrapped in eval so bash never has to parse zsh syntax.
  eval '_wt_source=${(%):-%x}'
else
  _wt_source=${BASH_SOURCE[0]}
fi
_wt_dir=$(cd "$(dirname "$_wt_source")" && pwd)
unset _wt_source

wt() {
  # Prefer a git-wt on PATH, so an installed copy wins over this checkout.
  local script cd_file dest rc
  script=$(command -v git-wt 2>/dev/null) || script="$_wt_dir/git-wt"

  cd_file=$(mktemp "${TMPDIR:-/tmp}/wt.XXXXXX") || return 1

  # Not `$(...)`: git's own output -- fetch progress, `worktree add`'s
  # summary -- should reach the terminal while it happens rather than being
  # captured and replayed.  Hence the file.
  GIT_WT_CD_FILE=$cd_file "$script" "$@"
  rc=$?

  dest=$(cat "$cd_file" 2>/dev/null)
  rm -f "$cd_file"
  if [ -n "$dest" ] && [ -d "$dest" ]; then
    cd "$dest" || return 1
  fi
  return $rc
}

# ── Completion ──────────────────────────────────────────────────────────────
#
# Branch names, local and on the remote, plus the subcommands.  The remote
# ones are the point: `wt 82<TAB>` completes a branch that exists only on
# GitHub, which is exactly the branch you are about to make a worktree for.

_wt_candidates() {
  git for-each-ref --format='%(refname:lstrip=2)' refs/heads 2>/dev/null
  git for-each-ref --format='%(refname:lstrip=3)' refs/remotes/origin 2>/dev/null |
    grep -v '^HEAD$'
  printf '%s\n' new list clean rm path main
}

if [ -n "${ZSH_VERSION:-}" ]; then
  # compdef only exists once compinit has run; sourcing this file before it
  # leaves the function working and uncompleted rather than printing an error.
  if whence compdef >/dev/null 2>&1; then
    _wt_complete() { compadd -- ${(f)"$(_wt_candidates)"}; }
    compdef _wt_complete wt
  fi
elif [ -n "${BASH_VERSION:-}" ]; then
  _wt_complete() {
    COMPREPLY=($(compgen -W "$(_wt_candidates)" -- "${COMP_WORDS[COMP_CWORD]}"))
  }
  # Programmable completion is a compile-time option, and a bash built without
  # it is rare but real -- nixpkgs' non-interactive build is one.  Sourcing
  # this file must not fail there over a convenience.
  if type complete >/dev/null 2>&1; then
    complete -F _wt_complete wt
  fi
fi
