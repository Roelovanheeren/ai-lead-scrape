# 🚀 Railway OAuth Setup Guide

You've successfully created your Google OAuth credentials! Now let's configure them in Railway.

## 🔑 Your OAuth Credentials

**Client ID**: `YOUR_GOOGLE_CLIENT_ID_HERE`
**Client Secret**: `YOUR_GOOGLE_CLIENT_SECRET_HERE`

> **Note**: Replace these placeholders with your actual credentials from the Google Cloud Console dialog you just saw.

## ⚙️ Step 1: Add Environment Variables to Railway

1. **Go to your Railway dashboard**: https://railway.app/dashboard
2. **Select your AI Lead Generation project**
3. **Click on your service** (the one running your app)
4. **Go to "Variables" tab**
5. **Add these environment variables**:

### Required Variables:
```bash
GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID_HERE
GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET_HERE
GOOGLE_REDIRECT_URI=https://your-railway-app.up.railway.app/auth/google/callback
```

## 🔧 Step 2: Update Google Cloud Console

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Navigate to "APIs & Services" → "Credentials"**
3. **Click on your OAuth 2.0 Client ID**
4. **Update "Authorized redirect URIs"**:
   - Add: `https://your-railway-app.up.railway.app/auth/google/callback`
   - Replace `your-railway-app` with your actual Railway app name

## 🧪 Step 3: Test the Integration

### Test OAuth Health Check:
```bash
curl https://your-railway-app.up.railway.app/auth/google/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "google_oauth_available": true,
  "client_configured": true,
  "message": "Google OAuth service ready"
}
```

### Test Authorization URL:
```bash
curl -X POST https://your-railway-app.up.railway.app/auth/google/authorize \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user_123"}'
```

**Expected Response**:
```json
{
  "success": true,
  "auth_url": "https://accounts.google.com/o/oauth2/auth?...",
  "state": "random_state_string"
}
```

## 🎯 Step 4: User Experience Flow

### How Users Will Connect Their Sheets:

1. **User visits your platform**
2. **Clicks "Connect Google Sheets"**
3. **Redirected to Google OAuth**
4. **Logs in with their Google account**
5. **Grants permissions to your app**
6. **Redirected back to your platform**
7. **Can now sync leads to their sheets**

## 🔒 Security Features

✅ **OAuth 2.0 Standard**: Industry-standard authentication
✅ **State Parameter**: Prevents CSRF attacks  
✅ **Token Refresh**: Automatic token renewal
✅ **Scope Limitation**: Only requested permissions
✅ **User Control**: Users can revoke access anytime

## 🚨 Troubleshooting

### Common Issues:

1. **"Invalid redirect URI" error**
   - **Solution**: Check that redirect URI in Google Cloud Console matches exactly
   - **Format**: `https://your-railway-app.up.railway.app/auth/google/callback`

2. **"Client not found" error**
   - **Solution**: Verify Client ID and Client Secret are set correctly in Railway
   - **Check**: Environment variables are visible in Railway dashboard

3. **"Access denied" error**
   - **Solution**: User denied permissions or OAuth consent screen not configured
   - **Check**: OAuth consent screen is published and verified

### Debug Steps:

1. **Check Railway logs**: Look for OAuth-related errors
2. **Test health endpoint**: Verify OAuth service is working
3. **Verify redirect URI**: Must match exactly in Google Cloud Console
4. **Check environment variables**: All three variables must be set

## 📈 What Happens Next

### For Users:
- **Simple Login**: Just click "Connect Google Sheets" and log in with Google
- **No Technical Setup**: No API keys, service accounts, or Google Cloud access needed
- **Secure Access**: Google handles all authentication securely
- **Easy Management**: Users can revoke access anytime

### For You:
- **No User Support**: Users handle their own Google account connections
- **Scalable**: Works for unlimited users
- **Secure**: Google OAuth handles all security
- **Familiar**: Same experience as Make.com and other platforms

## 🎉 Success!

Once configured, your platform will work exactly like Make.com - users simply log in with their Google account and connect their sheets directly! 🚀

## 📞 Need Help?

If you encounter issues:
1. Check Railway logs for error messages
2. Verify all environment variables are set
3. Test the health endpoint first
4. Ensure redirect URI matches exactly in Google Cloud Console

Your AI Lead Generation Platform is now ready for seamless Google Sheets integration! 🎯