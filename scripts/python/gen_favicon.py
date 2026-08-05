#!/usr/bin/env python3
"""Generate the site's mark: header/card logo, favicon, apple-touch icon.

The mark is the five-element fence poset drawn as a constellation -- the
zigzag W that alternates minimal and maximal elements.  It earns its place
the same way the hero's N₅, M₃, 𝟚³ and L₇ do: it is a real order-theoretic
object, not a decoration that happens to look mathematical, and it is also
the site owner's initial.  Five stars and four edges survive a 16px favicon,
which none of the hero's lattices would.

One STARS table is the single source of truth; everything below is derived
from it, so the header logo, the social-card logo and the favicon cannot
drift apart.  Four files are written:

  overrides/.icons/constellation-w.svg
      Referenced by `theme.icon.logo` in mkdocs.yml, which puts it in the
      site header and on every social card (the social plugin resolves
      custom icons from overrides/.icons/).  Deliberately monochrome and
      built from *filled* shapes only -- no strokes: the header colours it
      with CSS `currentColor`, and the social plugin tints it by writing a
      `fill` attribute onto the <svg> root, neither of which reaches a
      stroke.  The edges carry their opacity as their own attribute, which
      both consumers respect.

  docs/assets/favicon.svg, docs/assets/favicon.png
      The tab icon: the mark on a rounded badge of the dark scheme's page
      background with a hairline border.  The badge is what makes it read
      on both light and dark browser chrome -- it brings its own contrast
      instead of depending on whatever is behind it.  SVG for the browsers
      that take one, PNG (32px) for the rest; overrides/main.html emits the
      links.

  docs/assets/apple-touch-icon.png
      180px, full bleed, no rounded corners and no border: iOS applies its
      own mask, so baked-in corners render as dark notches inside it.

Colours are the Constellation dark-scheme tokens (tokens.css): stars in
--c-accent #8b88ff over --c-bg #0c0e1d, border in --c-line-strong #333757.
The one departure is the edges, at accent 0.5 rather than the page's faint
#333757 lines: at 16px the connecting lines are the only thing that makes
the W read as a W, and at hairline contrast they vanish.

Everything is committed, so neither the site build nor CI runs this; the
favicon flake check runs `--check` to keep the committed bytes honest, the
same bargain gen_cv.py --check makes for the PDF.  Rendering needs cairosvg
(and Pillow to downscale), which the dev shell and the flake's pythonEnv
already carry for the social plugin.  Byte-stability across Cairo versions
is not promised; regenerate from the dev shell, where the flake pins Cairo.
"""
from __future__ import annotations

import argparse
import io
import math
import sys
from pathlib import Path

try:
    import cairosvg
    from PIL import Image
except ImportError:
    sys.exit("error: cairosvg and Pillow are required.\n"
             "       Use the Nix dev shell, or pip install cairosvg pillow.")

ROOT = Path(__file__).resolve().parents[2]

# ── the mark ────────────────────────────────────────────────────────────────
#
# A 24-unit grid, y down, like Material's own icons.  The fence's covering
# pairs are consecutive entries; the geometry is slightly irregular on
# purpose, because the hero's constellations are star charts, not diagrams.
# The middle maximal element is the brightest star, same gesture as L₇'s
# twinkler.

STARS = [  # (x, y, radius)
    (2.8, 8.0, 1.70),
    (7.4, 17.6, 1.55),
    (12.0, 6.2, 1.90),
    (16.8, 18.2, 1.55),
    (21.2, 7.4, 1.70),
]
EDGE_W = 1.0        # edge thickness on the 24 grid
EDGE_OPACITY = 0.5
HALO = 2.5          # halo radius as a multiple of the star's

BG = "#0c0e1d"      # --c-bg, dark scheme
ACCENT = "#8b88ff"  # --c-accent, dark scheme
BORDER = "#333757"  # --c-line-strong, dark scheme


