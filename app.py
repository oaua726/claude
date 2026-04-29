import os
import hashlib
import hmac
import base64
import tempfile
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    TextMessage,
    ImageMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from generate_stickers import (
    draw_neon_planet,
    draw_retro_rocket,
    draw_pixel_moon,
    draw_neon_starfield,
    draw_cyber_portal,
    draw_arcade_badge,
    draw_space_cat,
    draw_y2k_burst,
)

app = Flask(__name__)

configuration = Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])

STICKERS = {
    "planet":    ("Neon Planet",    draw_neon_planet),
    "rocket":    ("Retro Rocket",   draw_retro_rocket),
    "moon":      ("Pixel Moon",     draw_pixel_moon),
    "stars":     ("Neon Starfield", draw_neon_starfield),
    "portal":    ("Cyber Portal",   draw_cyber_portal),
    "arcade":    ("Arcade Badge",   draw_arcade_badge),
    "cat":       ("Space Cat",      draw_space_cat),
    "y2k":       ("Y2K Burst",      draw_y2k_burst),
}

HELP_TEXT = (
    "🚀 Retro-Futurist Sticker Bot\n\n"
    "Send one of these keywords to get a sticker:\n"
    "  planet, rocket, moon, stars,\n"
    "  portal, arcade, cat, y2k\n\n"
    "Or send 'list' to see this menu again."
)

UPLOAD_DIR = Path(tempfile.gettempdir()) / "line_stickers"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _sticker_url(name: str) -> str:
    """Return the public URL for a sticker image."""
    base = os.environ.get("BASE_URL", "").rstrip("/")
    return f"{base}/stickers/{name}.png"


def _generate_and_save(key: str) -> Path:
    path = UPLOAD_DIR / f"{key}.png"
    if not path.exists():
        _, draw_fn = STICKERS[key]
        img = draw_fn()
        img.save(path, "PNG")
    return path


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@app.route("/stickers/<filename>")
def serve_sticker(filename: str):
    from flask import send_from_directory
    return send_from_directory(str(UPLOAD_DIR), filename)


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    text = event.message.text.strip().lower()

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        if text in ("help", "list", "start", "hi", "hello"):
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=HELP_TEXT)],
                )
            )
            return

        if text in STICKERS:
            label, _ = STICKERS[text]
            _generate_and_save(text)
            image_url = _sticker_url(text)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        ImageMessage(
                            original_content_url=image_url,
                            preview_image_url=image_url,
                        )
                    ],
                )
            )
            return

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text=f"Unknown sticker '{text}'.\n\n" + HELP_TEXT
                    )
                ],
            )
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
