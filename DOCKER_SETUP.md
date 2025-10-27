# NFL AI - Docker Setup Guide

Complete containerized deployment using Docker Compose.

## Quick Start

Start the entire application stack with a single command:

```bash
docker-compose up -d
```

Access the application:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

Stop all services:

```bash
docker-compose down
```

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- `.env` file with required API keys (see Environment Variables section)

## Environment Variables

Create a `.env` file in the project root:

```bash
# Required
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Database (defaults shown)
POSTGRES_USER=nfl_user
POSTGRES_PASSWORD=nfl_password
POSTGRES_DB=nfl_analytics

# Optional APIs
ODDS_API_KEY=your_key_here
TWITTER_API_KEY=your_key_here
WEATHER_API_KEY=your_key_here

# App Config
APP_ENV=development
LOG_LEVEL=INFO
DEBUG=true
```

## Services Overview

### PostgreSQL (postgres)
- **Purpose**: Relational database for structured data
- **Port**: 5434 (external) → 5432 (internal)
- **Data**: Teams, players, game stats, schedules
- **Volume**: `postgres_data` (persistent storage)

### Qdrant (qdrant)
- **Purpose**: Vector database for RAG system
- **Port**: 6336 (external) → 6333 (internal)
- **Data**: 1,329+ narrative embeddings for similar situation retrieval
- **Volume**: `qdrant_storage` (persistent storage)

### Redis (redis)
- **Purpose**: Cache and session storage
- **Port**: 6380 (external) → 6379 (internal)
- **Config**: 512MB max memory with LRU eviction
- **Volume**: `redis_data` (persistent storage)

### FastAPI Backend (api)
- **Purpose**: REST API for predictions and data access
- **Port**: 8000
- **Features**:
  - Prediction endpoint with opponent validation
  - Historical stats API
  - Schedule management
  - RAG integration
- **Hot Reload**: Enabled in development mode

### Next.js Frontend (frontend)
- **Purpose**: Web interface for predictions
- **Port**: 3000
- **Features**:
  - Prediction form
  - Confidence meters
  - Recent form charts
  - Similar situations display
- **Hot Reload**: Enabled in development mode

### Background Worker (worker)
- **Purpose**: Data collection and scheduled tasks
- **Features**:
  - Scheduled stat updates
  - Schedule fetching
  - Narrative generation
- **Status**: Currently disabled (commented out in docker-compose.yml)

## First-Time Setup

1. **Start services**:
   ```bash
   docker-compose up -d
   ```

2. **Check service health**:
   ```bash
   docker-compose ps
   ```

   All services should show "healthy" or "running" status.

3. **Initialize database** (if needed):
   ```bash
   docker-compose exec api python -m alembic upgrade head
   ```

4. **Populate teams**:
   ```bash
   docker-compose exec api python backend/scripts/populate_teams.py
   ```

5. **Fetch current schedule**:
   ```bash
   docker-compose exec api python backend/scripts/fetch_nfl_schedule.py --season 2025 --weeks 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18
   ```

6. **Backfill historical data** (optional):
   ```bash
   docker-compose exec api python backend/scripts/backfill_player_stats.py
   ```

7. **Generate RAG narratives** (optional):
   ```bash
   docker-compose exec api python backend/scripts/generate_narratives_limited.py --limit 500
   ```

## Common Operations

### View logs

All services:
```bash
docker-compose logs -f
```

