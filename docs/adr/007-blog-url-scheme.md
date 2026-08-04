<!-- File: docs/adr/007-blog-url-scheme.md -->

# ADR-007: The blog's URL scheme

**Status**: Accepted

**Date**: 2026-08-02

**Deciders**: William DeMeo

**Related**: [#35](https://github.com/williamdemeo/williamdemeo.github.io/issues/35) (M6-1), [#13](https://github.com/williamdemeo/williamdemeo.github.io/issues/13) (M2-4), [#15](https://github.com/williamdemeo/williamdemeo.github.io/issues/15) (M2-6), [#36](https://github.com/williamdemeo/williamdemeo.github.io/issues/36) (M6-2), [ADR-002](002-content-triage.md), [ADR-004](004-nix-environment.md)

---

## Context

The blog is the only part of this site that has to serve **three** URL spaces
at once: its own, and the two the abandoned sites left behind.

| | Posts | Index | Archive | Pagination | Categories | Feed |
| --- | --- | --- | --- | --- | --- | --- |
| Octopress | `/2014/02/13/isotopy/` | — | `/archives/` | `/blog/page/2/` | `/blog/categories/…` ×13 | `/atom.xml` |
| Zola | `/isotopy/` | `/posts/` | — | — | — | — |

Zola strips the date prefix from the filename, so the same post that Octopress
served at `/2014/02/13/isotopy/` was served at `/isotopy/` — a bare root-level
slug, in the same namespace as `/about/` and `/cv/`.

`redirects.yml` is the record of what has to keep resolving, and **37 of its 94
pending entries were blocked on this decision** — the single largest group.
That file, not taste, is the constraint.

Two details from it are worth stating up front, because they decide more than
they look like they should:

**The two legacy sites disagree about dates.** Octopress served
`congruences-of-partial-algebras` under `/2017/04/07/`; the Zola front matter
for the same post says `2017-04-06`. An hours-offset disagreement about one
publication, baked permanently into a path by one of the two sites. A date in
a URL is a claim the URL has to go on being right about.

**Root-level slugs are a shared namespace, and it is still filling up.**
`/typefunc/`, `/probability-quiz/` and `/touchpad-forensics/` already live
there as archived pages with `keep` rules. M5 adds `/research/`, `/talks/`
and `/teaching/`; M2-8 adds 48 pages under `/exams/`; M4 adds portfolio
entries.

## Decision

**Posts are served at `/blog/<slug>/`: under a blog prefix, with the slug
pinned in front matter and no date in the path. Every legacy post URL — both
schemes — redirects there.**

The rest of the scheme follows from putting the blog under `/blog/`:

| | URL | Set by |
| --- | --- | --- |
| Index | `/blog/` | `blog_dir: blog` |
| Post | `/blog/<slug>/` | `post_url_format: "{slug}"`, plus `slug:` in front matter |
| Category | `/blog/category/<slug>/` | plugin default |
| Archive | `/blog/archive/<yyyy>/` | plugin default, `archive_url_date_format: yyyy` |
| Tags index | `/blog/tags/` | `tags_file: blog/tags.md` |
| Page *n* | `/blog/page/<n>/` | plugin default, `pagination_per_page: 5` |

**The slug is pinned in front matter rather than derived from the title.** The
default is to slugify the title, which means retitling a post silently moves
it — and here a post's URL is also the target of two legacy redirects. The
slug is the post's identity; the title is editorial.

**The archive is `/blog/archive/<yyyy>/`, not `/archive/`.** The site already
has an archive area at `/archive/` (M2-9, ADR-002), and `redirects.yml` pins
it as `keep`. Two different things called "the archive" is a nav problem, but
one of them silently overwriting the other is a build problem — and it is the
exact failure #69 had to fix.

**Categories are an allow-list of three**: *Formal verification*,
*Mathematics*, *Tooling*. An unlisted category is a build error, verified:

```
ERROR - Error reading categories of post 'blog/posts/…' in 'docs':
        category 'Miscellany' not in allow list
```

Octopress generated thirteen category pages for fifteen posts, which is not a
taxonomy — it is what happens when the vocabulary is whatever was typed that
day. The list is expected to grow; growing it should be a line in `mkdocs.yml`
and not a side effect of writing.

**Tags are a second, deliberately different thing**: free keywords, one index
page at `/blog/tags/`, an anchor per tag. In mkdocs-material 9.5.49's
community edition there is no page per tag — `material/plugins/tags/plugin.py`
renders every tag as a heading on the one file named by `tags_file`. Read, not
assumed. So "tag pages render" in #35's acceptance criteria is satisfied by
one index page, and that is all the community edition offers.

**An excerpt is required.** Without a `<!-- more -->` separator the plugin
treats the whole post as its own excerpt and the index becomes a wall of
complete articles. `post_excerpt: required` turns that into a build error:

```
ERROR - Couldn't find '<!-- more -->' in post 'blog/posts/…' in 'docs'
```

**Authors are off.** One author; a byline under every post is noise, and
`.authors.yml` is a file to keep in step for no reader benefit.

**`pagination_per_page` is 5, not the default 10, and that is a URL decision
rather than a layout one.** `/blog/page/2/` is a real Octopress URL in the
inventory, and the new blog puts its own second page at exactly that path. At
five posts per page the eight posts #13 is converting produce it, and the rule
becomes `keep: true` — the legacy URL preserved rather than redirected. Five
is also the better number for posts this long.

## What this makes of the 37 blocked redirects

23 are switched on by this change; 14 remain, each for a stated reason.

| Legacy URLs | Now | |
| --- | --- | --- |
| `/posts/`, `/archives/` | → `/blog/` | Zola's index and Octopress's by-date listing |
| `/blog/categories/…` ×13 | → `/blog/` | none of the thirteen survives as a category |
| 4 dropped posts | → `/blog/` | ADR-002 drops them; the blog index is the nearest relevant page |
| 4 URLs for 2 posts | → `/blog/<slug>/` | the two posts this issue ships |
| 12 URLs for 6 posts | pending **#13** | target known and written down; the posts are not converted yet |
| `/blog/page/**` | pending **#13** | becomes `keep` at the second page of posts |
| `/atom.xml` | pending | no feed generator ships in 9.5.49 — see below |

`/blog/categories/**` had to be **expanded into thirteen exact rules**: the
loader rejects `to:` on a prefix rule, because one stub for a prefix would
leave twelve of the thirteen URLs 404ing while the build reported success.

They point at the blog index rather than at a best-guess category page, and
there is a hard reason as well as an editorial one: `check_redirects.py`
requires every internal `to:` target to exist as a file under `docs/`, and the
generated category views live in the plugin's temporary directory. A redirect
can only target a real source page.

## The RSS feed is not in this change, deliberately

#35 asks to "enable the RSS plugin". **There is no RSS plugin to enable.**
mkdocs-material 9.5.49 ships `blog`, `group`, `info`, `offline`, `privacy`,
`search`, `social` and `tags`, and none of them generates a feed; Material's
built-in RSS is an Insiders feature. So a feed here means one of two things,
and both are decisions rather than details:

- **`mkdocs-rss-plugin`** — a third-party dependency, which under ADR-004's
  `checks.requirements-pins` means a version to keep in step in `flake.nix` as
  well as `requirements.txt`.
- **A hook**, like `redirects_hook.py` and `recent_posts_hook.py` — no
  dependency, and Atom is a small format, but it is code to own, and a feed
  that is subtly wrong is worse than one that is missing.

Either is defensible; picking one silently while doing something else is not.
`/atom.xml` stays `pending` with that as its reason, and the checker keeps it
visible on every run. Note that it cannot be closed with a redirect in any
case: an HTML meta-refresh stub handed to a feed reader is worse than a 404,
and `check_redirects.py` rejects an active rule on a non-HTML URL.

## Alternatives considered

**Dated paths under the blog, `/blog/2014/02/13/isotopy/`** — the plugin's
default. It matches neither legacy scheme, so it costs exactly the same
sixteen redirects, and adds a date to every future URL. Nothing recommends it
here.

**Root-level slugs, `/isotopy/`, reproducing Zola exactly.** This is the one
that deserved a real answer, because it would turn eight redirects into eight
`keep` rules — the URLs preserved outright, no hop at all.

It is not impossible, which is what a first reading of the plugin suggests.
`post_url_format` is joined onto `blog_dir`, so `"../{slug}"` escapes it, and
**it was tried**: posts built to `site/diaconescus-theorem/index.html`, at the
root, with the rest of the blog still under `/blog/`. The build then failed
exactly where it should have —

```
redirects.yml: /diaconescus-theorem/ would overwrite a page the site already
builds at that URL.
  The site serves /diaconescus-theorem/ itself, so this should be `keep: true`,
  not a redirect.
```

— which is the guard from #69 doing its job.

Rejected anyway, for two reasons:

1. **The root namespace is shared and still filling up.** Every future page
   name would have to be checked against every post slug, forever, and a
   collision is silent: two files claiming one output path, last writer wins.
   `/blog/` walls the growing set off from the fixed one. This is the reason
   that would still hold in five years.
2. **`../` escaping `blog_dir` is not a documented feature.** It works because
   the path is joined and then resolved, not because the plugin supports it.
   Building the site's URL space on that means a mkdocs-material upgrade can
   move every post at once. The version is pinned, so this is a smaller risk
   than the first — but it is a risk taken for a benefit that only applies to
   eight URLs, once.

**Redirecting `/blog/page/2/` to the blog index** — works today, and starts
failing the build the moment #13 lands enough posts for a real page 2. Leaving
it pending is the honest state, and the pending reason says what unblocks it.

**A single taxonomy.** Categories alone would be simpler. But the milestone's
exit criterion names both, and they do different work: three categories that
are the blog's subjects and get real pages, against free keywords that get an
anchor. The risk is drift — two vocabularies for one purpose — which is what
the allow-list on one and not the other is there to prevent.

## Front matter

```yaml
---
title: Congruences of Partial Algebras   # editorial; may change
slug: congruences-of-partial-algebras    # the URL; should not
date: 2017-04-06
categories:                              # from the allow-list in mkdocs.yml
  - Mathematics
tags:                                    # free keywords
  - universal algebra
  - lattice theory
description: >-                          # the meta description
  ...
draft: true                              # optional; local only, never deploys
---
```

`draft` is verified in both directions rather than assumed: with the deploy
configuration a draft post produces no page and does not appear in the home
page's recent-writing list; with drafts enabled — which is what
`draft_on_serve` does during `mkdocs serve` — the same file builds at its URL
and appears in that list.

M6-2 (#36) turns this schema into `make post` and owns the rest of the
authoring workflow.

## Consequences

- **#13 (M2-4) can convert the six remaining posts without deciding anything.**
  Each one is a file in `docs/blog/posts/`, a `slug:` matching its Zola URL,
  and two `pending:` lines in `redirects.yml` becoming `to:`. The targets are
  written down there already.
- **A post's URL survives retitling** and does not survive a slug change; the
  redirect map points at source paths, so a slug change is picked up
  automatically and cannot leave a stub pointing at nothing.
- **`/blog/page/2/` becomes `keep: true`** once there is a second page.
- **The feed is an open decision**, tracked at `/atom.xml` in `redirects.yml`
  and here.
- **Nothing here is expensive to reverse.** The scheme is one line in
  `mkdocs.yml` and a `to:`/`keep:` flip per legacy URL, and both the checker
  and the build refuse to let the two disagree.
