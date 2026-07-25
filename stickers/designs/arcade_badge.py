"""Design 06 — an "insert coin" arcade badge with a 1UP token."""

import math

from PIL import Image, ImageDraw

from ..canvas import (
    HALF, SIZE, add_glow, centered_text, get_font, make_canvas,
)
from ..palette import DARK_NAVY, ELECTRIC_CYAN, NEON_GREEN, RETRO_YELLOW


def draw():
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

    # Coin / token
    coin_r = 100
    d.ellipse([HALF - coin_r, HALF - coin_r - 40, HALF + coin_r, HALF + coin_r - 40],
              fill=(200, 160, 0, 255), outline=RETRO_YELLOW, width=5)
    d.ellipse([HALF - coin_r + 12, HALF - coin_r - 28,
               HALF + coin_r - 12, HALF + coin_r - 52], fill=(230, 190, 20, 255))

    centered_text(d, "1UP", HALF - 85, get_font(52), fill=DARK_NAVY)

    font_sm = get_font(38)
    centered_text(d, "INSERT COIN", 130, font_sm, fill=NEON_GREEN, outline=DARK_NAVY)
    centered_text(d, "PLAY  AGAIN", SIZE - 200, font_sm,
                  fill=ELECTRIC_CYAN, outline=DARK_NAVY)

    # Pixel dot decoration around the badge
    for i in range(16):
        angle = math.radians(i * 22.5)
        px = int(HALF + 300 * math.cos(angle))
        py = int(HALF + 230 * math.sin(angle))
        color = NEON_GREEN if i % 2 == 0 else RETRO_YELLOW
        d.rectangle([px - 5, py - 5, px + 5, py + 5], fill=color)

    return img
