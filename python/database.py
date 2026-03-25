# database.py
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable, Iterator, Optional, Sequence

# Database stored locally in the project directory: ./db/gym.db
BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / ".." / "db"
DB_PATH = str(DB_DIR / "gym.db")


class DB:
    """sqlite3 wrapper with transactions and row_factory=sqlite3.Row."""
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")

    def fetch_all(self, sql: str, params: Sequence[Any] = ()) -> list[sqlite3.Row]:
        return self.conn.execute(sql, params).fetchall()

    def fetch_one(self, sql: str, params: Sequence[Any] = ()) -> Optional[sqlite3.Row]:
        return self.conn.execute(sql, params).fetchone()

    def execute(self, sql: str, params: Sequence[Any] = ()) -> sqlite3.Cursor:
        return self.conn.execute(sql, params)

    def executemany(self, sql: str, seq_params: Iterable[Sequence[Any]]) -> sqlite3.Cursor:
        return self.conn.executemany(sql, seq_params)

    def executescript(self, script: str) -> None:
        self.conn.executescript(script)

    def commit(self) -> None:
        self.conn.commit()

    def rollback(self) -> None:
        self.conn.rollback()

    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass

    @contextmanager
    def tx(self) -> Iterator["DB"]:
        try:
            yield self
            self.commit()
        except Exception:
            self.rollback()
            raise


def ensure_db_has_schema(db: DB, ddl_path: str | None = None) -> None:
    """
    If the database is empty (no user tables) and ddl_path is provided,
    execute the DDL (for example, the schema.sql file).
    """
    row = db.fetch_one("SELECT COUNT(*) AS n FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    if row and int(row["n"]) > 0:
        return
    if not ddl_path:
        return
    ddl = Path(ddl_path).read_text(encoding="utf-8", errors="replace")
    db.executescript(ddl)
    db.commit()