"""Sticker design registry.

Each design lives in its own module and exposes a ``draw()`` function that
returns an 800x800 RGBA image with a transparent background. To add a design,
create a module here and append it to ``DESIGNS``; the key becomes the output
filename.
"""

from . import (
    arcade_badge,
    cyber_portal,
    neon_planet,
    neon_starfield,
    pixel_moon,
    retro_rocket,
    space_cat,
    y2k_burst,
)

DESIGNS = {
    "01_neon_planet": neon_planet.draw,
    "02_retro_rocket": retro_rocket.draw,
    "03_pixel_moon": pixel_moon.draw,
    "04_neon_starfield": neon_starfield.draw,
    "05_cyber_portal": cyber_portal.draw,
    "06_arcade_badge": arcade_badge.draw,
    "07_space_cat": space_cat.draw,
    "08_y2k_burst": y2k_burst.draw,
}

__all__ = ["DESIGNS"]
