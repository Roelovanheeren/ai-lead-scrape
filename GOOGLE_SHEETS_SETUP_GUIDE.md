# 🔗 Google Sheets Direct Integration Setup Guide

This guide shows you how to set up direct Google Sheets integration using service account authentication for the AI Lead Generation Platform.

## 🎯 Why Direct Integration?

- **No Third-Party Dependencies**: Direct API access without Make.com
- **Real-Time Sync**: Immediate data updates
- **Full Control**: Complete control over data flow
- **Cost Effective**: No additional service fees
- **Reliable**: Direct Google API connection

## 📋 Prerequisites

1. **Google Account**: With access to Google Sheets
2. **Google Cloud Project**: For API credentials
3. **Railway Deployment**: Your AI Lead Generation Platform deployed

## 🚀 Step 1: Create Google Cloud Project

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Click "Select a Project" → "New Project"**
3. **Name it**: "AI Lead Sheet Connector"
4. **Click "Create"**

## 🔧 Step 2: Enable Required APIs

1. **Navigate to "APIs & Services" → "Library"**
2. **Search for and enable these APIs**:
   - **Google Sheets API**
   - **Google Drive API**

## 🔑 Step 3: Create Service Account

1. **Go to "APIs & Services" → "Credentials"**
2. **Click "Create Credentials" → "Service Account"**
3. **Enter details**:
   - **Name**: `ai-lead-sheet-connector`
   - **Description**: `Service account for AI Lead Generation Platform`
4. **Click "Create and Continue"**
5. **Grant role**: `Editor` (or `Writer` for more security)
6. **Click "Done"**

## 📄 Step 4: Create Service Account Key

1. **Click on your service account** (ai-lead-sheet-connector)
2. **Go to "Keys" tab**
3. **Click "Add Key" → "Create New Key"**
4. **Choose "JSON" format**
5. **Click "Create"**
6. **Download the JSON file** (keep it secure!)

## 📊 Step 5: Share Your Google Sheet

1. **Open your Google Sheet**
2. **Click "Share" button**
3. **Add your service account email** (looks like: `ai-lead-sheet-connector@your-project.iam.gserviceaccount.com`)
4. **Give it "Editor" access**
5. **Click "Send"**

## ⚙️ Step 6: Configure Railway Environment Variables

Add these environment variables to your Railway project:

### Option A: JSON String (Recommended)
```bash
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"your-project",...}
```

### Option B: File Path (Alternative)
```bash
GOOGLE_SERVICE_ACCOUNT_FILE=/app/credentials/service-account.json
```

## 🧪 Step 7: Test the Integration

### Test Connection
```bash
curl -X POST https://your-railway-app.up.railway.app/google-sheets/test-connection \
  -H "Content-Type: application/json" \
  -d '{"sheet_url": "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"}'
```

### Test Writing Data
```bash
curl -X POST https://your-railway-app.up.railway.app/google-sheets/write-lead \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Test Company",
    "contact_name": "John Doe",
    "email": "john@testcompany.com",
    "industry": "Technology"
  }' \
  -G -d "sheet_url=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
```

## 🎯 Step 8: Use in Your Platform

### Frontend Integration
The platform will now:
1. **Extract Sheet ID** from the Google Sheets URL
2. **Test Connection** using service account authentication
3. **Read/Write Data** directly to your sheet
4. **Sync Lead Data** automatically

### API Endpoints Available
- `POST /google-sheets/test-connection` - Test sheet access
- `POST /google-sheets/read-data` - Read sheet data
- `POST /google-sheets/write-lead` - Add new lead
- `POST /google-sheets/update-lead` - Update existing lead
- `POST /google-sheets/sync-leads` - Sync multiple leads
- `GET /google-sheets/health` - Check service status

## 🔒 Security Best Practices

### ✅ Do's
- **Keep credentials secure**: Never commit JSON keys to code
- **Use environment variables**: Store credentials in Railway
- **Limit permissions**: Use minimal required roles
- **Rotate keys regularly**: Update service account keys periodically
- **Monitor access**: Check Google Cloud audit logs

### ❌ Don'ts
- **Don't expose keys**: Never put credentials in frontend code
- **Don't share keys**: Keep service account files private
- **Don't use admin roles**: Use minimal required permissions
- **Don't ignore errors**: Handle API errors gracefully

## 🚨 Troubleshooting

### Common Issues

1. **"Access denied" error**
   - **Solution**: Share the sheet with your service account email
   - **Check**: Service account has Editor access

2. **"Sheet not found" error**
   - **Solution**: Verify the Google Sheets URL is correct
   - **Check**: Sheet ID is properly extracted from URL

3. **"Credentials not found" error**
   - **Solution**: Set `GOOGLE_SERVICE_ACCOUNT_JSON` environment variable
   - **Check**: JSON format is correct

4. **"API not enabled" error**
   - **Solution**: Enable Google Sheets API and Google Drive API
   - **Check**: APIs are enabled in Google Cloud Console

### Debug Steps

1. **Check Railway logs**: `railway logs`
2. **Test health endpoint**: `GET /google-sheets/health`
3. **Verify credentials**: Check environment variables
4. **Test with simple sheet**: Use a basic test sheet first

## 📈 Advanced Features

### Automated Lead Sync
```python
# Example: Sync leads when job completes
async def sync_leads_on_completion(job_id: str, leads: List[LeadData]):
    for lead in leads:
        await google_sheets_service.write_lead_data(
            sheet_url=LEAD_SHEET_URL,
            lead_data=lead.dict(),
            sheet_name="Leads"
        )
```

### Real-time Updates
```python
# Example: Update lead status
async def update_lead_status(lead_id: str, new_status: str):
    await google_sheets_service.update_lead_data(
        sheet_url=LEAD_SHEET_URL,
        lead_id=lead_id,
        updated_data={"status": new_status},
        sheet_name="Leads"
    )
```

## 🎉 Success!

Once configured, your AI Lead Generation Platform will:

✅ **Automatically sync leads** to Google Sheets
✅ **Update lead status** in real-time
✅ **Read existing data** for analysis
✅ **Handle errors gracefully** with retry logic
✅ **Scale efficiently** with Google's infrastructure

## 🔗 Useful Links

- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Railway Environment Variables](https://docs.railway.app/develop/variables)
- [Service Account Authentication](https://cloud.google.com/docs/authentication/service-accounts)

## 📞 Support

If you encounter issues:
1. Check Railway logs for error messages
2. Verify Google Cloud Console settings
3. Test with a simple sheet first
4. Contact support with specific error messages

Your AI Lead Generation Platform is now ready for seamless Google Sheets integration! 🚀
