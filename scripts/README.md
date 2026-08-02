## scripts

This directory contains miscellaneous utility scripts.

The Python utilities live under `scripts/python/`, separated from shell scripts and other scaffolding so that they can be lifted as a self-contained package if and when they become useful outside this repository.  See `scripts/python/_utils/` for the functional-programming primitives (Result monad, command-runner wrappers, file-ops wrappers) shared across the Python scripts.  Tool families get their own subdirectory: `scripts/python/flrp/` is the FLRP certificate emitter (WP-6, issue #457; see its README), tested by `make flrp-test`.

---

### `gh_project_populate`: automating GitHub project creation

This script is used to create a GitHub project, issues, and labels for a repository
from a single markdown file using the GitHub API.

**Prerequisites**.

- Python 3.8+
- `gh` CLI installed and authenticated

**Example Usage**.

The following commands assume the GitHub project/issue generation script is at
`scripts/python/gh_project_populate.py` and the Markdown file containing the
label/project/issue descriptions is `docs/GITHUB_PROJECT.md`.

+  Dry run — see what would be created (from the main project directory).

   ```zsh
   python3 scripts/python/gh_project_populate.py docs/GITHUB_PROJECT.md --repo williamdemeo/williamdemeo.github.io --dry-run
   ```

+  Create everything (will prompt for confirmation).


   ```zsh
   python3 scripts/python/gh_project_populate.py docs/GITHUB_PROJECT.md --repo williamdemeo/williamdemeo.github.io
   ```

+  Or create in stages.

   ```zsh
   python3 scripts/python/gh_project_populate.py docs/GITHUB_PROJECT.md --repo williamdemeo/williamdemeo.github.io --labels-only
   python3 scripts/python/gh_project_populate.py docs/GITHUB_PROJECT.md --repo williamdemeo/williamdemeo.github.io --milestones-only
   python3 scripts/python/gh_project_populate.py docs/GITHUB_PROJECT.md --repo williamdemeo/williamdemeo.github.io --issues-only
   ```

+  Resume if interrupted (e.g., start from issue M1-3).

   ```zsh
   python3 scripts/python/gh_project_populate.py docs/GITHUB_PROJECT.md --repo williamdemeo/williamdemeo.github.io --issues-only --start-from M1-3
   ```

---

### `ci/project-plan-check.sh`: the drift report CI runs

`scripts/ci/project-plan-check.sh` is what the weekly workflow executes.  It
runs the staleness check, classifies the result, and writes a report to
`$GITHUB_STEP_SUMMARY` — or to stdout when that is unset, so running it
locally shows exactly what CI would say:

```zsh
make project-plan-report
```

It is advisory and always exits 0.  Use `make project-plan-check` when you
want the raw exit code.

It lives here rather than in a workflow `run:` block because shell in YAML
cannot be run locally, cannot be linted, and cannot be tested — and because
editing it requires the `workflow` scope to push.  The workflow is now
structure only: when it runs, what it may access, and what it calls.

`scripts/ci/test_project_plan_check.sh` covers all three reporting branches
plus an unexpected exit code, using the `RENDER` seam to stand in for the
render script so no GitHub API access is needed.

---

### `audit_math.mjs`: checking that every expression renders

`scripts/js/audit_math.mjs` renders every `$...$` and `$$...$$` expression in a
content tree with KaTeX and reports what fails.  It loads the bundle the site
ships (`docs/assets/katex/katex.min.js`) and the site's macro table
(`docs/javascripts/katex-macros.js`), so the audit cannot drift from what
visitors actually get, and it needs nothing from npm.

```zsh
make math-audit                         # defaults to import/zola-converted
make math-audit MATH_SRC=docs           # or any other tree
```

Exits non-zero when anything fails to render, so it works as a CI gate once the
mathematical content has moved into `docs/`.

Fenced and inline code are stripped before scanning, so `$PATH` in a shell
example is not mistaken for mathematics.
---

### `gh_project_render`: regenerating GITHUB_PROJECT.md from GitHub

Once the project is bootstrapped, GitHub becomes the source of truth for issue state.  This script pulls live GitHub state and regenerates the issue listings inside `docs/GITHUB_PROJECT.md`, leaving hand-edited prose (milestone descriptions, exit criteria, mermaid graphs) untouched.

The file is treated as a sequence of manual prose segments interleaved with regions delimited by HTML-comment markers:

```markdown
<!-- BEGIN GENERATED: milestone-1 -->
...
<!-- END GENERATED: milestone-1 -->
```

Render preserves manual segments byte-for-byte and rebuilds each generated region from the live GitHub API.  The convention is that a region with id `milestone-N` is rebuilt from issues bearing the `milestone-N-*` label, ordered by their `[MN-k]` ordinal.

**Example Usage**.

+  Regenerate in place:

   ```zsh
   make project-plan
   ```

+  Or run the script directly:

   ```zsh
   python3 scripts/python/gh_project_render.py docs/GITHUB_PROJECT.md --repo williamdemeo/williamdemeo.github.io
   ```

+  Verify staleness without rewriting:

   ```zsh
   make project-plan-check
   ```

   Exit codes follow `diff(1)`, so a caller can tell a stale plan from a
   check that never ran:

   | Code | Meaning |
   | --- | --- |
   | 0 | the file is current |
   | 1 | the file differs from live GitHub state |
   | 2 | the run failed — authentication, API error, bad markers |

   A scheduled CI job runs this weekly and reports drift without failing the
   build: a stale plan is worth knowing about, but it is not a reason to
   block a merge.  It distinguishes 1 from 2, so a broken check is not
   reported as drift.

**Requirements**.

Both targets need an authenticated `gh` on `PATH`; the `Makefile` guards for
it and prints an actionable message rather than a stack trace when it is
missing.  Override the target repository with `make project-plan REPO=owner/name`.

Where authentication comes through `GH_TOKEN` or `GITHUB_TOKEN` rather than a
keychain — GitHub Actions, and some sandboxes — pass `NO_ENV_PREFIX=1`:

```zsh
make project-plan-check NO_ENV_PREFIX=1
```

**A note on `--no-env-prefix`**.

By default the scripts prepend `env -u GH_TOKEN -u GITHUB_TOKEN` to every `gh`
invocation, working around a `gh` quirk where those variables override the
keychain-stored token.  In an environment that authenticates *through* those
variables — some CI runners and sandboxes do — stripping them leaves `gh` with
no credentials at all, and every call fails with exit code 4.  Pass
`--no-env-prefix` there.

**The populate / render symmetry**.

The two scripts cover disjoint phases of the project's life cycle: populate is the one-shot bootstrap from a hand-authored markdown plan to GitHub project state; render is the steady-state inverse, pulling live GitHub state back into the same markdown.  After bootstrap, manual edits to issue bodies should happen on GitHub; the next `make project-plan` propagates them back into `GITHUB_PROJECT.md`.

---

### `check_redirects`: the legacy-URL redirect map

Two dead sites' URLs land on this one: the Octopress paths from
`williamdemeo.github.io`, which is where this site deploys today, and the Zola
paths from `williamdemeo.org`, which M8-1 points here.  147 URLs between them,
with inbound links from published papers, talk slides and `ualib.org`.

`redirects.yml` at the repo root is the only copy of that map.  Each entry
carries one of four dispositions and, where it matters, the reasoning:

| | |
| --- | --- |
| `to:` | redirect here — a `docs/`-relative markdown path or an `http(s)` URL |
| `keep:` | the new site serves this URL itself; no stub, but the page is verified to exist |
| `pending:` | target known, not built yet; the value says what blocks it |
| `none:` | deliberately not redirected; the value says why |

`from` is a URL path, and a trailing `/**` matches everything under a prefix.
Exact matches beat prefix matches and longer prefixes beat shorter ones, so a
specific rule can carve an exception out of a section-wide one.

**A prefix rule cannot carry `to:`,** and the loader rejects it rather than
letting it look like it worked.  `to:` emits exactly one stub, at the prefix
itself, so `/exams/** → …` would redirect `/exams/` and leave the other 47
URLs 404ing with the build reporting success.  Switching a prefix rule on
means either listing its URLs individually, or — for a host move, where each
URL should map onto the matching path under the new host — teaching the hook
prefix rewriting first.  `keep:`, `pending:` and `none:` are fine on a prefix
rule, since none of them emits anything.

**`redirects_hook.py`** emits the stubs at build time, wired in through
mkdocs.yml's `hooks:`.  Only `to:` rules produce output; an active rule whose
target does not resolve aborts the build rather than shipping a stub that
404s.  This deliberately does *not* use the `mkdocs-redirects` plugin, which
as of 1.2.3 hard-depends on `properdocs` — an entire alternative site
generator that installs itself and advertises for a replacement on every
build.  That is a large supply-chain surface, and two more packages to pin in
`flake.nix`, for about forty lines of "write a meta-refresh file".

**`check_redirects.py`** proves the map is trustworthy, in three parts:

```console
$ make redirect-check          # builds the site, then checks against it
  zola        103 urls
  octopress    46 urls
  union       147 urls
  rules: 64
    to         2 rules     2 urls
    keep       3 rules     3 urls
    pending   55 rules   138 urls
    none       4 rules     4 urls
OK -- every legacy URL is accounted for exactly once.
```

- **coverage** — every URL in both inventories is governed by a rule, and every
  rule governs at least one URL.  Several rules may *match* one URL — a
  carve-out inside a prefix rule is exactly that — but precedence picks a
  unique winner, and the tests check that uniqueness exhaustively against the
  real inventories.  A legacy URL nobody thought about is the failure this
  exists to prevent, and it is invisible without the check.
- **`--site DIR`** — what the map claims resolves does resolve: `keep` URLs
  have a real page, active redirects emitted a stub.  Claiming a URL is
  preserved and then not serving it is worse than an honest redirect.
- **`--verify-inventory`** — the Zola URL list still corresponds 1:1 with the
  imported page tree, re-derived rather than taken on trust.  This is what
  turned up that Zola slugifies to lowercase, so `exams/real/1991Nov21.md` is
  served at `/exams/real/1991nov21/` — 43 of the highest-traffic URLs differ
  from their filenames by case alone.

Exit codes follow `diff(1)`: 0 current, 1 a check failed, 2 could not run.
`make redirect-test` runs the rule-matching unit tests.  Both run in CI as
`nix flake check` derivations.

The pending count is printed on every run, grouped by what blocks each group,
so the remainder stays visible instead of being quietly forgotten.  Switching
a redirect on when its target lands is changing `pending:` to `to:` — one
line, one file.

---

### `gen_publications`: rendering the bibliography

`bibliography.json` is the only authoritative publication list (ADR-006).
`make publications` renders it into two committed snippets, and pages include
them rather than holding a copy:

| output | entries | consumed by |
| --- | --- | --- |
| `docs/_snippets/publications-page.md` | all of them | `docs/publications.md` |
| `docs/_snippets/publications-cv.md` | those marked `_cv` | `docs/cv.md`, *Selected publications* |
| `docs/publications.bib` | all of them | anyone citing this work |

Each entry renders as title, authors, imprint, and a row putting **the version
of record and the preprint side by side**. The CV's is the same, a little
tighter: the year rather than the full date, and no DOI.

The page groups entries by **where the work appeared** — journal, conference,
preprint, thesis, edited volume — rather than by whether it was refereed, which
nothing in `bibliography.json` records. A reader still tells a journal paper
from a preprint at a glance, and no heading claims something no source backs.
An entry whose type matches no group fails validation: a publications page that
silently drops a publication is the worst bug available to it.

Abstracts render collapsed, from arXiv or DataCite, with `_abstract-source`
recording which. The verifier checks the stored text against that service, so a
truncated or hand-edited abstract fails.

The BibTeX needs no dependency — the mapping from CSL-JSON is mechanical.
Titles are double-braced: they were checked against the publishers, and a `.bst`
case-folding *Agda* or *Birkhoff* would undo that.

`make publications-check` validates the file *and* reports whether either
snippet has drifted from it — a hand-edit to a generated file survives every
other check in this repository. Exit codes follow `diff(1)`: 0 current, 1 stale
or invalid, 2 could not run. `nix flake check` runs it as part of
`checks.bibliography-tooling`, so drift fails CI; it needs no network, unlike
`publications-verify`.

It guards the *snippets*, not the pages that include them. Deleting an
`--8<--` line, or adding entries by hand beneath one, is not something any
check here would notice.

Two rules keep the rendering honest, and both are tested:

- **Say only what the record supports.** An entry with no issue number says
  nothing about issues; a date shows to the precision the publisher gave. The
  thesis keeps a bare year, because its arXiv posting date is not its
  completion date.
- **Label a link by what vouches for it.** A DOI is a publisher asserting "this
  is the record of that work", so the entry's type may name it — *Journal*,
  *Proceedings*. A bare URL is not: the ISMA 2004 link is the author's own copy
  of the PDF, so it renders as *PDF*, not as *Proceedings*.

One arXiv identifier may sit on two entries when one declares `_version-of` the
other — a preprint and the paper it became are two documents. That is a
*relaxation* of a check, which is easier to get wrong than a check, so
`test_gen_publications.py` covers both directions.

---

### `verify_bibliography`: checking the publication list against the publishers

`bibliography.json` was built by reconciling three hand-maintained lists
(ADR-006). Reconciling makes copies agree with each other; it does not make
them right. This asks the publishers:

```console
$ make publications-verify
verifying 16 entries against api.crossref.org, api.datacite.org and export.arxiv.org
...
19 record(s) fetched and compared
  ! 0 difference(s) needing a decision
  ~/+/i 23 of spelling, of a field only the publisher carries, or for information

not verifiable against either service (4):
  adaricheva2018alh: no DOI and no arXiv id
  demeo2004isma: no DOI and no arXiv id
  demeo2002icmc: no DOI and no arXiv id
  demeo1998eigenvalues: no DOI and no arXiv id
```

More records than entries: an entry with both a DOI and an arXiv identifier is
two lookups.

Every entry with a DOI is looked up at Crossref; where Crossref does not index
it, the registration-agency endpoint says who does and a DataCite DOI is
followed to DataCite. Every entry with an arXiv identifier is looked up at the
arXiv API. Title, authors, container-title, volume, issue, page and date are
compared against what the file claims, and each difference is marked:

| | |
| --- | --- |
| `!` | the values genuinely differ — someone has to decide |
| `~` | the same value spelled differently: case, accents, `Vol. 30` against `30` |
| `+` | a field the publisher carries and the file does not |
| `i` | context rather than a difference — the raw `journal_ref`, a posting date |

Only `!` fails the run. Exit codes follow `diff(1)`: 0 everything checked
agrees, 1 a difference wants a human, 2 could not run.

Two fields are `i` by design, because the publisher's value and a
bibliography's are different things: the `container-title` of a *proceedings*
article, where the publisher holds the registered title of the volume (*2021
36th Annual ACM/IEEE Symposium on Logic in Computer Science (LICS)*) rather
than the name of the conference; and arXiv's free-text `journal_ref`, checked
by containment and printed in full rather than parsed into fields it does not
really have. For a *journal* article `container-title` is the journal, and a
difference there still fails.

**Two things it is built not to do**, both of which this repository has been
caught by:

- **Report a clean run it did not earn.** Any request that never reaches a
  service — a refused `CONNECT`, a timeout, a 429 or 503 surviving three
  attempts — exits 2, and so does a *partial* run. A checker that passes
  because the network is blocked is worse than no checker. A failure to connect
  also never means "the resource is dead": a sandbox that denies `CONNECT` for
  a host outside its egress allowlist looks exactly like a host that is gone,
  and the message says so.
- **Trust a status code.** Crossref must answer `status: ok` carrying the DOI
  that was asked for; arXiv must return a feed with one entry whose id is the
  one that was asked for. A 200 holding a proxy error page is treated as a
  transport failure, because it means the publisher was never reached — and
  arXiv answers an unknown identifier with a 200 whose entry points at its
  error vocabulary, which is exactly why the body has to be read.

It needs the network, so it is not a build gate: CI has none by design
(ADR-004). `make publications-test` runs both tools' unit tests, which use fixtures and
need nothing, and `nix flake check` runs them as `checks.bibliography-tooling`.
The tests that matter are the ones proving the two behaviours above, since
"it fails loudly" is exactly the kind of claim that should not be taken on
trust.

Dates are compared to the precision the file states: an entry saying "June
2020" agrees with a record saying 2020-06-15, and fails only when it matches
none of the dates the publisher offers. Publishers routinely offer several — a
print issue and its online-first appearance are different dates, and both are
real.

Nothing from PyPI: `urllib`, `json` and `xml.etree` are all in the standard
library, so there is no new pin in `requirements.txt` for `flake.nix` to match
under ADR-004's `requirements-pins` check.

---

### Notes

- The script uses `env -u GH_TOKEN -u GITHUB_TOKEN` by default to work around
  token precedence issues.  Use `--no-env-prefix` to disable this.
- A 1.5-second delay between API calls avoids rate limiting (adjustable with `--delay`).
- Labels and milestones are idempotent — re-running skips existing ones.
- Issue titles are prefixed with `[M0-1]`, `[M1-2]`, etc. for easy identification.

---
