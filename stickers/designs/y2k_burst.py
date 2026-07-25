"""Design 08 — a Y2K starburst with chunky centered lettering."""

import math

from PIL import Image, ImageDraw

from ..canvas import (
    HALF, SIZE, add_glow, centered_text, get_font, make_canvas, star_polygon,
)
from ..palette import DARK_NAVY, DEEP_PURPLE, ELECTRIC_CYAN, NEON_PINK, RETRO_YELLOW, WHITE

SPIKES = 16


def draw():
    img = make_canvas()

    # Outer starburst
    burst = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    bl = ImageDraw.Draw(burst)
    bl.polygon(star_polygon(HALF, HALF, 360, 280, SPIKES), fill=(*RETRO_YELLOW[:3], 255))
    img = Image.alpha_composite(img, burst)

    img = add_glow(img, (HALF, HALF), 340, RETRO_YELLOW, layers=8)
    d = ImageDraw.Draw(img)

    # Inner starburst
    d.polygon(star_polygon(HALF, HALF, 240, 190, SPIKES), fill=(*NEON_PINK[:3], 230))

    # Center circle
    d.ellipse([HALF - 150, HALF - 150, HALF + 150, HALF + 150],
              fill=DARK_NAVY, outline=ELECTRIC_CYAN, width=6)

    centered_text(d, "Y2K", HALF - 68, get_font(110),
                  fill=ELECTRIC_CYAN, outline=(*DEEP_PURPLE[:3], 255))
    centered_text(d, "∞ FUTURE IS NOW ∞", HALF + 60, get_font(36),
                  fill=RETRO_YELLOW, outline=DARK_NAVY)

    # Small stars on alternating burst tips
    for i in range(0, SPIKES, 2):
        angle = math.radians(i * (360 / SPIKES)) - math.pi / 2
        sx = int(HALF + 340 * math.cos(angle))
        sy = int(HALF + 340 * math.sin(angle))
        d.polygon(star_polygon(sx, sy, 18, 8, 5), fill=WHITE)

    return img
