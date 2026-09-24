#!/usr/bin/env python3
"""Bakes the Quick Settings tile icon out of the dictionary's own mark.

WHY NOT JUST POINT THE TILE AT A MIPMAP: the adaptive launcher icon's foreground is drawn inside
the mask's safe zone — the mark itself occupies ~39% of the canvas — so using it directly for a
tile renders a mark a third of the size the shade expects. A tile wants the glyph, cropped to its
own bounds, at the density it will be drawn at (24dp).

SOURCE: dict-app's own monochrome launcher foreground (mipmap-*/ic_launcher_monochrome.png), which
is the pāli mark in a single flat colour with alpha — exactly what SystemUI tints. It is the same
shape the launcher icon shows, so the tile and the app icon can never drift apart.

USAGE:
    python3 scripts/make-dict-tile-icon.py           # writes drawable-*/ic_tile.png
    python3 scripts/make-dict-tile-icon.py --check   # fails if a baked PNG is stale
"""

import argparse
import os
import sys

from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SOURCE = os.path.join(ROOT, "dict-app", "src", "main", "res", "mipmap-xxxhdpi",
                      "ic_launcher_monochrome.png")
OUT_DIR = os.path.join(ROOT, "dict-app", "src", "main", "res")

# 24dp, the size SystemUI draws a tile icon at, per density bucket.
DENSITIES = {"mdpi": 24, "hdpi": 36, "xhdpi": 48, "xxhdpi": 72, "xxxhdpi": 96}

# A hair of breathing room: the glyph is a wide mark with thin strokes, and a tile draws it inside a
# circle, so the corners of the square are never seen.
MARGIN = 0.06


def bake():
    image = Image.open(SOURCE).convert("RGBA")
    box = image.split()[3].getbbox()
    if box:
        image = image.crop(box)

    out = {}
    for density, size in DENSITIES.items():
        inner = int(round(size * (1 - 2 * MARGIN)))
        scale = min(inner / image.width, inner / image.height)
        target = (max(1, int(round(image.width * scale))),
                  max(1, int(round(image.height * scale))))
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        resized = image.resize(target, Image.LANCZOS)
        canvas.paste(resized, ((size - target[0]) // 2, (size - target[1]) // 2), resized)
        out[os.path.join(OUT_DIR, "drawable-%s" % density, "ic_tile.png")] = canvas
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="fail if a baked PNG differs from what this script would write")
    args = parser.parse_args()

    if not os.path.exists(SOURCE):
        print("source mark not found: %s" % SOURCE, file=sys.stderr)
        return 1

    stale = False
    for path, canvas in bake().items():
        if args.check:
            if not os.path.exists(path):
                print("missing: %s" % path, file=sys.stderr)
                stale = True
                continue
            current = Image.open(path).convert("RGBA")
            if current.size != canvas.size or current.tobytes() != canvas.tobytes():
                print("stale: %s (run without --check)" % path, file=sys.stderr)
                stale = True
            continue

        os.makedirs(os.path.dirname(path), exist_ok=True)
        canvas.save(path, optimize=True)
        print("wrote %s (%dx%d)" % (path, canvas.width, canvas.height))
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
