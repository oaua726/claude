"""Design 03 — a cratered crescent moon carved out of a full disc."""

from PIL import Image, ImageDraw

from ..canvas import HALF, SIZE, add_glow, add_small_stars, make_canvas, star_polygon
from ..palette import RETRO_YELLOW


def draw():
    img = make_canvas()
    d = ImageDraw.Draw(img)
    add_small_stars(d, count=35, seed=3)

    # Glow behind the moon
    img = add_glow(img, (HALF, HALF), 230, RETRO_YELLOW, layers=8)
    d = ImageDraw.Draw(img)

    # Full moon disc
    mr = 200
    d.ellipse([HALF - mr, HALF - mr, HALF + mr, HALF + mr],
              fill=(255, 230, 150, 255), outline=RETRO_YELLOW, width=5)

    # Punch an offset circle out of the alpha channel to leave a crescent
    offset = 80
    cutout = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cutout)
    cd.ellipse([HALF - mr + offset, HALF - mr, HALF + mr + offset, HALF + mr],
               fill=(0, 0, 0, 255))
    hole = cutout.getchannel("A").point(lambda v: 255 if v > 128 else 0)
    alpha = img.getchannel("A")
    alpha.paste(0, mask=hole)
    img.putalpha(alpha)
    d = ImageDraw.Draw(img)

    # Craters, skipping any that would fall outside the crescent
    for cx, cy, cr in [(HALF - 60, HALF - 80, 22), (HALF + 20, HALF + 60, 16),
                       (HALF - 140, HALF + 30, 12), (HALF - 30, HALF + 120, 18)]:
        if cx < HALF + offset - 10:
            d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr],
                      fill=(220, 190, 100, 200), outline=(180, 150, 60, 200), width=2)

    # Accent stars
    for sx, sy, sr, si in [(HALF + 250, 120, 20, 8), (100, HALF - 200, 15, 6),
                           (680, HALF + 100, 18, 7)]:
        d.polygon(star_polygon(sx, sy, sr, si, 5), fill=RETRO_YELLOW)

    return img
