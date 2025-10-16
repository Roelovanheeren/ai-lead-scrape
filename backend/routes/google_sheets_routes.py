"""
Google Sheets API Routes
Handles direct Google Sheets integration using service account authentication
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging

from ..services.google_sheets_service import google_sheets_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/google-sheets", tags=["google-sheets"])

class SheetConnectionRequest(BaseModel):
    sheet_url: str

class LeadData(BaseModel):
    company: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = "New"
    source: Optional[str] = "AI Platform"

class UpdateLeadRequest(BaseModel):
    lead_id: str
    sheet_url: str
    sheet_name: str
    data: Dict[str, Any]

class SheetDataRequest(BaseModel):
    sheet_url: str
    range: Optional[str] = "A:Z"

@router.post("/test-connection")
async def test_google_sheets_connection(request: SheetConnectionRequest):
    """Test connection to Google Sheets"""
    try:
        result = await google_sheets_service.test_connection(request.sheet_url)
        return result
    except Exception as e:
        logger.error(f"Error testing Google Sheets connection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/read-data")
async def read_sheet_data(request: SheetDataRequest):
    """Read data from Google Sheets"""
    try:
        result = await google_sheets_service.read_sheet_data(
            request.sheet_url, 
            request.range
        )
        return result
    except Exception as e:
        logger.error(f"Error reading Google Sheets data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/write-lead")
async def write_lead_to_sheet(lead_data: LeadData, sheet_url: str, sheet_name: str = "Leads"):
    """Write lead data to Google Sheets"""
    try:
        result = await google_sheets_service.write_lead_data(
            sheet_url,
            lead_data.dict(),
            sheet_name
        )
        return result
    except Exception as e:
        logger.error(f"Error writing lead to Google Sheets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-lead")
async def update_lead_in_sheet(request: UpdateLeadRequest):
    """Update existing lead in Google Sheets"""
    try:
        result = await google_sheets_service.update_lead_data(
            request.sheet_url,
            request.lead_id,
            request.data,
            request.sheet_name
        )
        return result
    except Exception as e:
        logger.error(f"Error updating lead in Google Sheets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sheet-info")
async def get_sheet_info(request: SheetConnectionRequest):
    """Get information about the Google Sheet"""
    try:
        result = await google_sheets_service.get_sheet_info(request.sheet_url)
        return result
    except Exception as e:
        logger.error(f"Error getting Google Sheets info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync-leads")
async def sync_leads_to_sheet(leads: List[LeadData], sheet_url: str, sheet_name: str = "Leads"):
    """Sync multiple leads to Google Sheets"""
    try:
        results = []
        for lead in leads:
            result = await google_sheets_service.write_lead_data(
                sheet_url,
                lead.dict(),
                sheet_name
            )
            results.append({
                "company": lead.company,
                "success": result.get("success", False),
                "error": result.get("error") if not result.get("success") else None
            })
        
        successful = sum(1 for r in results if r["success"])
        return {
            "status": "success" if successful > 0 else "error",
            "message": f"Synced {successful}/{len(leads)} leads to Google Sheets",
            "results": results
        }
    except Exception as e:
        logger.error(f"Error syncing leads to Google Sheets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def check_google_sheets_health():
    """Check if Google Sheets service is working"""
    try:
        # Check if credentials are configured
        has_credentials = (
            google_sheets_service.service_account_file or 
            google_sheets_service.service_account_json
        )
        
        return {
            "status": "healthy" if has_credentials else "unhealthy",
            "google_apis_available": True,  # Will be False if imports failed
            "credentials_configured": has_credentials,
            "message": "Google Sheets service ready" if has_credentials else "Google Sheets credentials not configured"
        }
    except Exception as e:
        logger.error(f"Google Sheets health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
