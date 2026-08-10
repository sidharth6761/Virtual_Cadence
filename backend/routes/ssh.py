from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from backend.config.settings import SSHSettings
from backend.services.ssh_service import SSHConnectionError, SSHService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["ssh"])


@router.get("/test-connection")
def test_connection() -> dict[str, Any]:
    try:
        settings = SSHSettings.from_env()
    except ValueError as error:
        logger.error("SSH configuration error: %s", error)
        raise HTTPException(status_code=500, detail=str(error)) from error

    service = SSHService(settings)

    try:
        whoami_result = service.run_command("whoami")
        pwd_result = service.run_command("pwd")
    except SSHConnectionError as error:
        logger.exception("SSH connection test failed")
        raise HTTPException(status_code=502, detail=str(error)) from error

    return {
        "success": True,
        "username": whoami_result["output"],
        "working_directory": pwd_result["output"],
        "host": settings.host,
        "message": "SSH connection established successfully.",
    }
