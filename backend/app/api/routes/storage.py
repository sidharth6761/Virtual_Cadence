from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.app.core.config import settings
from backend.app.services.cloud_storage import CloudStorageAdapter

router = APIRouter(prefix="/api/storage", tags=["storage"])


@router.get("/health")
def storage_health() -> dict[str, str]:
    try:
        adapter = CloudStorageAdapter(settings.storage_provider)
        result = adapter.health_check()
        return {"provider": result["provider"], "status": result["status"]}
    except Exception as error:
        raise HTTPException(status_code=503, detail="Storage provider unavailable") from error
