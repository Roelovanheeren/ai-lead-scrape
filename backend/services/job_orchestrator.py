"""
Simplified Job Orchestrator
Runs the high-level pipeline using the revised service layer.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import uuid

from ..database.connection import DatabaseConnection
from ..models.schemas import JobCreate, JobResponse, JobStatus, UsageAnalytics
from .company_discovery import CompanyDiscoveryService
from .contact_identification import ContactIdentificationService
from .research_engine import ResearchEngine
from .outreach_generator import OutreachGenerator
from .quality_assurance import QualityAssuranceService
from .export_service import ExportService

logger = logging.getLogger(__name__)


class JobOrchestrator:
    """Coordinate company discovery, contact identification, research, outreach, and QA."""

    def __init__(self, db: Optional[DatabaseConnection] = None):
        self.db = db or DatabaseConnection()
        self.company_discovery = CompanyDiscoveryService(self.db)
        self.contact_identification = ContactIdentificationService(self.db)
        self.research_engine = ResearchEngine(self.db)
        self.outreach_generator = OutreachGenerator(self.db)
        self.qa_service = QualityAssuranceService(self.db)
        self.export_service = ExportService(self.db)

    async def create_job(self, job_data: JobCreate) -> JobResponse:
        """Persist a new job."""
        job_id = str(uuid.uuid4())

        parameters = {**(job_data.parameters or {})}
        parsed_parameters = await self._parse_prompt(job_data.prompt)
        parameters = {**parsed_parameters, **parameters}

        await self.db.execute(
            """
            INSERT INTO jobs (
                id, prompt, parameters, status, vertical,
                target_count, quality_threshold, created_at, updated_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """,
            job_id,
            job_data.prompt,
            parameters,
            JobStatus.PENDING.value,
            job_data.vertical,
            job_data.target_count,
            job_data.quality_threshold,
            datetime.utcnow(),
            datetime.utcnow(),
        )

        row = await self.db.fetch_one(
            "SELECT * FROM jobs WHERE id = $1",
            job_id,
        )
        return JobResponse(**row)  # type: ignore[arg-type]

    async def process_job(self, job_id: str) -> None:
        """Execute the full pipeline for a job."""
        await self._update_job_status(job_id, JobStatus.RUNNING)

        try:
            companies = await self.company_discovery.discover_companies(job_id)
            for company in companies:
                await self.contact_identification.identify_contacts(company.id)
                await self.research_engine.research_company(company.id)
                await self.outreach_generator.generate_company_outreach(company.id)

            await self.qa_service.run_qa_pipeline(job_id)
            await self.export_service.export_job_results(job_id)

            await self._update_job_status(job_id, JobStatus.COMPLETED, completed=True)
            logger.info("Job %s completed successfully", job_id)
        except Exception as exc:
            logger.exception("Job %s failed: %s", job_id, exc)
            await self._update_job_status(job_id, JobStatus.FAILED)
            raise

    async def get_job(self, job_id: str) -> Optional[JobResponse]:
        row = await self.db.fetch_one(
            """
            SELECT j.*,
                   COUNT(DISTINCT c.id) AS companies_found,
                   COUNT(DISTINCT ct.id) AS contacts_found,
                   COUNT(DISTINCT oc.id) AS outreach_generated,
                   AVG(cp.research_confidence) AS quality_score
            FROM jobs j
            LEFT JOIN companies c ON j.id = c.job_id
            LEFT JOIN contacts ct ON c.id = ct.company_id
            LEFT JOIN outreach_content oc ON c.id = oc.company_id
            LEFT JOIN company_profiles cp ON c.id = cp.company_id
            WHERE j.id = $1
            GROUP BY j.id
            """,
            job_id,
        )
        return JobResponse(**row) if row else None  # type: ignore[arg-type]

    async def list_jobs(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[JobResponse]:
        clauses = []
        params: List[Any] = []

        if status:
            clauses.append("j.status = $1")
            params.append(status)

        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

        query = f"""
            SELECT j.*,
                   COUNT(DISTINCT c.id) AS companies_found,
                   COUNT(DISTINCT ct.id) AS contacts_found,
                   COUNT(DISTINCT oc.id) AS outreach_generated,
                   AVG(cp.research_confidence) AS quality_score
            FROM jobs j
            LEFT JOIN companies c ON j.id = c.job_id
            LEFT JOIN contacts ct ON c.id = ct.company_id
            LEFT JOIN outreach_content oc ON c.id = oc.company_id
            LEFT JOIN company_profiles cp ON c.id = cp.company_id
            {where_sql}
            GROUP BY j.id
            ORDER BY j.created_at DESC
            LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
        """

        params.extend([limit, offset])
        rows = await self.db.fetch_all(query, *params)
        return [JobResponse(**row) for row in rows]  # type: ignore[arg-type]

    async def cancel_job(self, job_id: str) -> bool:
        result = await self.db.execute(
            """
            UPDATE jobs
            SET status = $1, updated_at = $2
            WHERE id = $3 AND status IN ($4, $5)
            """,
            JobStatus.CANCELLED.value,
            datetime.utcnow(),
            job_id,
            JobStatus.PENDING.value,
            JobStatus.RUNNING.value,
        )
        return result.rowcount > 0

    async def get_usage_analytics(self, days: int = 30) -> UsageAnalytics:
        start_date = datetime.utcnow() - timedelta(days=days)

        job_stats = await self.db.fetch_one(
            """
            SELECT
                COUNT(*) AS total_jobs,
                COUNT(CASE WHEN status = $1 THEN 1 END) AS completed_jobs,
                COUNT(CASE WHEN status = $2 THEN 1 END) AS failed_jobs
            FROM jobs
            WHERE created_at >= $3
            """,
            JobStatus.COMPLETED.value,
            JobStatus.FAILED.value,
            start_date,
        )

        content_stats = await self.db.fetch_one(
            """
            SELECT
                COUNT(DISTINCT c.id) AS total_companies,
                COUNT(DISTINCT ct.id) AS total_contacts,
                COUNT(DISTINCT oc.id) AS total_outreach
            FROM jobs j
            JOIN companies c ON j.id = c.job_id
            LEFT JOIN contacts ct ON c.id = ct.company_id
            LEFT JOIN outreach_content oc ON c.id = oc.company_id
            WHERE j.created_at >= $1
            """,
            start_date,
        )

        api_stats_rows = await self.db.fetch_all(
            """
            SELECT provider, SUM(request_count) AS total_requests, SUM(cost_usd) AS total_cost
            FROM api_usage
            WHERE created_at >= $1
            GROUP BY provider
            """,
            start_date,
        )
        api_calls = {row["provider"]: row["total_requests"] for row in api_stats_rows}
        costs = {row["provider"]: float(row["total_cost"] or 0.0) for row in api_stats_rows}

        processing_time_rows = await self.db.fetch_all(
            """
            SELECT EXTRACT(EPOCH FROM (completed_at - created_at)) AS processing_time
            FROM jobs
            WHERE status = $1 AND created_at >= $2 AND completed_at IS NOT NULL
            """,
            JobStatus.COMPLETED.value,
            start_date,
        )
        avg_processing = (
            sum(row["processing_time"] for row in processing_time_rows) / len(processing_time_rows)
            if processing_time_rows
            else 0.0
        )

        return UsageAnalytics(
            total_jobs=job_stats["total_jobs"],
            completed_jobs=job_stats["completed_jobs"],
            failed_jobs=job_stats["failed_jobs"],
            total_companies=content_stats["total_companies"],
            total_contacts=content_stats["total_contacts"],
            total_outreach=content_stats["total_outreach"],
            api_calls=api_calls,
            costs=costs,
            average_processing_time=avg_processing,
        )

    async def _update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        completed: bool = False,
    ) -> None:
        await self.db.execute(
            """
            UPDATE jobs
            SET status = $1,
                updated_at = $2,
                completed_at = CASE WHEN $3 THEN $2 ELSE completed_at END
            WHERE id = $4
            """,
            status.value,
            datetime.utcnow(),
            completed,
            job_id,
        )

    async def _parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Placeholder prompt parsing. The heavy lifting is done downstream by real_research.
        """
        return {"prompt": prompt}
