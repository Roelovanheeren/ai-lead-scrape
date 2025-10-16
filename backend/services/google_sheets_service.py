"""
Google Sheets Service
Handles direct Google Sheets integration using service account authentication
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import re
import json

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_APIS_AVAILABLE = True
except ImportError:
    GOOGLE_APIS_AVAILABLE = False
    logging.warning("Google APIs not available. Install google-api-python-client and google-auth")

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    """Service for Google Sheets integration using service account authentication"""
    
    def __init__(self):
        self.service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
        self.service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.service = None
        
    def _get_credentials(self):
        """Get Google service account credentials"""
        try:
            if self.service_account_file and os.path.exists(self.service_account_file):
                # Load from file
                return service_account.Credentials.from_service_account_file(
                    self.service_account_file, 
                    scopes=self.scopes
                )
            elif self.service_account_json:
                # Load from JSON string
                service_account_info = json.loads(self.service_account_json)
                return service_account.Credentials.from_service_account_info(
                    service_account_info,
                    scopes=self.scopes
                )
            else:
                logger.error("No Google service account credentials found")
                return None
        except Exception as e:
            logger.error(f"Error loading Google credentials: {e}")
            return None
    
    def _get_service(self):
        """Get Google Sheets service instance"""
        if not GOOGLE_APIS_AVAILABLE:
            logger.error("Google APIs not available")
            return None
            
        if self.service is None:
            credentials = self._get_credentials()
            if credentials:
                try:
                    self.service = build('sheets', 'v4', credentials=credentials)
                except Exception as e:
                    logger.error(f"Error building Google Sheets service: {e}")
                    return None
        return self.service
    
    def extract_sheet_id(self, url: str) -> Optional[str]:
        """Extract spreadsheet ID from Google Sheets URL"""
        try:
            # Pattern: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
            pattern = r'/spreadsheets/d/([a-zA-Z0-9-_]+)'
            match = re.search(pattern, url)
            if match:
                return match.group(1)
            return None
        except Exception as e:
            logger.error(f"Error extracting sheet ID from URL: {e}")
            return None
    
    async def test_connection(self, sheet_url: str) -> Dict[str, Any]:
        """Test connection to Google Sheets"""
        try:
            sheet_id = self.extract_sheet_id(sheet_url)
            if not sheet_id:
                return {"success": False, "error": "Invalid Google Sheets URL"}
            
            service = self._get_service()
            if not service:
                return {"success": False, "error": "Google Sheets service not available"}
            
            # Try to get spreadsheet metadata
            spreadsheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            
            return {
                "success": True,
                "sheet_id": sheet_id,
                "title": spreadsheet.get('properties', {}).get('title', 'Unknown'),
                "sheets": [sheet.get('properties', {}).get('title', 'Unknown') 
                          for sheet in spreadsheet.get('sheets', [])]
            }
            
        except HttpError as e:
            if e.resp.status == 403:
                return {"success": False, "error": "Access denied. Please share the sheet with the service account."}
            elif e.resp.status == 404:
                return {"success": False, "error": "Sheet not found. Please check the URL."}
            else:
                return {"success": False, "error": f"Google Sheets API error: {e}"}
        except Exception as e:
            logger.error(f"Error testing Google Sheets connection: {e}")
            return {"success": False, "error": str(e)}
    
    async def read_sheet_data(self, sheet_url: str, range_name: str = "A:Z") -> Dict[str, Any]:
        """Read data from Google Sheets"""
        try:
            sheet_id = self.extract_sheet_id(sheet_url)
            if not sheet_id:
                return {"success": False, "error": "Invalid Google Sheets URL"}
            
            service = self._get_service()
            if not service:
                return {"success": False, "error": "Google Sheets service not available"}
            
            # Read data from the sheet
            result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            return {
                "success": True,
                "data": values,
                "row_count": len(values),
                "sheet_id": sheet_id
            }
            
        except HttpError as e:
            return {"success": False, "error": f"Google Sheets API error: {e}"}
        except Exception as e:
            logger.error(f"Error reading Google Sheets data: {e}")
            return {"success": False, "error": str(e)}
    
    async def write_lead_data(self, sheet_url: str, lead_data: Dict[str, Any], sheet_name: str = "Leads") -> Dict[str, Any]:
        """Write lead data to Google Sheets"""
        try:
            sheet_id = self.extract_sheet_id(sheet_url)
            if not sheet_id:
                return {"success": False, "error": "Invalid Google Sheets URL"}
            
            service = self._get_service()
            if not service:
                return {"success": False, "error": "Google Sheets service not available"}
            
            # Prepare data for writing
            values = [
                lead_data.get('company', ''),
                lead_data.get('contact_name', ''),
                lead_data.get('email', ''),
                lead_data.get('phone', ''),
                lead_data.get('industry', ''),
                lead_data.get('location', ''),
                lead_data.get('status', 'New'),
                lead_data.get('source', 'AI Platform'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
            
            # Append data to the sheet
            range_name = f"{sheet_name}!A:I"
            body = {'values': [values]}
            
            result = service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            return {
                "success": True,
                "updated_cells": result.get('updates', {}).get('updatedCells', 0),
                "sheet_id": sheet_id
            }
            
        except HttpError as e:
            return {"success": False, "error": f"Google Sheets API error: {e}"}
        except Exception as e:
            logger.error(f"Error writing to Google Sheets: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_lead_data(self, sheet_url: str, lead_id: str, updated_data: Dict[str, Any], sheet_name: str = "Leads") -> Dict[str, Any]:
        """Update existing lead data in Google Sheets"""
        try:
            sheet_id = self.extract_sheet_id(sheet_url)
            if not sheet_id:
                return {"success": False, "error": "Invalid Google Sheets URL"}
            
            service = self._get_service()
            if not service:
                return {"success": False, "error": "Google Sheets service not available"}
            
            # Find the row with the lead_id (assuming it's in column A)
            range_name = f"{sheet_name}!A:I"
            result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            row_index = None
            
            for i, row in enumerate(values):
                if row and row[0] == lead_id:
                    row_index = i + 1  # Sheets are 1-indexed
                    break
            
            if row_index is None:
                return {"success": False, "error": "Lead not found"}
            
            # Update the row
            update_values = [
                updated_data.get('company', ''),
                updated_data.get('contact_name', ''),
                updated_data.get('email', ''),
                updated_data.get('phone', ''),
                updated_data.get('industry', ''),
                updated_data.get('location', ''),
                updated_data.get('status', ''),
                updated_data.get('source', ''),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
            
            update_range = f"{sheet_name}!A{row_index}:I{row_index}"
            body = {'values': [update_values]}
            
            result = service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=update_range,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            return {
                "success": True,
                "updated_cells": result.get('updatedCells', 0),
                "sheet_id": sheet_id
            }
            
        except HttpError as e:
            return {"success": False, "error": f"Google Sheets API error: {e}"}
        except Exception as e:
            logger.error(f"Error updating Google Sheets data: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_sheet_info(self, sheet_url: str) -> Dict[str, Any]:
        """Get information about the Google Sheet"""
        try:
            sheet_id = self.extract_sheet_id(sheet_url)
            if not sheet_id:
                return {"success": False, "error": "Invalid Google Sheets URL"}
            
            service = self._get_service()
            if not service:
                return {"success": False, "error": "Google Sheets service not available"}
            
            # Get spreadsheet metadata
            spreadsheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            
            sheets_info = []
            for sheet in spreadsheet.get('sheets', []):
                sheet_props = sheet.get('properties', {})
                sheets_info.append({
                    'title': sheet_props.get('title', 'Unknown'),
                    'sheet_id': sheet_props.get('sheetId', 0),
                    'row_count': sheet_props.get('gridProperties', {}).get('rowCount', 0),
                    'column_count': sheet_props.get('gridProperties', {}).get('columnCount', 0)
                })
            
            return {
                "success": True,
                "sheet_id": sheet_id,
                "title": spreadsheet.get('properties', {}).get('title', 'Unknown'),
                "sheets": sheets_info,
                "url": sheet_url
            }
            
        except HttpError as e:
            return {"success": False, "error": f"Google Sheets API error: {e}"}
        except Exception as e:
            logger.error(f"Error getting Google Sheets info: {e}")
            return {"success": False, "error": str(e)}

# Global instance
google_sheets_service = GoogleSheetsService()
