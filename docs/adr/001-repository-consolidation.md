# ADR-001: Consolidate both personal sites into `williamdemeo/williamdemeo.github.io`

**Status**: Accepted

**Date**: 2026-07-30

**Deciders**: William DeMeo

**Related**: [#2](https://github.com/williamdemeo/williamdemeo.github.io/issues/2) (M1-1), [#3](https://github.com/williamdemeo/williamdemeo.github.io/issues/3) (M1-2), [#10](https://github.com/williamdemeo/williamdemeo.github.io/issues/10) (M2-1), [#13](https://github.com/williamdemeo/williamdemeo.github.io/issues/13) (M2-4)

---

## Context

Two personal websites exist, and neither is maintained.

**`williamdemeo/williamdemeo.github.io`** (GitHub) holds the *generated output* of an Octopress site: 512 tracked files, 22 MB, last content commit December 2017. There is no `_config.yml`, no `_posts/`, no `Rakefile`, and no `source` branch. What is in the repository is the deploy target of a source repository that no longer exists, so the Markdown behind those fifteen posts is not recoverable from here.

**`williamdemeo/williamdemeo.gitlab.io`** (GitLab) holds a Zola site titled "WJD Open Notebook", which serves `williamdemeo.org` today. It is pinned to Zola v0.5.0 (2018) with a hand-written theme, roughly 130 content files, and a most-recent post from November 2021.

The goal is a single, modern, actively maintained site built with MkDocs — chosen because it is already in daily use on two other sites the author maintains, and the tooling being familiar is the point rather than an incidental preference.

This ADR settles which repository becomes that site's home. Every other issue in the project assumes the answer.

## Decision

**Rebuild inside the existing `williamdemeo/williamdemeo.github.io` repository.**

The GitLab repository's *content* is imported (M2-1); its theme, search bundle, and CI are not. The GitLab repository itself remains public and is not deleted.

## Rationale

### Why not a new repository

`<username>.github.io` is not an ordinary repository name. GitHub Pages treats it as the **user site**: it is served from the repository root at `https://williamdemeo.github.io` with no path prefix, and no other repository in the account can occupy that position. Building the site anywhere else means either accepting a `/repository-name/` path prefix or attaching a custom domain to a project page — indirection that buys nothing, since `williamdemeo.github.io` would still need to exist and redirect.

The one genuine argument for a new repository is a clean history, and it does not survive scrutiny: the same result is available here by clearing the working tree, since the old content stays reachable through history and a tag. A new repository would also discard whatever inbound links point at `williamdemeo.github.io/*`, and would leave the project tooling under `scripts/python/` behind.

### Why not keep both sites

The failure this project exists to correct is that neither site gets updated. Two sites is strictly worse than one for that purpose: it doubles the maintenance surface and forces a decision about where each new thing goes, which is precisely the kind of friction that has stopped updates from happening.

### Why the GitLab repository is imported rather than mirrored

Only the Markdown under `content/` and the referenced images under `static/` are wanted. The Zola theme, the jQuery/elasticlunr search bundle, the `.gitlab-ci.yml`, and the vendored LaTeX helpers are all being replaced, and importing them would carry forward the visual and structural dead weight this rebuild exists to remove.

## The GitLab repository stays public, as the archive of its own history

The GitLab repository is **not** deleted and **not** made private, now or when its Pages deployment is retired in M8-6. It is archived in place, with its README rewritten to point here.

This is deliberate, and there is direct evidence for it rather than only caution. M2-1 imports the GitLab *working tree* in a single commit rather than merging its full history, on the grounds that the history is mostly theme tinkering. But the history is not *only* theme tinkering — it contains content that no longer exists in the working tree at all. Verified while writing this ADR:

- `content/2014-02-27-learn-you-an-agda.md` was added in the initial commit and deleted in `b001a4d` ("fix broken links"). At 1,431 lines it is the largest single content file either site ever had, and GitLab history is the only place its Markdown survives. It will **not** be republished: its front matter records the author as Liam O'Connor-Davis, with only minor corrections and additions by the repository owner, so it is third-party material rather than original work. Preserving it is an archival concern, not a publishing one — which is precisely the distinction this decision turns on.
- Three further post sources are absent from the working tree but present in history: `2019-02-10-composition.md`, `2019-02-10-f-algebras.md`, and `2020-04-10-lennon-wall.md`.

So the GitLab repository is not redundant with the import. Deleting it, or importing only its working tree and then discarding it, would destroy content. Keeping it public costs nothing and preserves the only copy of that history.

Two Octopress posts — `cloning-an-octopress-repo` and `commutator-as-least-fixed-point` — never existed in the GitLab repository in any form, and survive only as generated HTML in this repository's history. That is the reason M1-2 extracts post bodies to `archive/octopress/` before clearing the working tree, rather than relying on the tag alone.

## Consequences

### Positive

- The site is served from the canonical user-site URL with no path prefix.
- Inbound links to `williamdemeo.github.io/*` remain redirectable rather than dead.
- The existing project tooling under `scripts/python/` stays where it already works.
- One repository, one build, one place for new content.

### Costs accepted

- The repository carries an eight-year history of `Site updated at ...` Octopress deploy commits. This is cosmetic; it is not worth rewriting history to remove, and doing so would break every existing commit link.
- The 22 MB of generated output must be cleared from the working tree as a separate, careful step (M1-2) rather than being absent by construction.
- Content lives in two places until M2-1 completes the import.

### Neutral

- The default branch has been renamed `master` → `main`. GitHub redirects the old name, and the merged PR #1 that targeted `master` is unaffected.
- GitHub Pages is set to deploy from GitHub Actions rather than from a branch, which M1-5 depends on.
- `williamdemeo.org` continues to resolve to GitLab Pages until the cutover in M8-1. That cutover is deliberately last, gated on the replacement being verifiably better and on the redirect map having been checked against production.

## Implementation status

| Task | Status |
| --- | --- |
| Confirm option A and record it here | This ADR |
| Rename default branch `master` → `main` | Done |
| Set Pages source to GitHub Actions | Done |
| Set repository description and topics | Pending |
| Note the GitLab archive decision | This ADR |

## Notes

The repository description currently reads *"OLD personal and professional website (find my new site at williamdemeo.gitlab.io)"*, which now points visitors at the site being retired. Updating it is the remaining task on #2.
