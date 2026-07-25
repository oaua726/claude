"""Design 02 — a finned rocket on a burning orange exhaust."""

from PIL import ImageDraw

from ..canvas import HALF, add_glow, add_small_stars, make_canvas, star_polygon
from ..palette import (
    DARK_NAVY, DEEP_PURPLE, ELECTRIC_CYAN, NEON_PINK, ORANGE_NEON, RETRO_YELLOW,
)


def draw():
    img = make_canvas()
    d = ImageDraw.Draw(img)
    add_small_stars(d, count=30, seed=2)

    cx = HALF

    # Exhaust flame
    d.polygon([(cx - 40, 680), (cx - 20, 580), (cx, 640),
               (cx + 20, 580), (cx + 40, 680)], fill=(255, 140, 0, 200))
    d.polygon([(cx - 20, 660), (cx, 600), (cx + 20, 660)], fill=RETRO_YELLOW)

    # Rocket body
    d.polygon([(cx - 50, 550), (cx - 55, 400), (cx - 35, 280),
               (cx, 180),
               (cx + 35, 280), (cx + 55, 400), (cx + 50, 550)],
              fill=DARK_NAVY, outline=ELECTRIC_CYAN, width=4)

    # Nose cone stripe
    d.polygon([(cx - 20, 340), (cx, 180), (cx + 20, 340)],
              fill=(*NEON_PINK[:3], 200))

    # Porthole window
    d.ellipse([cx - 28, 400, cx + 28, 456],
              fill=(30, 50, 100, 255), outline=ELECTRIC_CYAN, width=4)
    d.ellipse([cx - 14, 414, cx + 14, 442], fill=(*ELECTRIC_CYAN[:3], 180))

    # Fins
    for fin in [
        [(cx - 55, 520), (cx - 55, 400), (cx - 110, 560)],
        [(cx + 55, 520), (cx + 55, 400), (cx + 110, 560)],
    ]:
        d.polygon(fin, fill=(*DEEP_PURPLE[:3], 230), outline=NEON_PINK, width=3)

    # Body stripe
    d.rectangle([cx - 54, 460, cx + 54, 480], fill=(*NEON_PINK[:3], 200))

    # Stars near the rocket
    for sx, sy, ss in [(150, 200, 6), (620, 150, 5), (680, 400, 4), (120, 500, 5)]:
        d.polygon(star_polygon(sx, sy, ss * 2, ss, 5), fill=RETRO_YELLOW)

    return add_glow(img, (cx, 640), 60, ORANGE_NEON, layers=6)
