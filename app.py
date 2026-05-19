"""
Claude-powered sticker generation API with monetization.

Endpoints:
  POST /api/register        - Register new user (get free credits)
  GET  /api/credits         - Check credit balance
  POST /api/generate        - Generate custom sticker (costs 1 credit)
  GET  /api/stickers/{id}  - Download generated sticker
  POST /api/buy             - Purchase credit package
  POST /api/webhook/stripe  - Stripe payment webhook
  GET  /                    - API info and pricing page
"""

import os
import uuid
import hmac
import hashlib
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Header, Request, Depends
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel, EmailStr

import credit_manager as cm
from claude_designer import interpret_prompt
from sticker_service import generate_sticker, OUTPUT_DIR

# Initialize DB on startup
cm.init_db()

app = FastAPI(
    title="Claude Sticker API",
    description="AI-powered custom sticker generation with Claude",
    version="1.0.0",
)

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")


# ── Models ──────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: str


class GenerateRequest(BaseModel):
    prompt: str
    format: str = "png"


class BuyRequest(BaseModel):
    package: str  # starter | pro | unlimited_monthly


# ── Auth helper ─────────────────────────────────────────────────────────────

def get_current_user(x_api_key: str = Header(...)) -> cm.User:
    user = cm.get_user_by_api_key(x_api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user


# ── Routes ──────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    pricing_html = ""
    for pkg, info in cm.CREDIT_PACKAGES.items():
        pricing_html += f"""
        <div class="package">
          <h3>{pkg.replace('_', ' ').title()}</h3>
          <p class="price">${info['price_usd']}</p>
          <p>{info['credits']} credits</p>
          <p>${info['price_usd'] / info['credits']:.2f} per sticker</p>
        </div>"""

    return f"""<!DOCTYPE html>
<html>
<head>
  <title>Claude Sticker API</title>
  <style>
    body {{ font-family: system-ui; max-width: 900px; margin: 0 auto; padding: 40px 20px;
           background: #0d0d2b; color: #fff; }}
    h1 {{ color: #00f5ff; font-size: 2.5rem; }}
    h2 {{ color: #ff006e; margin-top: 2rem; }}
    .packages {{ display: flex; gap: 20px; flex-wrap: wrap; margin: 20px 0; }}
    .package {{ background: #1a1a4a; border: 2px solid #7b2fbe; border-radius: 12px;
                padding: 20px; min-width: 180px; text-align: center; }}
    .price {{ font-size: 2rem; font-weight: bold; color: #00f5ff; margin: 10px 0; }}
    code {{ background: #1a1a4a; padding: 4px 8px; border-radius: 4px; color: #39ff14; }}
    pre {{ background: #1a1a4a; padding: 20px; border-radius: 8px; overflow-x: auto; }}
    .endpoint {{ margin: 10px 0; }}
    .method {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-weight: bold; }}
    .post {{ background: #ff006e; }}
    .get {{ background: #00f5ff; color: #0d0d2b; }}
    a {{ color: #00f5ff; }}
  </style>
</head>
<body>
  <h1>⚡ Claude Sticker API</h1>
  <p>AI-powered custom sticker generation. Describe what you want — Claude creates it.</p>

  <h2>💳 Pricing</h2>
  <p>New users get <strong>3 free credits</strong> on registration.</p>
  <div class="packages">{pricing_html}</div>

  <h2>🚀 Quick Start</h2>
  <pre># 1. Register (get free credits)
curl -X POST /api/register -H "Content-Type: application/json" \\
     -d '{{"email": "you@example.com"}}'

# 2. Generate a sticker
curl -X POST /api/generate -H "X-Api-Key: YOUR_KEY" \\
     -H "Content-Type: application/json" \\
     -d '{{"prompt": "space cat with rainbow colors, playful vibe"}}'

# 3. Download your sticker
curl /api/stickers/STICKER_ID -H "X-Api-Key: YOUR_KEY" --output sticker.png</pre>

  <h2>📡 Endpoints</h2>
  <div class="endpoint"><span class="method post">POST</span> <code>/api/register</code> — Register &amp; get free credits</div>
  <div class="endpoint"><span class="method get">GET</span> <code>/api/credits</code> — Check balance (auth required)</div>
  <div class="endpoint"><span class="method post">POST</span> <code>/api/generate</code> — Generate sticker (1 credit)</div>
  <div class="endpoint"><span class="method get">GET</span> <code>/api/stickers/{{id}}</code> — Download sticker</div>
  <div class="endpoint"><span class="method post">POST</span> <code>/api/buy</code> — Buy credits</div>
  <div class="endpoint"><span class="method get">GET</span> <code>/docs</code> — <a href="/docs">Interactive API docs</a></div>
</body>
</html>"""


@app.post("/api/register")
async def register(req: RegisterRequest):
    """Register a new user and receive free credits."""
    try:
        user = cm.register_user(req.email)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    return {
        "user_id": user.user_id,
        "api_key": user.api_key,
        "credits": user.credits,
        "message": f"Welcome! You have {user.credits} free credits to start.",
    }


@app.get("/api/credits")
async def get_credits(user: cm.User = Depends(get_current_user)):
    """Check your credit balance and recent usage."""
    stats = cm.get_user_stats(user.user_id)
    return {
        "credits": stats["credits"],
        "total_generated": stats["total_generated"],
        "recent_generations": stats["recent_generations"][:5],
    }


@app.post("/api/generate")
async def generate(req: GenerateRequest, user: cm.User = Depends(get_current_user)):
    """
    Generate a custom sticker from a natural language prompt.
    Costs 1 credit. Describe your sticker in any language.
    """
    if not req.prompt or len(req.prompt.strip()) < 3:
        raise HTTPException(status_code=400, detail="Prompt must be at least 3 characters")
    if len(req.prompt) > 500:
        raise HTTPException(status_code=400, detail="Prompt must be 500 characters or less")

    # Check and deduct credits first
    if not cm.deduct_credit(user.user_id):
        raise HTTPException(
            status_code=402,
            detail={
                "error": "Insufficient credits",
                "credits": user.credits,
                "buy_credits_url": "/api/buy",
                "packages": cm.CREDIT_PACKAGES,
            }
        )

    # Interpret prompt with Claude
    try:
        design_params = interpret_prompt(req.prompt)
    except Exception as e:
        # Refund the credit if Claude fails
        cm.add_credits(user.user_id, "starter")  # Not ideal; in prod use transaction
        raise HTTPException(status_code=500, detail=f"AI interpretation failed: {str(e)}")

    # Generate the sticker
    sticker_id = str(uuid.uuid4())
    filename = f"{sticker_id}.png"

    try:
        output_path = generate_sticker(design_params, filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sticker generation failed: {str(e)}")

    # Record the generation
    cm.record_generation(user.user_id, req.prompt, design_params.design_type, output_path)

    return {
        "sticker_id": sticker_id,
        "design_type": design_params.design_type,
        "mood": design_params.mood,
        "reasoning": design_params.reasoning,
        "download_url": f"/api/stickers/{sticker_id}",
        "credits_remaining": user.credits - 1,
    }


@app.get("/api/stickers/{sticker_id}")
async def download_sticker(sticker_id: str, user: cm.User = Depends(get_current_user)):
    """Download a generated sticker by ID."""
    # Validate ID format to prevent path traversal
    if not all(c.isalnum() or c == '-' for c in sticker_id):
        raise HTTPException(status_code=400, detail="Invalid sticker ID")

    path = Path(OUTPUT_DIR) / f"{sticker_id}.png"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Sticker not found")

    return FileResponse(
        path=str(path),
        media_type="image/png",
        filename=f"sticker_{sticker_id}.png",
    )


@app.post("/api/buy")
async def buy_credits(req: BuyRequest, user: cm.User = Depends(get_current_user)):
    """
    Purchase a credit package. In production, integrate with Stripe.
    Currently simulates the purchase for demo purposes.
    """
    if req.package not in cm.CREDIT_PACKAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown package. Available: {list(cm.CREDIT_PACKAGES.keys())}"
        )

    pkg = cm.CREDIT_PACKAGES[req.package]

    # In production: create Stripe checkout session and return URL
    # For demo: simulate successful purchase
    new_balance = cm.add_credits(user.user_id, req.package)

    return {
        "success": True,
        "package": req.package,
        "credits_added": pkg["credits"],
        "amount_charged_usd": pkg["price_usd"],
        "new_balance": new_balance,
        "message": f"Added {pkg['credits']} credits. New balance: {new_balance}",
        # In production, return: "checkout_url": stripe_session.url
    }


@app.post("/api/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe payment webhooks to add credits after successful payment."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    # Verify Stripe signature
    if STRIPE_WEBHOOK_SECRET:
        try:
            expected_sig = hmac.new(
                STRIPE_WEBHOOK_SECRET.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(f"sha256={expected_sig}", sig_header):
                raise HTTPException(status_code=400, detail="Invalid signature")
        except Exception:
            raise HTTPException(status_code=400, detail="Signature verification failed")

    event = json.loads(payload)

    if event.get("type") == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("metadata", {}).get("user_id")
        package = session.get("metadata", {}).get("package")
        stripe_payment_id = session.get("payment_intent")

        if user_id and package:
            cm.add_credits(user_id, package, stripe_payment_id)

    return {"received": True}


@app.get("/api/packages")
async def list_packages():
    """List available credit packages and pricing."""
    return {
        "free_on_signup": cm.FREE_DAILY_CREDITS,
        "credits_per_sticker": cm.CREDITS_PER_STICKER,
        "packages": cm.CREDIT_PACKAGES,
    }
