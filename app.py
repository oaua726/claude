import os

from dotenv import load_dotenv
load_dotenv()

import anthropic
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)

_access_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")
_channel_secret = os.environ.get("LINE_CHANNEL_SECRET", "")
_anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")

if not _access_token or not _channel_secret:
    print("WARNING: LINE_CHANNEL_ACCESS_TOKEN or LINE_CHANNEL_SECRET not set. "
          "Webhook calls will fail until these are configured.")

if not _anthropic_key:
    print("WARNING: ANTHROPIC_API_KEY not set. Claude responses will fail.")

configuration = Configuration(access_token=_access_token)
handler = WebhookHandler(_channel_secret)
claude_client = anthropic.Anthropic(api_key=_anthropic_key)

SYSTEM_PROMPT = (
    "あなたは親切で賢いAIアシスタントです。"
    "ユーザーの質問に丁寧かつ簡潔に答えてください。"
    "日本語で話しかけられた場合は日本語で、英語で話しかけられた場合は英語で返答してください。"
)


@app.route("/")
@app.route("/health")
def health():
    return "OK"


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    user_text = event.message.text.strip()

    try:
        response = claude_client.messages.create(
            model="claude-opus-4-7",
            max_tokens=1000,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_text}],
        )
        reply_text = response.content[-1].text
    except Exception as e:
        print(f"Claude API error: {e}")
        reply_text = "申し訳ありません、エラーが発生しました。しばらくしてからもう一度お試しください。"

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)],
            )
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
