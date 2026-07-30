"""Prove the native dependency chain the Material `social` plugin needs.

Run by `checks.native-deps` in flake.nix.  The plugin (M3-5) rasterises Open
Graph cards through CairoSVG and Pillow, which reach libcairo, Pango,
FreeType and fontconfig at run time rather than link time.  That is the
dependency the pip path cannot pin and this flake exists to pin, so it is
worth an assertion rather than an assumption.

Expects SOCIAL_CHECK_FONT to name a TrueType file, resolved through
fontconfig by the caller.
"""

import io
import os
import sys

import cairosvg
from PIL import Image, ImageDraw, ImageFont

SVG = b"""<svg xmlns="http://www.w3.org/2000/svg" width="240" height="60">
  <rect width="240" height="60" fill="#111111"/>
  <text x="12" y="38" font-family="Roboto" font-size="24" fill="#ffffff">
    William DeMeo
  </text>
</svg>"""


def check_cairosvg() -> None:
    """CairoSVG renders text: libcairo plus the font stack behind it."""
    png = cairosvg.svg2png(bytestring=SVG, output_width=480, output_height=120)
    image = Image.open(io.BytesIO(png))

    if image.size != (480, 120):
        sys.exit(f"cairosvg produced {image.size}, expected (480, 120)")

    # A canvas with no glyphs on it is two colours -- the fill and the
    # background -- so shade count is what distinguishes "rendered the text"
    # from "silently dropped it for want of a font".
    shades = image.convert("L").getcolors(maxcolors=256)
    if shades is None or len(shades) < 3:
        sys.exit(
            "cairosvg rendered no antialiased glyphs: "
            f"{None if shades is None else len(shades)} shades in the output"
        )

    print(f"cairosvg: rendered text in {len(shades)} shades of grey")


def check_pillow(font_path: str) -> None:
    """Pillow loads a TrueType face and measures it: FreeType is wired up."""
    font = ImageFont.truetype(font_path, 28)

    image = Image.new("RGB", (320, 60), "#111111")
    draw = ImageDraw.Draw(image)
    draw.text((12, 12), "William DeMeo", font=font, fill="#ffffff")

    width = draw.textlength("William DeMeo", font=font)
    if width <= 0:
        sys.exit(f"pillow measured a zero-width string with {font_path}")

    print(f"pillow: {font.getname()} measured {width:.1f}px")


def check_plugin_imports() -> None:
    """The plugin's own import graph resolves in this environment."""
    import material.plugins.social.plugin  # noqa: F401

    print("mkdocs-material: material.plugins.social.plugin imports")


def main() -> None:
    font_path = os.environ.get("SOCIAL_CHECK_FONT")
    if not font_path or not os.path.isfile(font_path):
        sys.exit(f"SOCIAL_CHECK_FONT does not name a file: {font_path!r}")

    check_cairosvg()
    check_pillow(font_path)
    check_plugin_imports()


if __name__ == "__main__":
    main()
