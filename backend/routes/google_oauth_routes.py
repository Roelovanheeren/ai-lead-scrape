"""
Google OAuth API Routes
Handles user authentication and Google Sheets access
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging

try:
    from services.google_oauth_service import google_oauth_service
except ImportError:
    from ..services.google_oauth_service import google_oauth_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/google", tags=["google-oauth"])

class AuthRequest(BaseModel):
    user_id: str

class SheetConnectionRequest(BaseModel):
    user_id: str
    sheet_id: str
    sheet_name: Optional[str] = "Leads"

class LeadData(BaseModel):
    company: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = "New"
    source: Optional[str] = "AI Platform"

@router.post("/authorize")
async def start_google_auth(request: AuthRequest):
    """Start Google OAuth flow"""
    try:
        result = google_oauth_service.get_authorization_url(request.user_id)
        return result
    except Exception as e:
        logger.error(f"Error starting Google auth: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback")
async def handle_google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(..., description="State parameter for security")
):
    """Handle Google OAuth callback"""
    try:
        result = google_oauth_service.handle_callback(code, state)
        return result
    except Exception as e:
        logger.error(f"Error handling Google callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sheets")
async def get_user_sheets(request: AuthRequest):
    """Get user's Google Sheets"""
    try:
        result = google_oauth_service.get_user_sheets(request.user_id)
        return result
    except Exception as e:
        logger.error(f"Error getting user sheets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sheets/{sheet_id}/read")
async def read_sheet_data(
    sheet_id: str,
    request: AuthRequest,
    range: str = "A:Z"
):
    """Read data from user's Google Sheet"""
    try:
        result = google_oauth_service.read_sheet_data(
            request.user_id,
            sheet_id,
            range
        )
        return result
    except Exception as e:
        logger.error(f"Error reading sheet data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sheets/{sheet_id}/write-lead")
async def write_lead_to_sheet(
    sheet_id: str,
    lead_data: LeadData,
    user_id: str,
    sheet_name: str = "Leads"
):
    """Write lead data to user's Google Sheet"""
    try:
        result = google_oauth_service.write_lead_data(
            user_id,
            sheet_id,
            lead_data.dict(),
            sheet_name
        )
        return result
    except Exception as e:
        logger.error(f"Error writing lead to sheet: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sheets/{sheet_id}/sync-leads")
async def sync_leads_to_sheet(
    sheet_id: str,
    leads: List[LeadData],
    user_id: str,
    sheet_name: str = "Leads"
):
    """Sync multiple leads to user's Google Sheet"""
    try:
        results = []
        for lead in leads:
            result = google_oauth_service.write_lead_data(
                user_id,
                sheet_id,
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
        logger.error(f"Error syncing leads to sheet: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/disconnect")
async def disconnect_google_account(request: AuthRequest):
    """Disconnect user's Google account"""
    try:
        result = google_oauth_service.disconnect_user(request.user_id)
        return result
    except Exception as e:
        logger.error(f"Error disconnecting Google account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{user_id}")
async def get_auth_status(user_id: str):
    """Check if user is authenticated with Google"""
    try:
        credentials = google_oauth_service._get_user_credentials(user_id)
        return {
            "authenticated": credentials is not None,
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Error checking auth status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def check_oauth_health():
    """Check if Google OAuth service is working"""
    try:
        return {
            "status": "healthy",
            "google_oauth_available": True,
            "client_configured": bool(google_oauth_service.client_id and google_oauth_service.client_secret),
            "message": "Google OAuth service ready"
        }
    except Exception as e:
        logger.error(f"Google OAuth health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
