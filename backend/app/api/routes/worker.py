from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/worker", tags=["worker"])


@router.get("/jobs/next")
def next_job() -> dict[str, str]:
    return {"message": "Worker API placeholder", "status": "not_implemented"}


@router.post("/jobs/{job_id}/status")
def update_job_status(job_id: str) -> dict[str, str]:
    return {"job_id": job_id, "status": "accepted"}


@router.post("/jobs/{job_id}/results")
def upload_job_results(job_id: str) -> dict[str, str]:
    return {"job_id": job_id, "message": "Results endpoint placeholder"}
