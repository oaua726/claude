import anthropic
from .config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# user_id -> list of {"role": "user"|"assistant", "content": str}
conversation_history: dict[str, list[dict]] = {}

SYSTEM_PROMPT = """あなたは親切で役立つアシスタントです。
LINEを通じてユーザーと会話します。
日本語で自然に会話してください。
リマインダーを設定したい場合、ユーザーが「〇〇時に△△をリマインドして」のように言ったら、
以下のJSON形式で応答の末尾に付けてください（ユーザーには見せない形式です）:
[REMINDER:{"time": "HH:MM", "message": "リマインダーの内容"}]
"""


def chat(user_id: str, user_message: str) -> str:
    history = conversation_history.setdefault(user_id, [])
    history.append({"role": "user", "content": user_message})

    # keep last 20 messages to avoid token overflow
    if len(history) > 20:
        history[:] = history[-20:]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=history,
    )

    assistant_message = response.content[0].text
    history.append({"role": "assistant", "content": assistant_message})

    return assistant_message


def clear_history(user_id: str) -> None:
    conversation_history.pop(user_id, None)
