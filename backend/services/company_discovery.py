"""
Simplified Company Discovery Service
Uses the real_research module to locate companies and persists results.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..database.connection import DatabaseConnection
from ..models.schemas import CompanyResponse, CompanyAttributes
from .real_research import extract_targeting_criteria, search_companies

logger = logging.getLogger(__name__)


class CompanyDiscoveryService:
    """Discover companies for a job and store them in the database."""

    def __init__(self, db: Optional[DatabaseConnection] = None):
        self.db = db or DatabaseConnection()

    async def discover_companies(
        self,
        job_id: str,
        target_count: Optional[int] = None,
    ) -> List[CompanyResponse]:
        """
        Discover companies for the supplied job.

        Args:
            job_id: The job identifier.
            target_count: Optional override for the number of companies to fetch.
        """
        job = await self._get_job(job_id)
        if not job:
            logger.warning("Job %s not found while discovering companies", job_id)
            return []

        parameters = job.get("parameters") or {}
        prompt = job.get("prompt", "")

        # Ensure we have structured criteria to feed to the research engine.
        criteria = dict(parameters) if isinstance(parameters, dict) else {}
        if not criteria:
            logger.info("No structured parameters for job %s, extracting via AI fallback", job_id)
            criteria = await extract_targeting_criteria(prompt)
        criteria.setdefault("prompt", prompt)

        desired_count = target_count or job.get("target_count") or 25
        logger.info("Discovering up to %s companies for job %s", desired_count, job_id)

        raw_companies = await search_companies(criteria, desired_count)
        if not raw_companies:
            logger.warning("No companies returned for job %s", job_id)
            return []

        stored_companies: List[CompanyResponse] = []
        for company in raw_companies:
            record = await self._persist_company(job_id, company)
            if record:
                stored_companies.append(record)

        return stored_companies

    async def get_companies(
        self,
        job_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[CompanyResponse]:
        """Fetch companies already stored for a job."""
        rows = await self.db.fetch_all(
            """
            SELECT *
            FROM companies
            WHERE job_id = $1
            ORDER BY fit_score DESC, discovery_confidence DESC, created_at DESC
            LIMIT $2 OFFSET $3
            """,
            job_id,
            limit,
            offset,
        )
        return [CompanyResponse(**self._row_to_company(row)) for row in rows]

    async def refresh_company_data(self, company_id: str) -> Optional[CompanyResponse]:
        """
        Re-fetch company data using the research engine.
        Currently this simply re-runs the discovery pipeline for the single company.
        """
        company = await self.db.fetch_one(
            "SELECT * FROM companies WHERE id = $1",
            company_id,
        )
        if not company:
            logger.warning("Company %s not found during refresh", company_id)
            return None

        job_id = company["job_id"]
        job = await self._get_job(job_id)
        if not job:
            return None

        criteria = job.get("parameters") or {}
        criteria.setdefault("prompt", job.get("prompt", ""))

        refreshed = await search_companies(criteria, 1)
        if not refreshed:
            return CompanyResponse(**self._row_to_company(company))

        updated = await self._persist_company(job_id, refreshed[0], existing_id=company_id)
        return updated

    async def _get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.fetch_one(
            "SELECT id, prompt, parameters, target_count FROM jobs WHERE id = $1",
            job_id,
        )

    async def _persist_company(
        self,
        job_id: str,
        company_data: Dict[str, Any],
        existing_id: Optional[str] = None,
    ) -> Optional[CompanyResponse]:
        """
        Insert or update a company row.
        Only a subset of fields is required to get the pipeline running.
        """
        company_id = existing_id or str(uuid.uuid4())
        payload = {
            "id": company_id,
            "job_id": job_id,
            "name": company_data.get("name") or company_data.get("company_name"),
            "website": company_data.get("website"),
            "domain": company_data.get("domain"),
            "country": company_data.get("country"),
            "city": company_data.get("city"),
            "state": company_data.get("state"),
            "industry": company_data.get("industry"),
            "employee_count": company_data.get("employee_count"),
            "revenue_range": company_data.get("revenue_range"),
            "funding_stage": company_data.get("funding_stage"),
            "attributes": company_data.get("attributes"),
            "discovery_confidence": float(company_data.get("confidence", company_data.get("score", 0)) or 0.0),
            "fit_score": float(company_data.get("fit_score", 0.0) or 0.0),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        if not payload["name"]:
            logger.debug("Skipping company without name: %s", company_data)
            return None

        await self.db.execute(
            """
            INSERT INTO companies (
                id, job_id, name, website, domain, country, city, state,
                industry, employee_count, revenue_range, funding_stage,
                attributes, discovery_confidence, fit_score, created_at, updated_at
            )
            VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8,
                $9, $10, $11, $12,
                $13, $14, $15, $16, $17
            )
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                website = EXCLUDED.website,
                domain = EXCLUDED.domain,
                country = EXCLUDED.country,
                city = EXCLUDED.city,
                state = EXCLUDED.state,
                industry = EXCLUDED.industry,
                employee_count = EXCLUDED.employee_count,
                revenue_range = EXCLUDED.revenue_range,
                funding_stage = EXCLUDED.funding_stage,
                attributes = EXCLUDED.attributes,
                discovery_confidence = EXCLUDED.discovery_confidence,
                fit_score = EXCLUDED.fit_score,
                updated_at = EXCLUDED.updated_at
            """,
            payload["id"],
            payload["job_id"],
            payload["name"],
            payload["website"],
            payload["domain"],
            payload["country"],
            payload["city"],
            payload["state"],
            payload["industry"],
            payload["employee_count"],
            payload["revenue_range"],
            payload["funding_stage"],
            payload["attributes"],
            payload["discovery_confidence"],
            payload["fit_score"],
            payload["created_at"],
            payload["updated_at"],
        )

        # Fetch the stored row so we respect defaults computed by the database.
        row = await self.db.fetch_one(
            "SELECT * FROM companies WHERE id = $1",
            company_id,
        )
        return CompanyResponse(**self._row_to_company(row))

    def _row_to_company(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a DB row to the CompanyResponse schema payload."""
        attributes = row.get("attributes") or {}
        if attributes and not isinstance(attributes, dict):
            # asyncpg returns JSONB as dict already, but guard anyway.
            attributes = dict(attributes)

        return {
            "id": row["id"],
            "job_id": row["job_id"],
            "name": row["name"],
            "website": row.get("website"),
            "domain": row.get("domain"),
            "country": row.get("country"),
            "city": row.get("city"),
            "state": row.get("state"),
            "industry": row.get("industry"),
            "employee_count": row.get("employee_count"),
            "revenue_range": row.get("revenue_range"),
            "funding_stage": row.get("funding_stage"),
            "attributes": CompanyAttributes(**attributes) if attributes else None,
            "discovery_confidence": float(row.get("discovery_confidence") or 0.0),
            "fit_score": float(row.get("fit_score") or 0.0),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        }
