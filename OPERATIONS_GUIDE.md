# NFL AI - Operations Guide

**Quick reference for daily operations and maintenance**

---

## Quick Health Check

```bash
# System health
curl http://localhost:8000/api/health

# Active predictions count
docker-compose exec -T db psql -U nfl_user -d nfl_ai -c "
  SELECT COUNT(*) as active_predictions
  FROM predictions
  WHERE is_active = true;"

# PrizePicks props count
docker-compose exec -T db psql -U nfl_user -d nfl_ai -c "
  SELECT COUNT(*) as active_props
  FROM prizepicks_projections
  WHERE is_active = true;"
```

---

## Data Refresh Commands

###Full Refresh (Recommended Weekly)

```bash
docker-compose exec api python3 -m scripts.refresh_predictions
```

**What it does**:
1. Syncs latest PrizePicks props (~3,400 props)
2. Cleans up stale predictions (>24h, past games, wrong version)
3. Generates new predictions with fresh data
4. Validates everything is up-to-date

**Time**: 5-30 minutes
**Cost**: $5-50 in Claude API credits

### Sync PrizePicks Only (Fast)

```bash
docker-compose exec api python3 -m scripts.sync_prizepicks_props
```

**Time**: 10-30 seconds
**Cost**: Free

### Clear All Predictions (Emergency)

```bash
docker-compose exec api python3 -m scripts.clear_old_predictions
```

WARNING: Deactivates ALL predictions. Run refresh after.

---

## Service Management

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart API only
docker-compose restart api

# Restart frontend only
docker-compose restart frontend

# Rebuild after code changes
docker-compose up -d --build api

# View running containers
docker-compose ps

# View logs
docker-compose logs -f api
docker-compose logs --tail=100 api
```

---

## Database Operations

```bash
# PostgreSQL shell
docker-compose exec db psql -U nfl_user -d nfl_ai

# Quick stats
docker-compose exec -T db psql -U nfl_user -d nfl_ai -c "
  SELECT
    'Predictions' as table_name,
    COUNT(*) as total_count,
    COUNT(*) FILTER (WHERE is_active = true) as active_count
  FROM predictions
  UNION ALL
  SELECT
    'PrizePicks Props',
    COUNT(*),
    COUNT(*) FILTER (WHERE is_active = true)
  FROM prizepicks_projections;"

# Database size
docker-compose exec -T db psql -U nfl_user -c "\l+ nfl_ai"

# Table sizes
docker-compose exec -T db psql -U nfl_user -d nfl_ai -c "
  SELECT
    relname as table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS size
  FROM pg_catalog.pg_statio_user_tables
  ORDER BY pg_total_relation_size(relid) DESC
  LIMIT 10;"
```

---

## Troubleshooting

### No predictions showing?

```bash
# 1. Check props are loaded
docker-compose exec -T db psql -U nfl_user -d nfl_ai -c "
  SELECT COUNT(*) FROM prizepicks_projections WHERE is_active = true;"

# 2. Sync props if needed
docker-compose exec api python3 -m scripts.sync_prizepicks_props

# 3. Generate predictions
docker-compose exec api python3 -m scripts.refresh_predictions
```

### Stale predictions showing?

```bash
# Check freshness stats
docker-compose exec api python3 -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.services.prediction_freshness import get_freshness_service

async def check():
    async with AsyncSessionLocal() as db:
        service = get_freshness_service()
        stats = await service.get_prediction_freshness_stats(db)
        print('Freshness Stats:')
        print(f'  Total active: {stats[\"total_active\"]}')
        print(f'  Fresh (<24h): {stats[\"fresh\"]}')
        print(f'  Stale: {stats[\"stale_but_active\"]}')
        print(f'  Past game: {stats[\"past_game_time\"]}')
        print(f'  Wrong version: {stats[\"wrong_version\"]}')

asyncio.run(check())
"

# Fix: Run full refresh
docker-compose exec api python3 -m scripts.refresh_predictions
```

### API errors?

```bash
# Check Claude API key
docker-compose exec api printenv ANTHROPIC_API_KEY

# Check database connection
docker-compose exec api python3 -c "
from app.core.database import engine
print('Database URL:', engine.url)"

# View error logs
docker-compose logs --tail=50 api | grep -i error

# Restart services
docker-compose restart api
```

---

## Weekly Maintenance

**Every Monday** (before new game week):

```bash
# 1. Full refresh
docker-compose exec api python3 -m scripts.refresh_predictions

# 2. Check freshness
docker-compose exec api python3 -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.services.prediction_freshness import get_freshness_service

async def check():
    async with AsyncSessionLocal() as db:
        service = get_freshness_service()
        stats = await service.get_prediction_freshness_stats(db)
        print(f'✓ Active predictions: {stats[\"total_active\"]}')
        if stats['stale_but_active'] == 0:
            print('✓ All predictions fresh!')
        else:
            print(f'⚠ WARNING: {stats[\"stale_but_active\"]} stale predictions')

asyncio.run(check())
"

# 3. Check Claude API credits
# Visit: https://console.anthropic.com/

# 4. Review error logs
docker-compose logs --since 24h api | grep -i error
```

---

## Backup & Restore

### Backup

```bash
# Create backup
docker-compose exec -T db pg_dump -U nfl_user nfl_ai | gzip > backup_$(date +%Y%m%d).sql.gz

# Verify backup
ls -lh backup_*.sql.gz
```

### Restore

```bash
# Restore from backup
gunzip < backup_20251031.sql.gz | docker-compose exec -T db psql -U nfl_user nfl_ai
```

---

## Monitoring

```bash
# Container resource usage
docker stats

# API logs
docker-compose logs -f api

# Database connections
docker-compose exec -T db psql -U nfl_user -c "
  SELECT count(*) FROM pg_stat_activity
  WHERE datname = 'nfl_ai';"

# Check for long-running queries
docker-compose exec -T db psql -U nfl_user -d nfl_ai -c "
  SELECT pid, now() - query_start as duration, query
  FROM pg_stat_activity
  WHERE state = 'active' AND query != '<IDLE>'
  ORDER BY duration DESC;"
```

---

## Important Files

### Scripts
- `scripts/refresh_predictions.py` - Complete refresh workflow
- `scripts/sync_prizepicks_props.py` - Sync betting lines
- `scripts/clear_old_predictions.py` - Emergency reset

### Services
- `app/services/batch_predictions.py` - Prediction engine
- `app/services/prediction_freshness.py` - Freshness service
- `app/services/prizepicks.py` - PrizePicks integration
- `app/services/claude_prediction.py` - Claude AI

---

## URLs

### Local Development
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Qdrant: http://localhost:6333/dashboard

---

## Quick Commands

```bash
# View logs
docker-compose logs -f api

# Restart service
docker-compose restart api

# Shell access
docker-compose exec api bash
docker-compose exec db psql -U nfl_user nfl_ai

# Check disk usage
docker system df

# Clean up old images
docker system prune -a
```

---

## Remember

- Data freshness is automatic (cleanup on every request)
- Predictions expire after 24 hours
- Version tracking auto-invalidates old logic
- Run full refresh weekly
- PrizePicks API is free
- Claude API: ~$0.02 per prediction

---

**Last Updated**: October 31, 2025
