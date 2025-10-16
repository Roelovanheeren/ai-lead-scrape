"""
Make.com Integration API Routes
Handles Google Sheets integration through Make.com webhooks
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging

from ..services.makecom_integration import makecom_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/makecom", tags=["makecom"])

class LeadData(BaseModel):
    company: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = "New"

class SheetDataRequest(BaseModel):
    sheet_name: str
    range: Optional[str] = "A:Z"

class UpdateLeadRequest(BaseModel):
    lead_id: str
    sheet_name: str
    data: Dict[str, Any]

@router.post("/test-connection")
async def test_makecom_connection():
    """Test Make.com webhook connection"""
    try:
        success = await makecom_service.test_connection()
        if success:
            return {"status": "success", "message": "Make.com connection is working"}
        else:
            return {"status": "error", "message": "Make.com connection failed"}
    except Exception as e:
        logger.error(f"Error testing Make.com connection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-lead")
async def send_lead_to_sheet(lead_data: LeadData, sheet_name: str = "Leads"):
    """Send lead data to Google Sheets via Make.com"""
    try:
        success = await makecom_service.send_lead_to_sheet(
            lead_data.dict(), 
            sheet_name
        )
        if success:
            return {"status": "success", "message": "Lead sent to Google Sheets successfully"}
        else:
            return {"status": "error", "message": "Failed to send lead to Google Sheets"}
    except Exception as e:
        logger.error(f"Error sending lead to Make.com: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get-sheet-data")
async def get_sheet_data(request: SheetDataRequest):
    """Get data from Google Sheets via Make.com"""
    try:
        data = await makecom_service.get_sheet_data(
            request.sheet_name, 
            request.range
        )
        if data is not None:
            return {"status": "success", "data": data}
        else:
            return {"status": "error", "message": "Failed to retrieve sheet data"}
    except Exception as e:
        logger.error(f"Error getting sheet data from Make.com: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-lead")
async def update_lead_in_sheet(request: UpdateLeadRequest):
    """Update existing lead in Google Sheets via Make.com"""
    try:
        success = await makecom_service.update_lead_in_sheet(
            request.lead_id,
            request.data,
            request.sheet_name
        )
        if success:
            return {"status": "success", "message": "Lead updated in Google Sheets successfully"}
        else:
            return {"status": "error", "message": "Failed to update lead in Google Sheets"}
    except Exception as e:
        logger.error(f"Error updating lead in Make.com: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sheets")
async def list_available_sheets():
    """List available Google Sheets (mock implementation)"""
    # This would typically connect to Make.com to get available sheets
    # For now, return a mock response
    return {
        "status": "success",
        "sheets": [
            {"name": "Leads", "id": "leads_sheet", "url": "https://docs.google.com/spreadsheets/d/1fIUwNP7cOhIvOlKpDMIe2ukfmLoCGxEs9MHrRKZj1yA/edit"},
            {"name": "Contacts", "id": "contacts_sheet", "url": "https://docs.google.com/spreadsheets/d/1fIUwNP7cOhIvOlKpDMIe2ukfmLoCGxEs9MHrRKZj1yA/edit"},
            {"name": "Campaigns", "id": "campaigns_sheet", "url": "https://docs.google.com/spreadsheets/d/1fIUwNP7cOhIvOlKpDMIe2ukfmLoCGxEs9MHrRKZj1yA/edit"}
        ]
    }

@router.post("/sync-leads")
async def sync_leads_to_sheet(leads: List[LeadData], sheet_name: str = "Leads"):
    """Sync multiple leads to Google Sheets via Make.com"""
    try:
        results = []
        for lead in leads:
            success = await makecom_service.send_lead_to_sheet(
                lead.dict(), 
                sheet_name
            )
            results.append({
                "company": lead.company,
                "success": success
            })
        
        successful = sum(1 for r in results if r["success"])
        return {
            "status": "success" if successful > 0 else "error",
            "message": f"Synced {successful}/{len(leads)} leads to Google Sheets",
            "results": results
        }
    except Exception as e:
        logger.error(f"Error syncing leads to Make.com: {e}")
        raise HTTPException(status_code=500, detail=str(e))
