from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any, Iterator

from backend.app.core.config import settings


def _use_postgres() -> bool:
    raw = (os.getenv("DATABASE_URL") or "").strip().lower()
    return raw.startswith("postgres://") or raw.startswith("postgresql://")


def get_database_path() -> Path | None:
    settings.refresh()
    return Path(settings.database_url).resolve() if settings.database_url else None


class _SqliteCursor:
    def __init__(self, cursor: sqlite3.Cursor) -> None:
        self._cursor = cursor

    @property
    def lastrowid(self) -> int:
        return int(self._cursor.lastrowid)

    def fetchone(self) -> dict[str, Any] | None:
        row = self._cursor.fetchone()
        return dict(row) if row is not None else None

    def fetchall(self) -> list[dict[str, Any]]:
        return [dict(row) for row in self._cursor.fetchall()]


class _SqliteConnection:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> _SqliteCursor:
        return _SqliteCursor(self._conn.execute(sql, params))

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def close(self) -> None:
        self._conn.close()


class _PostgresCursor:
    def __init__(self, cursor: Any) -> None:
        self._cursor = cursor
        self._lastrowid: int | None = None

    @property
    def lastrowid(self) -> int:
        return int(self._lastrowid or 0)

    def fetchone(self) -> dict[str, Any] | None:
        row = self._cursor.fetchone()
        return dict(row) if row is not None else None

    def fetchall(self) -> list[dict[str, Any]]:
        return [dict(row) for row in self._cursor.fetchall()]


class _PostgresConnection:
    def __init__(self, conn: Any) -> None:
        self._conn = conn

    def _cursor(self) -> Any:
        return self._conn.cursor(cursor_factory=__import__("psycopg2.extras", fromlist=["RealDictCursor"]).RealDictCursor)

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> _PostgresCursor:
        statement = sql.replace("?", "%s")
        if statement.lstrip().upper().startswith("INSERT") and "RETURNING" not in statement.upper():
            statement = statement.rstrip().rstrip(";") + " RETURNING id"
        cur = self._cursor()
        cur.execute(statement, list(params))
        result = _PostgresCursor(cur)
        if "RETURNING" in statement.upper():
            row = cur.fetchone()
            if row is not None:
                result._lastrowid = int(dict(row)["id"])
        return result

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def close(self) -> None:
        self._conn.close()


def get_connection() -> Any:
    if _use_postgres():
        try:
            import psycopg2
        except ImportError as error:
            raise RuntimeError(
                "database uses Postgres but psycopg2 is not installed. "
                "Run: pip install psycopg2-binary"
            ) from error
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        conn.autocommit = False
        return _PostgresConnection(conn)

    db_path = get_database_path()
    if db_path is None:
        raise RuntimeError("Database path is not configured")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return _SqliteConnection(conn)


def init_db() -> None:
    if _use_postgres():
        init_db_postgres()
        return
    init_db_sqlite()


def init_db_sqlite() -> None:
    conn = get_connection()
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            " id INTEGER PRIMARY KEY AUTOINCREMENT,"
            " email TEXT UNIQUE NOT NULL,"
            " password_hash TEXT NOT NULL,"
            " created_at TEXT NOT NULL)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS projects ("
            " id INTEGER PRIMARY KEY AUTOINCREMENT,"
            " user_id INTEGER,"
            " name TEXT NOT NULL,"
            " created_at TEXT NOT NULL,"
            " FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS jobs ("
            " id INTEGER PRIMARY KEY AUTOINCREMENT,"
            " project_id INTEGER NOT NULL,"
            " status TEXT NOT NULL,"
            " created_at TEXT NOT NULL,"
            " updated_at TEXT NOT NULL,"
            " FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS files ("
            " id INTEGER PRIMARY KEY AUTOINCREMENT,"
            " job_id INTEGER NOT NULL,"
            " filename TEXT NOT NULL,"
            " stored_name TEXT NOT NULL,"
            " created_at TEXT NOT NULL,"
            " FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE)"
        )
        conn.commit()
    finally:
        conn.close()


def init_db_postgres() -> None:
    conn = get_connection()
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            " id SERIAL PRIMARY KEY,"
            " email TEXT UNIQUE NOT NULL,"
            " password_hash TEXT NOT NULL,"
            " created_at TEXT NOT NULL)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS projects ("
            " id SERIAL PRIMARY KEY,"
            " user_id INTEGER,"
            " name TEXT NOT NULL,"
            " created_at TEXT NOT NULL,"
            " FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS jobs ("
            " id SERIAL PRIMARY KEY,"
            " project_id INTEGER NOT NULL,"
            " status TEXT NOT NULL,"
            " created_at TEXT NOT NULL,"
            " updated_at TEXT NOT NULL,"
            " FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS files ("
            " id SERIAL PRIMARY KEY,"
            " job_id INTEGER NOT NULL,"
            " filename TEXT NOT NULL,"
            " stored_name TEXT NOT NULL,"
            " created_at TEXT NOT NULL,"
            " FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE)"
        )
        conn.commit()
    finally:
        conn.close()


def reset_database() -> None:
    if _use_postgres():
        conn = get_connection()
        try:
            conn.execute("DROP TABLE IF EXISTS files")
            conn.execute("DROP TABLE IF EXISTS jobs")
            conn.execute("DROP TABLE IF EXISTS projects")
            conn.execute("DROP TABLE IF EXISTS users")
            conn.commit()
        finally:
            conn.close()
        init_db()
        return
    db_path = get_database_path()
    if db_path is None:
        return
    if db_path.exists():
        db_path.unlink()
    init_db()


init_db()