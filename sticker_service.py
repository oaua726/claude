"""
Sticker generation pipeline.

  user idea (any language)
        │
        ▼
  Claude (claude-opus-4-7)  ── designs a pro die-cut sticker prompt
        │
        ▼
  image backend (FLUX / pluggable)  ── renders the artwork
        │
        ▼
  die-cut post-process  ── knock out the white background to transparent
        │
        ▼
  saved PNG
"""

import os

from PIL import Image

from claude_designer import design_sticker_brief, StickerBrief
from image_backend import generate_image, is_mock

OUTPUT_DIR = "generated_stickers"


def _make_diecut(png_bytes: bytes) -> bytes:
    """Knock out a near-white background so the sticker reads as die-cut.

    The Claude prompt always asks for a plain white background, so a simple
    luminance threshold on the border-connected white region is enough for a
    clean cutout without needing a segmentation model.
    """
    import io

    img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    px = img.load()
    w, h = img.size

    # Flood fill from the edges: only remove white that is connected to the
    # border, so white *inside* the artwork (eyes, highlights) is preserved.
    threshold = 238
    stack = []
    for x in range(w):
        stack.append((x, 0))
        stack.append((x, h - 1))
    for y in range(h):
        stack.append((0, y))
        stack.append((w - 1, y))

    seen = set()
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or not (0 <= x < w and 0 <= y < h):
            continue
        seen.add((x, y))
        r, g, b, a = px[x, y]
        if r >= threshold and g >= threshold and b >= threshold:
            px[x, y] = (r, g, b, 0)
            stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])

    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def create_sticker(user_idea: str, output_filename: str) -> dict:
    """Run the full pipeline. Returns metadata about the generated sticker."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Claude designs the brief
    brief: StickerBrief = design_sticker_brief(user_idea)

    # 2. Image backend renders it
    raw_png = generate_image(
        prompt=brief.image_prompt,
        negative_prompt=brief.negative_prompt,
        width=1024,
        height=1024,
    )

    # 3. Die-cut post-process (skip for mock placeholder cards)
    final_png = raw_png if is_mock() else _make_diecut(raw_png)

    # 4. Save
    full_path = os.path.join(OUTPUT_DIR, output_filename)
    with open(full_path, "wb") as f:
        f.write(final_png)

    return {
        "path": full_path,
        "title": brief.title,
        "style": brief.style,
        "subject": brief.subject,
        "palette": brief.palette,
        "suggested_tags": brief.suggested_tags,
        "reasoning": brief.reasoning,
        "image_prompt": brief.image_prompt,
        "mock": is_mock(),
    }
