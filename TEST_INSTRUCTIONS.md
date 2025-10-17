# Search API Test Instructions

## Purpose
Test if Google Custom Search API is working correctly and can find, scrape, and crawl real company pages.

## Test Files Created
- `test_search_simple.py` - Main test script
- `run_search_test.sh` - Helper script to run the test
- `TEST_INSTRUCTIONS.md` - This file

## How to Run the Test

### Option 1: Using Railway Environment (Recommended)
If your Railway deployment has the environment variables configured:

```bash
cd /home/user/webapp
railway run ./run_search_test.sh
```

### Option 2: Manual API Keys
If you have the API keys handy:

```bash
cd /home/user/webapp
./run_search_test.sh YOUR_GOOGLE_API_KEY YOUR_CSE_ID
```

### Option 3: Export Environment Variables
Set environment variables first, then run:

```bash
export GOOGLE_API_KEY="your_google_api_key_here"
export GOOGLE_CSE_ID="your_cse_id_here"
./run_search_test.sh
```

### Option 4: Direct Python Execution
If you have environment variables set:

```bash
python3 test_search_simple.py
```

## What the Test Does

The test will:

1. **✅ Verify API keys are set**
   - Checks GOOGLE_API_KEY
   - Checks GOOGLE_CSE_ID (or GOOGLE_SEARCH_ENGINE_ID)

2. **🔎 Test Google Custom Search**
   - Searches for: "real estate development companies"
   - Searches for: "commercial real estate developers"  
   - Searches for: "residential property developers"
   - Returns 3 results per query

3. **🕷️ Test Web Scraping**
   - Takes the first result URL
   - Fetches the actual webpage content
   - Shows first 500 characters
   - Verifies content can be retrieved

4. **📊 Show Summary**
   - Total results found
   - URLs discovered
   - Whether scraping worked

## Expected Output

If working correctly, you should see:

```
================================================================================
🔍 SIMPLE SEARCH API TESTER
================================================================================
✅ GOOGLE_API_KEY found: AIzaSyBxxxx...xxxxxxxxxx
✅ GOOGLE_CSE_ID found: 404c0e0620566459a

🔎 Testing Google Search API
   Query: 'real estate development companies'
   Requested results: 3

📡 Sending request to Google Custom Search API...
📥 Response status: 200

✅ SEARCH SUCCESSFUL!
   Total results available: 45,600,000
   Search time: 0.234 seconds

📄 Retrieved 3 results:

   [1] Company Name - Real Estate Development
       URL: https://example-company.com
       Snippet: Leading real estate development company...

   [2] Another Company
       URL: https://another-company.com
       Snippet: Commercial property developers...

   [3] Third Company
       URL: https://third-company.com
       Snippet: Residential development experts...

🕷️  Testing page scrape
   URL: https://example-company.com

📡 Fetching page content...
📥 Response status: 200
📄 Content-Type: text/html; charset=utf-8
✅ Page fetched successfully!
   Content length: 45,234 characters
   First 500 chars:
--------------------------------------------------------------------------------
<!DOCTYPE html><html><head><title>Company Name</title>...
--------------------------------------------------------------------------------

📊 TEST SUMMARY
================================================================================
✅ Total search results found: 9
✅ URLs discovered:
   [1] https://example-company.com
   [2] https://another-company.com
   [3] https://third-company.com
   ...

🎉 Test complete!
```

## Common Errors

### ❌ GOOGLE_API_KEY not set
**Solution**: Export the environment variable or pass as argument

### ❌ API KEY ERROR (403)
**Cause**: API key is invalid or doesn't have Custom Search enabled
**Solution**: 
1. Check your API key in Google Cloud Console
2. Ensure Custom Search API is enabled
3. Verify billing is set up (if needed)

### ❌ BAD REQUEST (400)
**Cause**: CSE ID is incorrect
**Solution**: Check your Custom Search Engine ID from https://cse.google.com

### ❌ Request timed out
**Cause**: Network issues or API slowness
**Solution**: Try again, the API might be temporarily slow

## Next Steps

Once this test passes:
1. ✅ We know Google Search API is working
2. ✅ We know web scraping is working
3. 🔧 We can integrate it into the full lead generation system
4. 🔧 Add contact finding (Apollo.io, Hunter.io)
5. 🔧 Add AI analysis for company research

## Troubleshooting

If the test fails, please share:
1. The full error message
2. Your API key (first 10 and last 10 characters only)
3. Your CSE ID
4. Any error logs

## Get Your API Keys

### Google Custom Search API Key
1. Go to: https://console.cloud.google.com/apis/credentials
2. Create a new API key (or use existing)
3. Enable "Custom Search API"
4. Copy the API key

### Google Custom Search Engine ID
1. Go to: https://cse.google.com/cse/all
2. Create a new search engine (or use existing)
3. Under "Search engine ID", copy the ID (format: `xxxxxxxxxxxxxxx`)
4. Make sure "Search the entire web" is enabled

---

**Ready to test?** Just run:
```bash
railway run ./run_search_test.sh
```

Or provide your keys manually:
```bash
./run_search_test.sh YOUR_API_KEY YOUR_CSE_ID
```
