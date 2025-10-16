# 🚀 Quick Start: Deploy AI Lead Generation Platform on Railway

Deploy your AI-powered lead generation platform to Railway in under 10 minutes!

## ⚡ Super Quick Deploy (5 minutes)

### 1. One-Click Deploy
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-id)

### 2. Set Environment Variables
In your Railway dashboard, add these required variables:

```bash
# Required API Keys
APOLLO_API_KEY=your_apollo_key
OPENAI_API_KEY=your_openai_key
CLAUDE_API_KEY=your_claude_key
GOOGLE_API_KEY=your_google_key

# Optional (for full functionality)
SLACK_BOT_TOKEN=your_slack_token
SENDGRID_API_KEY=your_sendgrid_key
AIMFOX_API_KEY=your_aimfox_key
GHL_API_KEY=your_ghl_key
```

### 3. Deploy!
Railway will automatically:
- ✅ Build your application
- ✅ Set up PostgreSQL database
- ✅ Deploy with SSL
- ✅ Provide public URL

## 🛠️ Manual Deploy (10 minutes)

### Prerequisites
- GitHub account
- Railway account (free)
- API keys for external services

### Step 1: Connect to Railway
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your `ai-lead-scrape` repository

### Step 2: Add Database
1. In your project dashboard
2. Click "New" → "Database" → "PostgreSQL"
3. Railway automatically sets `DATABASE_URL`

### Step 3: Configure Environment Variables
Add these in your Railway project settings:

#### Required Variables
```bash
APOLLO_API_KEY=your_apollo_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

#### Optional Variables (for full functionality)
```bash
SLACK_BOT_TOKEN=your_slack_bot_token
SENDGRID_API_KEY=your_sendgrid_api_key
AIMFOX_API_KEY=your_aimfox_api_key
GHL_API_KEY=your_ghl_api_key
```

### Step 4: Deploy
Railway will automatically:
- Build your Docker container
- Deploy to their infrastructure
- Set up SSL certificates
- Provide a public URL

## 🧪 Test Your Deployment

### 1. Health Check
Visit: `https://your-app.railway.app/health`

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 2. API Documentation
Visit: `https://your-app.railway.app/docs`

### 3. Test API Endpoint
```bash
curl -X POST "https://your-app.railway.app/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Find SaaS companies in San Francisco with 50-200 employees",
    "target_count": 5,
    "quality_threshold": 0.8
  }'
```

## 📊 Monitor Your App

### Railway Dashboard
- **Metrics**: CPU, Memory, Network
- **Logs**: Real-time application logs
- **Database**: PostgreSQL metrics
- **Deployments**: Build and deployment history

### Health Monitoring
- **Health Checks**: Automatic health monitoring
- **Uptime**: 99.9% uptime guarantee
- **Scaling**: Automatic scaling based on traffic

## 🔧 Configuration Options

### Environment Variables
```bash
# Application Settings
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false

# Database (automatically set by Railway)
DATABASE_URL=postgresql://...

# API Keys (set these)
APOLLO_API_KEY=...
OPENAI_API_KEY=...
CLAUDE_API_KEY=...
GOOGLE_API_KEY=...
```

### Custom Domains
1. Go to your Railway project
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Railway handles SSL automatically

## 💰 Cost Breakdown

### Railway Pricing
- **Free Tier**: $5 credit monthly (perfect for development)
- **Pro Plan**: $20/month (unlimited usage)
- **Database**: Included in project cost

### Estimated Monthly Costs
- **Development**: $0 (free tier)
- **Small Production**: $20-30/month
- **Medium Production**: $50-100/month
- **Large Production**: $100+/month

## 🚨 Troubleshooting

### Common Issues

#### 1. Build Failures
```bash
# Check build logs in Railway dashboard
# Common fixes:
# - Update requirements.txt
# - Check Dockerfile syntax
# - Verify file paths
```

#### 2. Database Connection Issues
```bash
# Test database connection
railway run python -c "
import os, asyncpg, asyncio
async def test():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    print('✅ Database connected')
    await conn.close()
asyncio.run(test())
"
```

#### 3. Missing Environment Variables
```bash
# Check all variables
railway variables

# Set missing variables
railway variables set VARIABLE_NAME=value
```

### Debug Mode
```bash
# Enable debug logging
railway variables set LOG_LEVEL=DEBUG

# View detailed logs
railway logs --follow
```

## 🔄 Updates and Maintenance

### Automatic Updates
Railway automatically:
- **Detects code changes** from GitHub
- **Builds new images** on push to main
- **Deploys updates** with zero downtime
- **Rolls back** on deployment failures

### Manual Updates
```bash
# Deploy specific branch
railway up --environment production

# Rollback to previous version
railway rollback
```

## 📈 Scaling Your App

### Automatic Scaling
Railway handles:
- **CPU scaling** based on usage
- **Memory allocation** optimization
- **Load balancing** across instances
- **High availability** with redundancy

### Manual Scaling
```bash
# Scale your service
railway scale --replicas 3

# Check current status
railway status
```

## 🎯 Next Steps

### 1. Test Your API
```bash
# Create a test job
curl -X POST "https://your-app.railway.app/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Find tech startups in New York",
    "target_count": 10
  }'
```

### 2. Monitor Performance
- Check Railway dashboard for metrics
- Monitor logs for any errors
- Test all API endpoints

### 3. Configure Integrations
- Set up Apollo.io for company data
- Configure OpenAI for content generation
- Connect Slack for notifications

### 4. Set Up Monitoring
- Enable Railway's built-in monitoring
- Set up alerts for errors
- Monitor API usage and costs

## 🆘 Need Help?

### Railway Support
- **Documentation**: [docs.railway.app](https://docs.railway.app)
- **Discord**: [discord.gg/railway](https://discord.gg/railway)
- **Support**: [railway.app/support](https://railway.app/support)

### Platform Support
- **GitHub Issues**: Create an issue in your repository
- **Email**: support@example.com
- **Slack**: #ai-lead-gen-support

---

**🎉 Congratulations! Your AI Lead Generation Platform is now live on Railway!**

**Next**: Test your API endpoints and start generating leads! 🚀
