# Railway Deployment Guide - AI Lead Generation Platform

This guide will help you deploy the AI Lead Generation Platform on Railway, a modern cloud platform that makes deployment simple and cost-effective.

## 🚀 Quick Start

### Prerequisites
- Railway account (free tier available)
- GitHub repository with your code
- API keys for external services

### 1. Connect to Railway

1. **Sign up at [Railway.app](https://railway.app)**
2. **Connect your GitHub account**
3. **Import your repository**

### 2. Create New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `ai-lead-scrape` repository
4. Railway will automatically detect the configuration

### 3. Add Database

1. In your Railway project dashboard
2. Click "New" → "Database" → "PostgreSQL"
3. Railway will automatically provision a PostgreSQL database
4. The `DATABASE_URL` environment variable will be set automatically

### 4. Configure Environment Variables

Add these environment variables in your Railway project settings:

```bash
# API Keys (Required)
APOLLO_API_KEY=your_apollo_api_key
OPENAI_API_KEY=your_openai_api_key
CLAUDE_API_KEY=your_claude_api_key
GOOGLE_API_KEY=your_google_api_key

# Optional Integrations
SLACK_BOT_TOKEN=your_slack_token
SENDGRID_API_KEY=your_sendgrid_key
AIMFOX_API_KEY=your_aimfox_key
GHL_API_KEY=your_ghl_key

# Application Settings
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 5. Deploy

Railway will automatically:
- Build your Docker container
- Deploy to their infrastructure
- Set up SSL certificates
- Provide a public URL

## 🔧 Configuration

### Railway Configuration Files

The platform uses these Railway-specific files:

- `railway.json` - Railway deployment configuration
- `railway.toml` - Alternative configuration format
- `backend/Dockerfile.railway` - Railway-optimized Dockerfile
- `backend/requirements-railway.txt` - Lightweight dependencies

### Database Configuration

Railway automatically provides:
- `DATABASE_URL` - PostgreSQL connection string
- Automatic SSL/TLS encryption
- Connection pooling
- Backup and monitoring

### Environment Variables

Railway supports environment variables at multiple levels:
- **Project level**: Shared across all services
- **Service level**: Specific to your application
- **Environment level**: Different values for staging/production

## 📊 Monitoring and Logs

### View Logs
1. Go to your Railway project dashboard
2. Click on your service
3. Navigate to "Logs" tab
4. View real-time application logs

### Metrics
Railway provides built-in metrics:
- CPU usage
- Memory consumption
- Network traffic
- Response times

### Health Checks
The platform includes health check endpoints:
- `/health` - Basic health check
- `/metrics` - Application metrics (if enabled)

## 🔄 CI/CD Pipeline

Railway automatically:
- **Detects changes** in your GitHub repository
- **Builds new images** when you push to main branch
- **Deploys updates** with zero downtime
- **Rolls back** automatically on deployment failures

### Branch-based Deployments
- `main` branch → Production deployment
- `staging` branch → Staging deployment
- Feature branches → Preview deployments

## 💰 Cost Optimization

### Railway Pricing
- **Free tier**: $5 credit monthly
- **Pro plan**: $20/month for unlimited usage
- **Database**: Included in project cost

### Cost-Saving Tips
1. **Use Railway's free tier** for development
2. **Optimize Docker images** to reduce build time
3. **Use environment variables** instead of hardcoded values
4. **Monitor usage** in Railway dashboard

## 🛠️ Development Workflow

### Local Development
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Run locally with Railway environment
railway run python -m uvicorn main:app --reload
```

### Environment Management
```bash
# Set environment variables
railway variables set APOLLO_API_KEY=your_key

# View all variables
railway variables

# Deploy to specific environment
railway up --environment production
```

## 🔒 Security

### Automatic Security Features
- **SSL/TLS encryption** for all connections
- **Environment variable encryption**
- **Network isolation** between services
- **Automatic security updates**

### Best Practices
1. **Never commit API keys** to your repository
2. **Use Railway's environment variables** for secrets
3. **Enable 2FA** on your Railway account
4. **Regularly rotate API keys**

## 📈 Scaling

### Automatic Scaling
Railway automatically:
- **Scales based on traffic**
- **Manages resource allocation**
- **Handles load balancing**
- **Provides high availability**

### Manual Scaling
```bash
# Scale your service
railway scale --replicas 3

# View current scaling
railway status
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Build Failures
```bash
# Check build logs
railway logs --build

# Common fixes:
# - Update requirements.txt
# - Check Dockerfile syntax
# - Verify file paths
```

#### 2. Database Connection Issues
```bash
# Test database connection
railway run python -c "
import os
import asyncpg
import asyncio

async def test_db():
    try:
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        print('Database connected successfully')
        await conn.close()
    except Exception as e:
        print(f'Database connection failed: {e}')

asyncio.run(test_db())
"
```

#### 3. Environment Variable Issues
```bash
# Check environment variables
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

## 🚀 Production Deployment

### Pre-deployment Checklist
- [ ] All API keys configured
- [ ] Database schema initialized
- [ ] Environment variables set
- [ ] Health checks passing
- [ ] Monitoring configured

### Deployment Steps
1. **Test locally** with Railway environment
2. **Deploy to staging** first
3. **Run integration tests**
4. **Deploy to production**
5. **Monitor deployment**

### Post-deployment
1. **Verify health endpoints**
2. **Check application logs**
3. **Test API endpoints**
4. **Monitor metrics**

## 📚 Additional Resources

### Railway Documentation
- [Railway Docs](https://docs.railway.app)
- [Railway CLI](https://docs.railway.app/develop/cli)
- [Environment Variables](https://docs.railway.app/develop/variables)
- [Database](https://docs.railway.app/databases/postgresql)

### Platform-Specific Guides
- [FastAPI on Railway](https://docs.railway.app/guides/fastapi)
- [PostgreSQL on Railway](https://docs.railway.app/databases/postgresql)
- [Docker on Railway](https://docs.railway.app/guides/docker)

## 🆘 Support

### Getting Help
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- **Railway Support**: [railway.app/support](https://railway.app/support)
- **GitHub Issues**: Create an issue in your repository

### Community
- **Railway Community**: [community.railway.app](https://community.railway.app)
- **GitHub Discussions**: Use your repository's discussions tab

---

**Ready to deploy? Follow this guide and your AI Lead Generation Platform will be live on Railway in minutes! 🚀**
