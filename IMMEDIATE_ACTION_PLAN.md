# Immediate Action Plan - Fix Job Processing

## 🎉 What's Fixed

✅ **Frontend routing** - All navigation works perfectly  
✅ **Diagnostic tools** - Added container restart tracking  
✅ **Error logging** - Comprehensive logging for debugging  

---

## 🔍 What We Need to Test

### Test 1: Verify Web Crawling Works (Ignore Job Persistence for Now)

**Purpose**: Confirm Google API is actually being called and web scraping happens

**Steps**:
1. Open Railway logs in real-time
2. Create a new job with simple prompt: "Find AI companies in San Francisco"
3. Watch logs for these indicators:

**✅ Success Indicators** (web crawling IS working):
```
🚀 BACKGROUND TASK STARTED for job abc-123
🔍 SEARCH_COMPANIES CALLED
Google API key available: True
Google CSE ID available: True
📡 Sending request to: https://www.googleapis.com/customsearch/v1
Response status: 200
✅ Received 10 search results from Google
```

**❌ Failure Indicators** (falling back to simulation):
```
⚠️ No companies found, falling back to simulation
⚠️ REAL RESEARCH IS NOT WORKING - Using simulation mode
```

**Expected Result**: You should see REAL Google API calls in the logs within 5-10 seconds of job creation.

---

### Test 2: Check Container Uptime

**URL**: `https://your-app.railway.app/debug/container-info`

**What to look for**:
```json
{
  "container_start_time": "2025-10-17T16:00:00.000000",
  "uptime_seconds": 3600,  ← If this is < 120, container just restarted
  "jobs_in_memory": 0,      ← Jobs lost on restart
  "real_research_available": true  ← MUST be true
}
```

**Action**: If `uptime_seconds` is very low (< 2 minutes), Railway is restarting frequently.

---

### Test 3: Quick Job Creation & Status Check

**Goal**: Create job and check status IMMEDIATELY (before potential restart)

```bash
# 1. Create job
curl -X POST https://your-app.railway.app/jobs/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Find tech companies", "target_count": 3}'

# You'll get back: {"job_id": "abc-123", ...}

# 2. IMMEDIATELY check status (replace abc-123)
curl https://your-app.railway.app/jobs/abc-123

# 3. Check again after 10 seconds
sleep 10 && curl https://your-app.railway.app/jobs/abc-123

# 4. Check again after 30 seconds
sleep 20 && curl https://your-app.railway.app/jobs/abc-123
```

**Expected Results**:

**Scenario A: Web Crawling Works, No Restart**
```
1st check: {"status": "started", "progress": 10, ...}
2nd check: {"status": "started", "progress": 40, ...}
3rd check: {"status": "completed", "leads": [...]}
```
✅ **Everything works!** Just add persistent storage.

**Scenario B: Web Crawling Works, But Container Restarted**
```
1st check: {"status": "started", "progress": 10, ...}
2nd check: {"status": "not_found", "container_start_time": "2025-10-17T16:05:00", ...}
```
✅ **Web crawling works**, ❌ **Container restarts frequently** → Add persistent storage (PostgreSQL/Redis)

**Scenario C: Simulation Mode (No Real Crawling)**
```
1st check: {"status": "started", "progress": 25, ...}
2nd check: {"status": "completed", "progress": 100, ...}  ← Too fast!
Logs show: "⚠️ falling back to simulation"
```
❌ **Web crawling NOT working** → Check API keys and environment variables

---

## 🎯 Next Steps Based on Test Results

### If Web Crawling Works (Scenario A or B)

**Problem**: Jobs disappear due to container restarts (in-memory storage)

**Solution**: Add persistent storage

#### Option 1: PostgreSQL (Recommended)

**Why**: Free tier on Railway, persistent, scalable

**Steps**:
1. Go to Railway dashboard
2. Click "New" → "Database" → "Add PostgreSQL"
3. Railway auto-connects via `DATABASE_URL` env var
4. Add to `requirements-railway.txt`:
   ```
   sqlalchemy==2.0.23
   psycopg2-binary==2.9.9
   ```
5. Update `backend/main_simple.py` to use SQLAlchemy (see JOB_TROUBLESHOOTING.md)

**Estimated Time**: 30 minutes

#### Option 2: Redis (Fastest)

**Why**: Super fast, simple key-value storage

**Steps**:
1. Go to Railway dashboard
2. Click "New" → "Database" → "Add Redis"
3. Railway auto-connects via `REDIS_URL` env var
4. Add to `requirements-railway.txt`:
   ```
   redis==5.0.1
   ```
5. Update `backend/main_simple.py` to use Redis (see JOB_TROUBLESHOOTING.md)

**Estimated Time**: 15 minutes

---

### If Web Crawling NOT Working (Scenario C)

