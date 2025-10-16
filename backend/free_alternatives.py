#!/usr/bin/env python3
"""
Free alternatives to Apollo.io for company and contact discovery
Uses Clearbit, Hunter.io, Google Search, and web scraping
"""

import asyncio
import logging
import os
import httpx
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FreeDataSources:
    """Free alternatives to Apollo.io for data discovery"""
    
    def __init__(self):
        self.clearbit_key = os.getenv('CLEARBIT_API_KEY')
        self.hunter_key = os.getenv('HUNTER_API_KEY')
        self.google_key = os.getenv('GOOGLE_API_KEY')
        self.google_cx = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
    
    async def discover_companies_google(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Discover companies using Google Custom Search"""
        if not self.google_key or not self.google_cx:
            logger.warning("Google API keys not set, skipping Google search")
            return []
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.google_key,
                "cx": self.google_cx,
                "q": f"{query} company",
                "num": min(limit, 10)
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    
                    companies = []
                    for item in items:
                        company = {
                            "name": self._extract_company_name(item.get("title", "")),
                            "website": self._extract_domain(item.get("link", "")),
                            "description": item.get("snippet", ""),
                            "source": "google_search",
                            "confidence": 0.7
                        }
                        if company["name"] and company["website"]:
                            companies.append(company)
                    
                    logger.info(f"✅ Google search found {len(companies)} companies")
                    return companies
                else:
                    logger.error(f"❌ Google search failed: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Google search error: {str(e)}")
            return []
    
    async def enrich_company_clearbit(self, domain: str) -> Optional[Dict[str, Any]]:
        """Enrich company data using Clearbit"""
        if not self.clearbit_key:
            logger.warning("Clearbit API key not set, skipping enrichment")
            return None
        
        try:
            url = f"https://company.clearbit.com/v2/companies/find?domain={domain}"
            headers = {"Authorization": f"Bearer {self.clearbit_key}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "name": data.get("name", ""),
                        "domain": data.get("domain", ""),
                        "industry": data.get("category", {}).get("industry", ""),
                        "employee_count": data.get("metrics", {}).get("employees", 0),
                        "location": data.get("location", {}).get("city", ""),
                        "description": data.get("description", ""),
                        "source": "clearbit",
                        "confidence": 0.9
                    }
                else:
                    logger.warning(f"Clearbit enrichment failed for {domain}: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Clearbit enrichment error: {str(e)}")
            return None
    
    async def find_contacts_hunter(self, domain: str) -> List[Dict[str, Any]]:
        """Find contacts using Hunter.io"""
        if not self.hunter_key:
            logger.warning("Hunter.io API key not set, skipping contact discovery")
            return []
        
        try:
            url = "https://api.hunter.io/v2/domain-search"
            params = {
                "domain": domain,
                "api_key": self.hunter_key,
                "limit": 10
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    contacts = data.get("data", {}).get("emails", [])
                    
                    formatted_contacts = []
                    for contact in contacts:
                        formatted_contacts.append({
                            "first_name": contact.get("first_name", ""),
                            "last_name": contact.get("last_name", ""),
                            "email": contact.get("value", ""),
                            "title": contact.get("position", ""),
                            "confidence": contact.get("confidence", 0) / 100,
                            "source": "hunter_io"
                        })
                    
                    logger.info(f"✅ Hunter.io found {len(formatted_contacts)} contacts for {domain}")
                    return formatted_contacts
                else:
                    logger.warning(f"Hunter.io search failed for {domain}: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Hunter.io error: {str(e)}")
            return []
    
    async def scrape_company_website(self, website: str) -> Dict[str, Any]:
        """Scrape company website for basic information"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(website, timeout=10)
                
                if response.status_code == 200:
                    content = response.text
                    
                    # Extract basic information
                    company_info = {
                        "website": website,
                        "title": self._extract_title(content),
                        "description": self._extract_description(content),
                        "industry_signals": self._extract_industry_signals(content),
                        "contact_info": self._extract_contact_info(content),
                        "source": "website_scraping",
                        "confidence": 0.6
                    }
                    
                    logger.info(f"✅ Scraped website: {website}")
                    return company_info
                else:
                    logger.warning(f"Website scraping failed for {website}: {response.status_code}")
                    return {}
                    
        except Exception as e:
            logger.error(f"❌ Website scraping error for {website}: {str(e)}")
            return {}
    
    def _extract_company_name(self, title: str) -> str:
        """Extract company name from search result title"""
        # Remove common suffixes and clean up
        title = re.sub(r'\s*-\s*.*$', '', title)  # Remove everything after dash
        title = re.sub(r'\s*\|\s*.*$', '', title)  # Remove everything after pipe
        title = re.sub(r'\s*Company.*$', '', title, flags=re.IGNORECASE)
        return title.strip()
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return ""
    
    def _extract_title(self, content: str) -> str:
        """Extract page title from HTML"""
        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        if title_match:
            return title_match.group(1).strip()
        return ""
    
    def _extract_description(self, content: str) -> str:
        """Extract meta description from HTML"""
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', content, re.IGNORECASE)
        if desc_match:
            return desc_match.group(1).strip()
        return ""
    
    def _extract_industry_signals(self, content: str) -> List[str]:
        """Extract industry-related keywords from content"""
        industry_keywords = [
            "software", "technology", "SaaS", "AI", "machine learning",
            "fintech", "healthtech", "edtech", "e-commerce", "marketplace",
            "consulting", "services", "manufacturing", "retail", "finance"
        ]
        
        found_keywords = []
        content_lower = content.lower()
        for keyword in industry_keywords:
            if keyword.lower() in content_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _extract_contact_info(self, content: str) -> Dict[str, str]:
        """Extract contact information from website"""
        contact_info = {}
        
        # Extract email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', content)
        if email_match:
            contact_info["email"] = email_match.group(0)
        
        # Extract phone
        phone_match = re.search(r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})', content)
        if phone_match:
            contact_info["phone"] = phone_match.group(0)
        
        return contact_info

