from __future__ import annotations

import io
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from fastapi import UploadFile

from backend.app.main import app
from backend.app.database.db import reset_database


@pytest.fixture(autouse=True)
def configure_test_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv("DB_PATH", str(tmp_path / "app.db"))
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path / "storage"))
    monkeypatch.setenv("MAX_UPLOAD_SIZE_MB", "1")
    reset_database()
    yield
    reset_database()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def test_register_and_login(client: TestClient) -> None:
    response = client.post(
        "/api/auth/register",
        json={"email": "alice@example.com", "password": "secret123"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["user"]["email"] == "alice@example.com"

    login_response = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "secret123"},
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


def test_auth_failure(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "missing@example.com", "password": "wrong"},
    )
    assert response.status_code == 401


def test_project_creation_and_listing(client: TestClient) -> None:
    token = client.post(
        "/api/auth/register",
        json={"email": "bob@example.com", "password": "secret123"},
    ).json()["access_token"]

    response = client.post(
        "/api/projects",
        json={"name": "Test Project"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    project_id = response.json()["id"]

    list_response = client.get(
        "/api/projects",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    assert any(item["id"] == project_id for item in list_response.json())


def test_unauthorized_project_access(client: TestClient) -> None:
    user_a_token = client.post(
        "/api/auth/register",
        json={"email": "carol@example.com", "password": "secret123"},
    ).json()["access_token"]
    user_b_token = client.post(
        "/api/auth/register",
        json={"email": "dave@example.com", "password": "secret123"},
    ).json()["access_token"]

    project_response = client.post(
        "/api/projects",
        json={"name": "Private Project"},
        headers={"Authorization": f"Bearer {user_a_token}"},
    )
    project_id = project_response.json()["id"]

    unauthorized_response = client.get(
        f"/api/projects/{project_id}",
        headers={"Authorization": f"Bearer {user_b_token}"},
    )
    assert unauthorized_response.status_code == 404


def test_job_creation_and_status(client: TestClient) -> None:
    token = client.post(
        "/api/auth/register",
        json={"email": "erin@example.com", "password": "secret123"},
    ).json()["access_token"]
    project_response = client.post(
        "/api/projects",
        json={"name": "Job Project"},
        headers={"Authorization": f"Bearer {token}"},
    )
    project_id = project_response.json()["id"]

    job_response = client.post(
        "/api/jobs",
        json={"project_id": project_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert job_response.status_code == 200
    job_id = job_response.json()["job_id"]

    details_response = client.get(
        f"/api/jobs/{job_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert details_response.status_code == 200
    assert details_response.json()["status"] == "CREATED"


def test_upload_flow_and_job_file_storage(client: TestClient) -> None:
    token = client.post(
        "/api/auth/register",
        json={"email": "frank@example.com", "password": "secret123"},
    ).json()["access_token"]

    response = client.post(
        "/upload",
        files=[
            ("design_files", ("top.v", b"module top(); endmodule\n", "text/plain")),
            ("library_file", ("std.lib", b"library(std){}\n", "text/plain")),
        ],
        data={"top_module": "top", "clock_period": 10},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["job_id"]


def test_invalid_file_type_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/upload",
        files=[("design_files", ("notes.txt", b"not supported", "text/plain"))],
        data={"top_module": "top", "clock_period": 10},
    )
    assert response.status_code == 400


def test_file_size_limit_is_enforced(client: TestClient) -> None:
    oversized_bytes = b"x" * (2 * 1024 * 1024)
    response = client.post(
        "/upload",
        files=[("design_files", ("big.v", oversized_bytes, "application/octet-stream"))],
        data={"top_module": "top", "clock_period": 10},
    )
    assert response.status_code == 413


def test_supabase_provider_requires_credentials(monkeypatch) -> None:
    monkeypatch.setenv("STORAGE_PROVIDER", "supabase")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_BUCKET_NAME", raising=False)

    from backend.app.services.storage_service import StorageService

    with pytest.raises(RuntimeError, match="Supabase"):
        StorageService()


def test_supabase_provider_uploads_to_bucket(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("STORAGE_PROVIDER", "supabase")
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role-key")
    monkeypatch.setenv("SUPABASE_BUCKET_NAME", "design-files")

    from backend.app.services.cloud_storage import CloudStorageAdapter

    adapter = CloudStorageAdapter("supabase")
    assert adapter.provider == "supabase"

    class FakeClient:
        def __init__(self) -> None:
            self.calls: list[dict[str, object]] = []
            self.service_key = "service-role-key"

        def request(self, method: str, path: str, *, headers: dict[str, str], body: bytes | None = None) -> dict[str, object]:
            self.calls.append({"method": method, "path": path, "headers": headers, "body": body})
            return {"status_code": 200}

    adapter.client = FakeClient()
    payload = b"module top(); endmodule\n"
    adapter.save_file("jobs/JOB_0001/top.v", io.BytesIO(payload))
    assert adapter.client.calls[0]["path"] == "/storage/v1/object/design-files/jobs/JOB_0001/top.v"
