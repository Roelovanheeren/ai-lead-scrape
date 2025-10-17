# 🔧 Fix Google Sheets OAuth on Cloudflare Pages

The Google OAuth integration isn't working because the redirect URI is configured for Railway, but you're now using Cloudflare Pages for the frontend.

## 🎯 Quick Fix

You need to update **ONE environment variable** in both Railway AND Cloudflare:

### Step 1: Get Your Cloudflare Pages URL

Your Cloudflare Pages URL is probably something like:
```
https://ai-lead-scrape.pages.dev
```

Or if it's a custom deployment:
```
https://ai-lead-scrape-xxx.pages.dev
```

### Step 2: Update Google Cloud Console

1. Go to: https://console.cloud.google.com/apis/credentials
2. Find your OAuth 2.0 Client ID (the one you're using)
3. Click "Edit"
4. Under **"Authorized redirect URIs"**, ADD these URLs:

```
https://ai-lead-scrape-production.up.railway.app/auth/google/callback
https://your-cloudflare-url.pages.dev/api/auth/google/callback
```

**Important:** Add BOTH URLs so it works from both Railway and Cloudflare!

### Step 3: Update Cloudflare Environment Variables

In your Cloudflare Pages dashboard:

1. Go to **Settings** → **Environment variables**
2. Find `GOOGLE_REDIRECT_URI`
3. Change it to:
```
https://ai-lead-scrape-production.up.railway.app/auth/google/callback
```

**Note:** Keep it pointing to Railway because that's where your backend API is running!

### Step 4: Redeploy

1. In Cloudflare, click **"Retry deployment"** or **"Create deployment"**
2. Wait for deployment to complete
3. Test the Google Sheets integration again

---

## 🔍 Why This Happens

- **Frontend**: Running on Cloudflare Pages (`https://ai-lead-scrape.pages.dev`)
- **Backend**: Running on Railway (`https://ai-lead-scrape-production.up.railway.app`)
- **API Proxy**: Cloudflare Functions proxy `/api/*` requests to Railway
- **OAuth Flow**: Google redirects back to the backend callback URL

---

## ✅ Complete Fix (Alternative)

If the above doesn't work, you can also update the frontend to use the Railway API directly:

### Option 1: Set VITE_API_URL in Cloudflare

Add this environment variable in Cloudflare Pages:

```
VITE_API_URL=https://ai-lead-scrape-production.up.railway.app
```

Then redeploy. This makes the frontend directly call Railway instead of using the proxy.

### Option 2: Update _redirects File

The `_redirects` file should proxy OAuth requests. Make sure it includes:

```
/api/auth/google/*  https://ai-lead-scrape-production.up.railway.app/auth/google/:splat  200
```

---

## 🧪 Test the Fix

After making changes:

1. Go to your Cloudflare Pages URL
2. Click "Connect Google Sheets"
3. You should see Google's OAuth consent screen
4. After authorizing, you should be redirected back to your app

---

## 📝 Current Configuration

Your environment variables should look like this:

**In Cloudflare Pages:**
```bash
GOOGLE_API_KEY=AIzaSyDjnfAynqW9F-nn8EiYYA2-QZtTP-p-UTK
GOOGLE_SEARCH_ENGINE_ID=404c0e062056459a
CLAUDE_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-proj-...
GOOGLE_CLIENT_ID=932138610546-t5k6tcbv5jc23q8l0n445t90admctboky.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
GOOGLE_REDIRECT_URI=https://ai-lead-scrape-production.up.railway.app/auth/google/callback
BACKEND_URL=https://ai-lead-scrape-production.up.railway.app
ENVIRONMENT=production
LOG_LEVEL=INFO
```

---

## 🆘 Still Not Working?

Check these:

1. **Browser Console**: Look for CORS errors or failed API calls
2. **Railway Logs**: Check if OAuth requests are reaching the backend
3. **Google Console**: Verify the redirect URI is whitelisted
4. **Cloudflare Functions**: Check if the proxy is working (`/api` requests)

---

Let me know which approach works best for you!
