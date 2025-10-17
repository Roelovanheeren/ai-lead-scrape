# ✅ Search API Test Ready!

## 🎯 What We Created

I've created a **simplified search test** that will verify:
1. ✅ Google Custom Search API is working
2. ✅ Web scraping is working  
3. ✅ Pages can be crawled and content retrieved

## 📁 Test Files Created

```
/home/user/webapp/
├── test_search_simple.py        # Main test script (Python)
├── run_search_test.sh           # Easy test runner (Bash)
├── check_api_keys.sh            # Check which API keys are available
├── setup_test_env.sh            # Interactive key setup
└── TEST_INSTRUCTIONS.md         # Detailed instructions
```

## 🚀 How to Run

### Quick Start (3 options):

#### **Option 1: With Railway** (if logged in)
```bash
cd /home/user/webapp
railway run ./run_search_test.sh
```

#### **Option 2: With API Keys Directly**
```bash
cd /home/user/webapp
./run_search_test.sh YOUR_GOOGLE_API_KEY YOUR_CSE_ID
```

#### **Option 3: Export then Run**
```bash
export GOOGLE_API_KEY="your_api_key"
export GOOGLE_CSE_ID="your_cse_id"
./run_search_test.sh
```

## 🔑 API Keys Needed

You need these two keys:

### 1. GOOGLE_API_KEY
- Get from: https://console.cloud.google.com/apis/credentials
- Enable: Custom Search API
- Copy the API key

### 2. GOOGLE_CSE_ID  
- Get from: https://cse.google.com/cse/all
- Create or use existing search engine
- Copy the Search Engine ID (looks like: `404c0e0620566459a`)
- ⚠️ Make sure "Search the entire web" is enabled

## 📊 What the Test Does

The test will:

1. **Search Google for real companies**
   - Query 1: "real estate development companies"
   - Query 2: "commercial real estate developers"
   - Query 3: "residential property developers"
   - Gets 3 results per query = 9 total

2. **Display search results**
   - Company names
   - URLs
   - Descriptions/snippets
   - Total results available

3. **Scrape first company website**
   - Fetches the actual webpage
   - Shows content length
   - Displays first 500 characters
   - Verifies scraping works

4. **Show summary**
   - How many results found
   - Which URLs discovered
   - Whether scraping succeeded

## ✅ Expected Success Output

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

   [1] Acme Real Estate Development
       URL: https://acme-realestate.com
       Snippet: Leading commercial and residential developers...

   [2] Global Property Developers
       URL: https://globalpropertydev.com
       Snippet: International real estate investment...

   [3] Urban Development Corp
       URL: https://urbandevcorp.com
       Snippet: Transforming cities through sustainable...

🕷️  Testing page scrape
   URL: https://acme-realestate.com

📡 Fetching page content...
📥 Response status: 200
📄 Content-Type: text/html; charset=utf-8
✅ Page fetched successfully!
   Content length: 45,234 characters
   First 500 chars:
--------------------------------------------------------------------------------
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>Acme Real Estate Development</title>...
--------------------------------------------------------------------------------

📊 TEST SUMMARY
================================================================================
✅ Total search results found: 9
✅ URLs discovered:
   [1] https://acme-realestate.com
   [2] https://globalpropertydev.com
   [3] https://urbandevcorp.com
   [4] https://premier-properties.com
   [5] https://skyline-developers.com

🎉 Test complete!
```

## ❌ Common Errors & Solutions

### Error: "GOOGLE_API_KEY not set!"
**Solution**: Export the environment variable or provide as argument
```bash
export GOOGLE_API_KEY="your_key"
export GOOGLE_CSE_ID="your_cse_id"
```

### Error: "API KEY ERROR (403)"
**Cause**: API key invalid or Custom Search not enabled
**Solution**: 
1. Check API key in Google Cloud Console
2. Enable "Custom Search API"
3. Ensure billing is set up (free tier available)

### Error: "BAD REQUEST (400)"
**Cause**: CSE ID is incorrect
**Solution**: Double-check your CSE ID from https://cse.google.com

### Error: "Request timed out"
**Cause**: Network or API slowness
**Solution**: Try again, usually temporary

## 🔍 Check Current Status

To see which API keys are available:
```bash
./check_api_keys.sh
```

## 📚 Full Documentation

See `TEST_INSTRUCTIONS.md` for complete details.

## 🎯 Next Steps After Test Passes

Once this test works, we'll know:
1. ✅ Google Search API is working
2. ✅ Web scraping is working
3. ✅ We can find real company websites

Then we can:
1. 🔧 Integrate into main lead generation system
2. 🔧 Add contact finding (Apollo.io, Hunter.io)
3. 🔧 Add AI analysis for company research
4. 🔧 Add real email/LinkedIn extraction
5. 🔧 Replace mock data with real contacts

## 💡 Current Status

According to your deployment docs (`CURRENT_STATUS.md`):
- ✅ Google API key is configured in Railway
- ✅ CSE ID is configured (404c0e0620566459a)
- ✅ API has been verified working (7.84B results)

So the test **should work** if run with Railway environment!

## 🚀 Ready to Test!

**I recommend running this to test:**

```bash
cd /home/user/webapp

# First, check what keys are available
./check_api_keys.sh

# Then run the test
./run_search_test.sh YOUR_API_KEY YOUR_CSE_ID
```

Or if you want to login to Railway first:
```bash
railway login
railway run ./run_search_test.sh
```

---

## 🤔 Questions?

- **Q: Is this safe to run?**  
  A: Yes! It only makes a few Google searches and scrapes one webpage. No data is modified.

- **Q: Will it cost money?**  
  A: Google Custom Search has a free tier (100 queries/day). This test uses 3 queries.

- **Q: What if it fails?**  
  A: Share the error output and we'll troubleshoot!

- **Q: How long does it take?**  
  A: About 5-10 seconds total.

---

**Ready when you are!** Just provide your API keys and run the test. 🚀
