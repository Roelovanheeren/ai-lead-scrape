"""
Web Scraper for Finding Company Contacts
Scrapes company websites to find team pages, leadership pages, and LinkedIn profiles
"""

import logging
import re
import asyncio
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Try to import aiohttp
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    logger.warning("aiohttp not available for web scraping")


class WebContactScraper:
    """Scrapes company websites to find contact information"""
    
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=15)
        
    async def find_contacts_at_company(
        self, 
        company_name: str, 
        website: str,
        target_roles: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Scrape a company website to find team members and their LinkedIn profiles
        
        Args:
            company_name: Name of the company
            website: Company website URL
            target_roles: Optional list of target role titles (e.g., ["Investment Director", "Portfolio Manager"])
            
        Returns:
            List of contact dictionaries with name, title, linkedin, etc.
        """
        logger.info(f"🌐 Scraping website for contacts: {website}")
        
        if not AIOHTTP_AVAILABLE:
            logger.error("❌ aiohttp not available, cannot scrape websites")
            return []
        
        try:
            # Step 1: Find team/about pages
            team_pages = await self._find_team_pages(website)
            
            if not team_pages:
                logger.warning(f"⚠️ No team pages found at {website}")
                return []
            
            logger.info(f"✅ Found {len(team_pages)} potential team pages")
            
            # Step 2: Scrape each team page for contacts
            all_contacts = []
            
            for page_url in team_pages[:3]:  # Limit to first 3 pages
                logger.info(f"📄 Scraping: {page_url}")
                contacts = await self._scrape_team_page(page_url, company_name)
                
                if contacts:
                    logger.info(f"  ✅ Found {len(contacts)} contacts on this page")
                    all_contacts.extend(contacts)
                    
            # Step 3: Filter by target roles if specified
            if target_roles and all_contacts:
                logger.info(f"🎯 Filtering {len(all_contacts)} contacts by target roles: {target_roles}")
                filtered = self._filter_by_roles(all_contacts, target_roles)
                logger.info(f"✅ Filtered to {len(filtered)} matching contacts")
                return filtered[:10]  # Return max 10
            
            logger.info(f"✅ Scraped {len(all_contacts)} total contacts from {website}")
            return all_contacts[:10]  # Return max 10
            
        except Exception as e:
            logger.error(f"❌ Error scraping website {website}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    async def _find_team_pages(self, website: str) -> List[str]:
        """
        Find team/leadership/about pages on a company website
        
        Returns list of URLs to team pages
        """
        team_page_keywords = [
            '/team', '/leadership', '/about-us', '/about', '/people',
            '/management', '/executives', '/our-team', '/who-we-are',
            '/board', '/staff', '/meet-the-team', '/leadership-team',
            '/investment-team', '/portfolio-team'
        ]
        
        potential_pages = []
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # Fetch homepage
                async with session.get(website, allow_redirects=True) as response:
                    if response.status != 200:
                        logger.warning(f"⚠️ Could not fetch homepage: HTTP {response.status}")
                        return []
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find all links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        full_url = urljoin(website, href)
                        
                        # Check if link contains team-related keywords
                        href_lower = href.lower()
                        link_text_lower = link.get_text().lower()
                        
                        for keyword in team_page_keywords:
                            if keyword in href_lower or keyword.replace('/', '') in link_text_lower:
                                if full_url not in potential_pages:
                                    potential_pages.append(full_url)
                                    logger.info(f"  📍 Found potential team page: {full_url}")
                                break
                    
                    # If no team pages found in links, try common URL patterns
                    if not potential_pages:
                        logger.info("  🔍 No team links found, trying common URL patterns...")
                        base_url = f"{urlparse(website).scheme}://{urlparse(website).netloc}"
                        
                        for keyword in ['/team', '/leadership', '/about-us', '/people', '/our-team']:
                            potential_pages.append(f"{base_url}{keyword}")
                    
                    return potential_pages[:5]  # Return max 5 team pages
                    
        except Exception as e:
            logger.error(f"❌ Error finding team pages: {e}")
            return []
    
    async def _scrape_team_page(self, page_url: str, company_name: str) -> List[Dict[str, Any]]:
        """
        Scrape a team page to extract contact information
        
        Looks for:
        - Names
        - Titles/roles
        - LinkedIn profile links
        - Email addresses (if visible)
        """
        contacts = []
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(page_url, allow_redirects=True) as response:
                    if response.status != 200:
                        logger.warning(f"⚠️ Could not fetch team page: HTTP {response.status}")
                        return []
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Strategy 1: Look for common team member structures
                    # Many sites use divs/sections with class names like "team-member", "person", "staff-member"
                    team_containers = soup.find_all(
                        ['div', 'section', 'article', 'li'],
                        class_=re.compile(r'(team|member|person|staff|executive|leadership|employee|profile)', re.I)
                    )
                    
                    logger.info(f"  🔍 Found {len(team_containers)} potential team member containers")
                    
                    for container in team_containers[:30]:  # Process max 30 containers
                        contact = self._extract_contact_from_container(container, company_name)
                        if contact and contact.get('contact_name'):
                            contacts.append(contact)
                    
                    # Strategy 2: Look for LinkedIn links on the page (people often link their LinkedIn)
                    if len(contacts) < 5:  # If we didn't find many contacts, try LinkedIn link strategy
                        logger.info("  🔍 Trying LinkedIn link extraction strategy...")
                        linkedin_contacts = self._extract_from_linkedin_links(soup, company_name)
                        contacts.extend(linkedin_contacts)
                    
                    logger.info(f"  ✅ Extracted {len(contacts)} contacts from page")
                    return contacts
                    
        except Exception as e:
            logger.error(f"❌ Error scraping team page {page_url}: {e}")
            return []
    
    def _extract_contact_from_container(self, container, company_name: str) -> Optional[Dict[str, Any]]:
        """Extract contact info from a team member container/div"""
        try:
            # Extract name (usually in h2, h3, h4, or span with class "name")
            name = None
            name_elem = (
                container.find(['h2', 'h3', 'h4'], class_=re.compile(r'name', re.I)) or
                container.find(['span', 'div', 'p'], class_=re.compile(r'name', re.I)) or
                container.find(['h2', 'h3', 'h4'])  # Fallback to any heading
            )
            
            if name_elem:
                name = name_elem.get_text(strip=True)
            
            # Extract title/role (usually in span, p, or div with class "title", "role", "position")
            title = None
            title_elem = (
                container.find(['span', 'p', 'div'], class_=re.compile(r'(title|role|position|job)', re.I))
            )
            
            if title_elem:
                title = title_elem.get_text(strip=True)
            
            # Extract LinkedIn profile link
            linkedin = None
            linkedin_link = container.find('a', href=re.compile(r'linkedin\.com', re.I))
            if linkedin_link:
                linkedin = linkedin_link.get('href')
            
            # Extract email if present
            email = None
            email_link = container.find('a', href=re.compile(r'mailto:', re.I))
            if email_link:
                email = email_link.get('href').replace('mailto:', '')
            
            # Only return if we have at least a name
            if name and len(name) > 2 and len(name) < 100:
                contact = {
                    "contact_name": name,
                    "role": title or "Team Member",
                    "company": company_name,
                    "linkedin": linkedin,
                    "email": email,
                    "source": "Web Scraping",
                    "confidence": 0.8 if (title and linkedin) else 0.6
                }
                
                logger.info(f"    👤 {name} - {title or 'No title'}")
                if linkedin:
                    logger.info(f"       🔗 LinkedIn: {linkedin[:50]}...")
                
                return contact
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting contact from container: {e}")
            return None
    
    def _extract_from_linkedin_links(self, soup, company_name: str) -> List[Dict[str, Any]]:
        """Extract contacts by finding LinkedIn profile links on the page"""
        contacts = []
        
        # Find all LinkedIn profile links
        linkedin_links = soup.find_all('a', href=re.compile(r'linkedin\.com/in/', re.I))
        
        logger.info(f"  🔍 Found {len(linkedin_links)} LinkedIn profile links")
        
        for link in linkedin_links[:15]:  # Process max 15 LinkedIn links
            try:
                linkedin_url = link.get('href')
                
                # Try to find the person's name near the LinkedIn link
                # Check parent elements for name
                parent = link.find_parent(['div', 'section', 'article', 'li'])
                if parent:
                    # Look for headings or name-like text
                    name_elem = parent.find(['h2', 'h3', 'h4', 'span', 'p'])
                    if name_elem:
                        name = name_elem.get_text(strip=True)
                        
                        # Extract title if available
                        title_elem = parent.find(['span', 'p'], class_=re.compile(r'(title|role)', re.I))
                        title = title_elem.get_text(strip=True) if title_elem else "Team Member"
                        
                        if name and len(name) > 2 and len(name) < 100:
                            contact = {
                                "contact_name": name,
                                "role": title,
                                "company": company_name,
                                "linkedin": linkedin_url,
                                "email": None,
                                "source": "Web Scraping (LinkedIn)",
                                "confidence": 0.7
                            }
                            contacts.append(contact)
                            logger.info(f"    👤 {name} - {title}")
                            logger.info(f"       🔗 LinkedIn: {linkedin_url[:50]}...")
            
            except Exception as e:
                continue
        
        return contacts
    
    def _filter_by_roles(self, contacts: List[Dict[str, Any]], target_roles: List[str]) -> List[Dict[str, Any]]:
        """Filter contacts to only those matching target roles"""
        if not target_roles:
            return contacts
        
        filtered = []
        
        # Extract keywords from target roles
        role_keywords = set()
        for role in target_roles:
            # Split and add each word
            words = role.lower().split()
            role_keywords.update(words)
        
        logger.info(f"  🎯 Filtering by keywords: {role_keywords}")
        
        for contact in contacts:
            contact_role = (contact.get('role') or '').lower()
            
            # Check if any target role keyword appears in contact's role
            if any(keyword in contact_role for keyword in role_keywords):
                filtered.append(contact)
                logger.info(f"    ✅ Matched: {contact.get('contact_name')} - {contact.get('role')}")
            else:
                logger.info(f"    ❌ Skipped: {contact.get('contact_name')} - {contact.get('role')}")
        
        return filtered


# Global instance
web_scraper = WebContactScraper()


# Export function for use in real_research.py
async def scrape_company_contacts(
    company_name: str,
    website: str,
    target_roles: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Scrape a company website to find contacts
    
    Args:
        company_name: Name of the company
        website: Company website URL
        target_roles: Optional list of roles to target
        
    Returns:
        List of contact dictionaries
    """
    return await web_scraper.find_contacts_at_company(company_name, website, target_roles)
