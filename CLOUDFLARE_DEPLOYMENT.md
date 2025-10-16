# 🚀 Cloudflare Pages Deployment Guide

Complete guide to deploy AI Lead Generation Platform to Cloudflare Pages.

---

## 📋 Prerequisites

- Cloudflare account (free): https://dash.cloudflare.com/sign-up
- GitHub account with access to this repository
- Your API keys ready (Google, OpenAI, Claude)

---

## 🎯 Deployment Steps

### Step 1: Connect GitHub to Cloudflare Pages

1. **Go to Cloudflare Dashboard**
   - Visit: https://dash.cloudflare.com
   - Login to your account

2. **Navigate to Pages**
   - Click "Workers & Pages" in the left sidebar
   - Click "Create application"
   - Choose "Pages"
   - Click "Connect to Git"

3. **Connect GitHub Repository**
   - Click "Connect GitHub"
   - Authorize Cloudflare to access your repositories
   - Select repository: `Roelovanheeren/ai-lead-scrape`
   - Click "Begin setup"

### Step 2: Configure Build Settings

On the setup page, configure:

**Project name:**
```
ai-lead-scrape
```

**Production branch:**
```
main
```

**Framework preset:**
```
Create React App
```

**Build command:**
```
cd frontend && npm ci && npm run build
```

**Build output directory:**
```
frontend/dist
```

**Root directory:**
```
/
```

**Environment variables (click "Add variable" for each):**

```bash
# Required for Web Crawling
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here

# Required for AI Analysis (at least one)
OPENAI_API_KEY=your_openai_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here

# Application Settings
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Step 3: Deploy

1. Click "Save and Deploy"
2. Wait for build to complete (~2-3 minutes)
3. You'll get a URL like: `https://ai-lead-scrape.pages.dev`

---

## 🔧 Backend API Setup (Option 1: Cloudflare Workers)

### Create a Cloudflare Worker for the Backend

1. **Go to Workers & Pages**
   - Click "Create application"
   - Choose "Workers"
   - Name it: `ai-lead-scrape-api`

2. **Deploy Worker Code**

Create a new file `worker.js` with your backend code, or use the provided worker configuration.

3. **Configure Environment Variables**
   - Go to Worker settings
   - Click "Variables"
   - Add the same environment variables as above

4. **Set up Routes**
   - Go to "Triggers" tab
   - Add route: `your-domain.pages.dev/api/*`
   - Point to your Worker

---

## 🔧 Backend API Setup (Option 2: Keep Railway Backend)

If you prefer to keep the backend on Railway:

1. **Update Frontend API URL**

Edit `frontend/.env.production`:
```bash
VITE_API_URL=https://ai-lead-scrape-production.up.railway.app
```

2. **Configure CORS on Backend**

The backend is already configured for CORS, but verify it allows requests from:
```
https://ai-lead-scrape.pages.dev
```

3. **Rebuild Frontend**
```bash
cd frontend
npm run build
```

4. **Redeploy to Cloudflare Pages**
   - Cloudflare will auto-deploy on git push
   - Or click "Retry deployment" in Cloudflare dashboard

---

## 🧪 Testing Your Deployment

### 1. Test Frontend
Visit your Cloudflare Pages URL:
```
https://ai-lead-scrape.pages.dev
```

### 2. Test API (if using Cloudflare Workers)
```bash
curl https://ai-lead-scrape.pages.dev/api/health
```

### 3. Test Job Creation
```bash
curl -X POST https://ai-lead-scrape.pages.dev/api/jobs/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "SaaS companies", "target_count": 3}'
```

---

## 🔄 Continuous Deployment

Once set up, Cloudflare Pages automatically:
- ✅ Builds on every push to `main`
- ✅ Creates preview deployments for PRs
- ✅ Rolls back on build failures
- ✅ Provides build logs and analytics

---

## 📊 Monitoring

### View Deployment Status
- Cloudflare Dashboard → Pages → ai-lead-scrape
- See build logs, deployment history, and analytics

### Check Build Logs
- Click on any deployment
- View "Build log" tab
- See detailed build output

### Monitor Performance
- Go to "Analytics" tab
- See requests, bandwidth, and performance metrics

---

## 🔑 Environment Variables Management

### Update Environment Variables

1. Go to Cloudflare Dashboard
2. Navigate to Pages → ai-lead-scrape
3. Click "Settings" → "Environment variables"
4. Add/Edit variables
5. Click "Save" → Redeploy automatically

**Note:** Changes to environment variables require a redeploy!

---

## 🚨 Troubleshooting

### Build Fails

**Problem:** Build command fails
**Solution:** Check build logs for specific errors

**Common Issues:**
- Missing dependencies: Run `npm ci` instead of `npm install`
- Wrong node version: Cloudflare uses Node 18 by default
- Build path issues: Verify `frontend/dist` exists

### Environment Variables Not Working

**Problem:** API keys not being read
**Solution:** 
1. Verify variables are set in Cloudflare dashboard
2. Check variable names match exactly (case-sensitive)
3. Redeploy after setting variables
4. Use `/api` endpoint to check which variables are set

### CORS Issues

**Problem:** Frontend can't connect to backend
**Solution:**
1. Update backend CORS to allow Cloudflare Pages domain
2. Or use Cloudflare Workers for backend
3. Check browser console for CORS errors

### Build Output Directory Wrong

**Problem:** 404 errors after deployment
**Solution:**
1. Verify build output directory is `frontend/dist`
2. Check that `npm run build` creates `dist` folder
3. Update build configuration if needed

---

## 📈 Performance Tips

### 1. Enable Cloudflare CDN
- Automatically enabled for static assets
- Frontend served from edge locations worldwide

### 2. Use Cloudflare Workers for API
- Faster than external backend
- No cold starts
- Global edge network

### 3. Configure Caching
- Set appropriate cache headers
- Use Cloudflare Page Rules
- Cache static assets longer

### 4. Enable Minification
- Cloudflare auto-minifies HTML, CSS, JS
- Check Settings → Optimization

---

## 💰 Pricing

### Cloudflare Pages (Free Tier)

- ✅ Unlimited bandwidth
- ✅ Unlimited requests
- ✅ 500 builds/month
- ✅ 1 build at a time
- ✅ 100 custom domains

### Cloudflare Workers (Free Tier)

- ✅ 100,000 requests/day
- ✅ 10ms CPU time per request
- ✅ 1MB script size

**Perfect for testing and small-scale production use!**

---

## 🎉 Next Steps

After successful deployment:

1. ✅ Set up custom domain (optional)
2. ✅ Configure DNS settings
3. ✅ Enable HTTPS (automatic with Cloudflare)
4. ✅ Set up analytics and monitoring
5. ✅ Configure automatic deployments
6. ✅ Test web crawling with real API keys

---

## 📚 Additional Resources

- [Cloudflare Pages Documentation](https://developers.cloudflare.com/pages/)
- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Build Configuration Guide](https://developers.cloudflare.com/pages/configuration/build-configuration/)
- [Environment Variables Guide](https://developers.cloudflare.com/pages/configuration/environment-variables/)

---

## 🆘 Need Help?

If you encounter issues:

1. Check Cloudflare build logs
2. Review this deployment guide
3. Check the GitHub repository issues
4. Contact Cloudflare support (free tier includes basic support)

---

**Ready to deploy? Follow Step 1 above!** 🚀
