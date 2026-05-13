import re
import json
import asyncio
from datetime import datetime, timedelta
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    PushMessageRequest,
    TextMessage,
)
from .config import LINE_CHANNEL_ACCESS_TOKEN

# user_id -> list of {"time": "HH:MM", "message": str, "task": asyncio.Task}
reminders: dict[str, list[dict]] = {}

REMINDER_PATTERN = re.compile(r"\[REMINDER:(\{.*?\})\]", re.DOTALL)


def extract_reminder(text: str) -> tuple[str, dict | None]:
    """Extract reminder JSON from AI response and return (clean_text, reminder_data)."""
    match = REMINDER_PATTERN.search(text)
    if not match:
        return text, None

    clean_text = REMINDER_PATTERN.sub("", text).strip()
    try:
        data = json.loads(match.group(1))
        return clean_text, data
    except json.JSONDecodeError:
        return clean_text, None


async def _send_reminder(user_id: str, message: str, delay_seconds: float) -> None:
    await asyncio.sleep(delay_seconds)
    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
    async with AsyncApiClient(configuration) as api_client:
        line_bot_api = AsyncMessagingApi(api_client)
        await line_bot_api.push_message(
            PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text=f"⏰ リマインダー\n{message}")],
            )
        )


def schedule_reminder(user_id: str, time_str: str, message: str) -> str:
    """Schedule a reminder for HH:MM today (or tomorrow if past)."""
    now = datetime.now()
    try:
        hour, minute = map(int, time_str.split(":"))
    except ValueError:
        return f"時刻の形式が正しくありません: {time_str}"

    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)

    delay = (target - now).total_seconds()
    task = asyncio.create_task(_send_reminder(user_id, message, delay))

    reminders.setdefault(user_id, []).append(
        {"time": time_str, "message": message, "task": task}
    )

    return f"✅ {time_str} に「{message}」をリマインドします！"


def list_reminders(user_id: str) -> str:
    user_reminders = [r for r in reminders.get(user_id, []) if not r["task"].done()]
    if not user_reminders:
        return "現在設定されているリマインダーはありません。"
    lines = [f"• {r['time']} — {r['message']}" for r in user_reminders]
    return "📋 設定中のリマインダー:\n" + "\n".join(lines)


def cancel_all_reminders(user_id: str) -> str:
    for r in reminders.get(user_id, []):
        r["task"].cancel()
    reminders.pop(user_id, None)
    return "🗑️ すべてのリマインダーをキャンセルしました。"
