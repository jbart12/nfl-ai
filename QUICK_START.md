# Quick Start Guide

Get the NFL AI Prediction System up and running in 15 minutes.

## Prerequisites Check

```bash
# Check Docker
docker --version
docker-compose --version

# Check Python
python --version  # Should be 3.11+
```

## Step-by-Step Setup

### 1. Configure Environment (2 minutes)

```bash
cd /Users/jace/dev/nfl-ai

# Environment variables are already set in .env
# Verify your API keys are present:
grep ANTHROPIC_API_KEY .env
grep OPENAI_API_KEY .env
```

✓ API keys are already configured!

### 2. Start Docker Services (3 minutes)

```bash
# Start all infrastructure
docker-compose up -d postgres qdrant redis

# Wait for services to be healthy
docker-compose ps

# Check logs if needed
docker-compose logs -f postgres
```

Expected services:
- ✓ nfl-ai-postgres (port 5433)
- ✓ nfl-ai-qdrant (port 6334)
- ✓ nfl-ai-redis (port 6380)

### 3. Run Database Migrations (2 minutes)

```bash
cd backend

# Run migrations
alembic upgrade head

# Verify migration
python -m scripts.db_utils status
```

Expected output:
```
✓ Database connection: OK
✓ Alembic migrations: Applied (version: 001)
```

### 4. Seed Initial Data (3 minutes)

```bash
# Seed all 32 NFL teams
python -m scripts.seed_teams

# Verify teams were created
python -m scripts.db_utils count
```

Expected output:
```
Teams........................... 32
```

### 5. Start the API (2 minutes)

Option A - Docker (recommended):
```bash
cd ..
docker-compose up -d api
docker-compose logs -f api
```

Option B - Local development:
```bash
cd backend
uvicorn app.main:app --reload --port 8002
```

### 6. Test the System (3 minutes)

```bash
# Test health endpoint
curl http://localhost:8002/health

# View API documentation
open http://localhost:8002/docs
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "development",
  "service": "NFL AI Prediction System"
}
```

## Next Steps

### Load Historical Data (Optional, 30-60 minutes)

The system works without historical data, but predictions will be better with it:

```bash
# Backfill 2024 season stats for active players
python -m scripts.backfill_player_stats --season 2024 --active-only

# This will take 30-60 minutes depending on number of players
# You can run this in the background
```

### Make Your First Prediction

```bash
curl -X POST http://localhost:8002/api/v1/predictions/predict \
  -H "Content-Type: application/json" \
  -d '{
    "player_name": "Patrick Mahomes",
    "stat_type": "passing_yards",
    "line_score": 275.5,
    "opponent": "BUF"
  }'
```

**Note**: First prediction may return an error if no player data exists yet. Run the backfill script first.

## Common Issues

### Docker Not Starting

```bash
# Stop all containers
docker-compose down

# Remove volumes and restart
docker-compose down -v
docker-compose up -d
```

### Database Connection Errors

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Restart if needed
docker-compose restart postgres
```

### API Not Accessible

```bash
# Check if port 8002 is in use
lsof -i :8002

# Try different port
uvicorn app.main:app --reload --port 8003
```

### Missing Dependencies

```bash
cd backend
pip install -r requirements/base.txt
```

## Verification Checklist

Use this checklist to verify everything is working:

- [ ] Docker services running (`docker-compose ps`)
- [ ] Database migrations applied (`alembic current`)
- [ ] Teams table populated (32 teams)
- [ ] API health check returns 200
- [ ] API docs accessible at http://localhost:8002/docs
- [ ] Qdrant accessible at http://localhost:6334

## Development Mode

If you want to develop and see live changes:

```bash
cd backend

# Install dev dependencies
pip install -r requirements/dev.txt

# Run with hot reload
uvicorn app.main:app --reload --port 8002

# In another terminal, run tests
pytest

# Format code
black .
ruff check .
```

## Production Deployment

For production deployment:

```bash
# Update .env with production settings
APP_ENV=production
DEBUG=false

# Use production docker-compose
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose exec api alembic upgrade head

# Seed data
docker-compose exec api python -m scripts.seed_teams
```

## Quick Commands Reference

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f api

# Restart service
docker-compose restart api

# Check database status
python -m scripts.db_utils status

# Count records
python -m scripts.db_utils count

# Seed teams
python -m scripts.seed_teams

# Backfill stats
python -m scripts.backfill_player_stats --season 2024
```

## Getting Help

- **API Documentation**: http://localhost:8002/docs
- **Main README**: See `README.md`
- **Database Utilities**: `python -m scripts.db_utils --help`
- **Backfill Script**: `python -m scripts.backfill_player_stats --help`

## What's Next?

1. **Load More Data**: Backfill multiple seasons for better predictions
2. **Generate Narratives**: Create embeddings for historical games
3. **Test Predictions**: Make predictions for different players and stat types
4. **Monitor Accuracy**: Track prediction results over time
5. **Optimize**: Tune RAG search parameters and Claude prompts
