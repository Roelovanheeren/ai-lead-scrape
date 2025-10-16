#!/bin/bash

# Railway Deployment Script for AI Lead Generation Platform
# This script helps you deploy to Railway with proper configuration

set -e

echo "🚀 Deploying AI Lead Generation Platform to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please log in to Railway:"
    railway login
fi

# Create new project or link to existing
echo "📁 Setting up Railway project..."
if [ -z "$RAILWAY_PROJECT_ID" ]; then
    echo "Creating new Railway project..."
    railway project create
else
    echo "Linking to existing project: $RAILWAY_PROJECT_ID"
    railway link $RAILWAY_PROJECT_ID
fi

# Add PostgreSQL database
echo "🗄️ Adding PostgreSQL database..."
railway add postgresql

# Set environment variables
echo "🔧 Setting up environment variables..."

# Required API keys
echo "Please provide your API keys:"

read -p "Apollo.io API Key: " APOLLO_KEY
read -p "OpenAI API Key: " OPENAI_KEY
read -p "Claude API Key: " CLAUDE_KEY
read -p "Google API Key: " GOOGLE_KEY

# Set the environment variables
railway variables set APOLLO_API_KEY="$APOLLO_KEY"
railway variables set OPENAI_API_KEY="$OPENAI_KEY"
railway variables set CLAUDE_API_KEY="$CLAUDE_KEY"
railway variables set GOOGLE_API_KEY="$GOOGLE_KEY"

# Optional integrations
read -p "Slack Bot Token (optional): " SLACK_TOKEN
if [ ! -z "$SLACK_TOKEN" ]; then
    railway variables set SLACK_BOT_TOKEN="$SLACK_TOKEN"
fi

read -p "SendGrid API Key (optional): " SENDGRID_KEY
if [ ! -z "$SENDGRID_KEY" ]; then
    railway variables set SENDGRID_API_KEY="$SENDGRID_KEY"
fi

# Application settings
railway variables set ENVIRONMENT=production
railway variables set LOG_LEVEL=INFO

echo "🚀 Deploying application..."
railway up

echo "✅ Deployment completed!"
echo "🌐 Your application is now live at:"
railway domain

echo ""
echo "📊 Next steps:"
echo "1. Check the logs: railway logs"
echo "2. Monitor your app: railway status"
echo "3. View metrics in Railway dashboard"
echo "4. Test your API endpoints"

echo ""
echo "🔗 Useful commands:"
echo "- View logs: railway logs"
echo "- Check status: railway status"
echo "- Open dashboard: railway open"
echo "- Set variables: railway variables set KEY=value"
