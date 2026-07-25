"""Design 07 — a magenta-lit cat astronaut with an antenna."""

from PIL import ImageDraw

from ..canvas import HALF, add_glow, add_small_stars, make_canvas
from ..palette import DARK_NAVY, ELECTRIC_CYAN, HOT_MAGENTA, NEON_PINK, RETRO_YELLOW, WHITE


def _shrink_triangle(pts, factor=0.5):
    """Scale a triangle toward its own centroid."""
    mcx = sum(p[0] for p in pts) / 3
    mcy = sum(p[1] for p in pts) / 3
    return [(mcx + (x - mcx) * factor, mcy + (y - mcy) * factor) for x, y in pts]


def draw():
    img = make_canvas()
    d = ImageDraw.Draw(img)
    add_small_stars(d, count=20, seed=7)

    cx = HALF
    cy = HALF + 30

    img = add_glow(img, (cx, cy), 220, HOT_MAGENTA, layers=6)
    d = ImageDraw.Draw(img)

    # Head
    hr = 170
    d.ellipse([cx - hr, cy - hr, cx + hr, cy + hr],
              fill=DARK_NAVY, outline=HOT_MAGENTA, width=6)

    # Ears
    left_ear = [(cx - 160, cy - 130), (cx - 80, cy - 260), (cx - 30, cy - 140)]
    right_ear = [(cx + 160, cy - 130), (cx + 80, cy - 260), (cx + 30, cy - 140)]
    for ear in [left_ear, right_ear]:
        d.polygon(ear, fill=DARK_NAVY, outline=HOT_MAGENTA, width=5)
    for ear in [left_ear, right_ear]:
        d.polygon(_shrink_triangle(ear, 0.55), fill=(*NEON_PINK[:3], 200))

    # Eyes
    for ex, ey in [(cx - 65, cy - 30), (cx + 65, cy - 30)]:
        d.ellipse([ex - 30, ey - 30, ex + 30, ey + 30],
                  fill=(20, 20, 60, 255), outline=ELECTRIC_CYAN, width=4)
        d.ellipse([ex - 12, ey - 12, ex + 12, ey + 12], fill=ELECTRIC_CYAN)
        d.ellipse([ex + 6, ey - 16, ex + 16, ey - 6], fill=WHITE)

    # Nose
    d.polygon([(cx, cy + 20), (cx - 12, cy + 40), (cx + 12, cy + 40)], fill=NEON_PINK)

    # Whiskers
    for wx_start, wx_end, wy in [
        (cx - 170, cx - 45, cy + 35),
        (cx - 170, cx - 45, cy + 55),
        (cx + 45, cx + 170, cy + 35),
        (cx + 45, cx + 170, cy + 55),
    ]:
        d.line([(wx_start, wy), (wx_end, wy)], fill=ELECTRIC_CYAN, width=2)

    # Antenna
    d.line([(cx, cy - 170), (cx + 30, cy - 300)], fill=RETRO_YELLOW, width=4)
    d.ellipse([cx + 16, cy - 318, cx + 44, cy - 290],
              fill=RETRO_YELLOW, outline=WHITE, width=3)

    # Cheek blush
    for bx, by in [(cx - 100, cy + 40), (cx + 100, cy + 40)]:
        d.ellipse([bx - 28, by - 12, bx + 28, by + 12], fill=(*NEON_PINK[:3], 100))

    # Bow tie
    d.ellipse([cx - 30, cy + 140, cx + 30, cy + 200],
              fill=(*HOT_MAGENTA[:3], 180), outline=WHITE, width=3)

    return img
