# 🔒 Secure API Key Setup Guide

## ⚠️ IMPORTANT: Never commit API keys to your repository!

## 🚀 Setting Up Your New API Keys in Railway

### **Step 1: Go to Your Railway Project**
1. Go to: https://railway.app/dashboard
2. Click on your "ai-lead-scrape" project
3. Go to "Variables" tab

### **Step 2: Add Your New API Keys**

**Google Custom Search:**
```
GOOGLE_API_KEY=your_new_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=404c0e0620566459a
```

**OpenAI API:**
```
OPENAI_API_KEY=your_new_openai_api_key_here
```

**Claude API:**
```
CLAUDE_API_KEY=your_new_claude_api_key_here
```

**Application Settings:**
```
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### **Step 3: Update Each Variable**
1. Click "New Variable" for each key above
2. Enter the name (e.g., `GOOGLE_API_KEY`)
3. Enter the value (your new API key)
4. Click "Add"

### **Step 4: Verify Setup**
After adding all variables, Railway will automatically redeploy your application.

## 🔒 Security Best Practices

### **✅ DO:**
- Store API keys in Railway environment variables
- Use `.env` files locally (never commit them)
- Rotate API keys regularly
- Monitor API usage and billing

### **❌ DON'T:**
- Commit API keys to git repositories
- Share API keys in chat/email
- Hardcode keys in source code
- Use the same key across multiple projects

## 🧪 Testing Your Setup

Once Railway redeploys, test your platform:

```bash
# Test health endpoint
curl https://ai-lead-scrape-production.up.railway.app/health

# Test job creation
curl -X POST https://ai-lead-scrape-production.up.railway.app/jobs/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Find AI startups", "target_count": 5, "quality_threshold": 0.8}'
```

## 🎯 Your AI Lead Generation Platform is Now Secure!

With the new API keys properly configured in Railway environment variables, your platform will be:
- ✅ **Secure** - No exposed API keys
- ✅ **Functional** - All APIs working
- ✅ **Production-ready** - Properly configured

**Add those environment variables in Railway and your platform will be live and secure!** 🚀
