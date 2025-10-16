"""
Make.com Integration Service
Handles Google Sheets integration through Make.com webhooks
"""

import httpx
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class MakeComIntegration:
    """Make.com integration service for Google Sheets automation"""
    
    def __init__(self):
        self.webhook_url = os.getenv('MAKECOM_WEBHOOK_URL')
        self.api_key = os.getenv('MAKECOM_API_KEY')
        
    async def send_lead_to_sheet(self, lead_data: Dict[str, Any], sheet_name: str = "Leads") -> bool:
        """
        Send lead data to Google Sheets via Make.com webhook
        
        Args:
            lead_data: Lead information to send
            sheet_name: Name of the sheet to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.webhook_url:
            logger.warning("Make.com webhook URL not configured")
            return False
            
        payload = {
            "action": "add_lead",
            "sheet_name": sheet_name,
            "data": lead_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}" if self.api_key else None
                    },
                    timeout=30
                )
                response.raise_for_status()
                logger.info(f"Successfully sent lead to Make.com: {lead_data.get('company', 'Unknown')}")
                return True
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Make.com webhook HTTP error: {e.response.status_code} - {e.response.text}")
            return False
        except httpx.RequestError as e:
            logger.error(f"Make.com webhook request error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending to Make.com: {e}")
            return False
    
    async def get_sheet_data(self, sheet_name: str, range_name: str = "A:Z") -> Optional[List[Dict[str, Any]]]:
        """
        Get data from Google Sheets via Make.com webhook
        
        Args:
            sheet_name: Name of the sheet to read
            range_name: Range to read (e.g., "A:Z" for all columns)
            
        Returns:
            List of dictionaries representing sheet rows, or None if failed
        """
        if not self.webhook_url:
            logger.warning("Make.com webhook URL not configured")
            return None
            
        payload = {
            "action": "get_sheet_data",
            "sheet_name": sheet_name,
            "range": range_name,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}" if self.api_key else None
                    },
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                logger.info(f"Successfully retrieved data from sheet: {sheet_name}")
                return data.get("rows", [])
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Make.com webhook HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Make.com webhook request error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting sheet data: {e}")
            return None
    
    async def update_lead_in_sheet(self, lead_id: str, updated_data: Dict[str, Any], sheet_name: str = "Leads") -> bool:
        """
        Update existing lead in Google Sheets via Make.com webhook
        
        Args:
            lead_id: ID of the lead to update
            updated_data: New data for the lead
            sheet_name: Name of the sheet to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.webhook_url:
            logger.warning("Make.com webhook URL not configured")
            return False
            
        payload = {
            "action": "update_lead",
            "lead_id": lead_id,
            "sheet_name": sheet_name,
            "data": updated_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}" if self.api_key else None
                    },
                    timeout=30
                )
                response.raise_for_status()
                logger.info(f"Successfully updated lead in Make.com: {lead_id}")
                return True
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Make.com webhook HTTP error: {e.response.status_code} - {e.response.text}")
            return False
        except httpx.RequestError as e:
            logger.error(f"Make.com webhook request error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating lead: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """
        Test the Make.com webhook connection
        
        Returns:
            bool: True if connection is working, False otherwise
        """
        if not self.webhook_url:
            logger.warning("Make.com webhook URL not configured")
            return False
            
        payload = {
            "action": "test_connection",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}" if self.api_key else None
                    },
                    timeout=10
                )
                response.raise_for_status()
                logger.info("Make.com webhook connection test successful")
                return True
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Make.com webhook test HTTP error: {e.response.status_code} - {e.response.text}")
            return False
        except httpx.RequestError as e:
            logger.error(f"Make.com webhook test request error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error testing Make.com connection: {e}")
            return False

# Global instance
makecom_service = MakeComIntegration()
