"""Canvas geometry and drawing helpers shared by every sticker design."""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

from .palette import ELECTRIC_CYAN, RETRO_YELLOW, WHITE

SIZE = 800
HALF = SIZE // 2

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
]


def make_canvas():
    """Return a fully transparent RGBA canvas."""
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))


def add_glow(img, center, radius, color, layers=8):
    """Composite a soft neon halo around ``center`` on top of ``img``."""
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
    """Return the vertices of a star with ``points`` spikes, first spike up."""
    coords = []
    for i in range(points * 2):
        angle = math.pi / points * i - math.pi / 2
        r = outer if i % 2 == 0 else inner
        coords.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return coords


def add_small_stars(draw, count=20, seed=42):
    """Scatter tiny background stars deterministically for a given ``seed``."""
    rng = random.Random(seed)
    for _ in range(count):
        x = rng.randint(30, SIZE - 30)
        y = rng.randint(30, SIZE - 30)
        sz = rng.randint(2, 5)
        color = rng.choice([WHITE, ELECTRIC_CYAN, RETRO_YELLOW])
        draw.ellipse([x - sz, y - sz, x + sz, y + sz], fill=color)


def get_font(size):
    """Load a bold TrueType face, falling back to Pillow's built-in font."""
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def centered_text(draw, text, y, font, fill, outline=None):
    """Draw horizontally centered text, optionally with an outline pass."""
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = (SIZE - w) // 2
    if outline:
        for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2),
                       (0, -3), (0, 3), (-3, 0), (3, 0)]:
            draw.text((x + dx, y + dy), text, font=font, fill=outline)
    draw.text((x, y), text, font=font, fill=fill)
