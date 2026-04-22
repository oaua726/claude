import os
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUTPUT_DIR = "output"
SIZE = 800
HALF = SIZE // 2

# Retro-futurist color palette
NEON_PINK    = (255,   0, 110, 255)
ELECTRIC_CYA = (  0, 245, 255, 255)
DEEP_PURPLE  = (123,  47, 190, 255)
NEON_GREEN   = ( 57, 255,  20, 255)
RETRO_YELLOW = (255, 230,   0, 255)
HOT_MAGENTA  = (255,   0, 255, 255)
DARK_NAVY    = ( 13,  13,  43, 255)
WHITE        = (255, 255, 255, 255)
BLACK        = (  0,   0,   0, 255)
ORANGE_NEON  = (255, 100,   0, 255)


def make_canvas():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))


def add_glow(img, center, radius, color, layers=8):
    glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    cx, cy = center
    r, g, b, _ = color
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


def add_small_stars(draw, count=20, seed=42):
    rng = random.Random(seed)
    for _ in range(count):
        x = rng.randint(30, SIZE - 30)
        y = rng.randint(30, SIZE - 30)
        sz = rng.randint(2, 5)
        color = rng.choice([WHITE, ELECTRIC_CYA, RETRO_YELLOW])
        draw.ellipse([x - sz, y - sz, x + sz, y + sz], fill=color)


def rounded_rect(draw, bbox, radius, fill, outline=None, width=4):
    x0, y0, x1, y1 = bbox
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill,
                            outline=outline, width=width)


def get_font(size):
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    ]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def centered_text(draw, text, y, font, fill, outline=None):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = (SIZE - w) // 2
    if outline:
        for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, -3), (0, 3), (-3, 0), (3, 0)]:
            draw.text((x + dx, y + dy), text, font=font, fill=outline)
    draw.text((x, y), text, font=font, fill=fill)


# ── Design 1: Neon Planet ────────────────────────────────────────────────────
def draw_neon_planet():
    img = make_canvas()
    img = add_glow(img, (HALF, HALF), 220, DEEP_PURPLE, layers=10)

    d = ImageDraw.Draw(img)
    add_small_stars(d, count=25, seed=1)

    # Planet body
    pr = 160
    d.ellipse([HALF - pr, HALF - pr, HALF + pr, HALF + pr],
              fill=DARK_NAVY, outline=ELECTRIC_CYA, width=5)

    # Surface bands
    for i, (band_y, band_h, color) in enumerate([
        (HALF - 30, 18, (30, 60, 120, 180)),
        (HALF - 5,  14, (60, 20, 150, 160)),
        (HALF + 20, 18, (20, 100, 140, 180)),
    ]):
        band = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        bd = ImageDraw.Draw(band)
        bd.ellipse([HALF - pr + 6, HALF - pr + 6,
                    HALF + pr - 6, HALF + pr - 6], fill=DARK_NAVY)
        bd.rectangle([HALF - pr, band_y, HALF + pr, band_y + band_h], fill=color)
        # Clip band to planet circle
        mask = Image.new("L", (SIZE, SIZE), 0)
        md = ImageDraw.Draw(mask)
        md.ellipse([HALF - pr + 3, HALF - pr + 3, HALF + pr - 3, HALF + pr - 3], fill=255)
        img = Image.alpha_composite(img, Image.composite(band, make_canvas(), mask))
        d = ImageDraw.Draw(img)

    # Rings (ellipses)
    for ring_r, ring_color, ring_w in [
        (210, (*ELECTRIC_CYA[:3], 200), 6),
        (240, (*NEON_PINK[:3], 150), 4),
        (265, (*RETRO_YELLOW[:3], 100), 3),
    ]:
        d.ellipse([HALF - ring_r, HALF - 55, HALF + ring_r, HALF + 55],
                  outline=ring_color, width=ring_w)

    # Redraw planet over rings (front half)
    front = make_canvas()
    fd = ImageDraw.Draw(front)
    fd.ellipse([HALF - pr, HALF + 10, HALF + pr, HALF + pr],
               fill=DARK_NAVY)
    img = Image.alpha_composite(img, front)

    # Glint
    d = ImageDraw.Draw(img)
    d.ellipse([HALF - 110, HALF - 110, HALF - 70, HALF - 80],
              fill=(180, 220, 255, 120))

    return img


