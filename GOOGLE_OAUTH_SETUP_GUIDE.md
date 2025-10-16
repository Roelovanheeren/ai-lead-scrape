# 🔐 Google OAuth Integration Setup Guide

This guide shows you how to set up Google OAuth integration that allows users to connect their Google Sheets directly without any technical setup on their end.

## 🎯 Why OAuth Integration?

- **User-Friendly**: Users just log in with their Google account
- **No Technical Setup**: No service accounts or API keys for users
- **Secure**: Google handles authentication securely
- **Scalable**: Works for unlimited users
- **Familiar**: Same login flow users know from other apps

## 📋 Prerequisites

1. **Google Cloud Project**: For OAuth credentials
2. **Railway Deployment**: Your AI Lead Generation Platform deployed
3. **Domain**: Your platform needs a public domain for OAuth callbacks

## 🚀 Step 1: Create Google Cloud Project

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Click "Select a Project" → "New Project"**
3. **Name it**: "AI Lead Platform OAuth"
4. **Click "Create"**

## 🔧 Step 2: Enable Required APIs

1. **Navigate to "APIs & Services" → "Library"**
2. **Search for and enable these APIs**:
   - **Google Sheets API**
   - **Google Drive API**

## 🔑 Step 3: Create OAuth 2.0 Credentials

1. **Go to "APIs & Services" → "Credentials"**
2. **Click "Create Credentials" → "OAuth 2.0 Client IDs"**
3. **Configure OAuth consent screen** (if not done):
   - **User Type**: External
   - **App Name**: "AI Lead Generation Platform"
   - **User Support Email**: Your email
   - **Developer Contact**: Your email
   - **Scopes**: Add these scopes:
     - `https://www.googleapis.com/auth/spreadsheets`
     - `https://www.googleapis.com/auth/drive.readonly`
4. **Create OAuth 2.0 Client ID**:
   - **Application Type**: Web application
   - **Name**: "AI Lead Platform Web Client"
   - **Authorized JavaScript origins**: 
     - `https://your-railway-app.up.railway.app`
   - **Authorized redirect URIs**:
     - `https://your-railway-app.up.railway.app/auth/google/callback`
5. **Click "Create"**
6. **Copy the Client ID and Client Secret**

## ⚙️ Step 4: Configure Railway Environment Variables

Add these environment variables to your Railway project:

```bash
# Google OAuth Credentials
GOOGLE_CLIENT_ID=your_oauth_client_id_here
GOOGLE_CLIENT_SECRET=your_oauth_client_secret_here
GOOGLE_REDIRECT_URI=https://your-railway-app.up.railway.app/auth/google/callback
```

## 🧪 Step 5: Test the OAuth Flow

### Test Authorization URL
```bash
curl -X POST https://your-railway-app.up.railway.app/auth/google/authorize \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user_123"}'
```

### Test Health Check
```bash
curl https://your-railway-app.up.railway.app/auth/google/health
```

## 🎯 Step 6: User Experience Flow

### How Users Connect Their Sheets:

1. **User clicks "Connect Google Sheets"**
2. **Platform redirects to Google OAuth**
3. **User logs in with their Google account**
4. **User grants permissions to the platform**
5. **Platform redirects back with access token**
6. **User can now sync leads to their sheets**

### API Endpoints Available:

- `POST /auth/google/authorize` - Start OAuth flow
- `GET /auth/google/callback` - Handle OAuth callback
- `POST /auth/google/sheets` - Get user's sheets
- `POST /auth/google/sheets/{sheet_id}/read` - Read sheet data
- `POST /auth/google/sheets/{sheet_id}/write-lead` - Write lead data
- `POST /auth/google/sheets/{sheet_id}/sync-leads` - Sync multiple leads
- `POST /auth/google/disconnect` - Disconnect account
- `GET /auth/google/status/{user_id}` - Check auth status

## 🔒 Security Features

### ✅ Built-in Security:
- **OAuth 2.0**: Industry-standard authentication
- **State Parameter**: Prevents CSRF attacks
- **Token Refresh**: Automatic token renewal
- **Scope Limitation**: Only requested permissions
- **User Control**: Users can revoke access anytime

### ✅ Data Protection:
- **No Credential Storage**: Tokens stored securely
- **Automatic Expiry**: Tokens expire and refresh
- **User Isolation**: Each user's data is separate
- **Permission Scoping**: Only sheet access, not full account

## 🚨 Troubleshooting

### Common Issues:

1. **"Invalid redirect URI" error**
   - **Solution**: Check that redirect URI matches exactly in Google Cloud Console
   - **Format**: `https://your-domain.com/auth/google/callback`

2. **"Access denied" error**
   - **Solution**: User denied permissions or scope issues
   - **Check**: OAuth consent screen is configured properly

3. **"Client not found" error**
   - **Solution**: Verify Client ID and Client Secret are correct
   - **Check**: Environment variables are set properly

4. **"Token expired" error**
   - **Solution**: Tokens are automatically refreshed
   - **Fallback**: User needs to re-authenticate

### Debug Steps:

1. **Check Railway logs**: `railway logs`
2. **Test health endpoint**: `GET /auth/google/health`
3. **Verify OAuth flow**: Test authorization URL generation
4. **Check Google Cloud Console**: Verify credentials and scopes

## 📈 Advanced Features

### Multi-User Support:
```python
# Each user has their own credentials
user_credentials = {
    'user_123': {'credentials': oauth_creds, 'expires_at': datetime.now() + timedelta(hours=1)},
    'user_456': {'credentials': oauth_creds, 'expires_at': datetime.now() + timedelta(hours=1)}
}
```

### Sheet Selection:
```python
# Users can choose from their available sheets
sheets = await google_oauth_service.get_user_sheets(user_id)
# Returns: [{'id': 'sheet1', 'name': 'My Leads', 'url': '...'}, ...]
```

### Automatic Sync:
```python
# Sync leads when job completes
async def sync_leads_on_completion(user_id: str, leads: List[LeadData]):
    for lead in leads:
        await google_oauth_service.write_lead_data(
            user_id=user_id,
            sheet_id=user_selected_sheet_id,
            lead_data=lead.dict()
        )
```

## 🎉 Benefits for Users

### ✅ **No Technical Setup Required**:
- No Google Cloud Console access needed
- No API keys to manage
- No service accounts to create
- No permissions to configure

### ✅ **Familiar Experience**:
- Same Google login they use everywhere
- Standard OAuth flow they recognize
- Clear permission requests
- Easy to revoke access

### ✅ **Secure & Reliable**:
- Google handles authentication
- Industry-standard security
- Automatic token management
- User controls their own data

## 🔗 Useful Links

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [OAuth Consent Screen Setup](https://console.cloud.google.com/apis/credentials/consent)
- [Railway Environment Variables](https://docs.railway.app/develop/variables)

## 📞 Support

If you encounter issues:
1. Check Railway logs for error messages
2. Verify Google Cloud Console settings
3. Test OAuth flow step by step
4. Contact support with specific error messages

Your AI Lead Generation Platform now supports seamless Google Sheets integration for all users! 🚀
