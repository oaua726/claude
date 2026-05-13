from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.webhook import handle_webhook

app = FastAPI(title="LINE Bot")


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.post("/webhook")
async def webhook(request: Request) -> JSONResponse:
    await handle_webhook(request)
    return JSONResponse({"status": "ok"})
