import requests
import base64
from pathlib import Path

API_KEY = "AIzaSyAZ6PNg0URgSYPsqa6ExUMv8ZLBjiaBzWo"
MODEL = "gemini-2.5-flash-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

payload = {
    "contents": [
        {
            "parts": [
                {"text": "Generate an image of a cute cat astronaut wearing a space suit, floating in outer space among stars and colorful planets. Highly detailed digital art style."}
            ]
        }
    ],
    "generationConfig": {
        "responseModalities": ["image", "text"]
    }
}

print("画像生成中...")
response = requests.post(URL, json=payload, timeout=120)

if response.status_code != 200:
    print(f"エラー: {response.status_code}")
    print(response.text)
else:
    data = response.json()
    candidates = data.get("candidates", [])
    saved = 0
    for ci, candidate in enumerate(candidates):
        parts = candidate.get("content", {}).get("parts", [])
        for pi, part in enumerate(parts):
            if "inlineData" in part:
                mime = part["inlineData"]["mimeType"]
                ext = mime.split("/")[-1]
                img_bytes = base64.b64decode(part["inlineData"]["data"])
                path = Path(f"cat_astronaut_{ci}_{pi}.{ext}")
                path.write_bytes(img_bytes)
                print(f"保存しました: {path} ({len(img_bytes):,} bytes)")
                saved += 1
            elif "text" in part:
                print(f"テキスト応答: {part['text'][:200]}")
    if saved == 0:
        import json
        print("画像データなし。レスポンス:")
        print(json.dumps(data, indent=2)[:1000])
