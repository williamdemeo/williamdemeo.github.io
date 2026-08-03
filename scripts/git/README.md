# scripts/git

## `git-wt`: the worktree lifecycle in one command each

Starting work on a branch was five commands and a directory to remember:

```zsh
cd ~/git/williamdemeo/MKDOCS/williamdemeo.github.io/main
git fetch
git pull
git worktree add -b 82-m4-7-mathematics ../worktrees/82-m4-7-mathematics origin/82-m4-7-mathematics
cd ../worktrees/82-m4-7-mathematics
direnv allow          # because a new path is a new .envrc as far as direnv is concerned
```

It is now one, from anywhere inside the repository:

```zsh
wt 82-m4-7-mathematics
```

Finishing was worse, because it was a lookup rather than a command — which is
why worktrees accumulate. It is now:

```zsh
wt clean              # says what is finished and why; removes nothing
wt clean --yes        # removes it
```

## Install

Two lines in `~/.zshrc` (they work unchanged in `~/.bashrc`):

```zsh
export PATH="$HOME/git/williamdemeo/MKDOCS/williamdemeo.github.io/main/scripts/git:$PATH"
source "$HOME/git/williamdemeo/MKDOCS/williamdemeo.github.io/main/scripts/git/wt.sh"
```

The first makes git itself find the script, so `git wt list` works like any
other git subcommand — in any repository, and inside scripts. The second
defines the `wt` shell function, which runs the same tool and then `cd`s where
it says.

A third line is worth adding if one project is where you usually are:

```zsh
export GIT_WT_HOME="$HOME/git/williamdemeo/MKDOCS/williamdemeo.github.io/main"
```

With it, `wt 82-m4-7-mathematics` works from a fresh terminal in `$HOME` —
which is the `cd` that used to come before the other five commands. Inside any
repository the surrounding one still wins, so this changes nothing about
working elsewhere.

Both exist because **a process cannot change its parent's working directory**.
`git wt 82-m4-7-mathematics` can create the worktree but cannot put you in it;
only a function running *in* your shell can do that. So `git-wt` writes its
destination to the file named by `GIT_WT_CD_FILE`, and the three-line `wt`
function reads it and `cd`s. Everything else is identical between the two
spellings.

Nothing about the tool is specific to this repository: it reads the layout out
of whichever repository it is run in. It lives here rather than in `~/bin`
because a copy in `~/bin` is a copy that never gets updated.

## Starting work: `wt <branch>`

```zsh
wt 82-m4-7-mathematics
```

1. `git fetch --prune` in the main worktree.
2. Fast-forwards the base branch there — `merge --ff-only`, so a `main` that
   has diverged says so instead of quietly opening a merge.
3. Creates the worktree at `<project>/worktrees/<branch>`, choosing between
   three cases without being told which one applies:

   | the branch | what happens |
   | --- | --- |
   | exists on `origin` (the usual case — GitHub made it from an issue) | checked out, tracking `origin/<branch>` |
   | exists locally already | checked out where it can be worked on |
   | does not exist at all | created from `origin/main`, **not** tracking it, with a reminder of how to publish it |

   The `--no-track` in that last case is deliberate: a feature branch tracking
   `origin/main` makes `git push` refuse with a complaint about mismatched
   upstreams, and `git pull` merge `main` into the branch. Neither is a
   surprise worth inheriting from a helper.
4. Runs `direnv allow` in the new worktree, because a new worktree is a new
   path to direnv and so its `.envrc` starts out blocked. The content is
   whatever the branch has committed, and you are about to run this branch's
   code anyway. `wt --no-direnv <branch>` or `GIT_WT_DIRENV=0` to skip it.
5. `cd`s there.

Running it again on the same branch just `cd`s: the operation is idempotent, so
it is also how you switch back to work you already have open.

`wt` on its own returns to the main worktree.

## Finishing: `wt list` and `wt clean`

```console
$ wt list
main worktree  ~/git/williamdemeo/MKDOCS/williamdemeo.github.io/main
worktree root  ~/git/williamdemeo/MKDOCS/williamdemeo.github.io/worktrees
base branch    origin/main

status    branch                               why
main      main                                 the main worktree
merged    13-m2-4-rescue-posts                 every commit is in origin/main
gone      15-m2-6-redirect-map                 origin/15-m2-6-redirect-map was deleted on the remote
dirty     17-m3-1-visual-system                uncommitted changes
unpushed  82-m4-7-mathematics                  1 commit(s) not on origin/82-m4-7-mathematics
missing   claude/nix-dev-environment-ci-ty4akt its directory is gone; the record needs pruning

6 worktree(s); `git wt clean` would remove 3.
```

