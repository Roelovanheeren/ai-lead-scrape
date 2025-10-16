#!/usr/bin/env python3
"""
Test script to check OAuth status and credentials
"""

import os
import sys
sys.path.append('.')

from services.google_oauth_service import GoogleOAuthService

def test_oauth_status():
    """Test OAuth service status"""
    print("🔍 Testing Google OAuth Service Status")
    print("=" * 50)
    
    # Initialize service
    service = GoogleOAuthService()
    
    # Check configuration
    print(f"✅ Client ID: {'Set' if service.client_id else '❌ Not Set'}")
    print(f"✅ Client Secret: {'Set' if service.client_secret else '❌ Not Set'}")
    print(f"✅ Redirect URI: {service.redirect_uri}")
    
    # Check stored credentials
    print(f"\n📊 Stored Credentials:")
    if service.user_credentials:
        for user_id, data in service.user_credentials.items():
            print(f"  - User: {user_id}")
            print(f"    Connected: {data['connected_at']}")
            print(f"    Expires: {data['expires_at']}")
    else:
        print("  ❌ No credentials stored")
    
    # Test reading a specific sheet (if credentials exist)
    test_user_id = 'user_123'
    test_sheet_id = '1fIUwNP7cOhIvOlKpDMIe2ukfmLoCGxEs9MHrRKZj1yA'  # Your sheet ID
    
    print(f"\n🧪 Testing Sheet Read for User: {test_user_id}")
    result = service.read_sheet_data(test_user_id, test_sheet_id)
    
    if result.get('success'):
        print(f"✅ Sheet read successful: {result.get('row_count', 0)} rows")
    else:
        print(f"❌ Sheet read failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_oauth_status()
