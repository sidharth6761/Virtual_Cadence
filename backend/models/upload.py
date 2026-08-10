from __future__ import annotations

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    success: bool = Field(default=True)
    job_id: str
    files_received: int
    upload_path: str


class JobMetadata(BaseModel):
    job_id: str
    created_at: str
    status: str = Field(default="Uploaded")
    files: list[str]
