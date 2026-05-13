from linebot.v3 import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    ReplyMessageRequest,
    TextMessage,
)
from fastapi import HTTPException, Request

from .config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from .ai import chat, clear_history
from .reminder import extract_reminder, schedule_reminder, list_reminders, cancel_all_reminders

parser = WebhookParser(LINE_CHANNEL_SECRET)


async def handle_webhook(request: Request) -> None:
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()

    try:
        events = parser.parse(body.decode(), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
    async with AsyncApiClient(configuration) as api_client:
        line_bot_api = AsyncMessagingApi(api_client)
        for event in events:
            if not isinstance(event, MessageEvent):
                continue
            if not isinstance(event.message, TextMessageContent):
                continue
            await _handle_text(line_bot_api, event)


async def _handle_text(
    line_bot_api: AsyncMessagingApi, event: MessageEvent
) -> None:
    user_id = event.source.user_id
    text = event.message.text.strip()

    # Built-in commands
    if text in ("/reset", "リセット", "会話リセット"):
        clear_history(user_id)
        reply = "会話履歴をリセットしました。"
    elif text in ("/reminders", "リマインダー一覧"):
        reply = list_reminders(user_id)
    elif text in ("/cancel", "リマインダーキャンセル"):
        reply = cancel_all_reminders(user_id)
    else:
        # AI conversation
        ai_response = chat(user_id, text)
        clean_response, reminder_data = extract_reminder(ai_response)

        reply = clean_response

        # Schedule reminder if AI detected one
        if reminder_data and "time" in reminder_data and "message" in reminder_data:
            result = schedule_reminder(user_id, reminder_data["time"], reminder_data["message"])
            reply = f"{clean_response}\n\n{result}" if clean_response else result

    await line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=reply)],
        )
    )
