from __future__ import annotations

import logging
from typing import Any

import paramiko

from backend.config.settings import SSHSettings

logger = logging.getLogger(__name__)


class SSHConnectionError(Exception):
    """Raised when the SSH connection cannot be established or commands fail."""


class SSHService:
    def __init__(self, settings: SSHSettings) -> None:
        self.settings = settings

    def connect(self) -> paramiko.SSHClient:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            if self.settings.auth_method == "key":
                if not self.settings.private_key_path:
                    raise SSHConnectionError("SSH private key path is not configured")
                client.connect(
                    hostname=self.settings.host,
                    port=self.settings.port,
                    username=self.settings.username,
                    key_filename=self.settings.private_key_path,
                    timeout=10,
                    banner_timeout=10,
                )
            else:
                if not self.settings.password:
                    raise SSHConnectionError("SSH password is not configured")
                client.connect(
                    hostname=self.settings.host,
                    port=self.settings.port,
                    username=self.settings.username,
                    password=self.settings.password,
                    timeout=10,
                    banner_timeout=10,
                )
        except (paramiko.AuthenticationException, paramiko.SSHException, OSError) as error:
            logger.exception("SSH connection failed for %s@%s", self.settings.username, self.settings.host)
            raise SSHConnectionError(str(error)) from error

        return client

    def disconnect(self, client: paramiko.SSHClient) -> None:
        try:
            client.close()
        except Exception as error:  # pragma: no cover - defensive cleanup
            logger.warning("Failed to close SSH client cleanly: %s", error)

    def run_command(self, command: str) -> dict[str, Any]:
        client = self.connect()
        try:
            _, stdout, stderr = client.exec_command(command, timeout=10)
            stdout_text = stdout.read().decode("utf-8", errors="replace").strip()
            stderr_text = stderr.read().decode("utf-8", errors="replace").strip()
            exit_status = stdout.channel.recv_exit_status()

            if exit_status != 0:
                raise SSHConnectionError(stderr_text or f"Command failed with exit status {exit_status}")

            return {
                "success": True,
                "output": stdout_text,
                "command": command,
            }
        except SSHConnectionError:
            raise
        except Exception as error:  # pragma: no cover - defensive cleanup
            logger.exception("SSH command execution failed: %s", command)
            raise SSHConnectionError(str(error)) from error
        finally:
            self.disconnect(client)
