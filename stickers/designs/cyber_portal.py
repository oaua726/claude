"""Design 05 — concentric rings closing on a targeting reticle."""

import math

from PIL import ImageDraw

from ..canvas import HALF, add_glow, add_small_stars, make_canvas
from ..palette import (
    DARK_NAVY, DEEP_PURPLE, ELECTRIC_CYAN, HOT_MAGENTA, NEON_GREEN, NEON_PINK,
    RETRO_YELLOW, WHITE,
)

RINGS = [
    (320, HOT_MAGENTA, 8),
    (275, NEON_PINK, 6),
    (232, DEEP_PURPLE, 5),
    (192, ELECTRIC_CYAN, 5),
    (155, NEON_GREEN, 4),
    (120, RETRO_YELLOW, 4),
    (88, WHITE, 3),
]


def draw():
    img = make_canvas()
    d = ImageDraw.Draw(img)
    add_small_stars(d, count=25, seed=5)

    for r, color, width in RINGS:
        d.ellipse([HALF - r, HALF - r, HALF + r, HALF + r],
                  outline=(*color[:3], 220), width=width)
        img = add_glow(img, (HALF, HALF), r, color, layers=3)
        d = ImageDraw.Draw(img)

    # Dark center
    d.ellipse([HALF - 60, HALF - 60, HALF + 60, HALF + 60], fill=DARK_NAVY)

    # Targeting reticle
    for angle in [0, 45, 90, 135]:
        a = math.radians(angle)
        for sign in (1, -1):
            d.line([(HALF + sign * 20 * math.cos(a), HALF + sign * 20 * math.sin(a)),
                    (HALF + sign * 55 * math.cos(a), HALF + sign * 55 * math.sin(a))],
                   fill=ELECTRIC_CYAN, width=3)

    # Tick marks around the outer ring
    for i in range(36):
        angle = math.radians(i * 10)
        r_inner = 330 if i % 3 == 0 else 335
        d.line([(HALF + r_inner * math.cos(angle), HALF + r_inner * math.sin(angle)),
                (HALF + 345 * math.cos(angle), HALF + 345 * math.sin(angle))],
               fill=WHITE if i % 3 == 0 else ELECTRIC_CYAN, width=2)

    return img