# ── Design 2: Retro Rocket ────────────────────────────────────────────────────
def draw_retro_rocket():
    img = make_canvas()
    d = ImageDraw.Draw(img)
    add_small_stars(d, count=30, seed=2)

    cx = HALF
    # Exhaust flame
    flame = [
        (cx - 40, 680), (cx - 20, 580), (cx, 640),
        (cx + 20, 580), (cx + 40, 680)
    ]
    d.polygon(flame, fill=(255, 140, 0, 200))
    inner_flame = [(cx - 20, 660), (cx, 600), (cx + 20, 660)]
    d.polygon(inner_flame, fill=RETRO_YELLOW)

    # Rocket body
    body = [
        (cx - 50, 550), (cx - 55, 400), (cx - 35, 280),
        (cx, 180),
        (cx + 35, 280), (cx + 55, 400), (cx + 50, 550)
    ]
    d.polygon(body, fill=DARK_NAVY, outline=ELECTRIC_CYA, width=4)

    # Nose cone stripe
    d.polygon([(cx - 20, 340), (cx, 180), (cx + 20, 340)],
              fill=(*NEON_PINK[:3], 200))

    # Porthole window
    d.ellipse([cx - 28, 400, cx + 28, 456],
              fill=(30, 50, 100, 255), outline=ELECTRIC_CYA, width=4)
    d.ellipse([cx - 14, 414, cx + 14, 442],
              fill=(*ELECTRIC_CYA[:3], 180))

    # Left fin
    left_fin = [(cx - 55, 520), (cx - 55, 400), (cx - 110, 560)]
    d.polygon(left_fin, fill=(*DEEP_PURPLE[:3], 230), outline=NEON_PINK, width=3)

    # Right fin
    right_fin = [(cx + 55, 520), (cx + 55, 400), (cx + 110, 560)]
    d.polygon(right_fin, fill=(*DEEP_PURPLE[:3], 230), outline=NEON_PINK, width=3)

    # Body stripe
    d.rectangle([cx - 54, 460, cx + 54, 480], fill=(*NEON_PINK[:3], 200))

    # Stars near rocket
    for sx, sy, ss in [(150, 200, 6), (620, 150, 5), (680, 400, 4), (120, 500, 5)]:
        pts = star_polygon(sx, sy, ss * 2, ss, 5)
        d.polygon(pts, fill=RETRO_YELLOW)

    # Exhaust glow
    img = add_glow(img, (cx, 640), 60, ORANGE_NEON, layers=6)

    return img


# ── Design 3: Pixel Moon ────────────────────────────────────────────────────
def draw_pixel_moon():
    img = make_canvas()
    d = ImageDraw.Draw(img)
    add_small_stars(d, count=35, seed=3)

    # Glow behind moon
    img = add_glow(img, (HALF, HALF), 230, RETRO_YELLOW, layers=8)
    d = ImageDraw.Draw(img)

    # Full moon circle
    mr = 200
    d.ellipse([HALF - mr, HALF - mr, HALF + mr, HALF + mr],
              fill=(255, 230, 150, 255), outline=RETRO_YELLOW, width=5)

    # Crescent cutout — offset circle to create crescent
    cutout = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cutout)
    offset = 80
    cd.ellipse([HALF - mr + offset, HALF - mr, HALF + mr + offset, HALF + mr],
               fill=(0, 0, 0, 255))
    # Use composite to cut out crescent
    r_ch, g_ch, b_ch, a_ch = img.split()
    cutout_alpha = cutout.split()[3]
    new_alpha = Image.fromarray(
        __import__('numpy').where(
            __import__('numpy').array(cutout_alpha) > 128,
            0,
            __import__('numpy').array(a_ch)
        ).astype('uint8')
    )
    img.putalpha(new_alpha)
    d = ImageDraw.Draw(img)

    # Crater dots
    for cx2, cy2, cr in [(HALF - 60, HALF - 80, 22), (HALF + 20, HALF + 60, 16),
                         (HALF - 140, HALF + 30, 12), (HALF - 30, HALF + 120, 18)]:
        # Only draw if within crescent (x < HALF + offset - mr)
        if cx2 < HALF + offset - 10:
            d.ellipse([cx2 - cr, cy2 - cr, cx2 + cr, cy2 + cr],
                      fill=(220, 190, 100, 200), outline=(180, 150, 60, 200), width=2)

    # Star burst near moon top
    for star_data in [(HALF + 250, 120, 20, 8), (100, HALF - 200, 15, 6),
                      (680, HALF + 100, 18, 7)]:
        sx, sy, sr, si = star_data
        pts = star_polygon(sx, sy, sr, si, 5)
        d.polygon(pts, fill=RETRO_YELLOW)

    return img


