from __future__ import annotations

from pydantic import BaseModel, Field


class JobCreateRequest(BaseModel):
    project_id: int


class JobResponse(BaseModel):
    id: int
    project_id: int
    status: str
    created_at: str
    updated_at: str
    job_id: str


class JobDetailResponse(JobResponse):
    pass
