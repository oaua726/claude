"""Design 01 — a ringed planet wrapped in a purple haze."""

from PIL import Image, ImageDraw

from ..canvas import HALF, SIZE, add_glow, add_small_stars, make_canvas
from ..palette import DARK_NAVY, DEEP_PURPLE, ELECTRIC_CYAN, NEON_PINK, RETRO_YELLOW


def draw():
    img = make_canvas()
    img = add_glow(img, (HALF, HALF), 220, DEEP_PURPLE, layers=10)

    d = ImageDraw.Draw(img)
    add_small_stars(d, count=25, seed=1)

    # Planet body
    pr = 160
    d.ellipse([HALF - pr, HALF - pr, HALF + pr, HALF + pr],
              fill=DARK_NAVY, outline=ELECTRIC_CYAN, width=5)

    # Surface bands, each clipped to the planet circle
    for band_y, band_h, color in [
        (HALF - 30, 18, (30, 60, 120, 180)),
        (HALF - 5, 14, (60, 20, 150, 160)),
        (HALF + 20, 18, (20, 100, 140, 180)),
    ]:
        band = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        bd = ImageDraw.Draw(band)
        bd.ellipse([HALF - pr + 6, HALF - pr + 6,
                    HALF + pr - 6, HALF + pr - 6], fill=DARK_NAVY)
        bd.rectangle([HALF - pr, band_y, HALF + pr, band_y + band_h], fill=color)
        mask = Image.new("L", (SIZE, SIZE), 0)
        md = ImageDraw.Draw(mask)
        md.ellipse([HALF - pr + 3, HALF - pr + 3, HALF + pr - 3, HALF + pr - 3], fill=255)
        img = Image.alpha_composite(img, Image.composite(band, make_canvas(), mask))
        d = ImageDraw.Draw(img)

    # Rings
    for ring_r, ring_color, ring_w in [
        (210, (*ELECTRIC_CYAN[:3], 200), 6),
        (240, (*NEON_PINK[:3], 150), 4),
        (265, (*RETRO_YELLOW[:3], 100), 3),
    ]:
        d.ellipse([HALF - ring_r, HALF - 55, HALF + ring_r, HALF + 55],
                  outline=ring_color, width=ring_w)

    # Redraw the planet's front half over the rings
    front = make_canvas()
    fd = ImageDraw.Draw(front)
    fd.ellipse([HALF - pr, HALF + 10, HALF + pr, HALF + pr], fill=DARK_NAVY)
    img = Image.alpha_composite(img, front)

    # Glint
    d = ImageDraw.Draw(img)
    d.ellipse([HALF - 110, HALF - 110, HALF - 70, HALF - 80],
              fill=(180, 220, 255, 120))

    return img
