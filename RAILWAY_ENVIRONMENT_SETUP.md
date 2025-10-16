# 🔧 Railway Environment Variables Setup

Your deployment is in progress! Now we need to set up the environment variables.

## 📋 Environment Variables to Add

Go to your Railway project dashboard and add these environment variables:

### **Google Custom Search API**
```
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

### **OpenAI API**
```
OPENAI_API_KEY=your_openai_api_key_here
```

### **Claude API**
```
CLAUDE_API_KEY=your_claude_api_key_here
```

### **Application Settings**
```
ENVIRONMENT=production
LOG_LEVEL=INFO
```

## 🎯 How to Add Variables in Railway Dashboard

1. **Go to your project**: `ai-lead-scrape`
2. **Click on**: "Variables" tab
3. **Add each variable** one by one:
   - Click "New Variable"
   - Enter the name (e.g., `GOOGLE_API_KEY`)
   - Enter the value (e.g., `AIzaSyB9mZpl8VFdbEOH3ujHqxOLICkYFgcPu4E`)
   - Click "Add"

## 🚀 After Adding Variables

Once you've added all the environment variables:

1. **Redeploy** your application (Railway will automatically redeploy)
2. **Check the logs** to see if everything is working
3. **Test your API endpoints**

## 📊 What to Expect

Your AI Lead Generation Platform will be available at:
`https://ai-lead-scrape-production.up.railway.app`

## 🔍 Testing Your Deployment

Once deployed, you can test:
- **Health Check**: `GET /health`
- **Create Job**: `POST /jobs/`
- **Company Discovery**: Real Google search
- **AI Research**: Real OpenAI + Claude analysis

## 🎉 Ready to Generate Leads!

Your platform will be able to:
- ✅ Discover companies using Google Search
- ✅ Enrich company data with website scraping  
- ✅ Research companies using AI
- ✅ Generate personalized outreach content
- ✅ Manage leads and contacts

**Add those environment variables and your platform will be live!** 🚀
