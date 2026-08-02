"""Expand `<!-- recent-posts -->` into the most recent blog posts.

A hand-written "recent writing" list on the home page is wrong the moment a
post is published, and nothing catches it -- the links still resolve, they are
just the wrong links.  So the list is generated from the posts themselves.

## Why a hook and not a plugin

The same reasoning as `redirects_hook.py`: this is a few dozen lines against a
dependency to pin in both `requirements.txt` and `flake.nix` (ADR-004's
`checks.requirements-pins`).  Material's own "recent posts" component is an
Insiders feature and is not in the pinned 9.5.49.

## What it couples to

Only two things, both deliberately chosen to be the stable ones:

  * the blog plugin's *configuration* -- `blog_dir` and `post_dir`, read from
    the live config rather than hard-coded, so moving the posts directory
    moves this too;
  * `File.url`, which is MkDocs' public API.

It does not touch the plugin's internal post objects.  Because the blog plugin
rewrites each post's URL in `on_files` at priority -50, and because a link is
emitted as a *source path* for MkDocs to resolve (exactly as the tags plugin
does), the rewriting has happened by the time any `on_page_markdown` runs.

Drafts are excluded for free: the plugin sets their inclusion to EXCLUDED
during `on_files`, and `Files.documentation_pages()` filters on inclusion.  So
a draft is absent from this list on a build and present on `mkdocs serve`,
which is what `draft_on_serve` promises everywhere else.
"""

from __future__ import annotations

import logging

from babel.dates import format_date
from mkdocs.exceptions import PluginError
from mkdocs.plugins import event_priority
from mkdocs.utils import get_relative_url, meta

log = logging.getLogger("mkdocs.plugins.recent_posts")

#: What to replace.  The comment form is Material's own convention for this
#: kind of marker (`<!-- material/tags -->`), and it renders as nothing if this
#: hook is ever removed, rather than as stray text on the page.
MARKER = "<!-- recent-posts -->"

#: How many posts the list shows.
LIMIT = 3


def _blog_config(config):
    """The blog plugin's config, whichever name it was enabled under.

    MkDocs keys `config.plugins` by the name written in `mkdocs.yml`, and
    Material's plugins can be named either way round -- `blog` resolves
    through the theme namespace to `material/blog`.
    """
    for name in ("blog", "material/blog"):
        plugin = config.plugins.get(name)
        if plugin is not None:
            return plugin.config
    raise PluginError(
        f"{MARKER} needs the blog plugin, which is not enabled in mkdocs.yml."
    )


def _posts(files, config):
    """Every published post, newest first, as (date, title, File)."""
    blog = _blog_config(config)
    post_dir = blog.post_dir.format(blog=blog.blog_dir).strip("/") + "/"

    found = []
    for file in files.documentation_pages():
        if not file.src_uri.startswith(post_dir):
            continue
        with open(file.abs_src_path, encoding="utf-8") as fh:
            _, front = meta.get_data(fh.read())

        date = front.get("date")
        # Material accepts both `date: 2014-02-05` and the nested form with
        # `created:`; a post with neither is a post the blog plugin would have
        # rejected already, so this is a belt-and-braces error rather than a
        # reachable one.
        if isinstance(date, dict):
            date = date.get("created")
        if date is None or "title" not in front:
            raise PluginError(
                f"{file.src_uri}: a post needs both `title` and `date` in its "
                f"front matter for {MARKER} to list it."
            )
        found.append((date, str(front["title"]), file))

    found.sort(key=lambda item: item[0], reverse=True)
    return found


def _render(posts, page, config):
    """A Markdown list, linking by source path so MkDocs resolves the URL.

    Linking to `blog/posts/<file>.md` rather than to the post's built URL is
    what keeps `--strict` link validation meaningful: MkDocs checks the target
    exists and rewrites it to `/blog/<slug>/` itself.
    """
    locale = config.theme["language"].replace("-", "_")
    lines = []
    for date, title, file in posts:
        href = get_relative_url(file.src_uri, page.file.src_uri)
        when = format_date(date, format="long", locale=locale)
        lines.append(f"- [{title}]({href}) &middot; {when}")
    return "\n".join(lines)


# After the blog plugin's own -50 handlers, for no reason other than that a
# marker expanded before the plugin has had its say would be a subtle bug to
# find later.  The URLs this needs are already final by `on_files`.
@event_priority(-100)
def on_page_markdown(markdown, *, page, config, files):
    if MARKER not in markdown:
        return None

    posts = _posts(files, config)[:LIMIT]
    if not posts:
        # Reachable exactly once, before the first post is published, and
        # while every post in the tree is a draft.  Neither is a build error.
        log.info("%s: no published posts to list on %s", MARKER, page.file.src_uri)
        return markdown.replace(MARKER, "*Nothing published yet.*")

    return markdown.replace(MARKER, _render(posts, page, config))
