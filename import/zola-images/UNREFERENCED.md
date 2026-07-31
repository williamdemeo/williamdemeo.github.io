# Images not imported

333 of 350 files under the Zola repository's `static/images/` are not referenced by any imported content page and were deliberately not imported: theme furniture (pager arrows, toggle sprites, social icons, tile backgrounds, login graphics) and large unused photographs.

They remain in the GitLab repository, which stays public as the archive of its own history (ADR-001). Recover any of them from there rather than re-importing the directory wholesale -- committing 46 MB of unused assets would permanently bloat this repository's history, which is the cost M1-2 just finished paying down.
