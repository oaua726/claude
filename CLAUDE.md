# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Install dependencies:
```
pip install -r requirements.txt
```

Generate all stickers:
```
python generate_stickers.py
```

Output PNGs are written to `./output/` as `NN_name.png`.

## Architecture

The entire project is a single file: `generate_stickers.py`. It generates 8 retro-futuristic 800×800 RGBA PNG stickers using Pillow and numpy.

**Structure pattern:**
- Global color constants (RGBA tuples) define the shared palette.
- Shared helpers (`make_canvas`, `add_glow`, `star_polygon`, `add_small_stars`, `rounded_rect`, `get_font`, `centered_text`) are used across designs.
- Each design is a standalone `draw_*()` function that returns a composited `Image` object.
- The `DESIGNS` list at the bottom maps output filename prefixes to their draw functions. `main()` iterates this list, calls each function, and saves the result.

**Adding a new sticker:**
1. Write a `draw_my_design()` function following the same pattern (call `make_canvas()`, draw on it, return the `Image`).
2. Append `("NN_my_design", draw_my_design)` to the `DESIGNS` list.

**Key constraints:**
- All canvases are `SIZE × SIZE` (800×800) RGBA mode; transparency is meaningful — stickers have transparent backgrounds.
- `add_glow` uses `Image.alpha_composite`, so it must operate on RGBA layers. Always call `ImageDraw.Draw(img)` again after compositing since the original draw handle is stale.
- `draw_pixel_moon` imports `numpy` inline via `__import__('numpy')` to manipulate alpha channel pixels directly — this is the only place numpy is used.
- Font loading falls back gracefully through several system TTF paths; if none exist it falls back to the default bitmap font.
