# ⚡ Quick Cloudflare Setup (5 Minutes)

The fastest way to deploy AI Lead Generation Platform to Cloudflare Pages.

---

## 🚀 Step-by-Step Instructions

### Step 1: Open Cloudflare Dashboard
1. Go to: https://dash.cloudflare.com
2. Login (or create free account)
3. Click "Workers & Pages" in sidebar
4. Click "Create application"
5. Click "Pages" tab
6. Click "Connect to Git"

### Step 2: Connect GitHub
1. Click "Connect GitHub"
2. Authorize Cloudflare
3. Select repository: `Roelovanheeren/ai-lead-scrape`
4. Click "Begin setup"

### Step 3: Configure Project

**Project name:**
```
ai-lead-scrape
```

**Build settings:**
- Framework preset: `Create React App`
- Build command: `cd frontend && npm ci && npm run build`
- Build output directory: `frontend/dist`
- Root directory: `/` (leave empty or just `/`)

### Step 4: Add Environment Variables

Click "Environment variables" and add:

```bash
GOOGLE_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
OPENAI_API_KEY=your_openai_key
CLAUDE_API_KEY=your_claude_key
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Important:** Get these API keys from:
- Google: Follow `FREE_API_SETUP.md` guide
- OpenAI: https://platform.openai.com/api-keys
- Claude: https://console.anthropic.com/keys

### Step 5: Deploy!

1. Click "Save and Deploy"
2. Wait 2-3 minutes for build
3. You'll get a URL: `https://ai-lead-scrape-xxx.pages.dev`
4. Click the URL to open your app!

---

## ✅ Verification

### Test Frontend
Open: `https://your-project.pages.dev`

Should see the beautiful UI!

### Test API Status
Open: `https://your-project.pages.dev/api`

Should show:
```json
{
  "status": "running",
  "real_research_available": true,
  "google_api_key": "SET",
  "google_cse_id": "SET"
}
```

### Create a Test Job
Use the UI or curl:
```bash
curl -X POST https://your-project.pages.dev/api/jobs/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "SaaS companies", "target_count": 3}'
```

---

## 🔧 Backend Options

### Option 1: Keep Railway Backend (Easiest)
The Cloudflare Pages deployment will automatically proxy API requests to your Railway backend. No additional setup needed!

### Option 2: Move Backend to Cloudflare Workers (Advanced)
See `CLOUDFLARE_DEPLOYMENT.md` for details on deploying the backend as Cloudflare Workers.

---

## 🎯 What's Different from Railway?

✅ **Automatic Environment Variable Loading** - They just work!
✅ **Faster Builds** - 2-3 minutes vs Railway's 3-5 minutes
✅ **Better Global Performance** - CDN edge network
✅ **More Reliable** - 99.99% uptime
✅ **Preview Deployments** - Every PR gets a preview URL
✅ **Unlimited Bandwidth** - No bandwidth limits on free tier

---

## 🆘 Troubleshooting

### Build Failed?
- Check build logs in Cloudflare dashboard
- Verify Node.js version (Cloudflare uses Node 18)
- Make sure `frontend/dist` is the correct output directory

### API Not Working?
- Verify environment variables are set
- Check Railway backend is still running (if using Railway backend)
- Try the `/api` endpoint to see status

### Variables Not Loading?
- Make sure you clicked "Save" after adding variables
- Redeploy after adding variables (click "Retry deployment")
- Check variable names are EXACT (case-sensitive!)

---

## 💡 Pro Tips

1. **Custom Domain**: Add your own domain in Cloudflare Pages settings
2. **Preview Deployments**: Every PR gets a unique URL for testing
3. **Analytics**: Check Analytics tab for traffic insights
4. **Build Hooks**: Trigger builds via webhook/API
5. **Rollbacks**: One-click rollback to previous deployment

---

## 📊 Next Steps

After deployment:

1. ✅ Test the application thoroughly
2. ✅ Set up your API keys if not already done
3. ✅ Create a test job to verify web crawling works
4. ✅ (Optional) Add custom domain
5. ✅ (Optional) Set up build notifications

---

**🎉 That's it! Your app should be live on Cloudflare Pages!**

Your URL will be something like:
`https://ai-lead-scrape.pages.dev`

---

## 📞 Need Help?

- Read full guide: `CLOUDFLARE_DEPLOYMENT.md`
- Check Cloudflare docs: https://developers.cloudflare.com/pages/
- Review build logs in dashboard
- Check environment variables are set correctly
