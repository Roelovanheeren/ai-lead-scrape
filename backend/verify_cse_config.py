#!/usr/bin/env python3
"""
Verify Google Custom Search Engine Configuration
This script helps you check if your CSE is properly configured
"""

import os
import sys

print("="*80)
print("🔧 GOOGLE CUSTOM SEARCH ENGINE CONFIGURATION CHECKER")
print("="*80)

# Get environment variables
google_api_key = os.getenv("GOOGLE_API_KEY")
google_cse_id = os.getenv("GOOGLE_CSE_ID") or os.getenv("GOOGLE_SEARCH_ENGINE_ID")

print("\n📋 Current Configuration:")
print(f"  GOOGLE_API_KEY: {'✅ SET' if google_api_key else '❌ NOT SET'}")
print(f"  GOOGLE_CSE_ID: {'✅ SET' if google_cse_id else '❌ NOT SET'}")

if not google_api_key or not google_cse_id:
    print("\n❌ Missing credentials! Cannot proceed.")
    sys.exit(1)

print("\n" + "="*80)
print("🌐 CRITICAL: Verify Your CSE Configuration")
print("="*80)

print(f"""
Your Custom Search Engine ID: {google_cse_id}

⚠️  CRITICAL CONFIGURATION CHECK:

1. Visit: https://programmablesearchengine.google.com/controlpanel/all

2. Click on your search engine (ID: {google_cse_id})

3. Click "Setup" or "Edit search engine"

4. Check "Search the entire web" setting:

   ❌ WRONG (will return NO results):
      [ ] Search the entire web
      Sites to search:
        - example.com
        - another.com

   ✅ CORRECT (will search all websites):
      [✓] Search the entire web
      (Optionally emphasize certain sites...)

5. If you see "Sites to search" with specific domains listed,
   you MUST enable "Search the entire web"!

6. Save changes and wait 5 minutes for propagation

═══════════════════════════════════════════════════════════════════════════════

🔑 API KEY CHECK:

1. Visit: https://console.cloud.google.com/apis/credentials

2. Find your API key and verify:
   ✅ Custom Search API is ENABLED
   ✅ Billing is ENABLED (required for more than 100 queries/day)
   ✅ No IP/HTTP referrer restrictions (or add Railway's IPs)

═══════════════════════════════════════════════════════════════════════════════

📊 QUOTA CHECK:

Free Tier Limits:
  - 100 queries per day
  - 10,000 queries per day (with billing enabled)

If you've exceeded quota, you'll get HTTP 429 errors.

Visit: https://console.cloud.google.com/apis/api/customsearch.googleapis.com/quotas

═══════════════════════════════════════════════════════════════════════════════

🧪 MANUAL TEST:

Run this curl command to test directly:

curl "https://www.googleapis.com/customsearch/v1?key={google_api_key[:10]}...&cx={google_cse_id}&q=technology+companies&num=3"

Expected response:
{{
  "items": [
    {{
      "title": "Company Name",
      "link": "https://example.com",
      "snippet": "Description..."
    }}
  ]
}}

If you get "items" with results → CSE is working!
If you get "error" → Check the error message

═══════════════════════════════════════════════════════════════════════════════

🎯 NEXT STEPS:

1. Verify "Search the entire web" is enabled
2. Ensure billing is enabled (for production use)
3. Check quota hasn't been exceeded
4. Test with curl command above
5. Create a new job in your app and check Railway logs

═══════════════════════════════════════════════════════════════════════════════
""")

print("\n✅ Configuration check complete!")
print("If all settings are correct, your web scraping should work!\n")
