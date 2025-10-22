"""
Simplified Export Service
Creates lightweight JSON exports of job results.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime

from ..database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class ExportService:
    """Generate JSON exports of job results for download or delivery."""

    def __init__(self, db: Optional[DatabaseConnection] = None):
        self.db = db or DatabaseConnection()

    async def export_job_results(self, job_id: str) -> Dict[str, Any]:
        """
        Produce a JSON representation of the companies and contacts associated with a job.
        The export is stored in-memory and returned to the caller.
        """
        companies = await self.db.fetch_all(
            """
            SELECT *
            FROM companies
            WHERE job_id = $1
            ORDER BY fit_score DESC, discovery_confidence DESC
            """,
            job_id,
        )

        company_ids = [row["id"] for row in companies]
        contacts = []
        if company_ids:
            contacts = await self.db.fetch_all(
                """
                SELECT *
                FROM contacts
                WHERE company_id = ANY($1::uuid[])
                ORDER BY fit_score DESC, email_confidence DESC
                """,
                company_ids,
            )

        export_payload = {
            "job_id": job_id,
            "generated_at": datetime.utcnow().isoformat(),
            "companies": companies,
            "contacts": contacts,
        }

        logger.info("Generated export for job %s containing %d companies and %d contacts", job_id, len(companies), len(contacts))

        return {
            "format": "json",
            "content": json.dumps(export_payload, default=str),
            "record_count": len(companies) + len(contacts),
        }
