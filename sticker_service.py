"""
Sticker generation service that uses Claude-interpreted parameters
to customize the existing sticker generator.
"""

import os
import math
import random
from PIL import Image, ImageDraw, ImageFont

from claude_designer import StickerDesignParams

OUTPUT_DIR = "generated_stickers"
SIZE = 800
HALF = SIZE // 2


def get_font(size: int):
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    ]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def make_canvas():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))


def add_glow(img, center, radius, color, layers=8):
    glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    cx, cy = center
    r, g, b = color[:3]
    for i in range(layers, 0, -1):
        alpha = int(40 * (i / layers))
        expand = int(radius * 0.4 * (i / layers))
        d.ellipse(
            [cx - radius - expand, cy - radius - expand,
             cx + radius + expand, cy + radius + expand],
            fill=(r, g, b, alpha)
        )
    return Image.alpha_composite(img, glow)


def star_polygon(cx, cy, outer, inner, points):
    coords = []
    for i in range(points * 2):
        angle = math.pi / points * i - math.pi / 2
        r = outer if i % 2 == 0 else inner
        coords.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return coords


def centered_text(draw, text, y, font, fill, outline=None):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = (SIZE - w) // 2
    if outline:
        for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
            draw.text((x + dx, y + dy), text, font=font, fill=outline)
    draw.text((x, y), text, font=font, fill=fill)


def _rgba(color: tuple, alpha: int = 255) -> tuple:
    if len(color) == 3:
        return (*color, alpha)
    return color


