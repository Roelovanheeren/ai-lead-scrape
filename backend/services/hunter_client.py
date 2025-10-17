"""
Hunter.io API Client for Email Finding and Verification
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    logging.warning("aiohttp not available")

logger = logging.getLogger(__name__)


class HunterClient:
    """Client for Hunter.io API - Email finding and verification"""
    
    def __init__(self):
        self.api_key = os.getenv("HUNTER_API_KEY")
        self.base_url = "https://api.hunter.io/v2"
        
        if not self.api_key:
            logger.warning("⚠️ HUNTER_API_KEY not set - Hunter.io features disabled")
        else:
            logger.info(f"✅ Hunter.io client initialized with API key: {self.api_key[:10]}...{self.api_key[-10:]}")
    
    async def find_emails_at_domain(self, domain: str, department: str = "executive") -> List[Dict[str, Any]]:
        """Find all emails at a domain
        
        Args:
            domain: Company domain (e.g., "google.com")
            department: Filter by department (executive, it, sales, marketing, etc.)
        
        Returns:
            List of email data with names, positions, confidence scores
        """
        if not self.api_key:
            logger.warning("❌ Hunter.io API key not available")
            return []
        
        if not AIOHTTP_AVAILABLE:
            logger.error("❌ aiohttp not available")
            return []
        
        logger.info(f"🔍 Hunter.io: Searching for emails at {domain} (department: {department})")
        
        url = f"{self.base_url}/domain-search"
        params = {
            "domain": domain,
            "api_key": self.api_key,
            "department": department,
            "limit": 10  # Limit results
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        emails = data.get("data", {}).get("emails", [])
                        logger.info(f"✅ Found {len(emails)} emails at {domain}")
                        
                        # Parse and return structured data
                        results = []
                        for email_data in emails:
                            result = {
                                "email": email_data.get("value"),
                                "first_name": email_data.get("first_name"),
                                "last_name": email_data.get("last_name"),
                                "position": email_data.get("position"),
                                "department": email_data.get("department"),
                                "seniority": email_data.get("seniority"),
                                "linkedin": email_data.get("linkedin"),
                                "twitter": email_data.get("twitter"),
                                "phone_number": email_data.get("phone_number"),
                                "confidence": email_data.get("confidence", 0) / 100,  # Convert to 0-1
                                "verification_status": email_data.get("verification", {}).get("status"),
                                "source": "Hunter.io"
                            }
                            results.append(result)
                        
                        return results
                    
                    elif response.status == 401:
                        logger.error("❌ Hunter.io API: Unauthorized (check API key)")
                        return []
                    
                    elif response.status == 429:
                        logger.error("❌ Hunter.io API: Rate limit exceeded")
                        return []
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Hunter.io API error {response.status}: {error_text[:200]}")
                        return []
        
        except asyncio.TimeoutError:
            logger.error("❌ Hunter.io API request timed out")
            return []
        except Exception as e:
            logger.error(f"❌ Exception in Hunter.io domain search: {type(e).__name__}: {str(e)}")
            return []
    
    async def find_email(self, domain: str, first_name: str, last_name: str) -> Optional[Dict[str, Any]]:
        """Find email address for a specific person
        
        Args:
            domain: Company domain
            first_name: Person's first name
            last_name: Person's last name
        
        Returns:
            Email data with confidence score, or None if not found
        """
        if not self.api_key:
            logger.warning("❌ Hunter.io API key not available")
            return None
        
        if not AIOHTTP_AVAILABLE:
            logger.error("❌ aiohttp not available")
            return None
        
        logger.info(f"🔍 Hunter.io: Finding email for {first_name} {last_name} at {domain}")
        
        url = f"{self.base_url}/email-finder"
        params = {
            "domain": domain,
            "first_name": first_name,
            "last_name": last_name,
            "api_key": self.api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        email_data = data.get("data", {})
                        
                        if email_data.get("email"):
                            logger.info(f"✅ Found email: {email_data.get('email')}")
                            
                            return {
                                "email": email_data.get("email"),
                                "first_name": email_data.get("first_name"),
                                "last_name": email_data.get("last_name"),
                                "position": email_data.get("position"),
                                "linkedin": email_data.get("linkedin"),
                                "twitter": email_data.get("twitter"),
                                "phone_number": email_data.get("phone_number"),
                                "confidence": email_data.get("score", 0) / 100,  # Convert to 0-1
                                "source": "Hunter.io Email Finder"
                            }
                        else:
                            logger.info(f"⚠️ No email found for {first_name} {last_name}")
                            return None
                    else:
                        logger.error(f"❌ Hunter.io API error {response.status}")
                        return None
        
        except Exception as e:
            logger.error(f"❌ Exception in Hunter.io email finder: {type(e).__name__}: {str(e)}")
            return None
    
    async def verify_email(self, email: str) -> Dict[str, Any]:
        """Verify if an email is valid and deliverable
        
        Args:
            email: Email address to verify
        
        Returns:
            Verification result with status and score
        """
        if not self.api_key:
            logger.warning("❌ Hunter.io API key not available")
            return {"valid": False, "status": "no_api_key"}
        
        if not AIOHTTP_AVAILABLE:
            logger.error("❌ aiohttp not available")
            return {"valid": False, "status": "no_aiohttp"}
        
        logger.info(f"🔍 Hunter.io: Verifying email {email}")
        
        url = f"{self.base_url}/email-verifier"
        params = {
            "email": email,
            "api_key": self.api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        verification = data.get("data", {})
                        
                        result = verification.get("result")
                        score = verification.get("score", 0)
                        
                        logger.info(f"✅ Email verification: {result} (score: {score})")
                        
                        return {
                            "valid": result == "deliverable",
                            "status": result,  # deliverable, undeliverable, risky, unknown
                            "score": score,  # 0-100
                            "regexp": verification.get("regexp"),
                            "gibberish": verification.get("gibberish"),
                            "disposable": verification.get("disposable"),
                            "webmail": verification.get("webmail"),
                            "mx_records": verification.get("mx_records"),
                            "smtp_server": verification.get("smtp_server"),
                            "smtp_check": verification.get("smtp_check"),
                            "accept_all": verification.get("accept_all"),
                            "block": verification.get("block"),
                            "source": "Hunter.io"
                        }
                    else:
                        logger.error(f"❌ Hunter.io API error {response.status}")
                        return {"valid": False, "status": "api_error"}
        
        except Exception as e:
            logger.error(f"❌ Exception in Hunter.io email verification: {type(e).__name__}: {str(e)}")
            return {"valid": False, "status": "exception", "error": str(e)}
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information and usage statistics
        
        Returns:
            Account data with remaining requests, limits, etc.
        """
        if not self.api_key:
            return {"error": "API key not set"}
        
        if not AIOHTTP_AVAILABLE:
            return {"error": "aiohttp not available"}
        
        url = f"{self.base_url}/account"
        params = {"api_key": self.api_key}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        account = data.get("data", {})
                        
                        logger.info(f"📊 Hunter.io Account Info:")
                        logger.info(f"   Plan: {account.get('plan_name')}")
                        logger.info(f"   Requests used: {account.get('requests', {}).get('used', 0)}")
                        logger.info(f"   Requests available: {account.get('requests', {}).get('available', 0)}")
                        
                        return account
                    else:
                        return {"error": f"API error {response.status}"}
        
        except Exception as e:
            return {"error": str(e)}


# Global instance
hunter_client = HunterClient()
