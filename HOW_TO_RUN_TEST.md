# 🚀 Quick Start: Test Your Search API

## ⚡ Fastest Way to Test

Run this command with your API keys:

```bash
cd /home/user/webapp
./run_search_test.sh YOUR_GOOGLE_API_KEY YOUR_CSE_ID
```

**Replace:**
- `YOUR_GOOGLE_API_KEY` - Your Google API key
- `YOUR_CSE_ID` - Your Custom Search Engine ID

## 📋 Example

```bash
./run_search_test.sh AIzaSyBdKZ9vFQ5x_example_key 404c0e0620566459a
```

## ✅ What You'll See if Working

The test will:
1. Search for real estate development companies
2. Show 9 company results with URLs
3. Scrape one company website
4. Display the content

**Success looks like:**
```
✅ SEARCH SUCCESSFUL!
   Total results available: 45,600,000
   Search time: 0.234 seconds

📄 Retrieved 3 results:
   [1] Acme Real Estate Development
       URL: https://acme-realestate.com
```

## ❌ What You'll See if Broken

**If API key is wrong:**
```
❌ API KEY ERROR (403): Invalid API key
   Check if your API key is valid
```

**If CSE ID is wrong:**
```
❌ BAD REQUEST (400): Invalid CSE ID
   Check if your CSE ID is correct
```

## 🔑 Where to Get Your Keys

### Google API Key
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click "Create Credentials" > "API Key"
3. Copy the key (starts with `AIza...`)

### Custom Search Engine ID
1. Go to: https://cse.google.com/cse/all
2. Click your search engine (or create one)
3. Copy the "Search engine ID" (like `404c0e0620566459a`)

## 📖 More Details

See `SEARCH_TEST_READY.md` for complete instructions.

---

**Ready?** Just run:
```bash
./run_search_test.sh YOUR_API_KEY YOUR_CSE_ID
```
