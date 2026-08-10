from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.jobs import router as jobs_router
from backend.app.api.routes.projects import router as projects_router
from backend.app.api.routes.storage import router as storage_router
from backend.app.api.routes.worker import router as worker_router
from backend.app.core.config import settings
from backend.services.storage import ROOT_UPLOAD_DIR
from backend.routes.upload import router as legacy_upload_router
from backend.routes.ssh import router as ssh_router

app = FastAPI(title="Virtual Cadence Cloud Backend", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(jobs_router)
app.include_router(storage_router)
app.include_router(worker_router)
app.include_router(legacy_upload_router)
app.include_router(ssh_router)


@app.on_event("startup")
def ensure_storage_root() -> None:
    ROOT_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    (settings.storage_path / "jobs").mkdir(parents=True, exist_ok=True)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
