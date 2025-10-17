# Job Processing Troubleshooting Guide

## Issue: "Job not found" Status

**Symptom**: After creating a job, the status page shows "Job not found" with 0% progress.

**Root Cause**: Jobs are stored **in-memory** and lost when the container restarts.

---

## Why Jobs Disappear

### In-Memory Storage (Current Implementation)

```python
# backend/main_simple.py line 78
job_storage = {}  # Dictionary stored in RAM
```

**Behavior**:
- ✅ Jobs created and stored successfully
- ✅ Background processing starts
- ❌ If container restarts → all jobs lost
- ❌ If you refresh too slowly → job already gone

### Container Restart Triggers

Railway may restart your container for several reasons:
1. **Deployment** - When you push new code to GitHub
2. **Health check failure** - If endpoint doesn't respond
3. **Resource limits** - If memory/CPU exceeds limits
4. **Scaling** - If Railway scales your service
5. **Maintenance** - Platform updates

---

## Diagnostic Tools

### 1. Check Container Uptime

```bash
curl https://your-app.railway.app/debug/container-info
```

**Response Example**:
```json
{
  "container_start_time": "2025-10-17T15:45:23.123456",
  "current_time": "2025-10-17T15:47:30.654321",
  "uptime_seconds": 127.53,
  "jobs_in_memory": 2,
  "job_ids": ["abc-123", "def-456"],
  "real_research_available": true,
  "warning": "Jobs stored in memory will be lost on container restart"
}
```

**What to look for**:
- `uptime_seconds` < 60 → Container just restarted
- `jobs_in_memory` = 0 → No active jobs (may have been lost)
- `job_ids` → Lists currently stored jobs

### 2. Check Job Status with Restart Info

When you GET `/jobs/{job_id}` and it's not found, you'll now see:

```json
{
  "id": "c23db619-443d-41aa-8324-005e611da2d8",
  "status": "not_found",
  "message": "Job not found. The container may have restarted after job creation.",
  "container_start_time": "2025-10-17T15:45:23.123456",
  "note": "Jobs are stored in memory and lost on restart. Consider using persistent storage."
}
```

### 3. Monitor Railway Logs

Check Railway logs for these indicators:

**Container Start**:
```
🚀 Container started at: 2025-10-17T15:45:23.123456
⚠️ Using in-memory job storage - jobs will be lost on restart!
```

**Job Creation**:
```
Creating job abc-123 with prompt: Find SaaS companies in healthcare
✅ Stored job abc-123 in job_storage
🚀 BACKGROUND TASK STARTED for job abc-123
```

**Job Processing**:
```
✅ Job abc-123 verified in storage
🔍 SEARCH_COMPANIES CALLED
📡 Sending request to: https://www.googleapis.com/customsearch/v1
✅ Received 10 search results from Google
```

**Job Not Found** (after restart):
```
🔍 Getting job status for job_id: abc-123
❌ Job abc-123 not found in storage
❌ This may be due to container restart after job creation
```

---

## Solutions

### Option 1: Quick Test (Verify System Works)

Create a job and **immediately** start polling the status endpoint:

```bash
# 1. Create job
curl -X POST https://your-app.railway.app/jobs/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Find AI startups in San Francisco",
    "target_count": 5
  }'

# Response will give you job_id: "abc-123"

# 2. IMMEDIATELY start checking status (every 2 seconds)
while true; do
  curl https://your-app.railway.app/jobs/abc-123
  sleep 2
done
```

**Expected Behavior**:
- First few polls: `"status": "started"`, progress increases
- After ~30-60 seconds: `"status": "completed"` with leads
- If you see `"not_found"` → Container restarted

### Option 2: Add Persistent Storage (Recommended)

Replace in-memory storage with a database.

#### A. PostgreSQL (Recommended for Railway)

**1. Add Railway PostgreSQL**:
```bash
# In Railway dashboard:
# 1. Click "New" → "Database" → "Add PostgreSQL"
# 2. Railway automatically sets DATABASE_URL environment variable
```

**2. Install dependencies**:
```bash
# Add to requirements-railway.txt
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
```

**3. Update code**:
```python
# backend/main_simple.py
from sqlalchemy import create_engine, Column, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    Base = declarative_base()
    
    class Job(Base):
        __tablename__ = "jobs"
        id = Column(String, primary_key=True)
        status = Column(String)
        data = Column(JSON)
        created_at = Column(DateTime)
    
    Base.metadata.create_all(engine)
```

#### B. Redis (Fast, Simple)

**1. Add Railway Redis**:
```bash
# In Railway dashboard:
# 1. Click "New" → "Database" → "Add Redis"
# 2. Railway sets REDIS_URL environment variable
```

**2. Install dependency**:
```bash
# Add to requirements-railway.txt
redis==5.0.1
```

**3. Update code**:
```python
# backend/main_simple.py
import redis
import json
import os

redis_url = os.getenv("REDIS_URL")
if redis_url:
    redis_client = redis.from_url(redis_url)
    
    def store_job(job_id, job_data):
        redis_client.set(f"job:{job_id}", json.dumps(job_data), ex=86400)  # 24h TTL
    
    def get_job(job_id):
        data = redis_client.get(f"job:{job_id}")
        return json.loads(data) if data else None
```

