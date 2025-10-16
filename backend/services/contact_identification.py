"""
Contact Identification Service
Handles contact discovery, verification, and enrichment for companies
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from ..database.connection import DatabaseConnection
from ..models.schemas import ContactResponse, ContactSeniority
from ..integrations.apollo_client import ApolloClient
from ..integrations.linkedin_client import LinkedInClient
from ..integrations.email_verification import EmailVerificationService
from ..integrations.hunter_client import HunterClient
from ..integrations.dropcontact_client import DropcontactClient
from ..utils.contact_scoring import ContactScoringService
from ..utils.email_finder import EmailFinderService

logger = logging.getLogger(__name__)

class ContactIdentificationService:
    """Service for identifying and verifying contacts at companies"""
    
    def __init__(self):
        self.apollo_client = ApolloClient()
        self.linkedin_client = LinkedInClient()
        self.email_verification = EmailVerificationService()
        self.hunter_client = HunterClient()
        self.dropcontact_client = DropcontactClient()
        self.contact_scoring = ContactScoringService()
        self.email_finder = EmailFinderService()
    
    async def identify_contacts(self, company_id: str) -> List[ContactResponse]:
        """Identify contacts for a company using multiple sources"""
        try:
            # Get company information
            company = await self._get_company_info(company_id)
            if not company:
                logger.warning(f"Company {company_id} not found")
                return []
            
            all_contacts = []
            
            # 1. Apollo.io Contact Discovery
            apollo_contacts = await self._discover_via_apollo(company)
            all_contacts.extend(apollo_contacts)
            
            # 2. LinkedIn Contact Discovery
            linkedin_contacts = await self._discover_via_linkedin(company)
            all_contacts.extend(linkedin_contacts)
            
            # 3. Hunter.io Email Finding
            hunter_contacts = await self._discover_via_hunter(company)
            all_contacts.extend(hunter_contacts)
            
            # 4. Dropcontact Enrichment
            dropcontact_contacts = await self._discover_via_dropcontact(company)
            all_contacts.extend(dropcontact_contacts)
            
            # 5. Web Scraping Contact Discovery
            scraped_contacts = await self._discover_via_web_scraping(company)
            all_contacts.extend(scraped_contacts)
            
            # Deduplicate contacts
            unique_contacts = await self._deduplicate_contacts(all_contacts)
            
            # Verify email addresses
            verified_contacts = await self._verify_contacts(unique_contacts)
            
            # Score contacts
            scored_contacts = await self._score_contacts(verified_contacts, company)
            
            # Store contacts in database
            stored_contacts = await self._store_contacts(company_id, scored_contacts)
            
            logger.info(f"Identified {len(stored_contacts)} contacts for company {company_id}")
            return stored_contacts
            
        except Exception as e:
            logger.error(f"Error identifying contacts for company {company_id}: {str(e)}")
            raise
    
    async def _discover_via_apollo(self, company: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Discover contacts using Apollo.io API"""
        try:
            contacts = []
            
            # Search for people at the company
            apollo_params = {
                "organization_domains": [company.get('domain')],
                "person_titles": self._get_target_titles(),
                "page": 1,
                "per_page": 50
            }
            
            apollo_results = await self.apollo_client.search_people(apollo_params)
            
            for result in apollo_results:
                contact_data = await self._extract_contact_from_apollo(result)
                if contact_data:
                    contacts.append(contact_data)
            
            logger.info(f"Discovered {len(contacts)} contacts via Apollo")
            return contacts
            
        except Exception as e:
            logger.error(f"Error in Apollo contact discovery: {str(e)}")
            return []
    
    async def _discover_via_linkedin(self, company: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Discover contacts using LinkedIn Sales Navigator"""
        try:
            contacts = []
            
            # Search LinkedIn for company employees
            linkedin_params = {
                "company_name": company.get('name'),
                "company_domain": company.get('domain'),
                "titles": self._get_target_titles(),
                "seniority_levels": ["c_level", "vp", "director", "manager"]
            }
            
            linkedin_results = await self.linkedin_client.search_people(linkedin_params)
            
            for result in linkedin_results:
                contact_data = await self._extract_contact_from_linkedin(result)
                if contact_data:
                    contacts.append(contact_data)
            
            logger.info(f"Discovered {len(contacts)} contacts via LinkedIn")
            return contacts
            
        except Exception as e:
            logger.error(f"Error in LinkedIn contact discovery: {str(e)}")
            return []
    
    async def _discover_via_hunter(self, company: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Discover contacts using Hunter.io email finder"""
        try:
            contacts = []
            
            # Use Hunter.io to find email patterns and contacts
            hunter_params = {
                "domain": company.get('domain'),
                "company": company.get('name'),
                "limit": 50
            }
            
            hunter_results = await self.hunter_client.find_contacts(hunter_params)
            
            for result in hunter_results:
                contact_data = await self._extract_contact_from_hunter(result)
                if contact_data:
                    contacts.append(contact_data)
            
            logger.info(f"Discovered {len(contacts)} contacts via Hunter")
            return contacts
            
        except Exception as e:
            logger.error(f"Error in Hunter contact discovery: {str(e)}")
            return []
    
    async def _discover_via_dropcontact(self, company: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Discover contacts using Dropcontact enrichment"""
        try:
            contacts = []
            
            # Use Dropcontact to enrich contact data
            dropcontact_params = {
                "domain": company.get('domain'),
                "company_name": company.get('name')
            }
            
            dropcontact_results = await self.dropcontact_client.enrich_contacts(dropcontact_params)
            
            for result in dropcontact_results:
                contact_data = await self._extract_contact_from_dropcontact(result)
                if contact_data:
                    contacts.append(contact_data)
            
            logger.info(f"Discovered {len(contacts)} contacts via Dropcontact")
            return contacts
            
        except Exception as e:
            logger.error(f"Error in Dropcontact discovery: {str(e)}")
            return []
    
    async def _discover_via_web_scraping(self, company: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Discover contacts through web scraping"""
        try:
            contacts = []
            
            # Scrape company website for contact information
            website_url = company.get('website')
            if not website_url:
                return contacts
            
            # Scrape contact pages, about pages, team pages
            contact_pages = await self._get_contact_pages(website_url)
            
            for page_url in contact_pages:
                scraped_data = await self._scrape_contact_page(page_url)
                extracted_contacts = await self._extract_contacts_from_scraped_data(scraped_data)
                contacts.extend(extracted_contacts)
            
            logger.info(f"Discovered {len(contacts)} contacts via web scraping")
            return contacts
            
        except Exception as e:
            logger.error(f"Error in web scraping contact discovery: {str(e)}")
            return []
    
    async def _verify_contacts(self, contacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Verify email addresses for contacts"""
        try:
            verified_contacts = []
            
            for contact in contacts:
                email = contact.get('email')
                if not email:
                    contact['email_confidence'] = 0.0
                    contact['email_status'] = 'no_email'
                    verified_contacts.append(contact)
                    continue
                
                # Verify email using multiple services
                verification_result = await self._verify_email_address(email)
                
                contact['email_confidence'] = verification_result.get('confidence', 0.0)
                contact['email_status'] = verification_result.get('status', 'unknown')
                contact['verification_date'] = datetime.utcnow()
                
                verified_contacts.append(contact)
            
            return verified_contacts
            
        except Exception as e:
            logger.error(f"Error verifying contacts: {str(e)}")
            return contacts
    
    async def _score_contacts(self, contacts: List[Dict[str, Any]], company: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score contacts based on relevance and quality"""
        try:
            scored_contacts = []
            
            for contact in contacts:
                # Calculate fit score
                fit_score = await self.contact_scoring.calculate_fit_score(contact, company)
                contact['fit_score'] = fit_score
                
                # Determine seniority level
                seniority = await self._determine_seniority_level(contact)
                contact['seniority_level'] = seniority
                
                scored_contacts.append(contact)
            
            # Sort by fit score
            scored_contacts.sort(key=lambda x: x['fit_score'], reverse=True)
            
            return scored_contacts
            
        except Exception as e:
            logger.error(f"Error scoring contacts: {str(e)}")
            return contacts
    
    async def _store_contacts(self, company_id: str, contacts: List[Dict[str, Any]]) -> List[ContactResponse]:
        """Store contacts in the database"""
        try:
            stored_contacts = []
            
            for contact_data in contacts:
                contact_id = str(uuid.uuid4())
                
                # Prepare contact record
                contact_record = {
                    "id": contact_id,
                    "company_id": company_id,
                    "first_name": contact_data.get('first_name'),
                    "last_name": contact_data.get('last_name'),
                    "title": contact_data.get('title'),
                    "email": contact_data.get('email'),
                    "phone": contact_data.get('phone'),
                    "linkedin_url": contact_data.get('linkedin_url'),
                    "department": contact_data.get('department'),
                    "seniority_level": contact_data.get('seniority_level'),
                    "fit_score": contact_data.get('fit_score', 0.0),
                    "email_confidence": contact_data.get('email_confidence', 0.0),
                    "email_status": contact_data.get('email_status'),
                    "verification_date": contact_data.get('verification_date'),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                # Store in database
                await self._insert_contact(contact_record)
                
                # Convert to response model
                stored_contacts.append(ContactResponse(**contact_record))
            
            return stored_contacts
            
        except Exception as e:
            logger.error(f"Error storing contacts: {str(e)}")
            raise
    
    async def get_company_contacts(self, db: DatabaseConnection, company_id: str) -> List[ContactResponse]:
        """Get contacts for a specific company"""
        try:
            results = await db.fetch_all(
                """
                SELECT * FROM contacts 
                WHERE company_id = %s 
                ORDER BY fit_score DESC, email_confidence DESC
                """,
                (company_id,)
            )
            
            return [ContactResponse(**row) for row in results]
            
        except Exception as e:
            logger.error(f"Error getting contacts for company {company_id}: {str(e)}")
            raise
    
    async def refresh_company_contacts(self, db: DatabaseConnection, company_id: str):
        """Refresh contact data for a company"""
        try:
            # Get existing contacts
            existing_contacts = await self.get_company_contacts(db, company_id)
            
            # Re-identify contacts
            new_contacts = await self.identify_contacts(company_id)
            
            # Update existing contacts with new data
            for existing_contact in existing_contacts:
                # Find matching new contact
                matching_contact = next(
                    (nc for nc in new_contacts if self._contacts_match(existing_contact, nc)), 
                    None
                )
                
                if matching_contact:
                    # Update existing contact
                    await self._update_contact(db, existing_contact.id, matching_contact)
            
            logger.info(f"Refreshed contacts for company {company_id}")
            
        except Exception as e:
            logger.error(f"Error refreshing contacts for company {company_id}: {str(e)}")
            raise
    
    # Helper methods
    async def _get_company_info(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get company information from database"""
        # Implementation would fetch from database
        return None
    
    def _get_target_titles(self) -> List[str]:
        """Get target job titles for contact discovery"""
        return [
            "CEO", "Chief Executive Officer", "President",
            "CTO", "Chief Technology Officer", "VP Engineering",
            "CFO", "Chief Financial Officer", "VP Finance",
            "CMO", "Chief Marketing Officer", "VP Marketing",
            "COO", "Chief Operating Officer", "VP Operations",
            "Head of", "Director", "Manager"
        ]
    
    async def _extract_contact_from_apollo(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract contact information from Apollo result"""
        # Add extraction logic here
        return None
    
    async def _extract_contact_from_linkedin(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract contact information from LinkedIn result"""
        # Add extraction logic here
        return None
    
    async def _extract_contact_from_hunter(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract contact information from Hunter result"""
        # Add extraction logic here
        return None
    
    async def _extract_contact_from_dropcontact(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract contact information from Dropcontact result"""
        # Add extraction logic here
        return None
    
    async def _get_contact_pages(self, website_url: str) -> List[str]:
        """Get contact-related pages from a website"""
        pages = []
        # Add page discovery logic here
        return pages
    
    async def _scrape_contact_page(self, page_url: str) -> Dict[str, Any]:
        """Scrape a contact page for information"""
        # Add scraping logic here
        return {}
    
    async def _extract_contacts_from_scraped_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract contacts from scraped data"""
        contacts = []
        # Add extraction logic here
        return contacts
    
    async def _verify_email_address(self, email: str) -> Dict[str, Any]:
        """Verify an email address using multiple services"""
        # Use email verification service
        result = await self.email_verification.verify_email(email)
        return result
    
    async def _determine_seniority_level(self, contact: Dict[str, Any]) -> ContactSeniority:
        """Determine seniority level based on title"""
        title = contact.get('title', '').lower()
        
        if any(keyword in title for keyword in ['ceo', 'chief', 'president', 'founder']):
            return ContactSeniority.C_LEVEL
        elif any(keyword in title for keyword in ['vp', 'vice president', 'head of']):
            return ContactSeniority.VP
        elif any(keyword in title for keyword in ['director', 'head']):
            return ContactSeniority.DIRECTOR
        elif any(keyword in title for keyword in ['manager', 'lead', 'senior']):
            return ContactSeniority.MANAGER
        else:
            return ContactSeniority.INDIVIDUAL
    
    async def _deduplicate_contacts(self, contacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate contacts"""
        unique_contacts = []
        seen_emails = set()
        seen_linkedin = set()
        
        for contact in contacts:
            email = contact.get('email')
            linkedin = contact.get('linkedin_url')
            
            # Skip if we've seen this email or LinkedIn profile
            if email and email in seen_emails:
                continue
            if linkedin and linkedin in seen_linkedin:
                continue
            
            if email:
                seen_emails.add(email)
            if linkedin:
                seen_linkedin.add(linkedin)
            
            unique_contacts.append(contact)
        
        return unique_contacts
    
    def _contacts_match(self, contact1: ContactResponse, contact2: ContactResponse) -> bool:
        """Check if two contacts are the same person"""
        # Match by email
        if contact1.email and contact2.email and contact1.email == contact2.email:
            return True
        
        # Match by LinkedIn URL
        if contact1.linkedin_url and contact2.linkedin_url and contact1.linkedin_url == contact2.linkedin_url:
            return True
        
        # Match by name and company
        if (contact1.first_name and contact1.last_name and 
            contact2.first_name and contact2.last_name and
            contact1.first_name == contact2.first_name and 
            contact1.last_name == contact2.last_name):
            return True
        
        return False
    
    async def _insert_contact(self, contact_record: Dict[str, Any]):
        """Insert contact record into database"""
        # Implementation would insert into database
        pass
    
    async def _update_contact(self, db: DatabaseConnection, contact_id: str, new_contact: ContactResponse):
        """Update existing contact with new data"""
        # Implementation would update database
        pass
