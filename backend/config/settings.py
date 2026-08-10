from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class SSHSettings:
    host: str
    port: int
    username: str
    auth_method: str
    private_key_path: str | None = None
    password: str | None = None

    @classmethod
    def from_env(cls) -> "SSHSettings":
        host = os.getenv("SSH_HOST", "").strip()
        port_value = os.getenv("SSH_PORT", "22").strip()
        username = os.getenv("SSH_USERNAME", "").strip()
        auth_method = os.getenv("SSH_AUTH_METHOD", "key").strip().lower()
        private_key_path = os.getenv("SSH_PRIVATE_KEY_PATH", "").strip() or None
        password = os.getenv("SSH_PASSWORD", "").strip() or None

        if not host or not username:
            raise ValueError("SSH_HOST and SSH_USERNAME must be set")

        if auth_method not in {"key", "password"}:
            raise ValueError("SSH_AUTH_METHOD must be either 'key' or 'password'")

        if auth_method == "key" and not private_key_path:
            raise ValueError("SSH_PRIVATE_KEY_PATH must be set when SSH_AUTH_METHOD=key")

        if auth_method == "password" and not password:
            raise ValueError("SSH_PASSWORD must be set when SSH_AUTH_METHOD=password")

        return cls(
            host=host,
            port=int(port_value),
            username=username,
            auth_method=auth_method,
            private_key_path=private_key_path,
            password=password,
        )
