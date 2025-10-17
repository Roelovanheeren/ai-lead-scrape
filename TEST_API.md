# Test API Endpoints

## 1. Test /api endpoint (shows env var status)

```bash
curl https://ai-lead-scrape-production.up.railway.app/api
```

Expected response:
```json
{
  "message": "AI Lead Generation Platform API",
  "version": "2.0.0",
  "status": "running",
  "real_research_available": true,
  "google_api_key": "SET",
  "google_cse_id": "SET"
}
```

## 2. Test /health endpoint

```bash
curl https://ai-lead-scrape-production.up.railway.app/health
```

## 3. Test /health-check endpoint (Railway uses this)

```bash
curl https://ai-lead-scrape-production.up.railway.app/health-check
```

## 4. Test Google API directly

```bash
curl "https://www.googleapis.com/customsearch/v1?key=AIzaSyDjnfAynaW9F-nn8EiYYA2-QZtTP-p-UTk&cx=404c0e0620566459a&q=technology+companies&num=3"
```

## What to Look For

### If /api shows "NOT SET":
- Environment variables aren't being read by the app
- Need to check Railway variable configuration

### If /api shows "SET" but jobs still use simulation:
- Google API itself is failing
- Check the Google API direct test (#4)

### If /health-check fails:
- Railway can't reach the app
- Port binding issue
- App is crashing after startup
