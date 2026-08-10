from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from backend.app.core.config import settings


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 200_000)
    return f"pbkdf2_sha256$200000${salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    if not password_hash.startswith("pbkdf2_sha256"):
        return False
    _, iterations_text, salt, digest = password_hash.split("$", 3)
    iterations = int(iterations_text)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    return derived.hex() == digest


def create_access_token(subject: int) -> str:
    settings.refresh()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": int(expire.timestamp())}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    settings.refresh()
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
