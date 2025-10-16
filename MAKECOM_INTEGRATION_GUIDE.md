# 🔗 Make.com Google Sheets Integration Guide

This guide shows you how to set up Make.com (formerly Integromat) to handle Google Sheets integration for the AI Lead Generation Platform.

## 🎯 Why Make.com?

- **No OAuth Complexity**: No need to handle Google OAuth tokens
- **Visual Workflow**: Easy to set up and maintain
- **Reliable**: Built-in error handling and retry logic
- **Flexible**: Can connect to multiple Google Sheets
- **User-Friendly**: Non-technical users can manage the integration

## 📋 Prerequisites

1. **Make.com Account**: Sign up at [make.com](https://www.make.com/)
2. **Google Account**: With access to Google Sheets
3. **Railway Deployment**: Your AI Lead Generation Platform deployed on Railway

## 🚀 Step 1: Create Make.com Account

1. Go to [make.com](https://www.make.com/)
2. Sign up for a free account
3. Verify your email address

## 🔧 Step 2: Create a New Scenario

1. **Login to Make.com**
2. **Click "Create a new scenario"**
3. **Name it**: "AI Lead Generation - Google Sheets Integration"

## 📊 Step 3: Set Up Google Sheets Module

### 3.1 Add Google Sheets Module

1. **Click the "+" button** to add a module
2. **Search for "Google Sheets"**
3. **Select "Google Sheets"** from the results
4. **Choose "Watch Rows"** (to monitor for new data)

### 3.2 Connect Google Account

1. **Click "Add"** to create a new connection
2. **Sign in with your Google account**
3. **Grant permissions** to access Google Sheets
4. **Test the connection**

### 3.3 Configure the Module

1. **Select your Google Drive**
2. **Choose your spreadsheet** (the one with your leads)
3. **Select the sheet** (e.g., "Leads", "Contacts")
4. **Set the range** (e.g., "A:Z" for all columns)
5. **Set trigger conditions** (e.g., new rows added)

## 🔄 Step 4: Add Webhook Module

### 4.1 Add Webhook Module

1. **Click "+" to add another module**
2. **Search for "Webhooks"**
3. **Select "Custom webhook"**
4. **Choose "Create a webhook"**

### 4.2 Configure Webhook

1. **Copy the webhook URL** (you'll need this for Railway)
2. **Set HTTP method** to "POST"
3. **Add headers** if needed:
   ```
   Content-Type: application/json
   Authorization: Bearer YOUR_API_KEY (optional)
   ```

## 🔗 Step 5: Connect Modules

1. **Connect Google Sheets module** → **Webhook module**
2. **Map the data** from Google Sheets to webhook payload
3. **Test the connection**

## ⚙️ Step 6: Configure Railway Environment Variables

Add these environment variables to your Railway project:

```bash
# Make.com Webhook URL (from Step 4.2)
MAKECOM_WEBHOOK_URL=https://hook.eu1.make.com/YOUR_WEBHOOK_ID

# Optional: API Key for authentication
MAKECOM_API_KEY=your_optional_api_key_here
```

## 🧪 Step 7: Test the Integration

### 7.1 Test from Railway

```bash
# Test the connection
curl -X POST https://your-railway-app.up.railway.app/makecom/test-connection

# Send a test lead
curl -X POST https://your-railway-app.up.railway.app/makecom/send-lead \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Test Company",
    "contact_name": "John Doe",
    "email": "john@testcompany.com",
    "industry": "Technology"
  }'
```

### 7.2 Test from Frontend

1. **Go to your Railway app**
2. **Navigate to "Target Audience Intelligence"**
3. **Click "Connect Google Sheet"**
4. **Enter your Google Sheet URL**
5. **Test the connection**

## 📝 Step 8: Create Make.com Scenarios

### Scenario 1: Add New Leads

1. **Trigger**: Webhook receives data
2. **Action**: Add row to Google Sheets
3. **Mapping**:
   - Company → Column A
   - Contact Name → Column B
   - Email → Column C
   - Phone → Column D
   - Industry → Column E
   - Status → Column F

### Scenario 2: Update Existing Leads

1. **Trigger**: Webhook receives update request
2. **Action**: Update row in Google Sheets
3. **Logic**: Find row by ID/email, update fields

### Scenario 3: Sync Data Back

1. **Trigger**: Google Sheets changes
2. **Action**: Send data back to your app
3. **Use case**: Update lead status, add notes

## 🔧 Step 9: Advanced Configuration

### 9.1 Error Handling

1. **Add error handling** to each module
2. **Set retry logic** for failed operations
3. **Add notifications** for critical errors

### 9.2 Data Transformation

1. **Add "Set variable" modules** for data formatting
2. **Use filters** to process specific data
3. **Add data validation** before sending to sheets

### 9.3 Multiple Sheets

1. **Create separate scenarios** for different sheets
2. **Use different webhook URLs** for each sheet
3. **Organize by lead type** (new leads, qualified leads, etc.)

## 📊 Step 10: Monitor and Maintain

### 10.1 Monitoring

1. **Check Make.com logs** regularly
2. **Monitor webhook performance**
3. **Set up alerts** for failures

### 10.2 Maintenance

1. **Update webhook URLs** if needed
2. **Refresh Google Sheets connections** periodically
3. **Test scenarios** after Google Sheets changes

## 🎯 Benefits of This Approach

✅ **No OAuth Complexity**: Make.com handles Google authentication
✅ **Visual Workflow**: Easy to understand and modify
✅ **Reliable**: Built-in error handling and retries
✅ **Scalable**: Can handle multiple sheets and scenarios
✅ **User-Friendly**: Non-technical users can manage it
✅ **Flexible**: Easy to add new integrations

## 🔗 Example Make.com Scenario

```
Webhook (Receive) → Google Sheets (Add Row) → Slack (Notify)
```

1. **Your app sends lead data** to Make.com webhook
2. **Make.com adds the lead** to Google Sheets
3. **Make.com sends notification** to Slack channel

## 🆘 Troubleshooting

### Common Issues

1. **Webhook not receiving data**
   - Check webhook URL in Railway environment variables
   - Verify Make.com scenario is active
   - Check webhook logs in Make.com

2. **Google Sheets not updating**
   - Verify Google Sheets permissions
   - Check Make.com Google Sheets connection
   - Test the connection in Make.com

3. **Data not mapping correctly**
   - Check field mapping in Make.com
   - Verify data format from your app
   - Test with sample data

### Support Resources

- [Make.com Documentation](https://www.make.com/en/help)
- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Railway Documentation](https://docs.railway.app/)

## 🎉 Success!

Once configured, your AI Lead Generation Platform will automatically sync with Google Sheets through Make.com, providing a seamless integration without the complexity of direct API management.

The integration will:
- ✅ Automatically add new leads to Google Sheets
- ✅ Update existing lead information
- ✅ Sync data bidirectionally
- ✅ Handle errors gracefully
- ✅ Scale with your business needs
