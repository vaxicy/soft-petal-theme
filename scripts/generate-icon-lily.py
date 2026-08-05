#!/usr/bin/env python3
"""Generate lily-inspired icon options for Soft Petal Theme.

Reference: pink lily with 6 recurved petals, visible stamens, soft gradients.
Drawn in code with PIL so they remain reproducible and scalable.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SIZE = 512          # internal design canvas
OUT = 128           # final icon size
RADIUS = 112        # rounded-square corner radius @ SIZE
BG = (249, 245, 246)
SOFT = (253, 206, 223)
ACCENT = (242, 190, 209)
DEEP = (210, 138, 168)
DARK = (176, 108, 140)
TEXT = (107, 88, 96)
CREAM = (255, 250, 252)
STAMEN = (245, 185, 95)
ANTHER = (220, 100, 90)


def canvas():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=RADIUS, fill=BG)
    return img


def save(img, path):
    img.resize((OUT, OUT), Image.LANCZOS).save(path)


def _rotated_ellipse(img, cx, cy, w, h, angle_deg, fill):
    """Draw a rotated ellipse onto img using a temporary buffer."""
    pad = max(w, h) + 40
    tmp = Image.new("RGBA", (pad, pad), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.ellipse([(pad - w) // 2, (pad - h) // 2,
                (pad + w) // 2, (pad + h) // 2], fill=fill)
    if angle_deg != 0:
        tmp = tmp.rotate(angle_deg, resample=Image.BICUBIC, expand=False)
    img.paste(tmp, (cx - pad // 2, cy - pad // 2), tmp)


def _radial_gradient(size, center, inner_color, outer_color, radius):
    """Create a radial gradient image."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cx, cy = size // 2, size // 2
    for y in range(size):
        for x in range(size):
            dx, dy = x - cx, y - cy
            dist = math.hypot(dx, dy) / radius
            if dist > 1:
                continue
            t = dist
            r = int(inner_color[0] * (1 - t) + outer_color[0] * t)
            g = int(inner_color[1] * (1 - t) + outer_color[1] * t)
            b = int(inner_color[2] * (1 - t) + outer_color[2] * t)
            a = int(inner_color[3] * (1 - t) + outer_color[3] * t) if len(inner_color) > 3 else 255
            img.putpixel((x, y), (r, g, b, a))
    return img


def _linear_gradient(size, color_top, color_bottom):
    """Create a vertical linear gradient image."""
    img = Image.new("RGBA", (1, size), color_top)
    for y in range(size):
        t = y / (size - 1)
        r = int(color_top[0] * (1 - t) + color_bottom[0] * t)
        g = int(color_top[1] * (1 - t) + color_bottom[1] * t)
        b = int(color_top[2] * (1 - t) + color_bottom[2] * t)
        img.putpixel((0, y), (r, g, b, 255))
    return img.resize((size, size), Image.BICUBIC)


def _draw_petal(img, cx, cy, length, width, angle_deg, fill,
                curl=0.0, highlight=False, vein=False):
    """Draw one lily petal as a curved shape.

    Args:
        curl: how much the tip curves outward (0..1)
        highlight: add a soft highlight stripe
        vein: add a darker central vein line
    """
    d = ImageDraw.Draw(img)
    a = math.radians(angle_deg)
    # base center
    bx = cx - math.cos(a) * length * 0.25
    by = cy - math.sin(a) * length * 0.25
    # tip
    tx = cx + math.cos(a) * length * 0.75
    ty = cy + math.sin(a) * length * 0.75
    # curl offset
    px, py = -math.sin(a), math.cos(a)
    curl_x = px * length * curl
    curl_y = py * length * curl
    # control points for bezier-like polygon
    hw = width * 0.5
    tip_left = (tx - px * hw * 0.4 + curl_x, ty - py * hw * 0.4 + curl_y)
    tip_right = (tx + px * hw * 0.4 + curl_x, ty + py * hw * 0.4 + curl_y)
    mid_left = (bx - px * hw * 0.9 + math.cos(a) * length * 0.25,
                by - py * hw * 0.9 + math.sin(a) * length * 0.25)
    mid_right = (bx + px * hw * 0.9 + math.cos(a) * length * 0.25,
                 by + py * hw * 0.9 + math.sin(a) * length * 0.25)
    base_left = (bx - px * hw * 0.6, by - py * hw * 0.6)
    base_right = (bx + px * hw * 0.6, by + py * hw * 0.6)

    pts = [base_left, mid_left, tip_left, (tx + curl_x, ty + curl_y),
           tip_right, mid_right, base_right]
    d.polygon(pts, fill=fill)

    # subtle highlight
    if highlight:
        hl = tuple(min(255, c + 22) for c in fill[:3]) + (180,)
        hl_pts = [
            base_left,
            mid_left,
            (tip_left[0] * 0.7 + tx * 0.3, tip_left[1] * 0.7 + ty * 0.3),
            (tx + curl_x, ty + curl_y),
        ]
        d.polygon(hl_pts, fill=hl)

    # central vein
    if vein:
        vn = DARK + (120,)
        vx1, vy1 = bx, by
        vx2, vy2 = tx + curl_x * 0.7, ty + curl_y * 0.7
        d.line([(vx1, vy1), (vx2, vy2)], fill=vn, width=2)


