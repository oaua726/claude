"""
Claude-powered sticker designer.
Interprets natural language prompts and maps them to sticker design parameters.
"""

import json
import re
import anthropic
from pydantic import BaseModel
from typing import Literal


class StickerDesignParams(BaseModel):
    design_type: Literal[
        "neon_planet", "retro_rocket", "pixel_moon",
        "neon_starfield", "cyber_portal", "arcade_badge",
        "space_cat", "y2k_burst"
    ]
    primary_color: tuple[int, int, int]
    accent_color: tuple[int, int, int]
    mood: Literal["energetic", "calm", "mysterious", "playful", "bold"]
    text_overlay: str | None = None
    reasoning: str


DESIGN_SYSTEM_PROMPT = """You are an expert sticker designer who maps user requests to sticker parameters.

Available design types and their characteristics:
- neon_planet: Space planet with rings, cosmic atmosphere, glow effects
- retro_rocket: Vintage rocket ship with fins, porthole, exhaust flames
- pixel_moon: Crescent moon with pixel art style, craters
- neon_starfield: Radial burst of light rays, central star, cosmic energy
- cyber_portal: Concentric rings, targeting reticle, futuristic portal
- arcade_badge: Game-style badge with coin/token, retro gaming aesthetics
- space_cat: Cat with space helmet, whiskers, antenna, cosmic vibe
- y2k_burst: Starburst explosion, Y2K aesthetic, bold typography

Color palette available (use RGB tuples):
- Neon pink: (255, 0, 110)
- Electric cyan: (0, 245, 255)
- Deep purple: (123, 47, 190)
- Neon green: (57, 255, 20)
- Retro yellow: (255, 230, 0)
- Hot magenta: (255, 0, 255)
- Dark navy: (13, 13, 43)
- Orange neon: (255, 100, 0)

Match the user's request to the most appropriate design type and colors.
For text_overlay, only include if user explicitly requests text (max 8 chars).
"""


def interpret_prompt(user_prompt: str) -> StickerDesignParams:
    """Use Claude to interpret a natural language prompt into design parameters."""
    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        thinking={"type": "adaptive"},
        system=DESIGN_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"""Interpret this sticker request and return JSON with design parameters:

User request: "{user_prompt}"

Return ONLY valid JSON with these fields:
{{
  "design_type": "one of the 8 types",
  "primary_color": [r, g, b],
  "accent_color": [r, g, b],
  "mood": "energetic|calm|mysterious|playful|bold",
  "text_overlay": null or "SHORT TEXT",
  "reasoning": "brief explanation"
}}"""
            }
        ]
    )

    text = next(b.text for b in response.content if b.type == "text")

    # Extract JSON from response
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if not json_match:
        raise ValueError(f"No JSON found in Claude response: {text}")

    data = json.loads(json_match.group())

    # Convert color lists to tuples
    data["primary_color"] = tuple(data["primary_color"])
    data["accent_color"] = tuple(data["accent_color"])

    return StickerDesignParams(**data)
