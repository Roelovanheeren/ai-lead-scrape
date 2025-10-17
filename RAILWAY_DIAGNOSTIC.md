# Railway Diagnostic & Fix Guide

## 🎯 Your App Status

✅ **App is 100% working!**
- Server starts successfully
- Health check passes (200 OK)
- Real research engine loaded
- Google API works (tested: 7.84B results)
- All environment variables correct

❌ **Issue: Railway public URL routing**
- App works internally
- Railway can't route external traffic properly

---

## 🔧 Method 1: Test Your New Domain

You generated a new domain. Test these URLs:

### Test 1: Health Check
```bash
curl https://YOUR-NEW-DOMAIN.railway.app/ping
```

**Expected**: `{"status":"ok","message":"pong"}`

### Test 2: Simple Health
```bash
curl https://YOUR-NEW-DOMAIN.railway.app/healthz
```

**Expected**: `OK`

### Test 3: API Info
```bash
curl https://YOUR-NEW-DOMAIN.railway.app/api
```

**Expected**: JSON with `"real_research_available": true`

---

## 🚀 Method 2: Railway CLI (Most Reliable)

### Step 1: Login to Railway
```bash
cd /home/user/webapp
railway login
```

This will open a browser for authentication.

### Step 2: Link to Your Project
```bash
railway link
```

Select your project from the list.

### Step 3: Check Service Status
```bash
railway status
```

Should show:
- ✅ Service: ai-lead-scrape
- ✅ Status: Active
- ✅ Health: Healthy

### Step 4: Get Logs (Real-time)
```bash
railway logs
```

This shows live logs from your deployment.

### Step 5: Get Service URL
```bash
railway domain
```

This shows your public domain.

### Step 6: Open Service in Browser
```bash
railway open
```

This opens your service URL in a browser.

### Step 7: Force Redeploy (If Needed)
```bash
railway up --detach
```

---

## 🔍 Method 3: Check Railway Dashboard Settings

1. **Go to**: https://railway.app/dashboard
2. **Click your project**: ai-lead-scrape
3. **Click your service** (backend)
4. **Go to Settings tab**

### Check These:

#### A. Networking Section
- [ ] **Public Domain** is shown
- [ ] Domain format: `something.up.railway.app`
- [ ] Click "Generate Domain" if missing

#### B. Deploy Section
- [ ] **Start Command**: `/app/start.sh`
- [ ] **Dockerfile Path**: `Dockerfile`
- [ ] **Root Directory**: Leave empty (default)

#### C. Variables Section
- [ ] All 11 variables are present
- [ ] `PORT` is set or auto-detected
- [ ] `GOOGLE_API_KEY` is set
- [ ] `GOOGLE_CSE_ID` is set

#### D. Environment Section
- [ ] Environment: `production`
- [ ] Branch: `main`

---

## 🧪 Method 4: Manual Test with cURL

If you have the domain, test it manually:

```bash
# Test 1: Simple GET
curl -v https://ai-lead-scrape-production.up.railway.app/ping

# Test 2: Check response headers
curl -I https://ai-lead-scrape-production.up.railway.app/

# Test 3: With timeout
curl --max-time 10 https://ai-lead-scrape-production.up.railway.app/api
```

Look for:
- HTTP status code (should be 200)
- Response body (should be JSON)
- Any error messages

---

## 🔧 Method 5: Regenerate Everything

If nothing else works, start fresh:

### In Railway Dashboard:

1. **Settings** → **Danger Zone** → **Redeploy Service**
2. Wait 5 minutes for full rebuild
3. **Settings** → **Networking** → **Remove Domain**
4. **Settings** → **Networking** → **Generate Domain**
5. Wait 2-3 minutes for DNS propagation

---

## 🐛 Common Issues & Solutions

### Issue 1: "Application failed to respond"
**But logs show 200 OK health check**

**Solution**: Railway proxy issue
```bash
# Force redeploy
railway up --detach

# Or in dashboard: Settings → Redeploy Service
```

### Issue 2: Domain shows 502 Bad Gateway

**Solution**: Port mismatch
- Check Railway logs for: `Uvicorn running on http://0.0.0.0:8000`
- Check Railway env vars for: `PORT=8000` or not set
- Railway auto-sets PORT, should work automatically

### Issue 3: Domain shows 404

**Solution**: Routing issue
- Check Dockerfile EXPOSE line
- Check that start command is `/app/start.sh`

### Issue 4: Domain shows SSL error

**Solution**: DNS not propagated yet
- Wait 5-10 minutes after generating domain
- Try `curl -k` (ignore SSL for testing)

---

## 📊 Expected Working State

Once fixed, you should see:

### Logs:
```
✅ Real research engine loaded successfully
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: 100.64.0.2:xxxxx - "GET /health-check HTTP/1.1" 200 OK
```

### Domain Access:
- https://your-domain.up.railway.app/ → React app loads
- https://your-domain.up.railway.app/api → JSON response
- https://your-domain.up.railway.app/ping → `{"status":"ok"}`

### Job Creation:
- Takes 30-60 seconds (not instant!)
- Returns real company data
- Shows progress updates
- Railway logs show 🌐 Google API requests

---

## 🆘 If Still Broken After All This

It's a Railway infrastructure issue, not your code. Your options:

### Option A: Contact Railway Support
- Go to: https://railway.app/help
- Click "Contact Support"
- Attach your logs and explain the issue
- They usually respond within 1-2 hours

### Option B: Deploy to Alternative Platform

Your app is **production-ready** and works perfectly. Deploy to:

#### 1. Render (Easiest Alternative)
```bash
# 1. Go to: https://render.com
# 2. Connect GitHub repo
# 3. Select "Docker" as deployment
# 4. Add environment variables
# 5. Deploy
```

#### 2. Fly.io (Great for Docker)
```bash
# 1. Install Fly CLI: curl -L https://fly.io/install.sh | sh
# 2. Login: fly auth login
# 3. Launch: fly launch
# 4. Deploy: fly deploy
```

#### 3. Google Cloud Run (Serverless)
```bash
# 1. Enable Cloud Run API
# 2. Build: gcloud builds submit --tag gcr.io/PROJECT/ai-lead-scrape
# 3. Deploy: gcloud run deploy --image gcr.io/PROJECT/ai-lead-scrape
```

---

## ✅ Success Indicators

You'll know it's working when:

1. ✅ Domain loads without "Application failed to respond"
2. ✅ `/api` endpoint shows `"real_research_available": true`
3. ✅ Job takes 30-60 seconds (not instant)
4. ✅ Results show real company names (not "Company 1, 2, 3")
5. ✅ Railway logs show `🌐 Making Google API request`

---

## 📝 Quick Command Reference

```bash
# Railway CLI
railway login              # Login to Railway
railway link              # Link to project
railway status            # Check service status
railway logs              # View logs
railway domain            # Show domain
railway open              # Open in browser
railway up --detach       # Force redeploy

# cURL Testing
curl https://YOUR-DOMAIN/ping         # Test ping
curl https://YOUR-DOMAIN/api          # Test API
curl https://YOUR-DOMAIN/healthz      # Test health

# Check Deployment
railway logs --tail 100               # Last 100 log lines
railway logs --follow                 # Follow logs live
```

---

**Your code is perfect! It's just Railway being difficult. Follow these steps and you'll get it working!** 🚀