def _draw_stamen(img, cx, cy, angle_deg, length):
    """Draw a single stamen (filament + anther)."""
    d = ImageDraw.Draw(img)
    a = math.radians(angle_deg)
    x1 = cx + math.cos(a) * 12
    y1 = cy + math.sin(a) * 12
    x2 = cx + math.cos(a) * length
    y2 = cy + math.sin(a) * length
    d.line([(x1, y1), (x2, y2)], fill=STAMEN + (220,), width=3)
    # anther
    ax, ay = x2, y2
    _rotated_ellipse(img, int(ax), int(ay), 10, 18, angle_deg + 90, ANTHER + (230,))


def option_realistic_lily():
    """A: Realistic six-petal lily with stamens and veins."""
    img = canvas()
    cx, cy = SIZE // 2, SIZE // 2 + 8
    n = 6
    # outer petals (slightly lighter, behind)
    for i in range(n):
        ang = i * 360 / n - 90
        _draw_petal(img, cx, cy, 220, 92, ang, SOFT, curl=0.12,
                    highlight=True, vein=False)
    # inner petals (accent)
    for i in range(n):
        ang = i * 360 / n - 90 + 30  # offset half step for depth? No, lily is 6-fold
    # actually lily has 6 petals at same positions, draw second layer smaller
    for i in range(n):
        ang = i * 360 / n - 90
        _draw_petal(img, cx, cy, 190, 76, ang, ACCENT, curl=0.18,
                    highlight=True, vein=True)
    # deep shadows at base
    d = ImageDraw.Draw(img)
    d.ellipse([cx - 35, cy - 35, cx + 35, cy + 35], fill=DEEP + (160,))
    # stamens
    for i in range(6):
        ang = i * 60 + 15
        _draw_stamen(img, cx, cy, ang, 95)
    # pistil
    d.line([(cx, cy), (cx, cy - 55)], fill=STAMEN + (200,), width=4)
    _rotated_ellipse(img, cx, cy - 58, 10, 14, 0, (160, 120, 70, 200))
    return img


def option_flat_lily():
    """B: Flat, clean lily with 6 petals and simple stamens."""
    img = canvas()
    cx, cy = SIZE // 2, SIZE // 2 + 10
    n = 6
    for i in range(n):
        ang = i * 360 / n - 90
        # main petal
        _draw_petal(img, cx, cy, 205, 82, ang, ACCENT, curl=0.08)
        # inner tone
        _draw_petal(img, cx, cy, 155, 55, ang, SOFT, curl=0.08)
    # center
    d = ImageDraw.Draw(img)
    d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=DEEP)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=CREAM)
    # stamens as small dots
    for i in range(6):
        a = math.radians(i * 60 + 30)
        x = cx + math.cos(a) * 20
        y = cy + math.sin(a) * 20
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=STAMEN)
    return img


def option_profile_lily():
    """C: Single lily viewed from the side, elegant trumpet shape."""
    img = canvas()
    cx, cy = SIZE // 2, SIZE // 2 + 25
    d = ImageDraw.Draw(img)
    # Outer cup shape
    cup = [
        (cx - 110, cy + 90),
        (cx - 70, cy - 80),
        (cx - 30, cy - 150),
        (cx, cy - 165),
        (cx + 30, cy - 150),
        (cx + 70, cy - 80),
        (cx + 110, cy + 90),
        (cx + 60, cy + 60),
        (cx, cy + 80),
        (cx - 60, cy + 60),
    ]
    d.polygon(cup, fill=SOFT)
    # inner petals showing
    inner = [
        (cx - 60, cy + 50),
        (cx - 40, cy - 70),
        (cx - 10, cy - 110),
        (cx + 10, cy - 110),
        (cx + 40, cy - 70),
        (cx + 60, cy + 50),
        (cx, cy + 60),
    ]
    d.polygon(inner, fill=ACCENT)
    # center throat
    d.ellipse([cx - 35, cy - 35, cx + 35, cy + 35], fill=DEEP)
    d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=CREAM)
    # stamens poking out
    for ang in [-30, -10, 10, 30]:
        a = math.radians(ang - 90)
        x1, y1 = cx, cy
        x2 = cx + math.cos(a) * 85
        y2 = cy + math.sin(a) * 85
        d.line([(x1, y1), (x2, y2)], fill=STAMEN + (220,), width=3)
        _rotated_ellipse(img, int(x2), int(y2), 8, 14, ang, ANTHER + (230,))
    return img


