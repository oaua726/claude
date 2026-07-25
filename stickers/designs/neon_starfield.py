"""Design 04 — a radial burst framed inside a neon roundel."""

import math

from PIL import Image, ImageDraw

from ..canvas import HALF, SIZE, add_glow, add_small_stars, make_canvas, star_polygon
from ..palette import DARK_NAVY, DEEP_PURPLE, ELECTRIC_CYAN, NEON_PINK, RETRO_YELLOW, WHITE


def draw():
    img = make_canvas()

    # Background disc
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
        color = ELECTRIC_CYAN if i % 3 == 0 else (*NEON_PINK[:3], 180)
        d.line([(x1, y1), (x2, y2)], fill=color, width=2 if i % 3 == 0 else 1)

    # Outer borders
    d.ellipse([40, 40, SIZE - 40, SIZE - 40], outline=ELECTRIC_CYAN, width=6)
    d.ellipse([55, 55, SIZE - 55, SIZE - 55], outline=(*NEON_PINK[:3], 150), width=3)

    # Center star
    d.polygon(star_polygon(HALF, HALF, 80, 35, 6),
              fill=RETRO_YELLOW, outline=WHITE, width=2)

    # Surrounding stars
    for i in range(8):
        angle = math.radians(i * 45 + 22.5)
        sx = int(HALF + 200 * math.cos(angle))
        sy = int(HALF + 200 * math.sin(angle))
        d.polygon(star_polygon(sx, sy, 22, 10, 5),
                  fill=NEON_PINK if i % 2 == 0 else ELECTRIC_CYAN)

    add_small_stars(d, count=20, seed=4)

    return add_glow(img, (HALF, HALF), 80, RETRO_YELLOW, layers=5)
