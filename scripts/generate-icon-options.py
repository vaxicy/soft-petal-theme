#!/usr/bin/env python3
"""Generate alternative Soft Petal Theme icon proposals.

Outputs 128x128 PNG options and a preview grid. All designs use the theme
palette and avoid text/letters.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

SIZE = 512          # internal design size for anti-aliasing
OUT = 128           # final icon size
RADIUS = 112        # rounded-square corner radius @ SIZE
BG = (249, 245, 246)
SOFT = (253, 206, 223)
ACCENT = (242, 190, 209)
DEEP = (210, 138, 168)
TEXT = (107, 88, 96)


def canvas():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=RADIUS, fill=BG)
    return img


def ellipse_rot(img, cx, cy, w, h, angle_deg, fill):
    """Draw a rotated ellipse onto img using a temporary buffer."""
    pad = max(w, h) + 40
    tmp = Image.new("RGBA", (pad, pad), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.ellipse([(pad - w) // 2, (pad - h) // 2,
                (pad + w) // 2, (pad + h) // 2], fill=fill)
    if angle_deg != 0:
        tmp = tmp.rotate(angle_deg, resample=Image.BICUBIC, expand=False)
    off = (pad - SIZE) // 2
    img.paste(tmp, (cx - pad // 2, cy - pad // 2), tmp)


def save(img, path):
    img.resize((OUT, OUT), Image.LANCZOS).save(path)


def option_single_petal():
    """One gentle vertical petal with a soft highlight."""
    img = canvas()
    cx, cy = SIZE // 2, SIZE // 2 + 10
    ellipse_rot(img, cx, cy, 130, 330, 0, DEEP)
    ellipse_rot(img, cx, cy - 20, 90, 260, 0, ACCENT)
    ellipse_rot(img, cx, cy - 55, 45, 110, 0, SOFT)
    return img


def option_five_petals():
    """Open five-petal flower."""
    img = canvas()
    cx, cy = SIZE // 2, SIZE // 2
    n = 5
    for i in range(n):
        ang = i * 360 / n
        dx = math.cos(math.radians(ang - 90)) * 75
        dy = math.sin(math.radians(ang - 90)) * 75
        ellipse_rot(img, int(cx + dx), int(cy + dy), 105, 210, ang, SOFT)
    for i in range(n):
        ang = i * 360 / n
        dx = math.cos(math.radians(ang - 90)) * 60
        dy = math.sin(math.radians(ang - 90)) * 60
        ellipse_rot(img, int(cx + dx), int(cy + dy), 80, 170, ang, ACCENT)
    d = ImageDraw.Draw(img)
    r = 45
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=DEEP)
    r = 22
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SOFT)
    return img


def option_sakura():
    """Sakura / cherry blossom with five rounded petals."""
    img = canvas()
    cx, cy = SIZE // 2, SIZE // 2 + 6
    n = 5
    for i in range(n):
        ang = i * 360 / n
        dx = math.cos(math.radians(ang - 90)) * 70
        dy = math.sin(math.radians(ang - 90)) * 70
        ellipse_rot(img, int(cx + dx), int(cy + dy), 110, 190, ang, SOFT)
    for i in range(n):
        ang = i * 360 / n
        dx = math.cos(math.radians(ang - 90)) * 55
        dy = math.sin(math.radians(ang - 90)) * 55
        ellipse_rot(img, int(cx + dx), int(cy + dy), 85, 150, ang, ACCENT)
    # small notches between petals to suggest heart-shaped petals
    for i in range(n):
        ang = i * 360 / n + 36
        dx = math.cos(math.radians(ang - 90)) * 35
        dy = math.sin(math.radians(ang - 90)) * 35
        ellipse_rot(img, int(cx + dx), int(cy + dy), 22, 50, ang, BG)
    d = ImageDraw.Draw(img)
    r = 32
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=DEEP)
    r = 14
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SOFT)
    return img


def option_tulip():
    """Minimal tulip / bud shape made of three petals."""
    img = canvas()
    cx, cy = SIZE // 2, SIZE // 2 + 35
    # left petal
    ellipse_rot(img, cx - 55, cy - 30, 95, 240, -20, SOFT)
    ellipse_rot(img, cx - 55, cy - 20, 70, 190, -20, ACCENT)
    # right petal
    ellipse_rot(img, cx + 55, cy - 30, 95, 240, 20, SOFT)
    ellipse_rot(img, cx + 55, cy - 20, 70, 190, 20, ACCENT)
    # center petal
    ellipse_rot(img, cx, cy - 55, 85, 230, 0, DEEP)
    ellipse_rot(img, cx, cy - 45, 55, 170, 0, ACCENT)
    return img


def option_abstract_seed():
    """Abstract seed / swirl."""
    img = canvas()
    cx, cy = SIZE // 2, SIZE // 2
    d = ImageDraw.Draw(img)
    rings = [(210, SOFT), (165, ACCENT), (120, DEEP), (75, SOFT)]
    for r, col in rings:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    # asymmetric seed dot
    ellipse_rot(img, cx + 18, cy - 18, 55, 85, 45, TEXT + (200,))
    return img


def preview_grid(imgs, labels):
    n = len(imgs)
    gap = 48
    label_h = 64
    cell = OUT
    w = n * cell + (n + 1) * gap
    h = gap + cell + gap + label_h + gap
    bg = (255, 255, 255)
    grid = Image.new("RGBA", (w, h), bg)
    d = ImageDraw.Draw(grid)
    font = None
    for font_path in [r"C:\Windows\Fonts\msyh.ttc",
                      r"C:\Windows\Fonts\msyhbd.ttc",
                      r"C:\Windows\Fonts\simhei.ttf",
                      "arial.ttf"]:
        try:
            font = ImageFont.truetype(font_path, 22)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()
    for i, (img, label) in enumerate(zip(imgs, labels)):
        x = gap + i * (cell + gap)
        y = gap
        # subtle shadow
        shadow = Image.new("RGBA", (cell + 8, cell + 8), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rounded_rectangle([4, 4, cell + 4, cell + 4], radius=28,
                             fill=(0, 0, 0, 30))
        grid.paste(shadow, (x - 2, y - 2), shadow)
        grid.paste(img, (x, y), img)
        bbox = d.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0]
        d.text((x + (cell - tw) // 2, y + cell + 16), label, fill=TEXT, font=font)
    return grid


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(here, "..", "store-assets", "icon-options")
    os.makedirs(out_dir, exist_ok=True)

    makers = [
        (option_single_petal, "A · 单瓣"),
        (option_five_petals, "B · 五花"),
        (option_sakura, "C · 樱花"),
        (option_tulip, "D · 郁金香"),
        (option_abstract_seed, "E · 种子"),
    ]

    imgs128 = []
    paths = []
    for idx, (fn, label) in enumerate(makers, start=1):
        img = fn()
        path = os.path.join(out_dir, f"icon-option-{idx}.png")
        save(img, path)
        paths.append(path)
        imgs128.append(img.resize((OUT, OUT), Image.LANCZOS))
        print(f"Saved {path}")

    grid = preview_grid(imgs128, [m[1] for m in makers])
    grid_path = os.path.join(out_dir, "preview-all.png")
    grid.save(grid_path)
    print(f"Saved {grid_path}")


if __name__ == "__main__":
    main()
