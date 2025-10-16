# 🧪 Local Development Guide

Test your AI Lead Generation Platform locally before deploying to Railway.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements-dev.txt
```

### 2. Run Basic Tests
```bash
python local_dev.py test
```

### 3. Start Local Server
```bash
python local_dev.py server
```

### 4. Test API Endpoints
- Health Check: http://localhost:8000/health
- API Docs: http://localhost:8000/docs
- Create Job: http://localhost:8000/jobs

## 🔧 Local Development Setup

### Option A: SQLite (Simplest)
```bash
# No database setup needed - uses SQLite
python local_dev.py test
```

### Option B: PostgreSQL (Production-like)
```bash
# Install PostgreSQL locally
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql

# Create database
createdb lead_generation

# Set environment variable
export DATABASE_URL=postgresql://postgres:password@localhost:5432/lead_generation

# Run tests
python local_dev.py test
```

### Option C: Docker (Full Stack)
```bash
# Start PostgreSQL and Redis with Docker
docker-compose up -d postgres redis

# Run tests
python local_dev.py test
```

## 🧪 Testing Checklist

### Basic Functionality Tests
- [ ] Database connection
- [ ] API endpoints responding
- [ ] Module imports working
- [ ] Health check passing

### API Endpoint Tests
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test API documentation
open http://localhost:8000/docs

# Test job creation (mock data)
curl -X POST "http://localhost:8000/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Find SaaS companies in San Francisco",
    "target_count": 5,
    "quality_threshold": 0.8
  }'
```

### Expected Results
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Make sure you're in the backend directory
cd backend
python local_dev.py test
```

#### 2. Database Connection Issues
```bash
# For SQLite (default)
# No setup needed

# For PostgreSQL
# Make sure PostgreSQL is running
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Linux
```

#### 3. Port Already in Use
```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn main:app --port 8001
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python local_dev.py test
```

## 📊 What We're Testing

### 1. Core Platform
- ✅ Database schema and connections
- ✅ API endpoint structure
- ✅ Basic job creation workflow
- ✅ Health monitoring

### 2. Service Architecture
- ✅ Job orchestrator service
- ✅ Company discovery service
- ✅ Contact identification service
- ✅ Research engine service
- ✅ Outreach generator service

### 3. Data Models
- ✅ Pydantic schemas validation
- ✅ Database models and relationships
- ✅ API request/response formats

## 🎯 Next Steps After Local Testing

Once local tests pass:

1. **Get API Keys** - Set up external service accounts
2. **Configure Environment** - Add API keys to .env file
3. **Test with Real Data** - Run end-to-end tests
4. **Deploy to Railway** - Push to production

## 📝 Development Notes

### File Structure
```
backend/
├── local_dev.py          # Local testing script
├── requirements-dev.txt  # Development dependencies
├── main.py              # FastAPI application
├── models/              # Data models and schemas
├── services/            # Business logic services
├── database/            # Database configuration
└── integrations/        # External API clients
```

### Key Files
- `local_dev.py` - Local testing and development server
- `main.py` - FastAPI application entry point
- `database/schema.sql` - Database schema
- `models/schemas.py` - Pydantic data models

---

**Ready to test locally? Run: `python local_dev.py test`** 🚀
