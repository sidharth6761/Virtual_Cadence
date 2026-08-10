from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.app.core.security import decode_access_token
from backend.app.database.db import get_connection
from backend.app.schemas.project import ProjectCreateRequest, ProjectResponse

router = APIRouter(prefix="/api/projects", tags=["projects"])
security = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials) -> int:
    try:
        token_payload = decode_access_token(credentials.credentials)
        return int(token_payload["sub"])
    except Exception as error:
        raise HTTPException(status_code=401, detail="Invalid token") from error


@router.post("", response_model=ProjectResponse)
def create_project(payload: ProjectCreateRequest, credentials: HTTPAuthorizationCredentials = Depends(security)) -> ProjectResponse:
    user_id = get_current_user_id(credentials)
    conn = get_connection()
    try:
        created_at = datetime.now(timezone.utc).isoformat()
        cursor = conn.execute(
            "INSERT INTO projects (user_id, name, created_at) VALUES (?, ?, ?)",
            (user_id, payload.name, created_at),
        )
        conn.commit()
        return ProjectResponse(id=int(cursor.lastrowid), user_id=user_id, name=payload.name, created_at=created_at)
    finally:
        conn.close()


@router.get("", response_model=list[ProjectResponse])
def list_projects(credentials: HTTPAuthorizationCredentials = Depends(security)) -> list[ProjectResponse]:
    user_id = get_current_user_id(credentials)
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, user_id, name, created_at FROM projects WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
        return [ProjectResponse(id=int(row["id"]), user_id=int(row["user_id"]), name=row["name"], created_at=row["created_at"]) for row in rows]
    finally:
        conn.close()


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)) -> ProjectResponse:
    user_id = get_current_user_id(credentials)
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, user_id, name, created_at FROM projects WHERE id = ? AND user_id = ?",
            (project_id, user_id),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Project not found")
        return ProjectResponse(id=int(row["id"]), user_id=int(row["user_id"]), name=row["name"], created_at=row["created_at"])
    finally:
        conn.close()