Specific service:
```bash
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Restart a service

```bash
docker-compose restart api
docker-compose restart frontend
```

### Rebuild after code changes

Frontend:
```bash
docker-compose up -d --build frontend
```

Backend:
```bash
docker-compose up -d --build api
```

All services:
```bash
docker-compose up -d --build
```

### Execute commands in containers

Run Python script:
```bash
docker-compose exec api python backend/scripts/your_script.py
```

Open database shell:
```bash
docker-compose exec postgres psql -U nfl_user -d nfl_analytics
```

Open Redis CLI:
```bash
docker-compose exec redis redis-cli
```

### Database operations

Create backup:
```bash
docker-compose exec postgres pg_dump -U nfl_user nfl_analytics > backup.sql
```

Restore backup:
```bash
cat backup.sql | docker-compose exec -T postgres psql -U nfl_user -d nfl_analytics
```

## Development Workflow

### Hot Reload

Both frontend and backend support hot reload in development mode:

- **Frontend**: Edit files in `./frontend/` → changes reflected immediately
- **Backend**: Edit files in `./backend/` → uvicorn auto-reloads

### Debugging

Access container shell:
```bash
docker-compose exec api /bin/sh
docker-compose exec frontend /bin/sh
```

Check environment variables:
```bash
docker-compose exec api env
```

### Running tests

```bash
docker-compose exec api pytest
```

## Production Deployment

For production, switch to production Dockerfile:

1. **Edit `docker-compose.yml`**:
   ```yaml
   frontend:
     build:
       context: ./frontend
       dockerfile: Dockerfile  # Change from Dockerfile.dev
     environment:
       - NODE_ENV=production
   ```

2. **Build and start**:
   ```bash
   docker-compose up -d --build
   ```

## Troubleshooting

### Service won't start

Check logs:
```bash
docker-compose logs api
```

Common issues:
- Missing environment variables in `.env`
- Port conflicts (another service using 3000, 8000, etc.)
- Insufficient memory for Redis

### Database connection errors

1. Ensure postgres is healthy:
   ```bash
   docker-compose ps postgres
   ```

2. Check connection from API:
   ```bash
   docker-compose exec api python -c "from app.core.database import engine; print('Connected!')"
   ```

### Frontend can't reach API

- Internal Docker network uses `http://api:8000`
- External access uses `http://localhost:8000`
- Check `NEXT_PUBLIC_API_URL` in docker-compose.yml

### Qdrant connection issues

Verify Qdrant is running:
```bash
curl http://localhost:6336/collections
```

### Port conflicts

Change external ports in docker-compose.yml:
```yaml
ports:
  - "3001:3000"  # Change 3000 → 3001 if port 3000 is taken
```

### Out of disk space

Remove old volumes:
```bash
docker-compose down -v  # WARNING: Deletes all data
docker system prune -a --volumes
```

### Performance issues

Increase Docker resources:
- Docker Desktop: Settings → Resources → Memory (recommend 4GB+)

## Data Persistence

Data is stored in Docker volumes:

- `postgres_data`: All database tables
- `qdrant_storage`: Vector embeddings
- `redis_data`: Cache data

To completely reset:
```bash
docker-compose down -v  # WARNING: Deletes ALL data
docker-compose up -d
# Re-run first-time setup steps
```

## Network Architecture

All services communicate on the `nfl-ai-network` bridge network:

```
Frontend (port 3000)
    ↓ http://api:8000
API (port 8000)
    ↓ postgres:5432
    ↓ qdrant:6333
    ↓ redis:6379
PostgreSQL | Qdrant | Redis
```

External access:
- Frontend: `localhost:3000`
- API: `localhost:8000`
- PostgreSQL: `localhost:5434`
- Qdrant: `localhost:6336`
- Redis: `localhost:6380`

## Health Checks

Services implement health checks:

- **PostgreSQL**: `pg_isready` every 10s
- **Redis**: `redis-cli ping` every 10s
- **API**: `curl /health` every 30s

View health status:
```bash
docker-compose ps
```

## Security Notes

- PostgreSQL and Redis are not exposed to public internet (bound to localhost)
- Frontend runs as non-root user in production
- Passwords should be changed from defaults in production
- API keys should never be committed to git

## Resource Usage

Typical memory usage:
- PostgreSQL: ~100MB
- Qdrant: ~200MB
- Redis: ~512MB (configured limit)
- API: ~200MB
- Frontend: ~150MB
- **Total**: ~1.2GB

## Updates and Maintenance

Update base images:
```bash
docker-compose pull
docker-compose up -d --build
```

View container stats:
```bash
docker stats
```

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
