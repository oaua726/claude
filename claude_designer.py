"""
Claude as creative director.

Claude has no image-generation API of its own. Its job here is to turn a vague
user idea (in any language) into a world-class, production-ready prompt for a
text-to-image model, tuned specifically for die-cut stickers that sell on
marketplaces like Etsy and Redbubble.
"""

import anthropic
from pydantic import BaseModel
from typing import Literal


class StickerBrief(BaseModel):
    """Structured creative brief produced by Claude."""
    title: str
    image_prompt: str          # the prompt sent to the image model
    negative_prompt: str       # what to avoid
    style: Literal[
        "kawaii", "retro_vintage", "y2k_chrome", "minimal_line",
        "watercolor", "bold_cartoon", "vaporwave", "botanical"
    ]
    subject: str
    palette: list[str]         # human-readable color names
    suggested_tags: list[str]  # marketplace SEO tags
    reasoning: str             # why these choices sell


SYSTEM_PROMPT = """You are a world-class sticker designer and prompt engineer. \
You have sold thousands of die-cut stickers on Etsy and Redbubble and know \
exactly what converts.

Your task: take a user's rough idea (it may be in Japanese or any language) and \
produce a single, production-ready prompt for a modern text-to-image model \
(FLUX / SDXL class).

Hard requirements for every prompt you write:
- It MUST describe a die-cut sticker: a single centered subject, a thick clean \
white sticker border/outline, and a plain white background (so the background \
can be cut out to transparent).
- Use concrete art-direction language the image model understands: art style, \
line weight, shading, finish (matte/glossy), lighting, composition.
- Be vivid and specific about subject and color palette. Avoid vague words.
- No text in the image UNLESS the user explicitly asks for a word/phrase; if \
they do, specify it in quotes and keep it short.
- Aim for designs with proven commercial appeal (cute, nostalgic, witty, \
aesthetic) — not generic clip-art.

The negative_prompt should suppress: blurry, low-res, watermark, extra limbs, \
busy background, photo-realistic clutter, jpeg artifacts, multiple subjects.

Choose the single style that best fits the idea and the current market."""


def design_sticker_brief(user_idea: str) -> StickerBrief:
    """Use Claude (claude-opus-4-7) to produce a structured sticker brief."""
    client = anthropic.Anthropic()

    response = client.messages.parse(
        model="claude-opus-4-7",
        max_tokens=2048,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    "Create a sticker design brief for this idea. "
                    "Return the structured fields.\n\n"
                    f'Idea: "{user_idea}"'
                ),
            }
        ],
        output_format=StickerBrief,
    )

    brief = response.parsed_output
    if brief is None:
        raise ValueError("Claude did not return a valid sticker brief")
    return brief