# ── Design 4: Neon Starfield ────────────────────────────────────────────────
def draw_neon_starfield():
    img = make_canvas()

    # Background circle
    bg = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bg)
    bd.ellipse([40, 40, SIZE - 40, SIZE - 40], fill=DARK_NAVY)
    img = Image.alpha_composite(img, bg)

    img = add_glow(img, (HALF, HALF), 340, DEEP_PURPLE, layers=6)
    d = ImageDraw.Draw(img)

    # Radial burst lines
    for i in range(24):
        angle = math.radians(i * 15)
        x1 = HALF + 80 * math.cos(angle)
        y1 = HALF + 80 * math.sin(angle)
        x2 = HALF + 350 * math.cos(angle)
        y2 = HALF + 350 * math.sin(angle)
        color = ELECTRIC_CYA if i % 3 == 0 else (*NEON_PINK[:3], 180)
        d.line([(x1, y1), (x2, y2)], fill=color, width=2 if i % 3 == 0 else 1)

    # Outer circle border
    d.ellipse([40, 40, SIZE - 40, SIZE - 40], outline=ELECTRIC_CYA, width=6)
    d.ellipse([55, 55, SIZE - 55, SIZE - 55], outline=(*NEON_PINK[:3], 150), width=3)

    # Center star
    pts = star_polygon(HALF, HALF, 80, 35, 6)
    d.polygon(pts, fill=RETRO_YELLOW, outline=WHITE, width=2)

    # Smaller surrounding stars
    for i in range(8):
        angle = math.radians(i * 45 + 22.5)
        sx = int(HALF + 200 * math.cos(angle))
        sy = int(HALF + 200 * math.sin(angle))
        pts2 = star_polygon(sx, sy, 22, 10, 5)
        d.polygon(pts2, fill=NEON_PINK if i % 2 == 0 else ELECTRIC_CYA)

    # Tiny dots
    add_small_stars(d, count=20, seed=4)

    # Inner glow overlay
    img = add_glow(img, (HALF, HALF), 80, RETRO_YELLOW, layers=5)

    return img


# ── Design 5: Cyber Portal ──────────────────────────────────────────────────
def draw_cyber_portal():
    img = make_canvas()
    d = ImageDraw.Draw(img)
    add_small_stars(d, count=25, seed=5)

    # Concentric rings
    colors = [HOT_MAGENTA, NEON_PINK, DEEP_PURPLE, ELECTRIC_CYA,
              NEON_GREEN, RETRO_YELLOW, WHITE]
    widths = [8, 6, 5, 5, 4, 4, 3]
    radii = [320, 275, 232, 192, 155, 120, 88]

    for r, c, w in zip(radii, colors, widths):
        d.ellipse([HALF - r, HALF - r, HALF + r, HALF + r],
                  outline=(*c[:3], 220), width=w)
        img = add_glow(img, (HALF, HALF), r, c, layers=3)
        d = ImageDraw.Draw(img)

    # Dark center
    d.ellipse([HALF - 60, HALF - 60, HALF + 60, HALF + 60],
              fill=DARK_NAVY)

    # Cross / targeting reticle
    for angle in [0, 45, 90, 135]:
        a = math.radians(angle)
        x1 = HALF + 20 * math.cos(a)
        y1 = HALF + 20 * math.sin(a)
        x2 = HALF + 55 * math.cos(a)
        y2 = HALF + 55 * math.sin(a)
        d.line([(x1, y1), (x2, y2)], fill=ELECTRIC_CYA, width=3)
        x1b = HALF - 20 * math.cos(a)
        y1b = HALF - 20 * math.sin(a)
        x2b = HALF - 55 * math.cos(a)
        y2b = HALF - 55 * math.sin(a)
        d.line([(x1b, y1b), (x2b, y2b)], fill=ELECTRIC_CYA, width=3)

    # Tick marks around outer ring
    for i in range(36):
        angle = math.radians(i * 10)
        r_inner = 330 if i % 3 == 0 else 335
        r_outer = 345
        x1 = HALF + r_inner * math.cos(angle)
        y1 = HALF + r_inner * math.sin(angle)
        x2 = HALF + r_outer * math.cos(angle)
        y2 = HALF + r_outer * math.sin(angle)
        d.line([(x1, y1), (x2, y2)], fill=WHITE if i % 3 == 0 else ELECTRIC_CYA, width=2)

    return img


