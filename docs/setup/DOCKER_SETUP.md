# Docker Setup Guide

## Quick Start

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env with your API keys
# (Required: ANTHROPIC_API_KEY, OPENAI_API_KEY)

# 3. Start all services
make up

# 4. Check status
make status
```

That's it! All services are now running.

---

## Port Assignments

**NFL AI uses these unique ports** (to avoid conflicts with other projects):

| Service | External Port | Internal Port | URL |
|---------|--------------|---------------|-----|
| API | 8002 | 8000 | http://localhost:8002 |
| PostgreSQL | 5433 | 5432 | localhost:5433 |
| Qdrant HTTP | 6334 | 6333 | http://localhost:6334 |
| Qdrant gRPC | 6335 | 6334 | localhost:6335 |
| Redis | 6380 | 6379 | localhost:6380 |
| PgAdmin (dev) | 5434 | 80 | http://localhost:5434 |

**Note**: External ports are what you use from your host machine. Internal ports are used within Docker network.

---

## Services

### 1. API (FastAPI)
- **Container**: `nfl-ai-api`
- **Port**: 8002
- **Purpose**: REST API endpoints
- **Health Check**: http://localhost:8002/health

### 2. Worker (Background Jobs)
- **Container**: `nfl-ai-worker`
- **Purpose**: Data collection, scheduled jobs
- **Runs**: APScheduler for polling data sources

### 3. PostgreSQL
- **Container**: `nfl-ai-postgres`
- **Port**: 5433
- **Database**: nfl_ai
- **User**: nfl_ai_user
- **Data**: Persistent in `postgres_data` volume

### 4. Qdrant (Vector Database)
- **Container**: `nfl-ai-qdrant`
- **Port**: 6334 (HTTP), 6335 (gRPC)
- **Purpose**: Store narrative embeddings
- **Data**: Persistent in `qdrant_storage` volume
- **Dashboard**: http://localhost:6334/dashboard

### 5. Redis (Cache)
- **Container**: `nfl-ai-redis`
- **Port**: 6380
- **Purpose**: Caching, rate limiting
- **Data**: Persistent in `redis_data` volume

### 6. PgAdmin (Development Only)
- **Container**: `nfl-ai-pgadmin`
- **Port**: 5434
- **Login**: admin@nfl-ai.local / admin
- **Purpose**: Database management GUI

---

## Make Commands

```bash
# Setup
make setup           # Initial setup (copy .env)

# Service Management
make up              # Start all services
make dev             # Start in dev mode (includes pgAdmin)
make down            # Stop all services
make restart         # Restart services
make ps              # Show running services
make status          # Check health of all services

# Logs
make logs            # View all logs
make logs-api        # API logs only
make logs-worker     # Worker logs only

# Development
make shell-api       # Open shell in API container
make shell-worker    # Open shell in worker container
make shell-postgres  # Open PostgreSQL shell

# Testing
make test            # Run all tests
make test-unit       # Unit tests only
make test-integration # Integration tests
make test-cov        # Tests with coverage

# Code Quality
make lint            # Lint code
make format          # Format code (Black)

# Database
make migrate         # Run migrations
make migrate-create NAME=migration_name  # Create new migration
make seed            # Seed initial data

# Research Scripts
make research-espn      # Test ESPN API
make research-sleeper   # Test Sleeper API

# Cleanup
make clean           # Stop and remove ALL data (⚠️ WARNING)
```

---

## Development Workflow

### Starting Work
```bash
# Start services
make dev

# Check everything is running
make status

# View API logs
make logs-api
```

### Making Code Changes
- Code changes are automatically hot-reloaded
- Edit files in `src/` directory
- API will restart automatically

### Running Tests
```bash
# Run tests
make test

# Run specific test
docker-compose exec api pytest tests/unit/test_specific.py

# Run with coverage
make test-cov
# Open htmlcov/index.html to view coverage report
```

### Database Access

**Via PgAdmin** (GUI):
1. Open http://localhost:5434
2. Login: admin@nfl-ai.local / admin
3. Add server:
   - Name: NFL AI
   - Host: postgres
   - Port: 5432
   - Username: nfl_ai_user
   - Password: nfl_ai_password

**Via Command Line**:
```bash
make shell-postgres
# Now you're in psql
\dt          # List tables
\d players   # Describe players table
SELECT * FROM players LIMIT 10;
```

### Qdrant Dashboard
- Open http://localhost:6334/dashboard
- View collections
- Search vectors
- Inspect embeddings

---

## Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :8002

# Option 1: Stop that service
# Option 2: Change port in docker-compose.yml
```

### Services Not Starting
```bash
# View logs
make logs

# Check specific service
docker-compose logs postgres

# Rebuild images
make build
make up
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check health
docker-compose exec postgres pg_isready

# View PostgreSQL logs
docker-compose logs postgres
```

### Out of Disk Space
```bash
# Clean up old images
docker system prune

# Remove all volumes (⚠️ deletes data)
make clean
```

### Reset Everything
```bash
# Nuclear option - delete everything
make down
docker system prune -a --volumes
make up
```

---

## Environment Variables

Required in `.env`:

```bash
# AI APIs (REQUIRED)
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Data APIs (Optional - can research without these)
ODDS_API_KEY=your_key_here
TWITTER_API_KEY=your_key_here
WEATHER_API_KEY=your_key_here

# Database (use defaults or customize)
POSTGRES_USER=nfl_ai_user
POSTGRES_PASSWORD=nfl_ai_password
POSTGRES_DB=nfl_ai

# App
APP_ENV=development
LOG_LEVEL=INFO
DEBUG=true
```

---

## Production Deployment

For production, use the production build:

```bash
# Build production images
docker-compose build --build-arg BUILDKIT_INLINE_CACHE=1

# Start with production settings
APP_ENV=production docker-compose up -d

# Scale workers
docker-compose up -d --scale worker=4
```

**Production Checklist**:
- [ ] Set `APP_ENV=production`
- [ ] Set `DEBUG=false`
- [ ] Use strong PostgreSQL password
- [ ] Enable SSL for PostgreSQL
- [ ] Set up monitoring (Sentry, Prometheus)
- [ ] Configure backups for volumes
- [ ] Use secrets management (not .env)
- [ ] Set resource limits in docker-compose

---

## Backups

### Backup PostgreSQL
```bash
docker-compose exec postgres pg_dump -U nfl_ai_user nfl_ai > backup.sql
```

### Restore PostgreSQL
```bash
docker-compose exec -T postgres psql -U nfl_ai_user nfl_ai < backup.sql
```

### Backup Qdrant
```bash
docker-compose exec qdrant tar czf /tmp/qdrant-backup.tar.gz /qdrant/storage
docker cp nfl-ai-qdrant:/tmp/qdrant-backup.tar.gz ./qdrant-backup.tar.gz
```

---

## Next Steps

1. ✅ Services running
2. Start research: `make research-espn`
3. View API docs: http://localhost:8002/docs
4. Check Qdrant: http://localhost:6334/dashboard
