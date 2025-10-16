# 🚀 Railway Deployment Guide

## Step 1: Login to Railway

```bash
railway login
```

This will open your browser to authenticate with Railway.

## Step 2: Create New Project

```bash
railway init
```

Choose a name for your project (e.g., "ai-lead-generation")

## Step 3: Set Environment Variables

```bash
# Google Custom Search
railway variables set GOOGLE_API_KEY=your_google_api_key_here
railway variables set GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here

# OpenAI API
railway variables set OPENAI_API_KEY=your_openai_api_key_here

# Claude API
railway variables set CLAUDE_API_KEY=your_claude_api_key_here

# App Settings
railway variables set ENVIRONMENT=production
railway variables set LOG_LEVEL=INFO
```

## Step 4: Add PostgreSQL Database

```bash
railway add postgresql
```

## Step 5: Deploy

```bash
railway up
```

## Step 6: Check Deployment

```bash
# View logs
railway logs

# Check status
railway status

# Get your app URL
railway domain
```

## 🎉 Your AI Lead Generation Platform is Live!

Your platform will be available at: `https://your-app-name.railway.app`

## 🔧 Useful Commands

```bash
railway logs          # View application logs
railway status        # Check deployment status
railway variables     # Manage environment variables
railway connect       # Connect to database
railway domain        # Get your app URL
```

## 📋 What's Deployed

✅ **FastAPI Backend** - Your main application
✅ **PostgreSQL Database** - Data storage
✅ **Google Custom Search** - Company discovery
✅ **OpenAI API** - AI research & outreach
✅ **Claude API** - Enhanced AI capabilities
✅ **Website Scraping** - Company enrichment

## 🚀 Ready to Generate Leads!

Your AI Lead Generation Platform is now live and ready to:
- Discover companies using Google Search
- Enrich company data with website scraping
- Research companies using AI
- Generate personalized outreach content
- Manage leads and contacts

**Start generating leads now!** 🎯
