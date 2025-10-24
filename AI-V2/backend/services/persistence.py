from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from backend.core.settings import get_settings


@dataclass
class JobRecord:
    job_id: str
    status: str
    prompt: str
    target_count: int
    leads: List[Dict[str, Any]]
    raw_response: Dict[str, Any]


class PersistenceService:
    def __init__(self) -> None:
        settings = get_settings()
        db_url = settings.database_url
        if not db_url.startswith("sqlite:///"):
            raise ValueError("Only sqlite is supported in this minimal persistence service")
        path = db_url.replace("sqlite:///", "")
        self.db_path = Path(path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    status TEXT,
                    prompt TEXT,
                    target_count INTEGER,
                    leads_json TEXT,
                    raw_response_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT,
                    level TEXT,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def save_job(self, record: JobRecord) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO jobs (job_id, status, prompt, target_count, leads_json, raw_response_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record.job_id,
                    record.status,
                    record.prompt,
                    record.target_count,
                    json.dumps(record.leads, ensure_ascii=False),
                    json.dumps(record.raw_response, ensure_ascii=False),
                ),
            )

    def load_job(self, job_id: str) -> Dict[str, Any] | None:
        with self._connection() as conn:
            cur = conn.execute(
                "SELECT job_id, status, prompt, target_count, leads_json, raw_response_json, created_at FROM jobs WHERE job_id = ?",
                (job_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return {
                "job_id": row[0],
                "status": row[1],
                "prompt": row[2],
                "target_count": row[3],
                "leads": json.loads(row[4]) if row[4] else [],
                "raw_response": json.loads(row[5]) if row[5] else {},
                "created_at": row[6],
            }

    def append_log(self, job_id: str, level: str, message: str) -> None:
        with self._connection() as conn:
            conn.execute(
                "INSERT INTO logs (job_id, level, message) VALUES (?, ?, ?)",
                (job_id, level.upper(), message),
            )

    def fetch_logs(self, job_id: str, limit: int = 200) -> List[Dict[str, Any]]:
        with self._connection() as conn:
            cur = conn.execute(
                "SELECT level, message, created_at FROM logs WHERE job_id = ? ORDER BY id DESC LIMIT ?",
                (job_id, limit),
            )
            return [
                {"level": row[0], "message": row[1], "created_at": row[2]}
                for row in cur.fetchall()
            ]
