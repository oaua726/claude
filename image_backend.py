"""
Pluggable text-to-image backend.

Claude has no image-generation API, so the rendered pixels come from a
dedicated image model. The product owner plugs in their provider here.

A reference Replicate/FLUX implementation is included. If no API token is
configured, a clearly-labelled local mock backend is used so the whole
pipeline still runs end-to-end for development and tests.

Deployment note: the host running this must allow outbound HTTPS to the
image provider (e.g. api.replicate.com / replicate.delivery). In a
network-restricted environment, add those hosts to the allowlist.
"""

import io
import os
import time
import textwrap

import httpx

# Reference model. FLUX schnell is fast and cheap — ideal for stickers.
REPLICATE_MODEL = os.getenv(
    "STICKER_IMAGE_MODEL", "black-forest-labs/flux-schnell"
)


class ImageBackendError(RuntimeError):
    pass


def _generate_replicate(
    prompt: str, negative_prompt: str, width: int, height: int
) -> bytes:
    token = os.environ["REPLICATE_API_TOKEN"]

    create = httpx.post(
        f"https://api.replicate.com/v1/models/{REPLICATE_MODEL}/predictions",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Prefer": "wait",
        },
        json={
            "input": {
                "prompt": prompt,
                "aspect_ratio": "1:1",
                "output_format": "png",
                "num_outputs": 1,
                "disable_safety_checker": False,
            }
        },
        timeout=120,
    )
    if create.status_code >= 400:
        raise ImageBackendError(f"Replicate error {create.status_code}: {create.text}")

    pred = create.json()

    # If the "Prefer: wait" header didn't fully resolve, poll.
    poll_url = pred.get("urls", {}).get("get")
    while pred.get("status") in ("starting", "processing") and poll_url:
        time.sleep(1.5)
        pred = httpx.get(
            poll_url, headers={"Authorization": f"Bearer {token}"}, timeout=60
        ).json()

    if pred.get("status") != "succeeded":
        raise ImageBackendError(f"Generation failed: {pred.get('error') or pred.get('status')}")

    output = pred["output"]
    image_url = output[0] if isinstance(output, list) else output
    img = httpx.get(image_url, timeout=60)
    img.raise_for_status()
    return img.content


def _generate_mock(
    prompt: str, negative_prompt: str, width: int, height: int
) -> bytes:
    """Local placeholder so the pipeline runs without an image API key.

    Renders the Claude-engineered prompt onto a card so you can see exactly
    what *would* be sent to the real image model. Not for production output.
    """
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (width, height), (244, 241, 234))
    d = ImageDraw.Draw(img)

    def font(sz):
        for p in (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ):
            if os.path.exists(p):
                return ImageFont.truetype(p, sz)
        return ImageFont.load_default()

    d.rounded_rectangle(
        [40, 40, width - 40, height - 40], radius=40,
        outline=(123, 47, 190), width=10,
    )
    d.text((70, 80), "MOCK BACKEND", font=font(48), fill=(255, 0, 110))
    d.text(
        (70, 150),
        "Set REPLICATE_API_TOKEN for real AI images.",
        font=font(24), fill=(80, 80, 90),
    )
    d.text((70, 220), "Claude-engineered prompt:", font=font(26), fill=(13, 13, 43))

    y = 270
    for line in textwrap.wrap(prompt, width=52)[:18]:
        d.text((70, y), line, font=font(22), fill=(40, 40, 60))
        y += 32

    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def generate_image(
    prompt: str,
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 1024,
) -> bytes:
    """Generate a sticker image. Returns PNG bytes.

    Backend selection:
      - REPLICATE_API_TOKEN set  -> real FLUX generation
      - otherwise                -> local mock (clearly labelled)
    """
    if os.getenv("REPLICATE_API_TOKEN"):
        return _generate_replicate(prompt, negative_prompt, width, height)
    return _generate_mock(prompt, negative_prompt, width, height)


def is_mock() -> bool:
    return not os.getenv("REPLICATE_API_TOKEN")
