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
import pickle

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
        
        # Log configuration status
        logger.info(f"Google OAuth Service initialized:")
        logger.info(f"  - Client ID: {'Set' if self.client_id else 'Not set'}")
        logger.info(f"  - Client Secret: {'Set' if self.client_secret else 'Not set'}")
        logger.info(f"  - Redirect URI: {self.redirect_uri}")
        logger.info(f"  - OAuth Available: {GOOGLE_OAUTH_AVAILABLE}")
        logger.info(f"OAuth scopes configured: {self.scopes}")
        
        # Persistent storage for credentials (survives deployments)
        self.credentials_file = "/tmp/oauth_credentials.pkl"
        self.user_credentials = self._load_credentials()
        self._cleanup_expired_credentials()
        self.auth_states = {}
    
    def _load_credentials(self) -> Dict[str, Any]:
        """Load credentials from persistent storage"""
        try:
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, 'rb') as f:
                    credentials = pickle.load(f)
                    logger.info(f"Loaded {len(credentials)} stored credentials")
                    return credentials
            else:
                logger.info("No stored credentials found")
                return {}
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
            return {}
    
    def _save_credentials(self):
        """Save credentials to persistent storage"""
        try:
            with open(self.credentials_file, 'wb') as f:
                pickle.dump(self.user_credentials, f)
            logger.info(f"Saved {len(self.user_credentials)} credentials to persistent storage")
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
    
    def _cleanup_expired_credentials(self):
        """Clean up expired credentials on startup"""
        try:
            current_time = datetime.now()
            expired_users = []
            
            for user_id, user_data in self.user_credentials.items():
                if current_time > user_data['expires_at']:
                    expired_users.append(user_id)
            
            if expired_users:
                for user_id in expired_users:
                    del self.user_credentials[user_id]
                logger.info(f"Cleaned up {len(expired_users)} expired credentials")
                # Save the cleaned up credentials
                self._save_credentials()
        except Exception as e:
            logger.error(f"Error cleaning up expired credentials: {e}")
    
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
                state=state
            )
            
            logger.info(f"Generated auth URL with scopes: {self.scopes}")
            
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
            logger.info(f"Exchanging code for token with scopes: {self.scopes}")
            flow.fetch_token(code=code)
            credentials = flow.credentials
            logger.info(f"Successfully obtained credentials for user {user_id}")
            
            # Store credentials for user
            self.user_credentials[user_id] = {
                'credentials': credentials,
                'connected_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(hours=24)  # Extend expiration
            }
            
            # Save to persistent storage
            self._save_credentials()
            
            logger.info(f"Stored credentials for user {user_id}, expires at: {self.user_credentials[user_id]['expires_at']}")
            
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
    
    def read_sheet_data(self, user_id: str, sheet_id: str, range_name: str = None) -> Dict[str, Any]:
        """Read data from user's Google Sheet"""
        try:
            logger.info(f"Reading sheet data for user_id: {user_id}, sheet_id: {sheet_id}")
            
            if not GOOGLE_OAUTH_AVAILABLE:
                logger.error("Google OAuth not available")
                return {"success": False, "error": "Google OAuth not available"}
            
            credentials = self._get_user_credentials(user_id)
            if not credentials:
                logger.error(f"No credentials found for user_id: {user_id}")
                return {"success": False, "error": "User not authenticated"}
            
            # Build Sheets service
            sheets_service = build('sheets', 'v4', credentials=credentials)
            
            # If no range specified, get the entire sheet
            if not range_name:
                # First get sheet metadata to determine the range
                sheet_metadata = sheets_service.spreadsheets().get(
                    spreadsheetId=sheet_id
                ).execute()
                
                # Get the first sheet's range
                sheets = sheet_metadata.get('sheets', [])
                if sheets:
                    first_sheet = sheets[0]
                    sheet_properties = first_sheet.get('properties', {})
                    sheet_title = sheet_properties.get('title', 'Sheet1')
                    # Read all columns and rows - use a large range to get everything
                    range_name = f"{sheet_title}!A:ZZ"  # Read all columns A-ZZ to handle more data
                else:
                    range_name = "A:ZZ"
            
            # Read data
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            logger.info(f"Read {len(values)} rows from sheet {sheet_id}")
            if values:
                logger.info(f"First row (headers): {values[0] if values else 'No data'}")
                logger.info(f"Sample data: {values[1:3] if len(values) > 1 else 'No data rows'}")
            
            return {
                "success": True,
                "data": values,
                "values": values,
                "rows": values,
                "row_count": len(values),
                "range_used": range_name
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
        logger.info(f"Looking for credentials for user_id: {user_id}")
        logger.info(f"Available user credentials: {list(self.user_credentials.keys())}")
        
        if user_id not in self.user_credentials:
            logger.warning(f"User {user_id} not found in credentials store")
            return None
        
        user_data = self.user_credentials[user_id]
        
        # Check if credentials are expired
        if datetime.now() > user_data['expires_at']:
            logger.info(f"Credentials for user {user_id} are expired, attempting refresh")
            # Try to refresh
            try:
                credentials = user_data['credentials']
                if credentials.refresh_token:
                    credentials.refresh(None)
                    user_data['credentials'] = credentials
                    user_data['expires_at'] = datetime.now() + timedelta(hours=24)
                    # Save refreshed credentials
                    self._save_credentials()
                    logger.info(f"Successfully refreshed credentials for user {user_id}")
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
