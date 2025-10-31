# NFL AI Production Deployment Guide

**Status**: Ready for production deployment
**Last Updated**: October 31, 2025
**Version**: 2.0 (PrizePicks Integration)

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Key Features](#key-features)
4. [Pre-Deployment Checklist](#pre-deployment-checklist)
5. [Environment Setup](#environment-setup)
6. [Initial Deployment](#initial-deployment)
7. [Data Initialization](#data-initialization)
8. [Automated Scheduling](#automated-scheduling)
9. [Monitoring & Maintenance](#monitoring--maintenance)
10. [Troubleshooting](#troubleshooting)
11. [API Documentation](#api-documentation)

---

## System Overview

**NFL AI** is an AI-powered NFL player prop prediction platform that provides:

- Real-time betting line integration from PrizePicks (3,400+ live props)
- AI-generated predictions using Claude Sonnet 4.5
- Confidence scoring and edge calculation
- Automatic data freshness guarantees (4-layer defense system)
- Slate-based filtering (Early/Afternoon/Prime games)
- RAG-based historical performance analysis

**Target Users**: Sports bettors looking for data-driven prop betting insights

**Data Sources**:
- PrizePicks API (betting lines) - FREE, no API key required
- ESPN API (NFL schedules, scores)
- Sleeper API (player stats, injuries)
- Anthropic Claude API (AI predictions) - **REQUIRES API KEY**

---

## Architecture

### Tech Stack

**Backend**:
- FastAPI (Python 3.11+)
- PostgreSQL 15+ (with vector extension)
- Qdrant (vector database for RAG)
- SQLAlchemy (async ORM)
- Alembic (migrations)

**Frontend**:
- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS

**Infrastructure**:
- Docker & Docker Compose
- Nginx (reverse proxy)
- Supervisor (process management)

### System Architecture

```
┌─────────────┐
│   Frontend  │ (Next.js)
│  Port 3000  │
└──────┬──────┘
       │
┌──────▼──────────────────────────────────┐
│         Nginx Reverse Proxy             │
│  - /api → Backend (8000)                │
│  - / → Frontend (3000)                  │
└──────┬──────────────────────────────────┘
       │
┌──────▼──────┐     ┌───────────────┐     ┌─────────────┐
│   Backend   │────▶│  PostgreSQL   │     │   Qdrant    │
│  Port 8000  │     │   Port 5432   │     │  Port 6333  │
└─────────────┘     └───────────────┘     └─────────────┘
       │
       ├──▶ PrizePicks API (betting lines)
       ├──▶ Claude API (predictions)
       ├──▶ ESPN API (schedules)
       └──▶ Sleeper API (stats)
```

---

## Key Features

### 1. Real-Time PrizePicks Integration
- Syncs 3,400+ live betting lines hourly
- Smart main line detection algorithm
- Supports all major prop types (rushing, receiving, passing)

### 2. AI-Powered Predictions
- Claude Sonnet 4.5 analysis engine
- Context-aware predictions (stats, matchups, injuries)
- Confidence scoring (0-100)
- Edge calculation (projected value - line)

### 3. Automatic Data Freshness (CRITICAL)
**4-Layer Defense System** ensures stale data NEVER appears:

- **Layer 1: Version Tracking** - Predictions tagged with version, old logic auto-invalidated
- **Layer 2: Age-Based Cleanup** - Predictions >24 hours automatically deactivated
- **Layer 3: Game-Time Cleanup** - Past games automatically deactivated
- **Layer 4: API-Level Protection** - Cleanup runs on EVERY request

### 4. Slate Filtering
- **Early** (12-2pm ET)
- **Afternoon** (3-5pm ET)
- **Prime** (6pm+ ET including SNF/MNF)

### 5. RAG System
- Vector embeddings of historical performances
- Finds similar game situations
- Enhances prediction accuracy

---

## Pre-Deployment Checklist

### Required Services
- [ ] PostgreSQL 15+ running
- [ ] Qdrant vector DB running
- [ ] Docker & Docker Compose installed
- [ ] Domain/subdomain configured (if using custom domain)

### Required API Keys
- [ ] **Anthropic Claude API Key** (REQUIRED)
  - Get from: https://console.anthropic.com/
  - Billing: Pay-as-you-go (~$0.10-0.50 per prediction)
  - Minimum credit: $5 recommended

### Optional but Recommended
- [ ] SSL certificate (Let's Encrypt)
- [ ] Monitoring setup (Sentry, DataDog, etc.)
- [ ] Backup strategy for PostgreSQL
- [ ] CDN for frontend assets

---

## Environment Setup

### 1. Clone Repository

```bash
cd /opt  # or your preferred location
git clone <your-repo-url> nfl-ai
cd nfl-ai
```

### 2. Configure Environment Variables

Create `.env` files for backend and frontend:

#### Backend `.env`

```bash
# Database
DATABASE_URL=postgresql+asyncpg://nfl_user:your_secure_password@localhost:5432/nfl_ai
SYNC_DATABASE_URL=postgresql://nfl_user:your_secure_password@localhost:5432/nfl_ai

# Qdrant Vector Database
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Claude API (REQUIRED)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://yourdomain.com

# Security
SECRET_KEY=your-secret-key-here-generate-with-openssl
```

**Generate secure secret key**:
```bash
openssl rand -hex 32
```

#### Frontend `.env.local`

```bash
NEXT_PUBLIC_API_URL=https://yourdomain.com/api
```

### 3. Update Docker Compose (if needed)

Review `docker-compose.yml` and adjust:
- Port mappings
- Volume mounts
- Resource limits

---

## Initial Deployment

### 1. Build and Start Services

```bash
# Build all services
docker-compose build

# Start in detached mode
docker-compose up -d

# Check status
docker-compose ps
```

Expected output:
```
NAME                COMMAND                  SERVICE             STATUS
nfl-ai-api-1        "uvicorn app.main:ap…"   api                 running
nfl-ai-frontend-1   "docker-entrypoint.s…"   frontend            running
nfl-ai-db-1         "docker-entrypoint.s…"   db                  running
nfl-ai-qdrant-1     "./entrypoint.sh"        qdrant              running
```

### 2. Run Database Migrations

```bash
# Apply all migrations
docker-compose exec api alembic upgrade head

# Verify migrations
docker-compose exec api alembic current
```

---

## Data Initialization

### CRITICAL: Initial Data Load

Run these commands in order to populate the database:

#### 1. Load NFL Schedule (Week 1-18)

```bash
docker-compose exec api python3 -m scripts.fetch_nfl_schedule
```

Expected: ~300+ games loaded (18 weeks × 16-17 games/week)

#### 2. Load Player Data

```bash
docker-compose exec api python3 -m scripts.fetch_players
```

Expected: ~2,000+ active players loaded

#### 3. Load Historical Stats (for RAG)

```bash
docker-compose exec api python3 -m scripts.fetch_player_stats
```

Expected: ~50,000+ stat records loaded (may take 10-20 minutes)

#### 4. Sync PrizePicks Props

```bash
docker-compose exec api python3 -m scripts.sync_prizepicks_props
```

Expected: ~3,400+ active props loaded

#### 5. Generate Initial Predictions

```bash
docker-compose exec api python3 -m scripts.refresh_predictions
```

This will:
1. Sync latest PrizePicks props
2. Clean up any stale predictions
3. Generate fresh predictions for current week
4. Validate data freshness

Expected: 200-500+ predictions generated (depends on week)

**Cost Warning**: This will consume Claude API credits (~$10-50 depending on volume)

---

## Automated Scheduling

### Set Up Cron Jobs

Add to root crontab:

```bash
# Edit crontab
sudo crontab -e

# Add these jobs:

# Sync PrizePicks props every hour
0 * * * * cd /opt/nfl-ai && docker-compose exec -T api python3 -m scripts.sync_prizepicks_props >> /var/log/nfl-ai/sync.log 2>&1

# Refresh predictions every 6 hours during game weeks
0 */6 * * * cd /opt/nfl-ai && docker-compose exec -T api python3 -m scripts.refresh_predictions >> /var/log/nfl-ai/refresh.log 2>&1

# Fetch latest player stats daily at 3 AM
0 3 * * * cd /opt/nfl-ai && docker-compose exec -T api python3 -m scripts.fetch_player_stats >> /var/log/nfl-ai/stats.log 2>&1

# Clean up old logs weekly
0 0 * * 0 find /var/log/nfl-ai -name "*.log" -mtime +7 -delete
```

**Create log directory**:
```bash
sudo mkdir -p /var/log/nfl-ai
sudo chmod 755 /var/log/nfl-ai
```

### Alternative: Systemd Timers

More reliable than cron for production:

```bash
# Create timer files in /etc/systemd/system/
# See systemd documentation for details
```

---

## Monitoring & Maintenance

### Health Checks

#### API Health
```bash
curl https://yourdomain.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "qdrant": "connected"
}
```

#### Check Active Predictions
```bash
docker-compose exec api python3 -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.services.prediction_freshness import get_freshness_service

async def check():
    async with AsyncSessionLocal() as db:
        service = get_freshness_service()
        stats = await service.get_prediction_freshness_stats(db)
        print(f'Active predictions: {stats[\"total_active\"]}')
        print(f'Fresh predictions: {stats[\"fresh\"]}')
        print(f'Stale predictions: {stats[\"stale_but_active\"]}')
        if stats['stale_but_active'] > 0:
            print('WARNING: Stale predictions detected!')

asyncio.run(check())
"
```

### Database Backups

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/nfl-ai"
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker-compose exec -T db pg_dump -U nfl_user nfl_ai | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Keep last 7 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete
```

Add to crontab:
```bash
0 2 * * * /opt/nfl-ai/scripts/backup.sh >> /var/log/nfl-ai/backup.log 2>&1
```

### Monitoring Checklist

**Daily**:
- [ ] Check prediction freshness stats
- [ ] Review error logs: `docker-compose logs --tail=100 api`
- [ ] Verify PrizePicks sync completed

**Weekly**:
- [ ] Check database size: `docker-compose exec db psql -U nfl_user -c "\l+"`
- [ ] Review prediction accuracy (if tracking)
- [ ] Update player data if needed

**Before Each Game Week**:
- [ ] Run full refresh: `python3 -m scripts.refresh_predictions`
- [ ] Verify upcoming games loaded
- [ ] Check Claude API credits

---

## Troubleshooting

### Common Issues

#### Issue: No Predictions Showing

**Symptoms**: Empty opportunities feed

**Diagnosis**:
```bash
# Check active predictions
docker-compose exec db psql -U nfl_user -d nfl_ai -c "SELECT COUNT(*) FROM predictions WHERE is_active = true;"

# Check PrizePicks props
docker-compose exec db psql -U nfl_user -d nfl_ai -c "SELECT COUNT(*) FROM prizepicks_projections WHERE is_active = true;"
```

**Solutions**:
1. Run sync: `docker-compose exec api python3 -m scripts.sync_prizepicks_props`
2. Run refresh: `docker-compose exec api python3 -m scripts.refresh_predictions`
3. Check Claude API key is valid

---

#### Issue: Stale Predictions Showing

**Symptoms**: Old lines or past games appearing

**Diagnosis**:
```bash
# Check for stale predictions
docker-compose exec api python3 -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.services.prediction_freshness import get_freshness_service

async def check():
    async with AsyncSessionLocal() as db:
        service = get_freshness_service()
        stats = await service.get_prediction_freshness_stats(db)
        print(f'Stale predictions: {stats[\"stale_but_active\"]}')
        print(f'Past game time: {stats[\"past_game_time\"]}')
        print(f'Wrong version: {stats[\"wrong_version\"]}')

asyncio.run(check())
"
```

**Solution**:
```bash
# Manual cleanup
docker-compose exec api python3 -m scripts.clear_old_predictions

# Regenerate fresh predictions
docker-compose exec api python3 -m scripts.refresh_predictions
```

**NOTE**: This should NEVER happen - the 4-layer defense system prevents this automatically.

---

#### Issue: Claude API Errors

**Symptoms**:
- "API key invalid" errors
- "Rate limit exceeded" errors
- No new predictions generated

**Solutions**:

1. **Invalid API Key**:
   ```bash
   # Verify key in environment
   docker-compose exec api printenv ANTHROPIC_API_KEY

   # Update .env and restart
   docker-compose restart api
   ```

2. **Rate Limiting**:
   - Reduce prediction batch size in `batch_predictions.py`
   - Increase sleep time between predictions (currently 0.5s)
   - Upgrade Claude API tier

3. **Insufficient Credits**:
   - Check balance: https://console.anthropic.com/
   - Add credits to account

---

#### Issue: Database Connection Errors

**Symptoms**: "Connection refused" or "Connection timeout"

**Diagnosis**:
```bash
# Check database is running
docker-compose ps db

# Test connection
docker-compose exec db psql -U nfl_user -d nfl_ai -c "SELECT 1;"
```

**Solutions**:
```bash
# Restart database
docker-compose restart db

# Check logs
docker-compose logs db

# Verify DATABASE_URL in .env
```

---

#### Issue: PrizePicks API Errors

**Symptoms**:
- "Failed to fetch props" errors
- 0 props synced

**Diagnosis**:
```bash
# Test PrizePicks API directly
curl "https://api.prizepicks.com/projections?league_id=7"
```

**Solutions**:
1. **API Changed**: PrizePicks updated their API structure
   - Review response format
   - Update `prizepicks.py` parser

2. **Network Issue**: Server blocked by PrizePicks
   - Try from different IP
   - Add delay between requests
   - Contact PrizePicks if needed

3. **Temporary Outage**: PrizePicks API down
   - Wait and retry
   - Check PrizePicks website status

---

## API Documentation

### Endpoints

#### GET /api/opportunities

Returns filtered list of predictions with betting opportunities.

**Query Parameters**:
- `slate` (optional): "EARLY" | "AFTERNOON" | "PRIME"
- `min_confidence` (optional): Filter by minimum confidence (0-100)
- `min_edge` (optional): Filter by minimum edge

**Response**:
```json
{
  "opportunities": [
    {
      "id": "uuid",
      "player_name": "Patrick Mahomes",
      "player_position": "QB",
      "team": "KC",
      "opponent": "LV",
      "week": 9,
      "game_time": "2025-11-03T18:15:00",
      "slate": "PRIME",
      "stat_type": "passing_yards",
      "line_score": 265.5,
      "prediction": "OVER",
      "confidence": 78,
      "projected_value": 285.2,
      "edge": 19.7,
      "reasoning": "Mahomes historically performs well...",
      "key_factors": ["Factor 1", "Factor 2"],
      "risk_factors": ["Risk 1", "Risk 2"]
    }
  ],
  "total": 150,
  "filters_applied": {
    "slate": "PRIME"
  }
}
```

**Rate Limiting**: None currently, add if needed

---

#### GET /api/health

Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "qdrant": "connected",
  "version": "2.0"
}
```

---

## Manual Operations

### Refresh All Data (Complete Reset)

**When to use**:
- After prediction logic changes
- Data quality issues detected
- Weekly maintenance

```bash
docker-compose exec api python3 -m scripts.refresh_predictions
```

This runs the complete workflow:
1. ✓ Sync latest PrizePicks props
2. ✓ Clean up stale predictions
3. ✓ Check current state
4. ✓ Generate new predictions
5. ✓ Validate freshness

---

### Clear All Predictions (Nuclear Option)

**When to use**: Emergency reset only

```bash
docker-compose exec api python3 -m scripts.clear_old_predictions
```

**WARNING**: This deactivates ALL predictions. You must regenerate after.

---

### Test Prediction Generation

Test on small subset (5 players):

```bash
docker-compose exec api python3 -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.services.batch_predictions import get_batch_prediction_service

async def test():
    async with AsyncSessionLocal() as db:
        service = get_batch_prediction_service()
        result = await service.generate_weekly_predictions(
            db=db,
            week=9,
            season=2025,
            max_players=5
        )
        print(f'Generated: {result}')

asyncio.run(test())
"
```

---

## Performance Optimization

### Database Indexes

Ensure these indexes exist (should be in migrations):

```sql
CREATE INDEX idx_predictions_active ON predictions(is_active);
CREATE INDEX idx_predictions_week ON predictions(week);
CREATE INDEX idx_predictions_game_time ON predictions(game_time);
CREATE INDEX idx_prizepicks_active ON prizepicks_projections(is_active);
```

### Qdrant Optimization

For large datasets (>1M vectors):

```python
# Update collection config in rag_narrative.py
client.create_collection(
    collection_name="game_performances",
    vectors_config=models.VectorParams(
        size=3072,
        distance=models.Distance.COSINE
    ),
    optimizers_config=models.OptimizersConfigDiff(
        indexing_threshold=20000  # Increase for better performance
    )
)
```

---

## Cost Estimates

### Claude API Costs

**Per Prediction**:
- Input: ~1,000 tokens (~$0.003)
- Output: ~500 tokens (~$0.015)
- **Total**: ~$0.018 per prediction

**Weekly Costs** (typical):
- 300 predictions: ~$5.40
- 500 predictions: ~$9.00
- 1,000 predictions: ~$18.00

**Monthly** (4 weeks): $20-75

### Infrastructure Costs

**Self-Hosted**:
- VPS (4GB RAM, 2 CPU): $20-40/month
- PostgreSQL storage: $5-10/month
- **Total**: ~$30-50/month

**Cloud** (AWS/GCP):
- EC2/Compute Engine: $50-100/month
- RDS/Cloud SQL: $30-50/month
- Load Balancer: $20/month
- **Total**: ~$100-170/month

---

## Security Considerations

### API Keys
- Store in environment variables ONLY
- Never commit to git
- Rotate periodically
- Use secret management service in production

### Database
- Use strong passwords
- Enable SSL connections
- Regular backups
- Restrict network access

### Frontend
- Enable CORS properly
- Use HTTPS only
- Implement rate limiting if public

### Monitoring
- Log all API errors
- Monitor for unusual activity
- Set up alerts for failures

---

## Support & Resources

### Documentation
- Backend API: `http://localhost:8000/docs` (Swagger)
- Database Schema: See `backend/app/models/nfl.py`
- Frontend Components: See `frontend/components/`

### Useful Commands

```bash
# View logs
docker-compose logs -f api
docker-compose logs -f frontend

# Restart services
docker-compose restart api
docker-compose restart frontend

# Shell access
docker-compose exec api bash
docker-compose exec db psql -U nfl_user nfl_ai

# Check resource usage
docker stats
```

---

## Version History

### v2.0 - October 31, 2025
- ✓ PrizePicks real-time integration
- ✓ Smart main line detection
- ✓ 4-layer data freshness system
- ✓ Automatic staleness prevention
- ✓ Version tracking for predictions
- ✓ Slate filtering (Early/Afternoon/Prime)

### v1.0 - October 28, 2025
- ✓ Initial release
- ✓ Basic prediction system
- ✓ Opportunities feed
- ✓ RAG-based analysis

---

## Ready for Production?

### Pre-Launch Checklist

- [ ] All environment variables configured
- [ ] Database migrations applied
- [ ] Initial data loaded (schedule, players, stats, props)
- [ ] Test predictions generated successfully
- [ ] Health check endpoint responding
- [ ] Cron jobs configured
- [ ] Backups configured
- [ ] SSL certificate installed
- [ ] Domain DNS configured
- [ ] Monitoring/logging set up
- [ ] Claude API credits funded
- [ ] Emergency rollback plan documented

### Launch Steps

1. Deploy code to production server
2. Run database migrations
3. Load initial data
4. Generate first predictions
5. Test frontend access
6. Enable cron jobs
7. Monitor for 24 hours
8. Announce launch!

---

## Contact & Support

For issues or questions:
- Review logs: `/var/log/nfl-ai/`
- Check documentation above
- Review code comments
- Test in development first

**Remember**: The 4-layer freshness system ensures users NEVER see stale data. If you encounter data quality issues, run `refresh_predictions.py` to regenerate everything.

Good luck with your launch! 🚀
