# Digital Ocean Deployment Guide

## Overview

This guide covers migrating your NFL AI prediction system to Digital Ocean App Platform with a web frontend.

## Current Data

- **PostgreSQL**: 17,490 game stats, 8,297 players, 164 games
- **Qdrant**: 456 narrative embeddings (worth ~$0.05 in API costs, but valuable historical data)

## Architecture Options

### Option 1: Fully Managed (Recommended)

```
┌─────────────────┐
│ DO App Platform │
│   - Web UI      │
│   - FastAPI     │
└────────┬────────┘
         │
    ┌────┴────┬─────────────┐
    ▼         ▼             ▼
┌────────┐ ┌──────────┐ ┌──────────┐
│DO Mgd  │ │ Qdrant   │ │  Redis   │
│Postgres│ │  Cloud   │ │  Cloud   │
└────────┘ └──────────┘ └──────────┘
```

**Pros:**
- All managed services (less maintenance)
- Automatic backups
- Easy scaling

**Cons:**
- Qdrant Cloud costs (~$25/mo for starter)

### Option 2: Hybrid (Cost-Effective)

```
┌─────────────────────────┐
│ DO App Platform         │
│   - Web UI              │
│   - FastAPI             │
│   - Qdrant (container)  │
└────────┬────────────────┘
         │
    ┌────┴────┬──────────┐
    ▼         ▼          ▼
┌────────┐ ┌──────┐ ┌────────┐
│DO Mgd  │ │ DO   │ │ Redis  │
│Postgres│ │Volume│ │ Cloud  │
└────────┘ └──────┘ └────────┘
```

**Pros:**
- Lower cost (Qdrant in-app)
- Still managed DB

**Cons:**
- Need to manage Qdrant container
- Need persistent volume for Qdrant data

## Migration Steps

### 1. Backup Local Data

```bash
# Backup PostgreSQL
cd backend
./scripts/backup_postgres.sh

# Backup Qdrant
./scripts/backup_qdrant.sh

# You'll find backups in backend/backups/
```

### 2. Set Up Digital Ocean Resources

#### A. Create Managed PostgreSQL Database
1. Go to DO Dashboard → Databases → Create
2. Choose PostgreSQL 15
3. Select plan (Basic $15/mo sufficient to start)
4. Note connection details

#### B. Choose Qdrant Strategy

**Option 1 - Qdrant Cloud:**
1. Sign up at https://cloud.qdrant.io
2. Create free cluster
3. Note API key and URL

**Option 2 - Self-Hosted:**
- We'll run Qdrant as part of the app
- Need to add volume mount in app spec

#### C. Create App Platform App
1. Connect GitHub repo
2. Set as Dockerfile deployment
3. Configure environment variables (see below)

### 3. Restore Data

#### Restore PostgreSQL
```bash
# From your local machine
gunzip backups/nfl_analytics_*.sql.gz

# Restore to DO database
psql -h <DO_POSTGRES_HOST> \
     -p 25060 \
     -U <DO_USER> \
     -d <DO_DATABASE> \
     -f backups/nfl_analytics_*.sql
```

#### Restore Qdrant

**If using Qdrant Cloud:**
```bash
# Use their web UI to upload snapshot
# Or use their API:
curl -X POST 'https://<your-cluster>.qdrant.io/collections/game_performances/snapshots/upload' \
  -H 'api-key: <your-key>' \
  --data-binary @backups/qdrant_game_performances_*.snapshot
```

**If self-hosted:**
- Upload snapshot to DO Space
- Download in init script
- Restore on first boot

### 4. Environment Variables for DO App Platform

```bash
# Database
DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<host>:25060/<db>?sslmode=require

# Qdrant
QDRANT_URL=https://<cluster>.qdrant.io  # If Qdrant Cloud
# OR
QDRANT_HOST=localhost
QDRANT_PORT=6333
# (if self-hosted in same container)

# Redis
REDIS_URL=rediss://<user>:<pass>@<host>:25061

# API Keys (use DO's encrypted secrets)
ANTHROPIC_API_KEY=<your-key>
OPENAI_API_KEY=<your-key>

# Security
SECRET_KEY=<generate-random-key>
```

### 5. Add Web Frontend

Your web app should:
1. Call the FastAPI backend at `/api/predictions/predict`
2. Handle responses and display predictions
3. Show historical data visualizations

Example frontend tech stacks:
- **Next.js** (React) - Best for SEO
- **SvelteKit** - Lightweight and fast
- **Vue 3 + Vite** - Good DX

DO App Platform supports all of these with auto-deploy.

## Cost Estimate (Monthly)

### Minimal Setup
- App Platform (Basic): $5
- Managed PostgreSQL (Basic): $15
- Qdrant (self-hosted, included in app): $0
- Redis (free tier or $7): $0-7
- **Total: ~$20-27/mo**

### Recommended Setup
- App Platform (Pro): $12
- Managed PostgreSQL (Basic): $15
- Qdrant Cloud (Starter): $25
- Redis: $7
- **Total: ~$59/mo**

## Testing Deployment

Before migrating:
1. Test locally with docker-compose
2. Verify all services connect
3. Run prediction demo
4. Check logs for errors

After migration:
1. Test health endpoint: `GET /health`
2. Test prediction endpoint with sample data
3. Verify Qdrant returns similar situations
4. Check database connections

## Rollback Plan

If deployment fails:
1. Keep local environment running
2. Backups are in `backend/backups/`
3. Can restore locally anytime
4. Data is never deleted, only copied

## Next Steps After Deployment

1. Set up monitoring (DO has built-in metrics)
2. Configure alerts for API errors
3. Add rate limiting (protect API keys)
4. Set up weekly data updates (cron job)
5. Add authentication for web UI

## Important Notes

⚠️ **DO NOT delete local data until production is verified**

⚠️ **Store API keys in DO encrypted secrets, not environment variables**

⚠️ **Enable SSL for all database connections**

⚠️ **Set up automated backups in DO dashboard**

## Questions?

Common issues:
- **Connection timeout**: Check DO firewall rules
- **SSL required**: Add `?sslmode=require` to connection string
- **Qdrant not found**: Verify volume mount or cloud URL
- **API rate limits**: Implement caching/rate limiting