# ── Design 6: Arcade Badge ──────────────────────────────────────────────────
def draw_arcade_badge():
    img = make_canvas()

    # Badge background
    badge = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)
    bd.rounded_rectangle([60, 80, SIZE - 60, SIZE - 80], radius=80,
                          fill=DARK_NAVY, outline=NEON_GREEN, width=8)
    img = Image.alpha_composite(img, badge)
    img = add_glow(img, (HALF, HALF), 300, NEON_GREEN, layers=6)
    d = ImageDraw.Draw(img)

    # Inner border
    d.rounded_rectangle([80, 100, SIZE - 80, SIZE - 100], radius=65,
                         outline=(*RETRO_YELLOW[:3], 180), width=3)

    # Pixel art coin/token center
    coin_r = 100
    d.ellipse([HALF - coin_r, HALF - coin_r - 40, HALF + coin_r, HALF + coin_r - 40],
              fill=(200, 160, 0, 255), outline=RETRO_YELLOW, width=5)
    d.ellipse([HALF - coin_r + 12, HALF - coin_r - 28, HALF + coin_r - 12, HALF + coin_r - 52],
              fill=(230, 190, 20, 255))

    # "1UP" on coin
    font_lg = get_font(52)
    centered_text(d, "1UP", HALF - 85, font_lg, fill=DARK_NAVY, outline=None)

    # "INSERT COIN" top
    font_sm = get_font(38)
    centered_text(d, "INSERT COIN", 130, font_sm, fill=NEON_GREEN, outline=DARK_NAVY)

    # "PLAY AGAIN" bottom
    centered_text(d, "PLAY  AGAIN", SIZE - 200, font_sm, fill=ELECTRIC_CYA, outline=DARK_NAVY)

    # Pixel dots border decoration
    for i in range(16):
        angle = math.radians(i * 22.5)
        px = int(HALF + 300 * math.cos(angle))
        py = int(HALF + 230 * math.sin(angle))
        col = NEON_GREEN if i % 2 == 0 else RETRO_YELLOW
        d.rectangle([px - 5, py - 5, px + 5, py + 5], fill=col)

    return img


# ── Design 7: Space Cat ─────────────────────────────────────────────────────
def draw_space_cat():
    img = make_canvas()
    d = ImageDraw.Draw(img)
    add_small_stars(d, count=20, seed=7)

    cx = HALF
    cy = HALF + 30

    # Glow behind cat
    img = add_glow(img, (cx, cy), 220, HOT_MAGENTA, layers=6)
    d = ImageDraw.Draw(img)

    # Head (circle)
    hr = 170
    d.ellipse([cx - hr, cy - hr, cx + hr, cy + hr],
              fill=DARK_NAVY, outline=HOT_MAGENTA, width=6)

    # Ears (triangles)
    left_ear = [(cx - 160, cy - 130), (cx - 80, cy - 260), (cx - 30, cy - 140)]
    right_ear = [(cx + 160, cy - 130), (cx + 80, cy - 260), (cx + 30, cy - 140)]
    for ear in [left_ear, right_ear]:
        d.polygon(ear, fill=DARK_NAVY, outline=HOT_MAGENTA, width=5)

    # Inner ear
    def shrink_triangle(pts, factor=0.5):
        mcx = sum(p[0] for p in pts) / 3
        mcy = sum(p[1] for p in pts) / 3
        return [(mcx + (x - mcx) * factor, mcy + (y - mcy) * factor) for x, y in pts]

    d.polygon(shrink_triangle(left_ear, 0.55), fill=(*NEON_PINK[:3], 200))
    d.polygon(shrink_triangle(right_ear, 0.55), fill=(*NEON_PINK[:3], 200))

    # Eyes (neon)
    for ex, ey in [(cx - 65, cy - 30), (cx + 65, cy - 30)]:
        d.ellipse([ex - 30, ey - 30, ex + 30, ey + 30],
                  fill=(20, 20, 60, 255), outline=ELECTRIC_CYA, width=4)
        d.ellipse([ex - 12, ey - 12, ex + 12, ey + 12],
                  fill=ELECTRIC_CYA)
        # Shine
        d.ellipse([ex + 6, ey - 16, ex + 16, ey - 6], fill=WHITE)

    # Nose
    nose = [(cx, cy + 20), (cx - 12, cy + 40), (cx + 12, cy + 40)]
    d.polygon(nose, fill=NEON_PINK)

    # Whiskers
    for wx_start, wx_end, wy in [
        (cx - 170, cx - 45, cy + 35),
        (cx - 170, cx - 45, cy + 55),
        (cx + 45, cx + 170, cy + 35),
        (cx + 45, cx + 170, cy + 55),
    ]:
        d.line([(wx_start, wy), (wx_end, wy)], fill=ELECTRIC_CYA, width=2)

    # Antenna
    d.line([(cx, cy - 170), (cx + 30, cy - 300)], fill=RETRO_YELLOW, width=4)
    d.ellipse([cx + 16, cy - 318, cx + 44, cy - 290],
              fill=RETRO_YELLOW, outline=WHITE, width=3)

    # Cheek blush
    for bx, by in [(cx - 100, cy + 40), (cx + 100, cy + 40)]:
        d.ellipse([bx - 28, by - 12, bx + 28, by + 12],
                  fill=(*NEON_PINK[:3], 100))

    # Body / bow tie suggestion
    d.ellipse([cx - 30, cy + 140, cx + 30, cy + 200],
              fill=(*HOT_MAGENTA[:3], 180), outline=WHITE, width=3)

    return img


