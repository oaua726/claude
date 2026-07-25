"""Retro-futurist sticker generator.

Renders a set of 800x800 transparent PNG stickers with Pillow. See
``stickers.designs`` for the design registry and ``stickers.cli`` for the
command line entry point (``python -m stickers``).
"""

from .designs import DESIGNS

__all__ = ["DESIGNS"]
