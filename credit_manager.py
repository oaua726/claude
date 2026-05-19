"""
Credit management system for the sticker generation service.
Handles user registration, credit tracking, and monetization.
"""

import sqlite3
import uuid
import hashlib
import time
from dataclasses import dataclass
from contextlib import contextmanager


DB_PATH = "sticker_service.db"

FREE_DAILY_CREDITS = 3
CREDIT_PACKAGES = {
    "starter": {"credits": 20, "price_usd": 4.99},
    "pro": {"credits": 100, "price_usd": 14.99},
    "unlimited_monthly": {"credits": 9999, "price_usd": 29.99},
}
CREDITS_PER_STICKER = 1


@dataclass
class User:
    user_id: str
    api_key: str
    email: str
    credits: int
    total_generated: int
    created_at: float


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                api_key TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                credits INTEGER DEFAULT 0,
                total_generated INTEGER DEFAULT 0,
                daily_free_used INTEGER DEFAULT 0,
                last_free_reset TEXT DEFAULT '',
                created_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS generations (
                gen_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                prompt TEXT NOT NULL,
                design_type TEXT NOT NULL,
                output_path TEXT,
                credits_used INTEGER DEFAULT 1,
                created_at REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS payments (
                payment_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                package TEXT NOT NULL,
                credits_added INTEGER NOT NULL,
                amount_usd REAL NOT NULL,
                stripe_payment_id TEXT,
                created_at REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """)


def _generate_api_key(email: str) -> str:
    raw = f"{email}{uuid.uuid4()}{time.time()}"
    return "sk_" + hashlib.sha256(raw.encode()).hexdigest()[:32]


def register_user(email: str) -> User:
    with get_db() as conn:
        existing = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        if existing:
            raise ValueError(f"Email already registered: {email}")

        user_id = str(uuid.uuid4())
        api_key = _generate_api_key(email)
        now = time.time()

        conn.execute(
            """INSERT INTO users (user_id, api_key, email, credits, total_generated, created_at)
               VALUES (?, ?, ?, ?, 0, ?)""",
            (user_id, api_key, email, FREE_DAILY_CREDITS, now)
        )

        return User(
            user_id=user_id,
            api_key=api_key,
            email=email,
            credits=FREE_DAILY_CREDITS,
            total_generated=0,
            created_at=now,
        )


def get_user_by_api_key(api_key: str) -> User | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE api_key = ?", (api_key,)
        ).fetchone()
        if not row:
            return None

        # Reset daily free credits if new day
        import datetime
        today = datetime.date.today().isoformat()
        if row["last_free_reset"] != today:
            conn.execute(
                "UPDATE users SET daily_free_used = 0, last_free_reset = ? WHERE user_id = ?",
                (today, row["user_id"])
            )
            credits = row["credits"]
        else:
            credits = row["credits"]

        return User(
            user_id=row["user_id"],
            api_key=row["api_key"],
            email=row["email"],
            credits=credits,
            total_generated=row["total_generated"],
            created_at=row["created_at"],
        )


def deduct_credit(user_id: str) -> bool:
    """Deduct one credit. Returns False if insufficient credits."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT credits FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        if not row or row["credits"] < CREDITS_PER_STICKER:
            return False

        conn.execute(
            "UPDATE users SET credits = credits - ?, total_generated = total_generated + 1 WHERE user_id = ?",
            (CREDITS_PER_STICKER, user_id)
        )
        return True


def refund_credit(user_id: str) -> None:
    """Return one credit when generation fails after deduction."""
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET credits = credits + ?, total_generated = total_generated - 1 WHERE user_id = ?",
            (CREDITS_PER_STICKER, user_id)
        )


def record_generation(user_id: str, prompt: str, design_type: str, output_path: str) -> str:
    gen_id = str(uuid.uuid4())
    with get_db() as conn:
        conn.execute(
            """INSERT INTO generations (gen_id, user_id, prompt, design_type, output_path, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (gen_id, user_id, prompt, design_type, output_path, time.time())
        )
    return gen_id


def add_credits(user_id: str, package: str, stripe_payment_id: str | None = None) -> int:
    """Add credits from a package purchase. Returns new credit balance."""
    if package not in CREDIT_PACKAGES:
        raise ValueError(f"Unknown package: {package}")

    pkg = CREDIT_PACKAGES[package]
    payment_id = str(uuid.uuid4())

    with get_db() as conn:
        conn.execute(
            "UPDATE users SET credits = credits + ? WHERE user_id = ?",
            (pkg["credits"], user_id)
        )
        conn.execute(
            """INSERT INTO payments (payment_id, user_id, package, credits_added, amount_usd, stripe_payment_id, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (payment_id, user_id, package, pkg["credits"], pkg["price_usd"], stripe_payment_id, time.time())
        )
        row = conn.execute("SELECT credits FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return row["credits"]


def get_user_stats(user_id: str) -> dict:
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        recent_gens = conn.execute(
            "SELECT * FROM generations WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
            (user_id,)
        ).fetchall()

        return {
            "credits": user["credits"],
            "total_generated": user["total_generated"],
            "recent_generations": [dict(g) for g in recent_gens],
        }
