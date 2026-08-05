"""Seed the social plugin's font cache from the committed card faces.

The community-edition social plugin resolves a font family by listing
``<cache_dir>/fonts/<family>/`` and, when that directory does not exist,
downloading the family from fonts.google.com.  Nothing in this project may
fetch a font from another origin (#17), and the sandboxed Nix build could not
anyway -- so this hook copies the committed static TTFs from
``docs/assets/fonts/cards/`` into the cache before the plugin looks, and the
download path is never taken.  ``make fonts`` is what regenerates the TTFs;
see CARD_FACES in build_fonts.py for why their filenames are load-bearing.

An mkdocs hook rather than a shell step so that every way of building --
``make build``, ``mkdocs serve``, ``nix build`` -- seeds the cache the same
way; a seed done by the Makefile would be exactly the works-locally,
fails-in-CI split that checks.native-deps exists to prevent.

``on_config`` at high priority rather than ``on_startup``, for one reason:
``on_config`` receives the loaded configuration, so the destination comes
from the plugin's own ``cache_dir`` option instead of a hardcoded copy of its
default.  Priority 100 runs ahead of the plugin's default-priority
``on_config``, which is where it resolves fonts; mkdocs orders same-event
hooks by priority first, registration order second, so "hooks run after
plugins" only holds at equal priority and this is the documented way to get
ahead of one.
"""
from __future__ import annotations

import os
import shutil

from mkdocs.plugins import event_priority

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCE = os.path.join(ROOT, "docs", "assets", "fonts", "cards")


@event_priority(100)
def on_config(config):
    # The key is the resolved plugin name; mkdocs stores theme-provided
    # plugins under "<theme>/<name>" when mkdocs.yml says just "social".
    social = config.plugins.get("material/social") or config.plugins.get("social")
    if social is None or not social.config.enabled or not social.config.cards:
        return

    # A missing source directory falls through to copytree's FileNotFoundError
    # on purpose: the alternative is the plugin quietly downloading Roboto.
    dest = os.path.join(social.config.cache_dir, "fonts")
    for family in sorted(os.listdir(SOURCE)):
        src = os.path.join(SOURCE, family)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(dest, family), dirs_exist_ok=True)
