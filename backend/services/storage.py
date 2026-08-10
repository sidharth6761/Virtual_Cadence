from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException, UploadFile

from backend.models.upload import JobMetadata

ROOT_UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
SUPPORTED_EXTENSIONS = {".v", ".sv", ".sdc", ".lib"}


def get_next_job_id() -> str:
    """Generate the next local sequential Job ID like Job_0001."""
    ROOT_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    existing_job_numbers: list[int] = []
    for entry in ROOT_UPLOAD_DIR.iterdir():
        if not entry.is_dir() or not entry.name.startswith("Job_"):
            continue

        suffix = entry.name.split("_", 1)[1]
        try:
            existing_job_numbers.append(int(suffix))
        except ValueError:
            continue

    next_number = max(existing_job_numbers, default=0) + 1
    return f"Job_{next_number:04d}"


def create_job_directory() -> tuple[str, Path]:
    job_id = get_next_job_id()
    job_dir = ROOT_UPLOAD_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=False)
    return job_id, job_dir


def validate_supported_file(filename: str) -> None:
    if Path(filename).suffix.lower() not in SUPPORTED_EXTENSIONS:
        allowed = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {filename}. Allowed types: {allowed}")


def save_upload(file: UploadFile, destination: Path) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with destination.open("wb") as target:
            shutil.copyfileobj(file.file, target)
    except OSError as error:
        raise HTTPException(status_code=500, detail=f"Failed to save '{file.filename or destination.name}': {error}")

    return destination.name


def persist_job_metadata(job_dir: Path, metadata: JobMetadata) -> None:
    metadata_path = job_dir / "metadata.json"
    metadata_path.write_text(metadata.model_dump_json(indent=2), encoding="utf-8")
