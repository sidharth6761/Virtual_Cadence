from __future__ import annotations

import io
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import HTTPException, UploadFile

from backend.app.core.config import settings
from backend.app.services.cloud_storage import CloudStorageAdapter

SUPPORTED_EXTENSIONS = {".v", ".sv", ".sdc", ".lib"}


class StorageService:
    def __init__(self, base_path: Path | None = None) -> None:
        settings.refresh()
        self.base_path = (base_path or settings.storage_path).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.cloud_adapter = CloudStorageAdapter(settings.storage_provider)
        if settings.storage_provider != "local" and self.cloud_adapter.provider != settings.storage_provider:
            raise RuntimeError(f"Unsupported storage provider: {settings.storage_provider}")

    def _resolve_base_path(self) -> Path:
        settings.refresh()
        return settings.storage_path

    def ensure_job_dir(self, job_id: str) -> Path:
        job_dir = self.base_path / "jobs" / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        return job_dir

    def save_upload(self, job_id: str, upload_file: UploadFile) -> str:
        filename = Path(upload_file.filename or "").name
        if not filename:
            raise HTTPException(status_code=400, detail="Uploaded file is missing a filename")

        self.validate_supported_file(filename)
        object_key = f"jobs/{job_id}/{filename}"
        try:
            if settings.storage_provider == "local":
                destination = self.base_path / "jobs" / job_id / filename
                destination.parent.mkdir(parents=True, exist_ok=True)
                with destination.open("wb") as target:
                    shutil.copyfileobj(upload_file.file, target)
            else:
                upload_file.file.seek(0)
                self.cloud_adapter.save_file(object_key, upload_file.file)
        except OSError as error:
            raise HTTPException(status_code=500, detail=f"Failed to save '{filename}': {error}") from error
        except NotImplementedError as error:
            raise HTTPException(status_code=501, detail=str(error)) from error
        return object_key

    def validate_supported_file(self, filename: str) -> None:
        if Path(filename).suffix.lower() not in SUPPORTED_EXTENSIONS:
            allowed = ", ".join(sorted(SUPPORTED_EXTENSIONS))
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {filename}. Allowed types: {allowed}")

    def list_files(self, job_id: str) -> list[str]:
        if settings.storage_provider != "local":
            return []
        job_dir = self.base_path / "jobs" / job_id
        if not job_dir.exists():
            return []
        return [path.name for path in sorted(job_dir.iterdir()) if path.is_file()]

    def save_metadata_file(self, job_id: str, content: str) -> str:
        object_key = f"jobs/{job_id}/metadata.json"
        if settings.storage_provider == "local":
            destination = self.base_path / "jobs" / job_id / "metadata.json"
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")
        else:
            self.cloud_adapter.save_file(object_key, io.BytesIO(content.encode("utf-8")))
        return object_key

    def get_file_path(self, job_id: str, filename: str) -> Path:
        return self.base_path / "jobs" / job_id / filename

    def delete_job_files(self, job_id: str) -> None:
        if settings.storage_provider == "local":
            shutil.rmtree(self.base_path / "jobs" / job_id, ignore_errors=True)
            return
        self.cloud_adapter.delete_file(f"jobs/{job_id}")


storage_service = StorageService()
