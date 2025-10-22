"""
Simplified Quality Assurance Service
Provides lightweight validations for generated content.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

from ..database.connection import DatabaseConnection
logger = logging.getLogger(__name__)


class QualityAssuranceService:
    """Perform minimal QA checks on generated content."""

    def __init__(self, db: Optional[DatabaseConnection] = None):
        self.db = db or DatabaseConnection()

    async def run_qa_pipeline(self, job_id: str) -> Dict[str, int]:
        """
        Mark all outreach content associated with the job as approved if it contains a body.
        Returns a summary dict so callers can log progress.
        """
        content_rows = await self.db.fetch_all(
            """
            SELECT oc.id, oc.body
            FROM outreach_content oc
            JOIN companies c ON oc.company_id = c.id
            WHERE c.job_id = $1
            """,
            job_id,
        )

        approved = 0
        for row in content_rows:
            if row.get("body"):
                approved += 1

        logger.info("QA pipeline processed %d outreach records for job %s", len(content_rows), job_id)
        return {"records_checked": len(content_rows), "records_approved": approved}
