from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

load_dotenv(BASE_DIR / '.env')


class Settings:
    def __init__(self) -> None:
        self.refresh()

    def refresh(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "") or os.getenv("DB_PATH", str(BASE_DIR / "backend" / "app.db"))
        self.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
        self.cors_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if origin.strip()]
        self.storage_path = Path(os.getenv("STORAGE_PATH", str(BASE_DIR / "storage"))).resolve()
        self.max_upload_size_mb = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
        self.storage_provider = os.getenv("STORAGE_PROVIDER", "local").strip().lower()


settings = Settings()
