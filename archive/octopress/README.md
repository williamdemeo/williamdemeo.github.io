# Octopress site archive

This directory preserves the content of the Octopress site that occupied this
repository from 2014 until it was retired in July 2026, so that clearing the
generated files from the working tree did not destroy anything.

## What this repository held

The Octopress site was **deploy output, not source**. There was no
`_config.yml`, no `_posts/`, no `Rakefile`, and no `source` branch — only
generated HTML, a Jekyll theme, fonts, and assets: 512 tracked files, 22 MB.
The Markdown behind these posts was written in a separate source repository
that no longer exists, so the generated HTML in this directory is, for two
posts, the only surviving copy of that writing.

The last content commit was December 2017.

## Recovering the full site

The complete pre-cleanup tree is commit
**`1f272058e598b6f4a4ba3ff06bfc20b9f854ec85`** on `main`.

```zsh
git worktree add /tmp/octopress 1f27205
```

A tag `octopress-final` points at the same commit. It was created locally but
could not be pushed from the environment that performed this cleanup, whose git
proxy rejects tag refs; if it is absent from the remote, recreate it with:

```zsh
git tag -a octopress-final 1f27205 -m "Final state of the generated Octopress site"
git push origin octopress-final
```

Cite the SHA rather than the tag anywhere the reference needs to be durable.

## Contents

| Path | What it is |
| --- | --- |
| `posts/` | The `entry-content` body of each of the 15 posts, as raw HTML, with title, date, and original URL in a leading comment. |
| `POSTS.md` | Index of the posts with word counts and original URLs. |
| `urls.txt` | Every one of the 46 URLs the generated site served. Input to the redirect map in M2-6. |

Extraction is reproducible with `scripts/python/extract_octopress_posts.py`;
see its docstring for running it against the tag.

## Where these posts go next

Triage is M2-3 (#12) and conversion is M2-4 (#13). The relevant finding, made
while writing ADR-001:

- **12 of the 15** posts also exist as Zola Markdown in the GitLab repository's
  working tree. Those take the Markdown; the HTML here is a cross-check.
- **1** (`learn-you-an-agda`) exists as Markdown only in GitLab *history*,
  deleted in `b001a4d`. It will **not** be republished — its front matter
  records Liam O'Connor-Davis as the author, with only minor corrections and
  additions by the repository owner.
- **2** (`cloning-an-octopress-repo`, `commutator-as-least-fixed-point`) exist
  nowhere else in any form. The HTML here is the only copy. Of those,
  `cloning-an-octopress-repo` is being dropped as obsolete, which leaves
  `commutator-as-least-fixed-point` as the one post genuinely needing
  HTML-to-Markdown conversion.

## Notes for later issues

- The posts use LaTeX macros that are not standard KaTeX — `$\bA$` appears
  throughout `isotopy`, for instance. M3-4 will need macro definitions, not
  just KaTeX enabled.
- `learn-you-an-agda` contains 52 CodeRay-highlighted blocks; if any part of it
  is ever reused, that markup needs converting rather than copying.
- The six PDFs under `csp/` are retained at their original path so
  `/csp/*.pdf` keeps resolving, but MkDocs only publishes files under `docs/`,
  so M2-5 must relocate them for those URLs to work on the new site.
  Their licensing also needs a deliberate decision in M2-3: only the
  Barto–Kozik paper (LMCS) is open access; the rest were published in IJAC,
  TCS, and Algebra Universalis, and rehosting them may not be permitted.