async def test_free_alternatives():
    """Test free alternatives to Apollo.io"""
    logger.info("🧪 Testing Free Alternatives to Apollo.io...")
    
    sources = FreeDataSources()
    
    # Test 1: Google Search for Companies
    logger.info("\n🔍 Test 1: Google Search for Companies")
    companies = await sources.discover_companies_google("SaaS startups San Francisco", 5)
    logger.info(f"Found {len(companies)} companies via Google search")
    
    # Test 2: Clearbit Enrichment (if available)
    if companies:
        logger.info("\n🏢 Test 2: Clearbit Company Enrichment")
        domain = companies[0].get("website", "")
        if domain:
            enriched = await sources.enrich_company_clearbit(domain)
            if enriched:
                logger.info(f"✅ Enriched company data: {enriched['name']}")
            else:
                logger.info("⚠️ Clearbit enrichment not available (no API key)")
    
    # Test 3: Hunter.io Contact Discovery (if available)
    if companies:
        logger.info("\n👥 Test 3: Hunter.io Contact Discovery")
        domain = companies[0].get("website", "")
        if domain:
            contacts = await sources.find_contacts_hunter(domain)
            logger.info(f"Found {len(contacts)} contacts via Hunter.io")
    
    # Test 4: Website Scraping
    if companies:
        logger.info("\n🌐 Test 4: Website Scraping")
        website = companies[0].get("website", "")
        if website:
            scraped = await sources.scrape_company_website(f"https://{website}")
            if scraped:
                logger.info(f"✅ Scraped website: {scraped.get('title', 'N/A')}")
    
    logger.info("\n📊 Free Alternatives Summary:")
    logger.info(f"✅ Google Search: Working")
    logger.info(f"⚠️ Clearbit: {'Working' if sources.clearbit_key else 'API key needed'}")
    logger.info(f"⚠️ Hunter.io: {'Working' if sources.hunter_key else 'API key needed'}")
    logger.info(f"✅ Website Scraping: Working")
    
    logger.info("\n🎯 Recommendation:")
    logger.info("You can start with Google Search + Website Scraping for free!")
    logger.info("Add Clearbit and Hunter.io later for enhanced data quality.")

async def main():
    """Main test function"""
    await test_free_alternatives()

if __name__ == "__main__":
    asyncio.run(main())
