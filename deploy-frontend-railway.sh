#!/bin/bash

echo "🚀 AI Lead Generation Platform - Frontend Railway Deployment"
echo "============================================================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null
then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "   curl -fsSL https://railway.app/install.sh | bash"
    exit 1
fi

echo "✅ Railway CLI installed"
echo ""

# Navigate to frontend directory
cd frontend

# Check if logged in to Railway
if ! railway whoami &> /dev/null
then
    echo "🔐 Please log in to Railway:"
    echo "   Run: railway login"
    echo "   This will open your browser to authenticate"
    railway login
fi

echo "✅ Logged in to Railway as: $(railway whoami)"
echo ""

# Create a new project for frontend if not already in one
if ! railway status &> /dev/null
then
    echo "🏗️  Creating Railway project for frontend..."
    railway init --name ai-lead-scrape-frontend
    echo "✅ Railway project 'ai-lead-scrape-frontend' created"
else
    echo "✅ Already in a Railway project."
fi
echo ""

echo "🔧 Setting up environment variables..."
echo "   Adding frontend configuration to Railway..."

# Set environment variables for frontend
railway variables:set NODE_ENV=production
railway variables:set VITE_API_URL=https://ai-lead-scrape-production.up.railway.app
railway variables:set VITE_APP_NAME="AI Lead Generation Platform"
railway variables:set VITE_APP_VERSION="2.0.0"

echo "✅ Environment variables set"
echo ""

# Deploy to Railway
echo "🚀 Deploying frontend to Railway..."
railway up
echo ""

echo "🎉 Frontend deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Your frontend will be available at: https://ai-lead-scrape-frontend-production.up.railway.app"
echo "2. Check the logs: railway logs"
echo "3. Monitor your app: railway status"
echo ""
echo "🔗 Useful commands:"
echo "   railway logs          - View application logs"
echo "   railway status        - Check deployment status"
echo "   railway variables     - Manage environment variables"
echo "   railway connect       - Connect to database"
echo ""
echo "🎯 Your AI Lead Generation Platform frontend is now live!"
echo "🌐 Frontend: https://ai-lead-scrape-frontend-production.up.railway.app"
echo "🔧 Backend: https://ai-lead-scrape-production.up.railway.app"
