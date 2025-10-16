"""
Company Discovery Service
Handles company discovery through multiple channels: search APIs, databases, and web scraping
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from ..database.connection import DatabaseConnection
from ..models.schemas import CompanyResponse, CompanyAttributes
from ..integrations.google_search import GoogleSearchClient
from ..integrations.apollo_client import ApolloClient
from ..integrations.crunchbase_client import CrunchbaseClient
from ..integrations.web_scraper import WebScraperService
from ..utils.text_processing import TextProcessor
from ..utils.deduplication import DeduplicationService

logger = logging.getLogger(__name__)

class CompanyDiscoveryService:
    """Service for discovering companies through multiple channels"""
    
    def __init__(self):
        self.google_search = GoogleSearchClient()
        self.apollo_client = ApolloClient()
        self.crunchbase_client = CrunchbaseClient()
        self.web_scraper = WebScraperService()
        self.text_processor = TextProcessor()
        self.deduplication = DeduplicationService()
    
    async def discover_companies(self, job_id: str) -> List[CompanyResponse]:
        """Discover companies for a job using multiple channels"""
        try:
            # Get job parameters
            job_params = await self._get_job_parameters(job_id)
            
            # Discover companies through multiple channels
            all_companies = []
            
            # 1. Google Search Discovery
            google_companies = await self._discover_via_google_search(job_params)
            all_companies.extend(google_companies)
            
            # 2. Apollo.io Discovery
            apollo_companies = await self._discover_via_apollo(job_params)
            all_companies.extend(apollo_companies)
            
            # 3. Crunchbase Discovery
            crunchbase_companies = await self._discover_via_crunchbase(job_params)
            all_companies.extend(crunchbase_companies)
            
            # 4. Web Scraping Discovery
            scraped_companies = await self._discover_via_web_scraping(job_params)
            all_companies.extend(scraped_companies)
            
            # Deduplicate companies
            unique_companies = await self.deduplication.deduplicate_companies(all_companies)
            
            # Score and filter companies
            scored_companies = await self._score_companies(unique_companies, job_params)
            
            # Store companies in database
            stored_companies = await self._store_companies(job_id, scored_companies)
            
            logger.info(f"Discovered {len(stored_companies)} companies for job {job_id}")
            return stored_companies
            
        except Exception as e:
            logger.error(f"Error discovering companies for job {job_id}: {str(e)}")
            raise
    
    async def _discover_via_google_search(self, job_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Discover companies using Google Custom Search API"""
        try:
            companies = []
            
            # Construct search queries based on job parameters
            search_queries = await self._build_search_queries(job_params)
            
            for query in search_queries:
                # Perform Google search
                search_results = await self.google_search.search(query)
                
                # Extract company information from search results
                for result in search_results:
                    company_data = await self._extract_company_from_search_result(result)
                    if company_data:
                        companies.append(company_data)
            
            logger.info(f"Discovered {len(companies)} companies via Google search")
            return companies
            
        except Exception as e:
            logger.error(f"Error in Google search discovery: {str(e)}")
            return []
    
    async def _discover_via_apollo(self, job_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Discover companies using Apollo.io API"""
        try:
            companies = []
            
            # Build Apollo search parameters
            apollo_params = await self._build_apollo_search_params(job_params)
            
            # Search companies in Apollo
            apollo_results = await self.apollo_client.search_companies(apollo_params)
            
            for result in apollo_results:
                company_data = await self._extract_company_from_apollo(result)
                if company_data:
                    companies.append(company_data)
            
            logger.info(f"Discovered {len(companies)} companies via Apollo")
            return companies
            
        except Exception as e:
            logger.error(f"Error in Apollo discovery: {str(e)}")
            return []
    
    async def _discover_via_crunchbase(self, job_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Discover companies using Crunchbase API"""
        try:
            companies = []
            
            # Build Crunchbase search parameters
            cb_params = await self._build_crunchbase_search_params(job_params)
            
            # Search companies in Crunchbase
            cb_results = await self.crunchbase_client.search_companies(cb_params)
            
            for result in cb_results:
                company_data = await self._extract_company_from_crunchbase(result)
                if company_data:
                    companies.append(company_data)
            
            logger.info(f"Discovered {len(companies)} companies via Crunchbase")
            return companies
            
        except Exception as e:
            logger.error(f"Error in Crunchbase discovery: {str(e)}")
            return []
    
    async def _discover_via_web_scraping(self, job_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Discover companies using web scraping"""
        try:
            companies = []
            
            # Get target websites for scraping
            target_sites = await self._get_scraping_targets(job_params)
            
            for site in target_sites:
                # Scrape the website
                scraped_data = await self.web_scraper.scrape_website(site['url'])
                
                # Extract company information
                extracted_companies = await self._extract_companies_from_scraped_data(scraped_data, site)
                companies.extend(extracted_companies)
            
            logger.info(f"Discovered {len(companies)} companies via web scraping")
            return companies
            
        except Exception as e:
            logger.error(f"Error in web scraping discovery: {str(e)}")
            return []
    
    async def _score_companies(self, companies: List[Dict[str, Any]], job_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score companies based on relevance and quality"""
        try:
            scored_companies = []
            
            for company in companies:
                # Calculate discovery confidence
                discovery_confidence = await self._calculate_discovery_confidence(company)
                
                # Calculate fit score
                fit_score = await self._calculate_fit_score(company, job_params)
                
                # Add scores to company data
                company['discovery_confidence'] = discovery_confidence
                company['fit_score'] = fit_score
                
                scored_companies.append(company)
            
            # Sort by combined score
            scored_companies.sort(key=lambda x: (x['fit_score'] + x['discovery_confidence']) / 2, reverse=True)
            
            return scored_companies
            
        except Exception as e:
            logger.error(f"Error scoring companies: {str(e)}")
            return companies
    
    async def _store_companies(self, job_id: str, companies: List[Dict[str, Any]]) -> List[CompanyResponse]:
        """Store companies in the database"""
        try:
            stored_companies = []
            
            for company_data in companies:
                company_id = str(uuid.uuid4())
                
                # Prepare company record
                company_record = {
                    "id": company_id,
                    "job_id": job_id,
                    "name": company_data.get('name', ''),
                    "website": company_data.get('website'),
                    "domain": company_data.get('domain'),
                    "country": company_data.get('country'),
                    "city": company_data.get('city'),
                    "state": company_data.get('state'),
                    "attributes": company_data.get('attributes', {}),
                    "discovery_confidence": company_data.get('discovery_confidence', 0.0),
                    "fit_score": company_data.get('fit_score', 0.0),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                # Store in database
                await self._insert_company(company_record)
                
                # Convert to response model
                stored_companies.append(CompanyResponse(**company_record))
            
            return stored_companies
            
        except Exception as e:
            logger.error(f"Error storing companies: {str(e)}")
            raise
    
    async def get_companies(self, db: DatabaseConnection, job_id: str, 
                           limit: int = 100, offset: int = 0) -> List[CompanyResponse]:
        """Get companies for a job"""
        try:
            results = await db.fetch_all(
                """
                SELECT c.*, 
                       COUNT(DISTINCT ct.id) as contact_count,
                       CASE WHEN cp.id IS NOT NULL THEN true ELSE false END as research_completed,
                       CASE WHEN oc.id IS NOT NULL THEN true ELSE false END as outreach_generated
                FROM companies c
                LEFT JOIN contacts ct ON c.id = ct.company_id
                LEFT JOIN company_profiles cp ON c.id = cp.company_id
                LEFT JOIN outreach_content oc ON c.id = oc.company_id
                WHERE c.job_id = %s
                GROUP BY c.id
                ORDER BY c.fit_score DESC, c.discovery_confidence DESC
                LIMIT %s OFFSET %s
                """,
                (job_id, limit, offset)
            )
            
            return [CompanyResponse(**row) for row in results]
            
        except Exception as e:
            logger.error(f"Error getting companies for job {job_id}: {str(e)}")
            raise
    
    async def refresh_company_data(self, db: DatabaseConnection, company_id: str):
        """Refresh company data from external sources"""
        try:
            # Get company record
            company = await db.fetch_one(
                "SELECT * FROM companies WHERE id = %s",
                (company_id,)
            )
            
            if not company:
                logger.warning(f"Company {company_id} not found")
                return
            
            # Refresh from Apollo
            if company['website']:
                apollo_data = await self.apollo_client.get_company_by_domain(company['website'])
                if apollo_data:
                    await self._update_company_from_apollo(db, company_id, apollo_data)
            
            # Refresh from Crunchbase
            if company['name']:
                cb_data = await self.crunchbase_client.get_company_by_name(company['name'])
                if cb_data:
                    await self._update_company_from_crunchbase(db, company_id, cb_data)
            
            logger.info(f"Refreshed data for company {company_id}")
            
        except Exception as e:
            logger.error(f"Error refreshing company {company_id}: {str(e)}")
            raise
    
    # Helper methods
    async def _get_job_parameters(self, job_id: str) -> Dict[str, Any]:
        """Get job parameters from database"""
        # Implementation would fetch from database
        return {}
    
    async def _build_search_queries(self, job_params: Dict[str, Any]) -> List[str]:
        """Build Google search queries from job parameters"""
        queries = []
        # Add query building logic here
        return queries
    
    async def _build_apollo_search_params(self, job_params: Dict[str, Any]) -> Dict[str, Any]:
        """Build Apollo search parameters from job parameters"""
        params = {}
        # Add Apollo parameter building logic here
        return params
    
    async def _build_crunchbase_search_params(self, job_params: Dict[str, Any]) -> Dict[str, Any]:
        """Build Crunchbase search parameters from job parameters"""
        params = {}
        # Add Crunchbase parameter building logic here
        return params
    
    async def _get_scraping_targets(self, job_params: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get target websites for scraping"""
        targets = []
        # Add scraping target logic here
        return targets
    
    async def _extract_company_from_search_result(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract company information from Google search result"""
        # Add extraction logic here
        return None
    
    async def _extract_company_from_apollo(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract company information from Apollo result"""
        # Add extraction logic here
        return None
    
    async def _extract_company_from_crunchbase(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract company information from Crunchbase result"""
        # Add extraction logic here
        return None
    
    async def _extract_companies_from_scraped_data(self, data: Dict[str, Any], site: Dict[str, str]) -> List[Dict[str, Any]]:
        """Extract companies from scraped website data"""
        companies = []
        # Add extraction logic here
        return companies
    
    async def _calculate_discovery_confidence(self, company: Dict[str, Any]) -> float:
        """Calculate confidence in company discovery"""
        # Add confidence calculation logic here
        return 0.8
    
    async def _calculate_fit_score(self, company: Dict[str, Any], job_params: Dict[str, Any]) -> float:
        """Calculate fit score for company"""
        # Add fit score calculation logic here
        return 0.7
    
    async def _insert_company(self, company_record: Dict[str, Any]):
        """Insert company record into database"""
        # Implementation would insert into database
        pass
    
    async def _update_company_from_apollo(self, db: DatabaseConnection, company_id: str, apollo_data: Dict[str, Any]):
        """Update company data from Apollo"""
        # Implementation would update database
        pass
    
    async def _update_company_from_crunchbase(self, db: DatabaseConnection, company_id: str, cb_data: Dict[str, Any]):
        """Update company data from Crunchbase"""
        # Implementation would update database
        pass