def generate_sticker(params: StickerDesignParams, output_path: str) -> str:
    """Generate a sticker image based on Claude-interpreted parameters."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    primary = _rgba(params.primary_color)
    accent = _rgba(params.accent_color)
    dark_bg = (13, 13, 43, 255)
    white = (255, 255, 255, 255)

    # Mood-based adjustments
    glow_intensity = {
        "energetic": 12, "bold": 10, "playful": 8,
        "mysterious": 6, "calm": 5
    }.get(params.mood, 8)

    dispatch = {
        "neon_planet": _draw_planet,
        "retro_rocket": _draw_rocket,
        "pixel_moon": _draw_moon,
        "neon_starfield": _draw_starfield,
        "cyber_portal": _draw_portal,
        "arcade_badge": _draw_badge,
        "space_cat": _draw_cat,
        "y2k_burst": _draw_burst,
    }

    draw_fn = dispatch.get(params.design_type, _draw_starfield)
    img = draw_fn(primary, accent, dark_bg, white, glow_intensity)

    # Add text overlay if requested
    if params.text_overlay:
        d = ImageDraw.Draw(img)
        font = get_font(60)
        centered_text(d, params.text_overlay[:8].upper(), SIZE - 140, font,
                      fill=white, outline=dark_bg)

    full_path = os.path.join(OUTPUT_DIR, output_path)
    img.save(full_path, "PNG")
    return full_path


def _draw_planet(primary, accent, dark, white, glow_int):
    img = make_canvas()
    img = add_glow(img, (HALF, HALF), 220, primary, layers=glow_int)
    d = ImageDraw.Draw(img)

    # Stars
    rng = random.Random(42)
    for _ in range(25):
        x, y = rng.randint(30, SIZE - 30), rng.randint(30, SIZE - 30)
        sz = rng.randint(2, 5)
        d.ellipse([x - sz, y - sz, x + sz, y + sz], fill=white)

    pr = 160
    d.ellipse([HALF - pr, HALF - pr, HALF + pr, HALF + pr],
              fill=dark, outline=accent, width=5)

    for r, color_alpha, w in [
        (210, (*accent[:3], 200), 6),
        (240, (*primary[:3], 150), 4),
    ]:
        d.ellipse([HALF - r, HALF - 55, HALF + r, HALF + 55],
                  outline=color_alpha, width=w)

    front = make_canvas()
    fd = ImageDraw.Draw(front)
    fd.ellipse([HALF - pr, HALF + 10, HALF + pr, HALF + pr], fill=dark)
    img = Image.alpha_composite(img, front)
    return img


def _draw_rocket(primary, accent, dark, white, glow_int):
    img = make_canvas()
    d = ImageDraw.Draw(img)
    rng = random.Random(43)
    for _ in range(30):
        x, y = rng.randint(30, SIZE - 30), rng.randint(30, SIZE - 30)
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=white)

    cx = HALF
    flame = [(cx - 40, 680), (cx - 20, 580), (cx, 640), (cx + 20, 580), (cx + 40, 680)]
    d.polygon(flame, fill=(*primary[:3], 200))
    d.polygon([(cx - 20, 660), (cx, 600), (cx + 20, 660)], fill=(*accent[:3], 255))

    body = [(cx - 50, 550), (cx - 55, 400), (cx - 35, 280), (cx, 180),
            (cx + 35, 280), (cx + 55, 400), (cx + 50, 550)]
    d.polygon(body, fill=dark, outline=accent, width=4)
    d.polygon([(cx - 20, 340), (cx, 180), (cx + 20, 340)], fill=(*primary[:3], 200))
    d.ellipse([cx - 28, 400, cx + 28, 456], fill=(30, 50, 100, 255), outline=accent, width=4)

    for fin_pts in [[(cx - 55, 520), (cx - 55, 400), (cx - 110, 560)],
                    [(cx + 55, 520), (cx + 55, 400), (cx + 110, 560)]]:
        d.polygon(fin_pts, fill=(*dark[:3], 230), outline=primary, width=3)

    img = add_glow(img, (cx, 640), 60, primary, layers=glow_int // 2)
    return img


def _draw_moon(primary, accent, dark, white, glow_int):
    img = make_canvas()
    d = ImageDraw.Draw(img)
    rng = random.Random(44)
    for _ in range(35):
        x, y = rng.randint(30, SIZE - 30), rng.randint(30, SIZE - 30)
        sz = rng.randint(2, 4)
        d.ellipse([x - sz, y - sz, x + sz, y + sz], fill=accent)

    img = add_glow(img, (HALF, HALF), 230, primary, layers=glow_int)
    d = ImageDraw.Draw(img)

    mr = 200
    moon_color = (min(255, primary[0] + 100), min(255, primary[1] + 80), min(255, primary[2] + 50), 255)
    d.ellipse([HALF - mr, HALF - mr, HALF + mr, HALF + mr],
              fill=moon_color, outline=primary, width=5)

    # Crescent cutout
    cutout = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cutout)
    cd.ellipse([HALF - mr + 80, HALF - mr, HALF + mr + 80, HALF + mr], fill=(0, 0, 0, 255))
    r_ch, g_ch, b_ch, a_ch = img.split()
    cutout_alpha = cutout.split()[3]
    import numpy as np
    new_alpha = Image.fromarray(
        np.where(np.array(cutout_alpha) > 128, 0, np.array(a_ch)).astype('uint8')
    )
    img.putalpha(new_alpha)
    d = ImageDraw.Draw(img)

    for sx, sy, sr in [(HALF + 250, 120, 20), (100, HALF - 200, 15)]:
        pts = star_polygon(sx, sy, sr, sr // 2, 5)
        d.polygon(pts, fill=accent)

    return img


def _draw_starfield(primary, accent, dark, white, glow_int):
    img = make_canvas()
    bg = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bg)
    bd.ellipse([40, 40, SIZE - 40, SIZE - 40], fill=dark)
    img = Image.alpha_composite(img, bg)
    img = add_glow(img, (HALF, HALF), 340, primary, layers=glow_int // 2)
    d = ImageDraw.Draw(img)

    for i in range(24):
        angle = math.radians(i * 15)
        x1, y1 = HALF + 80 * math.cos(angle), HALF + 80 * math.sin(angle)
        x2, y2 = HALF + 350 * math.cos(angle), HALF + 350 * math.sin(angle)
        color = accent if i % 3 == 0 else (*primary[:3], 180)
        d.line([(x1, y1), (x2, y2)], fill=color, width=2 if i % 3 == 0 else 1)

    d.ellipse([40, 40, SIZE - 40, SIZE - 40], outline=accent, width=6)
    pts = star_polygon(HALF, HALF, 80, 35, 6)
    d.polygon(pts, fill=primary, outline=white, width=2)
    img = add_glow(img, (HALF, HALF), 80, accent, layers=5)
    return img


def _draw_portal(primary, accent, dark, white, glow_int):
    img = make_canvas()
    d = ImageDraw.Draw(img)
    rng = random.Random(45)
    for _ in range(25):
        x, y = rng.randint(30, SIZE - 30), rng.randint(30, SIZE - 30)
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=white)

    colors = [primary, accent, (*primary[:3], 200), (*accent[:3], 180), white]
    radii = [320, 275, 232, 192, 155]
    widths = [8, 6, 5, 5, 4]

    for r, c, w in zip(radii, colors, widths):
        d.ellipse([HALF - r, HALF - r, HALF + r, HALF + r], outline=c, width=w)
        img = add_glow(img, (HALF, HALF), r, c[:3], layers=3)
        d = ImageDraw.Draw(img)

    d.ellipse([HALF - 60, HALF - 60, HALF + 60, HALF + 60], fill=dark)

    for angle in [0, 45, 90, 135]:
        a = math.radians(angle)
        for sign in [1, -1]:
            x1 = HALF + sign * 20 * math.cos(a)
            y1 = HALF + sign * 20 * math.sin(a)
            x2 = HALF + sign * 55 * math.cos(a)
            y2 = HALF + sign * 55 * math.sin(a)
            d.line([(x1, y1), (x2, y2)], fill=accent, width=3)

    return img


def _draw_badge(primary, accent, dark, white, glow_int):
    img = make_canvas()
    badge = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)
    bd.rounded_rectangle([60, 80, SIZE - 60, SIZE - 80], radius=80,
                          fill=dark, outline=primary, width=8)
    img = Image.alpha_composite(img, badge)
    img = add_glow(img, (HALF, HALF), 300, primary, layers=glow_int // 2)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([80, 100, SIZE - 80, SIZE - 100], radius=65,
                         outline=(*accent[:3], 180), width=3)

    coin_r = 100
    d.ellipse([HALF - coin_r, HALF - coin_r - 40, HALF + coin_r, HALF + coin_r - 40],
              fill=accent, outline=primary, width=5)

    font_lg = get_font(52)
    centered_text(d, "1UP", HALF - 85, font_lg, fill=dark)
    font_sm = get_font(38)
    centered_text(d, "INSERT COIN", 130, font_sm, fill=primary, outline=dark)
    centered_text(d, "PLAY  AGAIN", SIZE - 200, font_sm, fill=accent, outline=dark)
    return img


def _draw_cat(primary, accent, dark, white, glow_int):
    img = make_canvas()
    d = ImageDraw.Draw(img)
    rng = random.Random(46)
    for _ in range(20):
        x, y = rng.randint(30, SIZE - 30), rng.randint(30, SIZE - 30)
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=white)

    cx, cy = HALF, HALF + 30
    img = add_glow(img, (cx, cy), 220, primary, layers=glow_int // 2)
    d = ImageDraw.Draw(img)

    hr = 170
    d.ellipse([cx - hr, cy - hr, cx + hr, cy + hr], fill=dark, outline=primary, width=6)

    left_ear = [(cx - 160, cy - 130), (cx - 80, cy - 260), (cx - 30, cy - 140)]
    right_ear = [(cx + 160, cy - 130), (cx + 80, cy - 260), (cx + 30, cy - 140)]
    for ear in [left_ear, right_ear]:
        d.polygon(ear, fill=dark, outline=primary, width=5)

    def shrink_tri(pts, f=0.5):
        mcx = sum(p[0] for p in pts) / 3
        mcy = sum(p[1] for p in pts) / 3
        return [(mcx + (x - mcx) * f, mcy + (y - mcy) * f) for x, y in pts]

    d.polygon(shrink_tri(left_ear, 0.55), fill=(*accent[:3], 200))
    d.polygon(shrink_tri(right_ear, 0.55), fill=(*accent[:3], 200))

    for ex, ey in [(cx - 65, cy - 30), (cx + 65, cy - 30)]:
        d.ellipse([ex - 30, ey - 30, ex + 30, ey + 30],
                  fill=(20, 20, 60, 255), outline=accent, width=4)
        d.ellipse([ex - 12, ey - 12, ex + 12, ey + 12], fill=accent)
        d.ellipse([ex + 6, ey - 16, ex + 16, ey - 6], fill=white)

    d.polygon([(cx, cy + 20), (cx - 12, cy + 40), (cx + 12, cy + 40)], fill=primary)

    for wx_start, wx_end, wy in [
        (cx - 170, cx - 45, cy + 35), (cx - 170, cx - 45, cy + 55),
        (cx + 45, cx + 170, cy + 35), (cx + 45, cx + 170, cy + 55),
    ]:
        d.line([(wx_start, wy), (wx_end, wy)], fill=accent, width=2)

    d.line([(cx, cy - 170), (cx + 30, cy - 300)], fill=accent, width=4)
    d.ellipse([cx + 16, cy - 318, cx + 44, cy - 290], fill=accent, outline=white, width=3)

    return img


def _draw_burst(primary, accent, dark, white, glow_int):
    img = make_canvas()
    burst_pts = star_polygon(HALF, HALF, 360, 280, 16)
    burst_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    bl = ImageDraw.Draw(burst_layer)
    bl.polygon(burst_pts, fill=(*accent[:3], 255))
    img = Image.alpha_composite(img, burst_layer)
    img = add_glow(img, (HALF, HALF), 340, accent, layers=glow_int // 2)
    d = ImageDraw.Draw(img)

    inner_pts = star_polygon(HALF, HALF, 240, 190, 16)
    d.polygon(inner_pts, fill=(*primary[:3], 230))
    d.ellipse([HALF - 150, HALF - 150, HALF + 150, HALF + 150],
              fill=dark, outline=accent, width=6)

    font_xl = get_font(110)
    centered_text(d, "Y2K", HALF - 68, font_xl, fill=accent, outline=(*dark[:3], 255))
    font_md = get_font(36)
    centered_text(d, "FUTURE IS NOW", HALF + 60, font_md, fill=primary, outline=dark)

    for i in range(0, 16, 2):
        angle = math.radians(i * (360 / 16)) - math.pi / 2
        sx = int(HALF + 340 * math.cos(angle))
        sy = int(HALF + 340 * math.sin(angle))
        pts = star_polygon(sx, sy, 18, 8, 5)
        d.polygon(pts, fill=white)

    return img