**Problem**: Google Custom Search API not being called

**Diagnosis Steps**:

1. **Check environment variables in Railway**:
   - `GOOGLE_API_KEY` → Should be ~44 characters
   - `GOOGLE_CSE_ID` → Should be `404c0e0620566459a`
   
2. **Check logs for**:
   ```
   ✅ Real research engine loaded successfully
   REAL_RESEARCH_AVAILABLE: True
   ```

3. **If `REAL_RESEARCH_AVAILABLE: False`**:
   - Dependencies missing (aiohttp, openai, anthropic)
   - Syntax error in `services/real_research.py`
   - Import error

4. **If API keys not set**:
   - Verify in Railway dashboard → Variables
   - Redeploy after setting

5. **If API keys set but not working**:
   - Test API key manually:
     ```bash
     curl "https://www.googleapis.com/customsearch/v1?key=YOUR_KEY&cx=404c0e0620566459a&q=test"
     ```
   - Should return JSON with search results

---

## 📋 Recommended Workflow

### Phase 1: Diagnosis (Do This First) ⏱️ 5 minutes

1. ✅ Open Railway logs
2. ✅ Create test job
3. ✅ Watch logs for "🚀 BACKGROUND TASK STARTED"
4. ✅ Look for "📡 Sending request to: https://www.googleapis.com"
5. ✅ Check if you see "✅ Received X search results"

**Decision Point**:
- **See Google API calls** → Web crawling works! Go to Phase 2.
- **See "falling back to simulation"** → Fix API keys first.

---

### Phase 2: Fix Job Persistence ⏱️ 30 minutes

**Only do this if Phase 1 shows web crawling works!**

1. ✅ Add PostgreSQL database in Railway
2. ✅ Update `requirements-railway.txt`
3. ✅ Update `main_simple.py` with database code
4. ✅ Commit and push
5. ✅ Test job creation again
6. ✅ Verify job persists after container restart

---

### Phase 3: Testing & Validation ⏱️ 10 minutes

1. ✅ Create job with realistic prompt
2. ✅ Monitor logs for full workflow:
   - Google API calls
   - Company research
   - Contact finding
   - Outreach generation
3. ✅ Verify job completes with real leads
4. ✅ Test Google Sheets export (if configured)

---

## 🚨 Critical Questions to Answer

Before proceeding, we need to know:

### Question 1: Does Web Crawling Work?

**How to check**: Look at Railway logs after creating a job

**Answer will be either**:
- ✅ "Yes, I see Google API calls in logs"
- ❌ "No, I see 'falling back to simulation' in logs"

**Impact**:
- If YES → Just add persistent storage (easy fix)
- If NO → Need to fix API configuration first

---

### Question 2: How Often Do Containers Restart?

**How to check**: Visit `/debug/container-info` multiple times over 10 minutes

**Answer will be either**:
- ✅ "Uptime stays high, container is stable"
- ❌ "Uptime keeps resetting, container restarts every few minutes"

**Impact**:
- If stable → Jobs might complete before restart (less urgent)
- If unstable → Must add persistent storage immediately

---

## 🎯 Your Next Action (Right Now)

**Do this IMMEDIATELY**:

1. Open Railway logs in your browser
2. Create a test job with prompt: "Find AI startups"
3. Watch the logs for 30 seconds
4. Take a screenshot or copy the log output
5. Share with me what you see

**I'm looking for**:
- Do you see "📡 Sending request to: https://www.googleapis.com"?
- Do you see "✅ Received X search results from Google"?
- Or do you see "⚠️ falling back to simulation"?

This single test will tell us if web crawling works or not.

---

## 📞 What to Tell Me

After running the tests, tell me:

1. **Web Crawling Status**:
   - "I see Google API calls in logs" ✅
   - OR "I see 'falling back to simulation'" ❌

2. **Container Uptime**:
   - "Uptime is 3600+ seconds (stable)" ✅
   - OR "Uptime keeps resetting (< 120 seconds)" ❌

3. **Job Status Behavior**:
   - "Job progresses and completes" ✅
   - OR "Job shows 'not_found' after a few seconds" ❌

Based on your answers, I'll give you the exact next steps!

---

## 📚 Reference Documents

- `FRONTEND_ROUTING_FIX.md` - Frontend navigation (already fixed ✅)
- `JOB_TROUBLESHOOTING.md` - Detailed job persistence solutions
- `RAILWAY_DIAGNOSTIC.md` - Railway deployment issues
- `WHY_YOUR_CODE_SHOULD_WORK.md` - Code validation
- `CURRENT_STATUS.md` - Overall project status

---

**Bottom Line**: We need ONE piece of information from you:

🔍 **Does the log show real Google API calls or "falling back to simulation"?**

That's it! Once you tell me, I'll know exactly what to fix next. 🚀
