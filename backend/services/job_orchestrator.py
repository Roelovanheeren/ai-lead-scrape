"""
Job Orchestrator Service
Coordinates the entire lead generation pipeline from prompt to delivery
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from ..database.connection import DatabaseConnection
from ..models.schemas import JobCreate, JobResponse, JobStatus, UsageAnalytics
from ..services.company_discovery import CompanyDiscoveryService
from ..services.contact_identification import ContactIdentificationService
from ..services.research_engine import ResearchEngine
from ..services.outreach_generator import OutreachGenerator
from ..services.quality_assurance import QualityAssuranceService
from ..services.export_service import ExportService
from ..integrations.notification_service import NotificationService

logger = logging.getLogger(__name__)

class JobOrchestrator:
    """Orchestrates the complete lead generation pipeline"""
    
    def __init__(self):
        self.company_discovery = CompanyDiscoveryService()
        self.contact_identification = ContactIdentificationService()
        self.research_engine = ResearchEngine()
        self.outreach_generator = OutreachGenerator()
        self.qa_service = QualityAssuranceService()
        self.export_service = ExportService()
        self.notification_service = NotificationService()
    
    async def create_job(self, db: DatabaseConnection, job_data: JobCreate) -> JobResponse:
        """Create a new lead generation job"""
        try:
            # Parse and validate the prompt
            parsed_parameters = await self._parse_prompt(job_data.prompt)
            
            # Create job record
            job_id = str(uuid.uuid4())
            job_record = {
                "id": job_id,
                "prompt": job_data.prompt,
                "parameters": {**parsed_parameters, **(job_data.parameters or {})},
                "status": JobStatus.PENDING,
                "vertical": job_data.vertical,
                "target_count": job_data.target_count,
                "quality_threshold": job_data.quality_threshold,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await db.execute(
                """
                INSERT INTO jobs (id, prompt, parameters, status, vertical, target_count, quality_threshold, created_at, updated_at)
                VALUES (%(id)s, %(prompt)s, %(parameters)s, %(status)s, %(vertical)s, %(target_count)s, %(quality_threshold)s, %(created_at)s, %(updated_at)s)
                """,
                job_record
            )
            
            logger.info(f"Created job {job_id} with prompt: {job_data.prompt[:100]}...")
            return JobResponse(**job_record)
            
        except Exception as e:
            logger.error(f"Error creating job: {str(e)}")
            raise
    
    async def process_job(self, job_id: str):
        """Process a job through the complete pipeline"""
        try:
            # Update job status to running
            await self._update_job_status(job_id, JobStatus.RUNNING)
            
            # Step 1: Company Discovery
            logger.info(f"Starting company discovery for job {job_id}")
            companies = await self.company_discovery.discover_companies(job_id)
            logger.info(f"Discovered {len(companies)} companies for job {job_id}")
            
            # Step 2: Contact Identification
            logger.info(f"Starting contact identification for job {job_id}")
            total_contacts = 0
            for company in companies:
                contacts = await self.contact_identification.identify_contacts(company.id)
                total_contacts += len(contacts)
            logger.info(f"Identified {total_contacts} contacts for job {job_id}")
            
            # Step 3: Deep Research
            logger.info(f"Starting deep research for job {job_id}")
            for company in companies:
                await self.research_engine.research_company(company.id)
            logger.info(f"Completed research for {len(companies)} companies in job {job_id}")
            
            # Step 4: Outreach Generation
            logger.info(f"Starting outreach generation for job {job_id}")
            total_outreach = 0
            for company in companies:
                outreach_content = await self.outreach_generator.generate_company_outreach(company.id)
                total_outreach += len(outreach_content)
            logger.info(f"Generated {total_outreach} outreach pieces for job {job_id}")
            
            # Step 5: Quality Assurance
            logger.info(f"Starting quality assurance for job {job_id}")
            qa_results = await self.qa_service.run_qa_pipeline(job_id)
            logger.info(f"QA completed for job {job_id}: {qa_results}")
            
            # Step 6: Export and Delivery
            logger.info(f"Starting export and delivery for job {job_id}")
            await self.export_service.export_job_results(job_id)
            logger.info(f"Export completed for job {job_id}")
            
            # Update job status to completed
            await self._update_job_status(job_id, JobStatus.COMPLETED)
            
            # Send completion notification
            await self.notification_service.send_job_completion(job_id)
            
            logger.info(f"Job {job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")
            await self._update_job_status(job_id, JobStatus.FAILED)
            await self.notification_service.send_job_failure(job_id, str(e))
            raise
    
    async def get_job(self, db: DatabaseConnection, job_id: str) -> Optional[JobResponse]:
        """Get job details"""
        try:
            result = await db.fetch_one(
                """
                SELECT j.*, 
                       COUNT(DISTINCT c.id) as companies_found,
                       COUNT(DISTINCT ct.id) as contacts_found,
                       COUNT(DISTINCT oc.id) as outreach_generated,
                       AVG(cp.research_confidence) as quality_score
                FROM jobs j
                LEFT JOIN companies c ON j.id = c.job_id
                LEFT JOIN contacts ct ON c.id = ct.company_id
                LEFT JOIN outreach_content oc ON c.id = oc.company_id
                LEFT JOIN company_profiles cp ON c.id = cp.company_id
                WHERE j.id = %s
                GROUP BY j.id
                """,
                (job_id,)
            )
            
            if not result:
                return None
                
            return JobResponse(**result)
            
        except Exception as e:
            logger.error(f"Error getting job {job_id}: {str(e)}")
            raise
    
    async def list_jobs(self, db: DatabaseConnection, status: Optional[str] = None, 
                       limit: int = 50, offset: int = 0) -> List[JobResponse]:
        """List jobs with optional filtering"""
        try:
            query = """
                SELECT j.*, 
                       COUNT(DISTINCT c.id) as companies_found,
                       COUNT(DISTINCT ct.id) as contacts_found,
                       COUNT(DISTINCT oc.id) as outreach_generated,
                       AVG(cp.research_confidence) as quality_score
                FROM jobs j
                LEFT JOIN companies c ON j.id = c.job_id
                LEFT JOIN contacts ct ON c.id = ct.company_id
                LEFT JOIN outreach_content oc ON c.id = oc.company_id
                LEFT JOIN company_profiles cp ON c.id = cp.company_id
            """
            params = []
            
            if status:
                query += " WHERE j.status = %s"
                params.append(status)
            
            query += " GROUP BY j.id ORDER BY j.created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            results = await db.fetch_all(query, params)
            return [JobResponse(**row) for row in results]
            
        except Exception as e:
            logger.error(f"Error listing jobs: {str(e)}")
            raise
    
    async def cancel_job(self, db: DatabaseConnection, job_id: str) -> bool:
        """Cancel a running job"""
        try:
            result = await db.execute(
                "UPDATE jobs SET status = %s, updated_at = %s WHERE id = %s AND status IN (%s, %s)",
                (JobStatus.CANCELLED, datetime.utcnow(), job_id, JobStatus.PENDING, JobStatus.RUNNING)
            )
            return result.rowcount > 0
            
        except Exception as e:
            logger.error(f"Error cancelling job {job_id}: {str(e)}")
            raise
    
    async def get_usage_analytics(self, db: DatabaseConnection, days: int = 30) -> UsageAnalytics:
        """Get usage analytics for the specified period"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Job statistics
            job_stats = await db.fetch_one(
                """
                SELECT 
                    COUNT(*) as total_jobs,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_jobs
                FROM jobs 
                WHERE created_at >= %s
                """,
                (start_date,)
            )
            
            # Company and contact statistics
            content_stats = await db.fetch_one(
                """
                SELECT 
                    COUNT(DISTINCT c.id) as total_companies,
                    COUNT(DISTINCT ct.id) as total_contacts,
                    COUNT(DISTINCT oc.id) as total_outreach
                FROM jobs j
                JOIN companies c ON j.id = c.job_id
                LEFT JOIN contacts ct ON c.id = ct.company_id
                LEFT JOIN outreach_content oc ON c.id = oc.company_id
                WHERE j.created_at >= %s
                """,
                (start_date,)
            )
            
            # API usage statistics
            api_stats = await db.fetch_all(
                """
                SELECT provider, SUM(request_count) as total_requests, SUM(cost_usd) as total_cost
                FROM api_usage 
                WHERE created_at >= %s
                GROUP BY provider
                """,
                (start_date,)
            )
            
            # Calculate average processing time
            processing_times = await db.fetch_all(
                """
                SELECT EXTRACT(EPOCH FROM (completed_at - created_at)) as processing_time
                FROM jobs 
                WHERE status = 'completed' AND created_at >= %s
                """,
                (start_date,)
            )
            
            avg_processing_time = sum(row['processing_time'] for row in processing_times) / len(processing_times) if processing_times else 0
            
            return UsageAnalytics(
                total_jobs=job_stats['total_jobs'],
                completed_jobs=job_stats['completed_jobs'],
                failed_jobs=job_stats['failed_jobs'],
                total_companies=content_stats['total_companies'],
                total_contacts=content_stats['total_contacts'],
                total_outreach=content_stats['total_outreach'],
                api_calls={row['provider']: row['total_requests'] for row in api_stats},
                costs={row['provider']: float(row['total_cost']) for row in api_stats},
                average_processing_time=avg_processing_time
            )
            
        except Exception as e:
            logger.error(f"Error getting usage analytics: {str(e)}")
            raise
    
    async def _parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """Parse the targeting prompt to extract structured parameters"""
        # This would use an LLM to extract structured data from the prompt
        # For now, return basic parsing
        return {
            "keywords": self._extract_keywords(prompt),
            "industries": self._extract_industries(prompt),
            "geography": self._extract_geography(prompt),
            "company_size": self._extract_company_size(prompt)
        }
    
    def _extract_keywords(self, prompt: str) -> List[str]:
        """Extract relevant keywords from the prompt"""
        # Simple keyword extraction - in production, use NLP/LLM
        keywords = []
        # Add keyword extraction logic here
        return keywords
    
    def _extract_industries(self, prompt: str) -> List[str]:
        """Extract industry mentions from the prompt"""
        industries = []
        # Add industry extraction logic here
        return industries
    
    def _extract_geography(self, prompt: str) -> List[str]:
        """Extract geographic mentions from the prompt"""
        geography = []
        # Add geography extraction logic here
        return geography
    
    def _extract_company_size(self, prompt: str) -> Dict[str, Any]:
        """Extract company size criteria from the prompt"""
        return {}
    
    async def _update_job_status(self, job_id: str, status: JobStatus):
        """Update job status"""
        # Implementation would update the database
        pass