### Option 3: Frontend Polling Strategy

Update frontend to handle restarts gracefully:

```typescript
// frontend/src/components/JobStatus.tsx
const pollJobStatus = async (jobId: string) => {
  const maxRetries = 3;
  let retries = 0;
  
  while (retries < maxRetries) {
    const response = await fetch(`/jobs/${jobId}`);
    const data = await response.json();
    
    if (data.status === 'not_found') {
      // Check if container restarted recently
      const containerInfo = await fetch('/debug/container-info').then(r => r.json());
      
      if (containerInfo.uptime_seconds < 120) {
        // Container restarted < 2 min ago - job was lost
        return {
          error: 'Job lost due to server restart. Please create a new job.',
          containerRestart: true
        };
      }
      
      // Maybe job hasn't been created yet, retry
      retries++;
      await new Promise(r => setTimeout(r, 2000));
    } else {
      return data;
    }
  }
  
  return { error: 'Job not found after multiple retries' };
};
```

---

## Testing Real Web Crawling

Even if jobs are being lost to restarts, you can verify the web crawling works by checking logs:

### What to Look For in Logs

**✅ Real Web Crawling is Working**:
```
🚀 BACKGROUND TASK STARTED for job abc-123
🔍 SEARCH_COMPANIES CALLED
Criteria: {'industry': 'SaaS', 'location': 'San Francisco'}
Google API key available: True
Google CSE ID available: True
📡 Sending request to: https://www.googleapis.com/customsearch/v1
Response status: 200
✅ Received 10 search results from Google
✅ search_companies() returned 10 companies
```

**❌ Falling Back to Simulation**:
```
⚠️ No companies found, falling back to simulation
⚠️ Job abc-123: REAL RESEARCH IS NOT WORKING - Using simulation mode
⚠️ This means the system is not doing actual web scraping
```

### Manual Test of Google API

Run this directly on the server:

```bash
cd /home/user/webapp && python backend/test_google_api.py
```

Expected output:
```
Testing Google Custom Search API...
✓ GOOGLE_API_KEY is set (44 characters)
✓ GOOGLE_CSE_ID is set (17 characters)

Sending test query to Google Custom Search API...
✓ API call successful!
✓ Received 10 results

Real research module test:
✓ Real research module loaded successfully
✓ Search companies function works

Conclusion: Everything is configured correctly!
```

---

## Common Issues & Solutions

### Issue: Jobs Complete Too Fast (< 5 seconds)

**Symptom**: Job goes from 0% to 100% instantly

**Cause**: Using simulation mode, not real web crawling

**Solution**: Check logs for "falling back to simulation" and verify:
1. `GOOGLE_API_KEY` is set correctly
2. `GOOGLE_CSE_ID` is set correctly
3. `REAL_RESEARCH_AVAILABLE = True` in logs
4. No errors when calling Google API

### Issue: Jobs Show Progress but Then "Not Found"

**Symptom**: Job progresses to 40%, then suddenly not found

**Cause**: Container restarted mid-processing

**Solution**:
1. Check `/debug/container-info` uptime
2. Review Railway logs for restart events
3. Implement persistent storage (Option 2 above)

### Issue: Background Task Never Starts

**Symptom**: Job created but stays at 0% forever

**Cause**: Background task crashed immediately

**Solution**: Check logs for:
```
❌ CRITICAL ERROR in background job processing
❌ Error: [error message]
❌ Full traceback: [stack trace]
```

Then fix the error shown in the traceback.

### Issue: "Real Research Not Available"

**Symptom**: Logs show `REAL_RESEARCH_AVAILABLE: False`

**Cause**: Import error in `services/real_research.py`

**Solution**:
1. Check for missing dependencies (aiohttp, openai, anthropic)
2. Check for syntax errors in real_research.py
3. Verify all imports work

---

## Current Status Check

Run these commands to verify system health:

```bash
# 1. Check container info
curl https://your-app.railway.app/debug/container-info

# 2. Check if real research is available
curl https://your-app.railway.app/api

# 3. List all jobs (should be empty after restart)
curl https://your-app.railway.app/jobs/

# 4. Create test job
curl -X POST https://your-app.railway.app/jobs/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test job", "target_count": 2}'

# 5. Immediately check status (replace abc-123 with job_id from step 4)
curl https://your-app.railway.app/jobs/abc-123
```

---

## Next Steps

Based on your symptoms, here's what to do:

1. **✅ Frontend routing fixed** - Navigation now works
2. **⏳ Check if jobs persist** - Create job, wait 60 seconds, check status
3. **⏳ Monitor logs** - Look for "BACKGROUND TASK STARTED" and Google API calls
4. **⏳ Decide on storage** - If jobs keep disappearing, add PostgreSQL or Redis

**Quick Win**: If Railway is restarting frequently, increase memory limits or use PostgreSQL for persistence.

---

**Created**: 2025-10-17
**Purpose**: Diagnose and fix "Job not found" issues
**Related**: FRONTEND_ROUTING_FIX.md, RAILWAY_DIAGNOSTIC.md
