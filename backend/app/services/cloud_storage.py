from __future__ import annotations

import os
from pathlib import Path
from typing import Any, BinaryIO


class CloudStorageAdapter:
    def __init__(self, provider: str | None = None) -> None:
        self.provider = (provider or os.getenv("STORAGE_PROVIDER", "local")).strip().lower()
        self.client = None
        if self.provider == "local":
            return
        if self.provider == "supabase":
            self._validate_supabase_settings()
            self.client = self._create_supabase_client()
            return
        raise RuntimeError(f"Unsupported storage provider: {self.provider}")

    def _validate_supabase_settings(self) -> None:
        required = ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_BUCKET_NAME"]
        missing = [name for name in required if not os.getenv(name)]
        if missing:
            raise RuntimeError("Supabase storage provider requires: " + ", ".join(missing))

    def _create_supabase_client(self) -> Any:
        class _SupabaseClient:
            def __init__(self, base_url: str, service_key: str) -> None:
                self.base_url = base_url.rstrip("/")
                self.service_key = service_key

            def request(self, method: str, path: str, *, headers: dict[str, str], body: bytes | None = None) -> dict[str, Any]:
                import urllib.request
                import urllib.error

                request = urllib.request.Request(
                    self.base_url + path,
                    data=body,
                    method=method,
                    headers=headers,
                )
                try:
                    with urllib.request.urlopen(request, timeout=10) as response:
                        payload = response.read()
                    return {"status_code": 200, "body": payload}
                except urllib.error.HTTPError as error:
                    payload = error.read()
                    raise RuntimeError(f"Supabase Storage request failed ({error.code}): {payload.decode('utf-8', errors='replace')}") from error

        return _SupabaseClient(
            os.getenv("SUPABASE_URL", ""),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
        )

    def _normalize_key(self, destination_path: str) -> str:
        normalized = destination_path.replace("\\", "/")
        if normalized.startswith("/"):
            normalized = normalized[1:]
        return normalized

    def save_file(self, destination_path: str, file_like: BinaryIO) -> None:
        if self.provider == "local":
            path = Path(destination_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("wb") as target:
                target.write(file_like.read())
            return

        if self.provider == "supabase" and self.client is not None:
            object_key = self._normalize_key(destination_path)
            bucket_name = os.getenv("SUPABASE_BUCKET_NAME", "")
            file_like.seek(0)
            payload = file_like.read()
            headers = {
                "Authorization": f"Bearer {self.client.service_key}",
                "apikey": self.client.service_key,
                "Content-Type": "application/octet-stream",
            }
            object_url = f"/storage/v1/object/{bucket_name}/{object_key}"
            try:
                self.client.request("POST", object_url, headers=headers, body=payload)
                return
            except RuntimeError as error:
                if "KeyAlreadyExists" not in str(error) and "409" not in str(error):
                    raise
                self.client.request(
                    "DELETE",
                    f"/storage/v1/object/{bucket_name}/{object_key}",
                    headers=headers,
                )
                self.client.request("POST", object_url, headers=headers, body=payload)
            return

        raise RuntimeError(f"Unsupported storage provider: {self.provider}")

    def get_file(self, object_key: str) -> bytes:
        if self.provider != "supabase" or self.client is None:
            raise RuntimeError("This operation is only available for the Supabase provider")
        bucket_name = os.getenv("SUPABASE_BUCKET_NAME", "")
        response = self.client.request(
            "GET",
            f"/storage/v1/object/{bucket_name}/{object_key}",
            headers={"Authorization": f"Bearer {self.client.service_key}"},
        )
        return response.get("body", b"")

    def delete_file(self, object_key: str) -> None:
        if self.provider != "supabase" or self.client is None:
            raise RuntimeError("This operation is only available for the Supabase provider")
        bucket_name = os.getenv("SUPABASE_BUCKET_NAME", "")
        self.client.request(
            "DELETE",
            f"/storage/v1/object/{bucket_name}/{object_key}",
            headers={"Authorization": f"Bearer {self.client.service_key}"},
        )

    def health_check(self) -> dict[str, object]:
        if self.provider != "supabase" or self.client is None:
            return {"provider": self.provider, "status": "available"}
        return {"provider": self.provider, "status": "connected"}
