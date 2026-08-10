from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.app.core.security import create_access_token, hash_password, verify_password
from backend.app.database.db import get_connection
from backend.app.schemas.auth import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


@router.post("/register", response_model=TokenResponse)
def register_user(payload: UserRegisterRequest) -> TokenResponse:
    conn = get_connection()
    try:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (str(payload.email),)).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        created_at = datetime.now(timezone.utc).isoformat()
        password_hash = hash_password(payload.password)
        cursor = conn.execute(
            "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
            (str(payload.email), password_hash, created_at),
        )
        conn.commit()
        user_id = int(cursor.lastrowid)
        token = create_access_token(user_id)
        return TokenResponse(
            access_token=token,
            user=UserResponse(id=user_id, email=str(payload.email), created_at=created_at),
        )
    finally:
        conn.close()


@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLoginRequest) -> TokenResponse:
    conn = get_connection()
    try:
        user = conn.execute("SELECT id, password_hash, email, created_at FROM users WHERE email = ?", (str(payload.email),)).fetchone()
        if not user or not verify_password(payload.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token(int(user["id"]))
        return TokenResponse(
            access_token=token,
            user=UserResponse(id=int(user["id"]), email=user["email"], created_at=user["created_at"]),
        )
    finally:
        conn.close()


@router.get("/me", response_model=UserResponse)
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    from backend.app.core.security import decode_access_token

    conn = get_connection()
    try:
        token_payload = decode_access_token(credentials.credentials)
        user_id = int(token_payload["sub"])
        user = conn.execute("SELECT id, email, created_at FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(id=int(user["id"]), email=user["email"], created_at=user["created_at"])
    except Exception as error:
        raise HTTPException(status_code=401, detail="Invalid token") from error
    finally:
        conn.close()