def edge_path(p1, p2, w=EDGE_W) -> str:
    """A filled quadrilateral standing in for a stroked line.

    The icon must survive being coloured through a `fill` attribute alone
    (see the module docstring), so edges cannot be strokes.
    """
    (x1, y1), (x2, y2) = p1, p2
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    nx, ny = -dy / length * w / 2, dx / length * w / 2
    pts = [(x1 + nx, y1 + ny), (x2 + nx, y2 + ny),
           (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)]
    return "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + "Z"


def mark(halos: bool, star_fill: str | None = None, edge_fill: str | None = None) -> str:
    """The fence on the 24 grid.  With fills of None, colour is inherited."""
    sf = f' fill="{star_fill}"' if star_fill else ""
    ef = f' fill="{edge_fill}"' if edge_fill else ""
    parts = [f'<g opacity="{EDGE_OPACITY}"{ef}>']
    for (x1, y1, _), (x2, y2, _) in zip(STARS, STARS[1:]):
        parts.append(f'<path d="{edge_path((x1, y1), (x2, y2))}"/>')
    parts.append("</g>")
    if halos:
        parts.append(f'<g opacity="0.14"{sf}>')
        for x, y, r in STARS:
            parts.append(f'<circle cx="{x}" cy="{y}" r="{r * HALO:.2f}"/>')
        parts.append("</g>")
    parts.append(f"<g{sf}>")
    for x, y, r in STARS:
        parts.append(f'<circle cx="{x}" cy="{y}" r="{r}"/>')
    parts.append("</g>")
    return "".join(parts)


def icon_svg() -> str:
    """The monochrome logo for the header and the social card."""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            + mark(halos=False) + "</svg>\n")


def badge_svg(rounded: bool, scale: float, size: float = 64) -> str:
    """The mark on its own background, centred on a size-unit canvas."""
    inset = 1.25
    corner = f' rx="{size * 0.22:.1f}"' if rounded else ""
    border = (f' stroke="{BORDER}" stroke-width="2.5"' if rounded else "")
    off = size / 2 - 12 * scale
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">'
        f'<rect x="{inset}" y="{inset}" width="{size - 2 * inset}" '
        f'height="{size - 2 * inset}"{corner} fill="{BG}"{border}/>'
        f'<g transform="translate({off:.2f} {off:.2f}) scale({scale})">'
        + mark(halos=True, star_fill=ACCENT, edge_fill=ACCENT)
        + "</g></svg>\n"
    )


def png(svg: str, pixels: int) -> bytes:
    """Rasterise at 4x and let Pillow downscale: Cairo antialiases a hairline
    at 16-32px more coarsely than a supersampled reduction does."""
    raw = cairosvg.svg2png(bytestring=svg.encode(), output_width=pixels * 4,
                           output_height=pixels * 4)
    image = Image.open(io.BytesIO(raw)).resize((pixels, pixels), Image.LANCZOS)
    out = io.BytesIO()
    image.save(out, format="PNG", optimize=True)
    return out.getvalue()


OUTPUTS: list[tuple[Path, "callable"]] = [
    (ROOT / "overrides" / ".icons" / "constellation-w.svg",
     lambda: icon_svg().encode()),
    (ROOT / "docs" / "assets" / "favicon.svg",
     lambda: badge_svg(rounded=True, scale=2.2).encode()),
    (ROOT / "docs" / "assets" / "favicon.png",
     lambda: png(badge_svg(rounded=True, scale=2.2), 32)),
    (ROOT / "docs" / "assets" / "apple-touch-icon.png",
     lambda: png(badge_svg(rounded=False, scale=1.7), 180)),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="report what would change; write nothing")
    args = ap.parse_args()

    stale = []
    for path, render in OUTPUTS:
        blob = render()
        rel = path.relative_to(ROOT)
        if args.check:
            if not path.exists() or path.read_bytes() != blob:
                stale.append(str(rel))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(blob)
            print(f"wrote {rel} ({len(blob)} bytes)")

    if args.check:
        if stale:
            print("stale: " + ", ".join(stale))
            print("run `make favicon`")
            return 1
        print("favicon outputs up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
