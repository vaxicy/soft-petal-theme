#!/usr/bin/env python3
"""Generate English Chrome Web Store promo tiles for Soft Petal theme.

Outputs:
  store-assets/promo/440x280.png
  store-assets/promo/1400x560.png

Rules followed:
- All text in English (Chrome theme store assets are English-only).
- Scale-aware font sizes: smaller canvas gets proportionally smaller type.
- Title/subtitle gap >= 8 px.
- Subtitle baseline < bottom frame - 14 px.
- CTA button text vertically centered; button bottom < canvas height - 12 px.
- No overlapping blocks; generous padding.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(ROOT, "..", "store-assets", "promo")
ICON_PATH = os.path.join(ROOT, "..", "store-assets", "icon.png")
os.makedirs(OUT_DIR, exist_ok=True)

# Soft Petal palette
CREAM = (249, 245, 246)
BLUSH = (248, 232, 238)
PETAL = (242, 190, 209)
PETAL_SOFT = (253, 206, 223)
PETAL_DEEP = (210, 138, 168)
TEXT = (107, 88, 96)
TEXT_LIGHT = (156, 138, 146)


def _get_font(size, bold=False):
    """Load a system font or fall back to PIL default."""
    candidates = []
    if bold:
        candidates = [
            r"C:\Windows\Fonts\segoeuib.ttf",
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\verdanab.ttf",
        ]
    else:
        candidates = [
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\verdana.ttf",
        ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _petal(d, cx, cy, r, angle_deg, fill, outline=None):
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


def _draw_flower(d, cx, cy, r):
    for ang in [i * 72 for i in range(5)]:
        _petal(d, cx, cy, r, ang, PETAL_SOFT, outline=(235, 195, 215))
    for ang in [i * 72 + 36 for i in range(5)]:
        _petal(d, cx, cy, r * 0.68, ang, PETAL, outline=PETAL_DEEP)
    d.ellipse([cx - r * 0.47, cy - r * 0.47, cx + r * 0.47, cy + r * 0.47], fill=PETAL_DEEP)
    d.ellipse([cx - r * 0.26, cy - r * 0.26, cx + r * 0.26, cy + r * 0.26], fill=PETAL_SOFT)


def _paste_logo(img, cx, cy, size):
    """Paste the theme icon onto the promo canvas, centered at (cx, cy)."""
    logo = Image.open(ICON_PATH).convert("RGBA")
    logo = logo.resize((size, size), Image.Resampling.LANCZOS)
    x = cx - size // 2
    y = cy - size // 2
    img.paste(logo, (x, y), logo)


def _text_size(d, text, font):
    bbox = d.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def generate_440x280():
    w, h = 440, 280
    img = Image.new("RGB", (w, h), CREAM)
    d = ImageDraw.Draw(img)

    # Decorative blush frame band at top
    d.rectangle([0, 0, w, 8], fill=BLUSH)

    # Logo decoration, right side vertically centered
    _paste_logo(img, w - 70, h // 2, 70)

    # Title
    title_font = _get_font(38, bold=True)
    title = "Soft Petal"
    tw, th = _text_size(d, title, title_font)
    title_x = 36
    title_y = 70
    d.text((title_x, title_y), title, font=title_font, fill=TEXT)

    # Subtitle, increased gap below title
    sub_font = _get_font(17)
    sub = "A calm Chrome theme"
    _, sh = _text_size(d, sub, sub_font)
    sub_y = title_y + th + 18
    d.text((title_x, sub_y), sub, font=sub_font, fill=TEXT_LIGHT)

    # Feature chips
    chip_font = _get_font(12)
    chips = ["No wallpaper", "Pure color", "Soft & clean"]
    chip_y = sub_y + sh + 20
    chip_x = title_x
    chip_h = 24
    for chip in chips:
        cw, _ = _text_size(d, chip, chip_font)
        pad = 10
        d.rounded_rectangle(
            [chip_x, chip_y, chip_x + cw + pad * 2, chip_y + chip_h],
            radius=chip_h // 2,
            fill=BLUSH,
            outline=PETAL,
        )
        d.text((chip_x + pad, chip_y + 5), chip, font=chip_font, fill=TEXT)
        chip_x += cw + pad * 2 + 8

    # Bottom safety check: last chip bottom < h - 12
    assert chip_y + chip_h < h - 12, "Bottom overflow on 440x280"

    out = os.path.join(OUT_DIR, "440x280.png")
    img.save(out)
    print(f"Saved {out}")
    return out


def _draw_browser_mock(d, x, y, bw, bh):
    """Draw a simplified Chrome browser window filled with theme colors."""
    r = 10
    # Window shadow
    d.rounded_rectangle([x + 4, y + 4, x + bw, y + bh], radius=r, fill=(230, 220, 225))
    # Window frame
    d.rounded_rectangle([x, y, x + bw - 4, y + bh - 4], radius=r, fill=BLUSH)
    # Toolbar
    d.rounded_rectangle([x, y, x + bw - 4, y + 56], radius=r, fill=CREAM)
    d.rectangle([x, y + 40, x + bw - 4, y + 56], fill=CREAM)
    # Omnibox
    d.rounded_rectangle([x + 86, y + 14, x + bw - 92, y + 38], radius=12, fill=(255, 255, 255), outline=PETAL)
    # Tab
    d.rounded_rectangle([x + 14, y + 10, x + 74, y + 40], radius=8, fill=PETAL_SOFT)
    # Toolbar buttons
    d.ellipse([x + bw - 66, y + 18, x + bw - 50, y + 34], fill=PETAL)
    d.ellipse([x + bw - 84, y + 18, x + bw - 68, y + 34], fill=PETAL_SOFT)
    # Content area
    d.rounded_rectangle([x + 8, y + 60, x + bw - 12, y + bh - 12], radius=8, fill=CREAM)
    # Content lines
    line_color = (235, 220, 228)
    for i in range(5):
        ly = y + 86 + i * 28
        lw = bw - 70 - (i % 2) * 80
        d.rounded_rectangle([x + 24, ly, x + 24 + lw, ly + 14], radius=7, fill=line_color)


def generate_1400x560():
    w, h = 1400, 560
    img = Image.new("RGB", (w, h), CREAM)
    d = ImageDraw.Draw(img)

    # Text block: left-center
    title_font = _get_font(74, bold=True)
    title = "Soft Petal"
    tw, th = _text_size(d, title, title_font)
    title_x = 380
    title_y = 130
    d.text((title_x, title_y), title, font=title_font, fill=TEXT)

    sub_font = _get_font(30)
    sub = "A calm and elegant Chrome theme"
    _, sh = _text_size(d, sub, sub_font)
    sub_y = title_y + th + 28
    d.text((title_x, sub_y), sub, font=sub_font, fill=TEXT_LIGHT)

    # Feature bullets
    bullet_font = _get_font(20)
    bullets = [
        "Warm cream toolbar & soft petal accents",
        "No wallpaper, no gradients — pure color",
        "Designed for calm, everyday browsing",
    ]
    bullet_y = sub_y + sh + 34
    for bullet in bullets:
        d.text((title_x, bullet_y), "·  " + bullet, font=bullet_font, fill=TEXT)
        _, bh = _text_size(d, bullet, bullet_font)
        bullet_y += bh + 14

    # CTA button
    cta_font = _get_font(22, bold=True)
    cta = "Add to Chrome"
    cw, ch = _text_size(d, cta, cta_font)
    btn_w = cw + 52
    btn_h = 54
    btn_x = title_x
    btn_y = bullet_y + 20
    btn_r = btn_h // 2
    d.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=btn_r, fill=PETAL, outline=PETAL_DEEP)
    d.text((btn_x + (btn_w - cw) // 2, btn_y + (btn_h - ch) // 2 - 1), cta, font=cta_font, fill=(255, 255, 255))

    # Browser mockup on the right
    _draw_browser_mock(d, w - 500, 110, 480, 340)

    # Safety checks
    assert btn_y + btn_h < h - 12, "CTA bottom overflow on 1400x560"
    assert sub_y + sh < h - 14, "Subtitle baseline overflow on 1400x560"

    out = os.path.join(OUT_DIR, "1400x560.png")
    img.save(out)
    print(f"Saved {out}")
    return out


def main():
    generate_440x280()
    generate_1400x560()


if __name__ == "__main__":
    main()
