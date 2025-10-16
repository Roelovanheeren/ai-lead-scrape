#!/bin/bash

echo "🚀 AI Lead Generation Platform - Railway Deployment"
echo "=================================================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

echo "✅ Railway CLI version: $(railway --version)"
echo ""

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please log in to Railway:"
    echo "   Run: railway login"
    echo "   This will open your browser to authenticate"
    echo ""
    read -p "Press Enter after you've logged in..."
fi

echo "✅ Logged in to Railway as: $(railway whoami)"
echo ""

# Create new Railway project
echo "🏗️  Creating Railway project..."
railway init

echo ""
echo "🔧 Setting up environment variables..."
echo "   Adding your API keys to Railway..."

# Set environment variables
railway variables set GOOGLE_API_KEY=your_google_api_key_here
railway variables set GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
railway variables set OPENAI_API_KEY=your_openai_api_key_here
railway variables set CLAUDE_API_KEY=your_claude_api_key_here
railway variables set ENVIRONMENT=production
railway variables set LOG_LEVEL=INFO

echo "✅ Environment variables set"
echo ""

# Add PostgreSQL database
echo "🗄️  Adding PostgreSQL database..."
railway add postgresql

echo "✅ PostgreSQL database added"
echo ""

# Deploy the application
echo "🚀 Deploying to Railway..."
railway up

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Your app will be available at: https://your-app-name.railway.app"
echo "2. Check the logs: railway logs"
echo "3. Monitor your app: railway status"
echo ""
echo "🔗 Useful commands:"
echo "   railway logs          - View application logs"
echo "   railway status        - Check deployment status"
echo "   railway variables     - Manage environment variables"
echo "   railway connect       - Connect to database"
echo ""
echo "🎯 Your AI Lead Generation Platform is now live!"