def option_gradient_lily():
    """D: Soft gradient petals, watercolor-like."""
    img = canvas()
    cx, cy = SIZE // 2, SIZE // 2 + 5
    n = 6
    for i in range(n):
        ang = i * 360 / n - 90
        # build petal polygon points
        pts = []
        for t in range(-40, 41, 5):
            ra = math.radians(ang + t * 0.6)
            rr = 110 - abs(t) * 0.8
            pts.append((cx + math.cos(ra) * rr, cy + math.sin(ra) * rr))
        pts.append((cx, cy))
        # mask for this petal
        mask = Image.new("L", (SIZE, SIZE), 0)
        md = ImageDraw.Draw(mask)
        md.polygon(pts, fill=255)
        # gradient layer centered on full canvas
        grad_size = 280
        grad = _linear_gradient(grad_size, SOFT, DEEP)
        grad = grad.rotate(ang + 90, resample=Image.BICUBIC, expand=False)
        layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        gx = cx - grad.width // 2
        gy = cy - grad.height // 2
        layer.paste(grad, (gx, gy))
        # apply mask
        layer.putalpha(mask)
        img = Image.alpha_composite(img, layer)
    # center
    d = ImageDraw.Draw(img)
    d.ellipse([cx - 32, cy - 32, cx + 32, cy + 32], fill=CREAM)
    d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=SOFT)
    return img


def option_line_lily():
    """E: Minimal line-art lily."""
    img = canvas()
    cx, cy = SIZE // 2, SIZE // 2 + 8
    d = ImageDraw.Draw(img)
    n = 6
    line = DEEP
    for i in range(n):
        ang = i * 360 / n - 90
        a = math.radians(ang)
        # petal outline
        pts = []
        for t in range(-35, 36, 4):
            ra = math.radians(ang + t * 0.5)
            rr = 105 - abs(t) * 0.6
            pts.append((cx + math.cos(ra) * rr, cy + math.sin(ra) * rr))
        pts.append((cx, cy))
        d.polygon(pts, outline=line, fill=(0, 0, 0, 0))
        # vein
        d.line([(cx, cy),
                (cx + math.cos(a) * 95, cy + math.sin(a) * 95)],
               fill=line, width=2)
    # center
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], outline=line, width=3)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=line)
    return img


def option_ai_lily():
    """F: AI-generated lily illustration, post-processed to icon."""
    here = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(here, "..", "store-assets", "icon-options-v2",
                            "A_clean_top_view_icon_of_a_pin_2026-08-05T13-10-41.png")
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"AI lily source not found: {src_path}")
    src = Image.open(src_path).convert("RGBA")
    src = src.resize((OUT, OUT), Image.LANCZOS)

    # round corners to match theme icon shape
    mask = Image.new("L", (OUT, OUT), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, OUT - 1, OUT - 1], radius=28, fill=255)

    out = Image.new("RGBA", (OUT, OUT), (0, 0, 0, 0))
    out.paste(src, (0, 0), mask)
    return out


def preview_grid(imgs, labels):
    n = len(imgs)
    gap = 48
    label_h = 64
    cell = OUT
    w = n * cell + (n + 1) * gap
    h = gap + cell + gap + label_h + gap
    grid = Image.new("RGBA", (w, h), (255, 255, 255, 255))
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
    out_dir = os.path.join(here, "..", "store-assets", "icon-options-v2")
    os.makedirs(out_dir, exist_ok=True)

    makers = [
        (option_realistic_lily, "A · 写实百合"),
        (option_flat_lily, "B · 扁平百合"),
        (option_profile_lily, "C · 侧面百合"),
        (option_gradient_lily, "D · 渐变水彩"),
        (option_line_lily, "E · 线条百合"),
        (option_ai_lily, "F · AI 百合"),
    ]

    imgs128 = []
    for idx, (fn, label) in enumerate(makers, start=1):
        img = fn()
        path = os.path.join(out_dir, f"icon-lily-{idx}.png")
        save(img, path)
        imgs128.append(img.resize((OUT, OUT), Image.LANCZOS))
        print(f"Saved {path}")

    grid = preview_grid(imgs128, [m[1] for m in makers])
    grid_path = os.path.join(out_dir, "preview-lily.png")
    grid.save(grid_path)
    print(f"Saved {grid_path}")

    # F (AI lily) is the chosen official icon
    ai_icon = option_ai_lily()
    theme_icon = os.path.join(here, "..", "store-assets", "icon.png")
    ai_icon.save(theme_icon, "PNG")
    print(f"Published F as {theme_icon}")


if __name__ == "__main__":
    main()
