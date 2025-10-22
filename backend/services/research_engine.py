"""
Simplified Research Engine Service
Builds company profiles using the real_research module.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from ..database.connection import DatabaseConnection
from ..models.schemas import (
    CompanyProfileResponse,
    ResearchSummary,
    PainPoints,
    GrowthSignals,
    TechStack,
    BuyingTriggers,
)
from .real_research import research_company_deep

logger = logging.getLogger(__name__)


class ResearchEngine:
    """Create and persist deep company research profiles."""

    def __init__(self, db: Optional[DatabaseConnection] = None):
        self.db = db or DatabaseConnection()

    async def research_company(self, company_id: str) -> Optional[CompanyProfileResponse]:
        company = await self.db.fetch_one("SELECT * FROM companies WHERE id = $1", company_id)
        if not company:
            logger.warning("Cannot research company %s: record not found", company_id)
            return None

        research_data = await research_company_deep(company)
        if not research_data:
            logger.warning("No research data returned for company %s", company_id)
            return None

        profile_id = str(uuid.uuid4())
        payload = {
            "id": profile_id,
            "company_id": company_id,
            "research_summary": research_data.get("research_summary"),
            "pain_points": research_data.get("pain_points"),
            "growth_signals": research_data.get("growth_signals"),
            "tech_stack": research_data.get("tech_stack"),
            "buying_triggers": research_data.get("buying_triggers"),
            "recent_investments": research_data.get("recent_investments"),
            "reasons_to_reach_out": research_data.get("reasons_to_reach_out"),
            "sources": research_data.get("sources"),
            "research_confidence": float(research_data.get("research_confidence") or 0.0),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        await self.db.execute(
            """
            INSERT INTO company_profiles (
                id, company_id, research_summary, pain_points, growth_signals,
                tech_stack, buying_triggers, recent_investments,
                reasons_to_reach_out, sources, research_confidence,
                created_at, updated_at
            )
            VALUES (
                $1, $2, $3, $4, $5,
                $6, $7, $8,
                $9, $10, $11,
                $12, $13
            )
            ON CONFLICT (company_id) DO UPDATE SET
                research_summary = EXCLUDED.research_summary,
                pain_points = EXCLUDED.pain_points,
                growth_signals = EXCLUDED.growth_signals,
                tech_stack = EXCLUDED.tech_stack,
                buying_triggers = EXCLUDED.buying_triggers,
                recent_investments = EXCLUDED.recent_investments,
                reasons_to_reach_out = EXCLUDED.reasons_to_reach_out,
                sources = EXCLUDED.sources,
                research_confidence = EXCLUDED.research_confidence,
                updated_at = EXCLUDED.updated_at
            """,
            payload["id"],
            payload["company_id"],
            payload["research_summary"],
            payload["pain_points"],
            payload["growth_signals"],
            payload["tech_stack"],
            payload["buying_triggers"],
            payload["recent_investments"],
            payload["reasons_to_reach_out"],
            payload["sources"],
            payload["research_confidence"],
            payload["created_at"],
            payload["updated_at"],
        )

    async def get_company_profile(self, company_id: str) -> Optional[CompanyProfileResponse]:
        row = await self.db.fetch_one(
            "SELECT * FROM company_profiles WHERE company_id = $1",
            company_id,
        )
        if not row:
            return None

        return CompanyProfileResponse(
            id=row["id"],
            company_id=row["company_id"],
            research_summary=self._as_model(ResearchSummary, row.get("research_summary")),
            pain_points=self._as_model(PainPoints, row.get("pain_points")),
            growth_signals=self._as_model(GrowthSignals, row.get("growth_signals")),
            tech_stack=self._as_model(TechStack, row.get("tech_stack")),
            buying_triggers=self._as_model(BuyingTriggers, row.get("buying_triggers")),
            recent_investments=row.get("recent_investments"),
            reasons_to_reach_out=row.get("reasons_to_reach_out"),
            sources=row.get("sources"),
            research_confidence=float(row.get("research_confidence") or 0.0),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )

    def _as_model(self, model, value: Any):
        if not value:
            return None
        if isinstance(value, model):
            return value
        if isinstance(value, dict):
            return model(**value)
        # asyncpg may return JSONB as dict already, but guard for strings.
        return model(**value)  # type: ignore[arg-type]
