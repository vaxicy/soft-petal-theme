#!/usr/bin/env python3
"""Generate the Soft Petal Theme icon (128x128 PNG).

Minimal flat design: warm cream rounded square with a simple abstract
flower petal symbol. No text, no letters, no complicated details.
"""
import math
import os
from PIL import Image, ImageDraw

SIZE = 128
BG = (249, 245, 246)          # warm cream white (toolbar)
PETAL = (242, 190, 209)       # accent pink
PETAL_SOFT = (253, 206, 223)  # active-tab pink
PETAL_DEEP = (210, 138, 168)  # hover/deep pink
RADIUS = 28


def _petal(d, cx, cy, r, angle_deg, fill, outline=None):
    """Draw a single rounded petal pointing outward at angle_deg (0=right)."""
    a = math.radians(angle_deg)
    dx, dy = math.cos(a), math.sin(a)
    tip = (cx + dx * r * 1.7, cy + dy * r * 1.7)
    px, py = -dy, dx
    c1 = (cx + dx * r * 0.55 + px * r * 0.95, cy + dy * r * 0.55 + py * r * 0.95)
    c2 = (cx + dx * r * 0.55 - px * r * 0.95, cy + dy * r * 0.55 - py * r * 0.95)
    base_w = r * 0.6
    b1 = (cx + px * base_w, cy + py * base_w)
    b2 = (cx - px * base_w, cy - py * base_w)
    d.polygon([b1, c1, tip, c2, b2], fill=fill, outline=outline)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(here, "..", "store-assets")
    os.makedirs(out_dir, exist_ok=True)

    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Cream rounded-square background
    draw.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=RADIUS, fill=BG)

    cx, cy = SIZE // 2, SIZE // 2 - 2

    # Soft outer ring of petals (lighter pink) for depth
    outer = [i * 72 for i in range(5)]
    for ang in outer:
        _petal(draw, cx, cy, 19, ang, PETAL_SOFT, outline=(235, 195, 215))

    # Inner petals (accent pink)
    inner = [i * 72 + 36 for i in range(5)]
    for ang in inner:
        _petal(draw, cx, cy, 13, ang, PETAL, outline=PETAL_DEEP)

    # Center core
    draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=PETAL_DEEP)
    draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=PETAL_SOFT)

    out_path = os.path.join(out_dir, "icon.png")
    img.save(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