# ── Design 8: Y2K Burst ─────────────────────────────────────────────────────
def draw_y2k_burst():
    img = make_canvas()

    # Outer starburst
    burst_pts = star_polygon(HALF, HALF, 360, 280, 16)
    burst_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    bl = ImageDraw.Draw(burst_layer)
    bl.polygon(burst_pts, fill=(*RETRO_YELLOW[:3], 255))
    img = Image.alpha_composite(img, burst_layer)

    img = add_glow(img, (HALF, HALF), 340, RETRO_YELLOW, layers=8)

    d = ImageDraw.Draw(img)

    # Inner burst
    inner_pts = star_polygon(HALF, HALF, 240, 190, 16)
    d.polygon(inner_pts, fill=(*NEON_PINK[:3], 230))

    # Center circle
    d.ellipse([HALF - 150, HALF - 150, HALF + 150, HALF + 150],
              fill=DARK_NAVY, outline=ELECTRIC_CYA, width=6)

    # "Y2K" main text
    font_xl = get_font(110)
    centered_text(d, "Y2K", HALF - 68, font_xl,
                  fill=ELECTRIC_CYA, outline=(*DEEP_PURPLE[:3], 255))

    # Sub text
    font_md = get_font(36)
    centered_text(d, "∞ FUTURE IS NOW ∞", HALF + 60, font_md,
                  fill=RETRO_YELLOW, outline=DARK_NAVY)

    # Small stars on burst tips
    for i in range(0, 16, 2):
        angle = math.radians(i * (360 / 16)) - math.pi / 2
        sx = int(HALF + 340 * math.cos(angle))
        sy = int(HALF + 340 * math.sin(angle))
        pts = star_polygon(sx, sy, 18, 8, 5)
        d.polygon(pts, fill=WHITE)

    return img


# ── Main ────────────────────────────────────────────────────────────────────
DESIGNS = [
    ("01_neon_planet",   draw_neon_planet),
    ("02_retro_rocket",  draw_retro_rocket),
    ("03_pixel_moon",    draw_pixel_moon),
    ("04_neon_starfield", draw_neon_starfield),
    ("05_cyber_portal",  draw_cyber_portal),
    ("06_arcade_badge",  draw_arcade_badge),
    ("07_space_cat",     draw_space_cat),
    ("08_y2k_burst",     draw_y2k_burst),
]


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for name, fn in DESIGNS:
        print(f"Generating {name}...", end=" ", flush=True)
        img = fn()
        path = os.path.join(OUTPUT_DIR, f"{name}.png")
        img.save(path, "PNG")
        print(f"saved → {path}")
    print(f"\nDone! {len(DESIGNS)} stickers generated in ./{OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
