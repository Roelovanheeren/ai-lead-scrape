"""
Simplified Outreach Generator
Generates outreach messages using the real_research helper.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from ..database.connection import DatabaseConnection
from ..models.schemas import OutreachContentResponse, OutreachChannel
from .real_research import generate_personalized_outreach

logger = logging.getLogger(__name__)


class OutreachGenerator:
    """Generate outreach content for contacts."""

    def __init__(self, db: Optional[DatabaseConnection] = None):
        self.db = db or DatabaseConnection()

    async def generate_company_outreach(self, company_id: str) -> List[OutreachContentResponse]:
        contacts = await self.db.fetch_all(
            "SELECT * FROM contacts WHERE company_id = $1",
            company_id,
        )
        company = await self.db.fetch_one(
            "SELECT * FROM companies WHERE id = $1",
            company_id,
        )

        if not company or not contacts:
            logger.info("No contacts/company found for outreach generation (company_id=%s)", company_id)
            return []

        generated: List[OutreachContentResponse] = []
        for contact in contacts:
            outreach_payload = await generate_personalized_outreach(
                {
                    "company": company,
                    "contact": contact,
                }
            )

            content_id = str(uuid.uuid4())
            payload = {
                "id": content_id,
                "company_id": company_id,
                "contact_id": contact["id"],
                "channel": OutreachChannel.LINKEDIN.value,
                "subject": outreach_payload.get("email_subject"),
                "body": outreach_payload.get("email_body"),
                "tone": "professional",
                "word_count": len((outreach_payload.get("email_body") or "").split()),
                "qa_feedback": None,
                "quality_score": 0.0,
                "status": "draft",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            await self.db.execute(
                """
                INSERT INTO outreach_content (
                    id, company_id, contact_id, channel, subject, body,
                    tone, word_count, qa_feedback, quality_score, status, created_at, updated_at
                )
                VALUES (
                    $1, $2, $3, $4, $5, $6,
                    $7, $8, $9, $10, $11, $12, $13
                )
                ON CONFLICT (id) DO NOTHING
                """,
                payload["id"],
                payload["company_id"],
                payload["contact_id"],
                payload["channel"],
                payload["subject"],
                payload["body"],
                payload["tone"],
                payload["word_count"],
                payload["qa_feedback"],
                payload["quality_score"],
                payload["status"],
                payload["created_at"],
                payload["updated_at"],
            )

            generated.append(
                OutreachContentResponse(
                    **{
                        "id": payload["id"],
                        "company_id": payload["company_id"],
                        "contact_id": payload["contact_id"],
                        "channel": payload["channel"],
                        "subject": payload["subject"],
                        "body": payload["body"],
                        "tone": payload["tone"],
                        "word_count": payload["word_count"],
                        "qa_feedback": payload["qa_feedback"],
                        "quality_score": payload["quality_score"],
                        "status": payload["status"],
                        "created_at": payload["created_at"],
                        "updated_at": payload["updated_at"],
                    }
                )
            )

        return generated

    async def get_outreach_content(
        self,
        company_id: str,
        channel: Optional[str] = None,
    ) -> List[OutreachContentResponse]:
        if channel:
            rows = await self.db.fetch_all(
                """
                SELECT * FROM outreach_content
                WHERE company_id = $1 AND channel = $2
                ORDER BY created_at DESC
                """,
                company_id,
                channel,
            )
        else:
            rows = await self.db.fetch_all(
                """
                SELECT * FROM outreach_content
                WHERE company_id = $1
                ORDER BY created_at DESC
                """,
                company_id,
            )

        return [
            OutreachContentResponse(
                **{
                    "id": row["id"],
                    "company_id": row["company_id"],
                    "contact_id": row.get("contact_id"),
                    "channel": row.get("channel"),
                    "subject": row.get("subject"),
                    "body": row.get("body"),
                    "tone": row.get("tone"),
                    "word_count": row.get("word_count"),
                    "qa_feedback": row.get("qa_feedback"),
                    "quality_score": float(row.get("quality_score") or 0.0),
                    "status": row.get("status"),
                    "created_at": row.get("created_at"),
                    "updated_at": row.get("updated_at"),
                }
            )
            for row in rows
        ]