Every worktree is in exactly one of these states, and the state decides what
`clean` does:

| status | what it means | `clean` |
| --- | --- | --- |
| `merged` | every commit on the branch is an ancestor of `origin/main` | removes it, and the branch |
| `gone` | the branch was deleted on the remote | removes it, and the branch |
| `missing` | the directory was deleted by hand; only git's record is left | prunes the record |
| `dirty` | uncommitted changes | keeps it |
| `unpushed` | commits that exist nowhere else | keeps it |
| `active` | pushed, up to date, not merged anywhere | keeps it |
| `fresh` | no commits of its own yet — opened and not used | keeps it |
| `locked`, `detached` | someone made a decision here on purpose | keeps it |

**`gone` is the one that matters**, and it is the reason `list` and `clean`
fetch before they judge. A pull request merged with *Squash and merge* or
*Rebase and merge* produces new commits on `main`; the branch's own commits are
ancestors of nothing, so the merged test says no and the branch looks live
forever. The only evidence the work landed is that GitHub deleted the branch on
merge — and that evidence is invisible until a `fetch --prune` removes the
remote-tracking ref. Judging without the prune reports every finished branch as
active, which is exactly the state the list gets into by hand.

Dirty beats everything: an uncommitted change is never traded for tidiness,
whatever else is true of the branch.

Nothing is removed without `--yes`. When something is, the branch it deleted is
printed with its tip:

```console
  deleted branch 15-m2-6-redirect-map (was 47c1781 -- `git branch 15-m2-6-redirect-map 47c1781` restores it)
```

That line is there because `clean` uses `git branch -D` on a squash-merged
branch — `-d` refuses, since by its reckoning the commits were never merged.
The reflog holds them for 90 days either way.

## Removing one: `wt rm`

```zsh
wt rm                       # the worktree you are standing in; cd's you back to main
wt rm 17-m3-1-visual-system # by branch name, from anywhere
wt rm --force <branch>      # also when it has uncommitted changes
```

Without `--force` it refuses a worktree with uncommitted changes, and keeps the
branch when the branch has commits of its own, so the work stays reachable by
name after the directory is gone. It will not remove the main worktree.

## Configuration

Each is an environment variable, falling back to a git config key, falling back
to something read out of the repository. Set the config keys in the main
worktree; every worktree of a repository shares one config.

| variable | config key | default |
| --- | --- | --- |
| `GIT_WT_ROOT` | `wt.root` | `worktrees/` beside the main worktree |
| `GIT_WT_REMOTE` | `wt.remote` | `origin` |
| `GIT_WT_BASE` | `wt.base` | what `refs/remotes/origin/HEAD` points at, then `main`, then `master` |
| `GIT_WT_DIRENV` | — | on; `0` never runs `direnv allow` |
| `GIT_WT_HOME` | — | unset; the repository to act on when the working directory is not inside one |
| `GIT_WT_CD_FILE` | — | unset; the wrapper sets it |

The default root is what this project already does: a main worktree at
`<project>/main` puts branches at `<project>/worktrees/<branch>`, including
nested ones like `worktrees/claude/nix-dev-environment-ci-ty4akt`.

## From make, and from CI

The two commands that do not need to change the shell's directory are also make
targets, so they work without the shell function installed:

```zsh
make wt-list
make wt-clean            # dry run
make wt-clean YES=1
make wt-test
```

`scripts/git/test_git_wt.sh` builds a bare "remote" and two clones in `$TMPDIR`
and drives the tool through every state above — merged, squash-merged and
deleted, dirty, unpushed, live, empty, and a directory deleted by hand — then
checks what `clean` did to each. It needs git and nothing else: no network, no
GitHub, no state outside `$TMPDIR`. `nix flake check` runs it as
`checks.worktree-tooling`.

That test is not ceremony. `clean` deletes worktrees and branches, it decides
what to delete from four questions no single git command answers, and both ways
of being wrong — deleting live work, or keeping finished work — are silent.

## The commands underneath

Worth keeping, for a machine without this checkout on it:

```zsh
git worktree list                                   # what exists
git worktree add -b <branch> ../worktrees/<branch> origin/<branch>
git worktree remove ../worktrees/<branch>           # refuses if dirty
git worktree prune                                  # drop records of deleted directories
git branch -d <branch>                              # refuses unless merged
git branch --merged origin/main                     # what -d would accept
git fetch --prune                                   # drop refs for branches deleted on the remote
git branch -vv | grep ': gone]'                     # branches whose remote is gone
```

The last two are the pair that `wt clean` is built around.
