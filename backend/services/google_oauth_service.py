"""
Google OAuth Service for User Authentication
Allows users to connect their Google Sheets directly without service account setup
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import secrets
import hashlib

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_OAUTH_AVAILABLE = True
except ImportError:
    GOOGLE_OAUTH_AVAILABLE = False
    logging.warning("Google OAuth not available. Install google-auth-oauthlib")

logger = logging.getLogger(__name__)

class GoogleOAuthService:
    """Service for Google OAuth authentication and sheet management"""
    
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/auth/google/callback')
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
        
        # In-memory storage for demo (use Redis/DB in production)
        self.user_credentials = {}
        self.auth_states = {}
    
    def get_authorization_url(self, user_id: str) -> Dict[str, Any]:
        """Generate Google OAuth authorization URL"""
        try:
            if not GOOGLE_OAUTH_AVAILABLE:
                return {"success": False, "error": "Google OAuth not available"}
            
            if not self.client_id or not self.client_secret:
                return {"success": False, "error": "Google OAuth not configured"}
            
            # Create OAuth flow
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=self.scopes
            )
            flow.redirect_uri = self.redirect_uri
            
            # Generate state for security
            state = secrets.token_urlsafe(32)
            self.auth_states[state] = {
                'user_id': user_id,
                'timestamp': datetime.now()
            }
            
            # Get authorization URL
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=state
            )
            
            return {
                "success": True,
                "auth_url": auth_url,
                "state": state
            }
            
        except Exception as e:
            logger.error(f"Error generating authorization URL: {e}")
            return {"success": False, "error": str(e)}
    
    def handle_callback(self, code: str, state: str) -> Dict[str, Any]:
        """Handle OAuth callback and exchange code for tokens"""
        try:
            if not GOOGLE_OAUTH_AVAILABLE:
                return {"success": False, "error": "Google OAuth not available"}
            
            # Verify state
            if state not in self.auth_states:
                return {"success": False, "error": "Invalid state"}
            
            user_data = self.auth_states[state]
            user_id = user_data['user_id']
            
            # Clean up state
            del self.auth_states[state]
            
            # Create OAuth flow
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=self.scopes
            )
            flow.redirect_uri = self.redirect_uri
            
            # Exchange code for credentials
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            # Store credentials for user
            self.user_credentials[user_id] = {
                'credentials': credentials,
                'connected_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(hours=1)  # Refresh token expires
            }
            
            return {
                "success": True,
                "user_id": user_id,
                "message": "Google account connected successfully"
            }
            
        except Exception as e:
            logger.error(f"Error handling OAuth callback: {e}")
            return {"success": False, "error": str(e)}
    
    def get_user_sheets(self, user_id: str) -> Dict[str, Any]:
        """Get user's Google Sheets"""
        try:
            if not GOOGLE_OAUTH_AVAILABLE:
                return {"success": False, "error": "Google OAuth not available"}
            
            credentials = self._get_user_credentials(user_id)
            if not credentials:
                return {"success": False, "error": "User not authenticated"}
            
            # Build Drive service to list sheets
            drive_service = build('drive', 'v3', credentials=credentials)
            
            # Search for Google Sheets
            results = drive_service.files().list(
                q="mimeType='application/vnd.google-apps.spreadsheet'",
                fields="files(id, name, webViewLink, modifiedTime)",
                orderBy="modifiedTime desc"
            ).execute()
            
            sheets = []
            for file in results.get('files', []):
                sheets.append({
                    'id': file['id'],
                    'name': file['name'],
                    'url': file['webViewLink'],
                    'modified': file.get('modifiedTime', '')
                })
            
            return {
                "success": True,
                "sheets": sheets
            }
            
        except HttpError as e:
            if e.resp.status == 401:
                return {"success": False, "error": "Authentication expired. Please reconnect your Google account."}
            return {"success": False, "error": f"Google API error: {e}"}
        except Exception as e:
            logger.error(f"Error getting user sheets: {e}")
            return {"success": False, "error": str(e)}
    
    def read_sheet_data(self, user_id: str, sheet_id: str, range_name: str = "A:Z") -> Dict[str, Any]:
        """Read data from user's Google Sheet"""
        try:
            if not GOOGLE_OAUTH_AVAILABLE:
                return {"success": False, "error": "Google OAuth not available"}
            
            credentials = self._get_user_credentials(user_id)
            if not credentials:
                return {"success": False, "error": "User not authenticated"}
            
            # Build Sheets service
            sheets_service = build('sheets', 'v4', credentials=credentials)
            
            # Read data
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            return {
                "success": True,
                "data": values,
                "row_count": len(values)
            }
            
        except HttpError as e:
            if e.resp.status == 401:
                return {"success": False, "error": "Authentication expired. Please reconnect your Google account."}
            elif e.resp.status == 403:
                return {"success": False, "error": "Access denied. Please check sheet permissions."}
            return {"success": False, "error": f"Google API error: {e}"}
        except Exception as e:
            logger.error(f"Error reading sheet data: {e}")
            return {"success": False, "error": str(e)}
    
    def write_lead_data(self, user_id: str, sheet_id: str, lead_data: Dict[str, Any], sheet_name: str = "Leads") -> Dict[str, Any]:
        """Write lead data to user's Google Sheet"""
        try:
            if not GOOGLE_OAUTH_AVAILABLE:
                return {"success": False, "error": "Google OAuth not available"}
            
            credentials = self._get_user_credentials(user_id)
            if not credentials:
                return {"success": False, "error": "User not authenticated"}
            
            # Build Sheets service
            sheets_service = build('sheets', 'v4', credentials=credentials)
            
            # Prepare data
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
            
            # Append data
            range_name = f"{sheet_name}!A:I"
            body = {'values': [values]}
            
            result = sheets_service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            return {
                "success": True,
                "updated_cells": result.get('updates', {}).get('updatedCells', 0)
            }
            
        except HttpError as e:
            if e.resp.status == 401:
                return {"success": False, "error": "Authentication expired. Please reconnect your Google account."}
            elif e.resp.status == 403:
                return {"success": False, "error": "Access denied. Please check sheet permissions."}
            return {"success": False, "error": f"Google API error: {e}"}
        except Exception as e:
            logger.error(f"Error writing lead data: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_user_credentials(self, user_id: str) -> Optional[Credentials]:
        """Get user's stored credentials"""
        if user_id not in self.user_credentials:
            return None
        
        user_data = self.user_credentials[user_id]
        
        # Check if credentials are expired
        if datetime.now() > user_data['expires_at']:
            # Try to refresh
            try:
                credentials = user_data['credentials']
                if credentials.refresh_token:
                    credentials.refresh(None)
                    user_data['credentials'] = credentials
                    user_data['expires_at'] = datetime.now() + timedelta(hours=1)
                    return credentials
                else:
                    # No refresh token, need to re-authenticate
                    del self.user_credentials[user_id]
                    return None
            except Exception:
                # Refresh failed, need to re-authenticate
                del self.user_credentials[user_id]
                return None
        
        return user_data['credentials']
    
    def disconnect_user(self, user_id: str) -> Dict[str, Any]:
        """Disconnect user's Google account"""
        try:
            if user_id in self.user_credentials:
                del self.user_credentials[user_id]
            
            return {
                "success": True,
                "message": "Google account disconnected successfully"
            }
        except Exception as e:
            logger.error(f"Error disconnecting user: {e}")
            return {"success": False, "error": str(e)}

# Global instance
google_oauth_service = GoogleOAuthService()
