"""
Apollo.io API Integration
Handles company and contact discovery through Apollo.io API
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
import aiohttp
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class ApolloClient:
    """Apollo.io API client for company and contact discovery"""
    
    def __init__(self):
        self.api_key = os.getenv('APOLLO_API_KEY')
        self.base_url = "https://api.apollo.io/v1"
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request to Apollo.io"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            url = f"{self.base_url}/{endpoint}"
            headers = {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache'
            }
            
            # Add API key to params
            params['api_key'] = self.api_key
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.error(f"Apollo API error: {response.status} - {await response.text()}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error making Apollo API request: {str(e)}")
            return {}
    
    async def search_companies(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for companies using Apollo.io"""
        try:
            # Build search parameters
            search_params = {
                'q': params.get('query', ''),
                'page': params.get('page', 1),
                'per_page': min(params.get('per_page', 25), 100),
                'organization_locations': params.get('locations', []),
                'organization_num_employees_ranges': params.get('employee_ranges', []),
                'organization_industries': params.get('industries', []),
                'organization_keywords': params.get('keywords', [])
            }
            
            # Remove empty parameters
            search_params = {k: v for k, v in search_params.items() if v}
            
            result = await self._make_request('mixed_companies/search', search_params)
            
            if result.get('organizations'):
                return result['organizations']
            else:
                logger.warning("No companies found in Apollo search")
                return []
                
        except Exception as e:
            logger.error(f"Error searching companies in Apollo: {str(e)}")
            return []
    
    async def search_people(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for people using Apollo.io"""
        try:
            # Build search parameters
            search_params = {
                'q': params.get('query', ''),
                'page': params.get('page', 1),
                'per_page': min(params.get('per_page', 25), 100),
                'person_titles': params.get('titles', []),
                'person_locations': params.get('locations', []),
                'organization_domains': params.get('organization_domains', []),
                'person_seniorities': params.get('seniorities', [])
            }
            
            # Remove empty parameters
            search_params = {k: v for k, v in search_params.items() if v}
            
            result = await self._make_request('mixed_people/search', search_params)
            
            if result.get('people'):
                return result['people']
            else:
                logger.warning("No people found in Apollo search")
                return []
                
        except Exception as e:
            logger.error(f"Error searching people in Apollo: {str(e)}")
            return []
    
    async def get_company_by_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get company information by domain"""
        try:
            params = {
                'domain': domain
            }
            
            result = await self._make_request('organizations/match_domain', params)
            
            if result.get('organization'):
                return result['organization']
            else:
                logger.warning(f"No company found for domain: {domain}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting company by domain {domain}: {str(e)}")
            return None
    
    async def get_people_by_company(self, company_id: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get people associated with a company"""
        try:
            search_params = {
                'organization_id': company_id,
                'page': 1,
                'per_page': 100
            }
            
            if params:
                search_params.update(params)
            
            result = await self._make_request('organizations/people', search_params)
            
            if result.get('people'):
                return result['people']
            else:
                logger.warning(f"No people found for company {company_id}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting people for company {company_id}: {str(e)}")
            return []
    
    async def enrich_person(self, person_id: str) -> Optional[Dict[str, Any]]:
        """Enrich person data with additional information"""
        try:
            params = {
                'id': person_id
            }
            
            result = await self._make_request('people/match', params)
            
            if result.get('person'):
                return result['person']
            else:
                logger.warning(f"No enriched data found for person {person_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error enriching person {person_id}: {str(e)}")
            return None
    
    async def get_company_technologies(self, company_id: str) -> List[Dict[str, Any]]:
        """Get technology stack for a company"""
        try:
            params = {
                'organization_id': company_id
            }
            
            result = await self._make_request('organizations/technologies', params)
            
            if result.get('technologies'):
                return result['technologies']
            else:
                logger.warning(f"No technologies found for company {company_id}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting technologies for company {company_id}: {str(e)}")
            return []
    
    async def get_company_news(self, company_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent news about a company"""
        try:
            params = {
                'organization_id': company_id,
                'limit': limit
            }
            
            result = await self._make_request('organizations/news', params)
            
            if result.get('news'):
                return result['news']
            else:
                logger.warning(f"No news found for company {company_id}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting news for company {company_id}: {str(e)}")
            return []
    
    async def get_company_funding(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get funding information for a company"""
        try:
            params = {
                'organization_id': company_id
            }
            
            result = await self._make_request('organizations/funding', params)
            
            if result.get('funding'):
                return result['funding']
            else:
                logger.warning(f"No funding data found for company {company_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting funding for company {company_id}: {str(e)}")
            return None
    
    async def search_by_industry(self, industry: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search companies by industry"""
        try:
            search_params = {
                'organization_industries': [industry],
                'page': 1,
                'per_page': 100
            }
            
            if params:
                search_params.update(params)
            
            result = await self._make_request('mixed_companies/search', search_params)
            
            if result.get('organizations'):
                return result['organizations']
            else:
                logger.warning(f"No companies found for industry: {industry}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching companies by industry {industry}: {str(e)}")
            return []
    
    async def search_by_location(self, location: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search companies by location"""
        try:
            search_params = {
                'organization_locations': [location],
                'page': 1,
                'per_page': 100
            }
            
            if params:
                search_params.update(params)
            
            result = await self._make_request('mixed_companies/search', search_params)
            
            if result.get('organizations'):
                return result['organizations']
            else:
                logger.warning(f"No companies found for location: {location}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching companies by location {location}: {str(e)}")
            return []
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        try:
            result = await self._make_request('usage_stats', {})
            
            if result:
                return result
            else:
                logger.warning("No usage stats available")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting usage stats: {str(e)}")
            return {}
    
    def _normalize_company_data(self, apollo_company: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Apollo company data to our schema"""
        try:
            return {
                'name': apollo_company.get('name', ''),
                'website': apollo_company.get('website_url', ''),
                'domain': apollo_company.get('primary_domain', ''),
                'industry': apollo_company.get('industry', ''),
                'employee_count': apollo_company.get('estimated_num_employees', 0),
                'city': apollo_company.get('city', ''),
                'state': apollo_company.get('state', ''),
                'country': apollo_company.get('country', ''),
                'linkedin_url': apollo_company.get('linkedin_url', ''),
                'twitter_url': apollo_company.get('twitter_url', ''),
                'facebook_url': apollo_company.get('facebook_url', ''),
                'description': apollo_company.get('short_description', ''),
                'founded_year': apollo_company.get('founded_year'),
                'annual_revenue': apollo_company.get('annual_revenue'),
                'total_funding': apollo_company.get('total_funding'),
                'last_funding_date': apollo_company.get('last_funding_date'),
                'apollo_id': apollo_company.get('id'),
                'apollo_url': apollo_company.get('apollo_url'),
                'raw_data': apollo_company
            }
        except Exception as e:
            logger.error(f"Error normalizing company data: {str(e)}")
            return {}
    
    def _normalize_person_data(self, apollo_person: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Apollo person data to our schema"""
        try:
            return {
                'first_name': apollo_person.get('first_name', ''),
                'last_name': apollo_person.get('last_name', ''),
                'full_name': apollo_person.get('name', ''),
                'title': apollo_person.get('title', ''),
                'email': apollo_person.get('email', ''),
                'phone': apollo_person.get('phone_numbers', [{}])[0].get('raw_number', '') if apollo_person.get('phone_numbers') else '',
                'linkedin_url': apollo_person.get('linkedin_url', ''),
                'twitter_url': apollo_person.get('twitter_url', ''),
                'github_url': apollo_person.get('github_url', ''),
                'photo_url': apollo_person.get('photo_url', ''),
                'city': apollo_person.get('city', ''),
                'state': apollo_person.get('state', ''),
                'country': apollo_person.get('country', ''),
                'seniority': apollo_person.get('seniority', ''),
                'department': apollo_person.get('department', ''),
                'apollo_id': apollo_person.get('id'),
                'apollo_url': apollo_person.get('apollo_url'),
                'raw_data': apollo_person
            }
        except Exception as e:
            logger.error(f"Error normalizing person data: {str(e)}")
            return {}
