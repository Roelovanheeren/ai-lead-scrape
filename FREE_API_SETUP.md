# 🔑 Free API Setup Guide

Get your AI Lead Generation Platform working with real data using free APIs.

## 1. Google Custom Search API (Free - 100 queries/day)

### Step 1: Create Google Cloud Project
1. Go to: https://console.cloud.google.com
2. Click "Create Project"
3. Name: "AI Lead Generation"
4. Click "Create"

### Step 2: Enable Custom Search API
1. Go to "APIs & Services" → "Library"
2. Search for "Custom Search API"
3. Click "Enable"

### Step 3: Create API Key
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "API Key"
3. Copy your API key
4. (Optional) Restrict the key to Custom Search API

### Step 4: Create Custom Search Engine
1. Go to: https://cse.google.com/cse/
2. Click "Add" to create new search engine
3. Sites to search: `*` (search entire web)
4. Name: "AI Lead Generation Search"
5. Click "Create"
6. Go to "Setup" → "Basics"
7. Copy your "Search engine ID"

### Step 5: Test Your Setup
```bash
# Set your environment variables
export GOOGLE_API_KEY=your_api_key_here
export GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here

# Test the integration
python3 test_all_apis.py
```

## 2. OpenAI API (Free - $5 credit)

### Step 1: Create OpenAI Account
1. Go to: https://platform.openai.com
2. Sign up with email
3. Verify your email

### Step 2: Get API Key
1. Go to: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Name: "AI Lead Generation"
4. Copy your API key (save it securely!)

### Step 3: Add Payment Method (Required)
1. Go to: https://platform.openai.com/settings/billing
2. Add a payment method
3. You get $5 free credit to start

### Step 4: Test Your Setup
```bash
# Set your environment variable
export OPENAI_API_KEY=your_openai_key_here

# Test the integration
python3 test_all_apis.py
```

## 3. Claude API (Free - $5 credit)

### Step 1: Create Anthropic Account
1. Go to: https://console.anthropic.com
2. Sign up with email
3. Verify your email

### Step 2: Get API Key
1. Go to: https://console.anthropic.com/keys
2. Click "Create Key"
3. Name: "AI Lead Generation"
4. Copy your API key

### Step 3: Add Payment Method
1. Go to billing settings
2. Add payment method
3. You get $5 free credit

### Step 4: Test Your Setup
```bash
# Set your environment variable
export CLAUDE_API_KEY=your_claude_key_here

# Test the integration
python3 test_all_apis.py
```

## 4. Optional Free APIs

### Clearbit (Free - 50 API calls/month)
1. Go to: https://clearbit.com
2. Sign up for free account
3. Get API key from dashboard
4. Set: `export CLEARBIT_API_KEY=your_key_here`

### Hunter.io (Free - 25 searches/month)
1. Go to: https://hunter.io
2. Sign up for free account
3. Get API key from dashboard
4. Set: `export HUNTER_API_KEY=your_key_here`

## 🧪 Testing Your APIs

Once you have your API keys, test them:

```bash
# Set all your environment variables
export GOOGLE_API_KEY=your_google_key
export GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
export OPENAI_API_KEY=your_openai_key
export CLAUDE_API_KEY=your_claude_key

# Test all APIs
python3 test_all_apis.py

# Test the full platform
python3 free_lead_generator.py
```

## 💰 Cost Breakdown

| Service | Free Tier | Cost After Free |
|---------|-----------|-----------------|
| Google Custom Search | 100 queries/day | $5 per 1000 queries |
| OpenAI | $5 credit | ~$0.002 per 1K tokens |
| Claude | $5 credit | ~$0.00025 per 1K tokens |
| Clearbit | 50 calls/month | $99/month |
| Hunter.io | 25 searches/month | $49/month |

**Total monthly cost for testing: ~$0-10**

## 🚀 Next Steps

1. **Get Google Custom Search** (5 minutes)
2. **Get OpenAI API** (5 minutes) 
3. **Get Claude API** (5 minutes)
4. **Test all integrations** (2 minutes)
5. **Deploy to Railway** (10 minutes)

**Total setup time: ~25 minutes**

---

**Ready to get started? Let's set up Google Custom Search first!** 🔍
