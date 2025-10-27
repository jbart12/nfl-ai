# NFL AI Prediction System

AI-powered NFL prop prediction system using **Claude 3.5 Sonnet** + **RAG (Retrieval-Augmented Generation)** for intelligent, context-aware predictions.

## Overview

This system makes NFL prop predictions (over/under on player stats) by combining:

1. **Structured Data** (PostgreSQL) - Player stats, games, injuries, matchups
2. **Semantic Search** (Qdrant Vector DB) - Find similar historical game situations
3. **AI Reasoning** (Claude 3.5 Sonnet) - Analyze all context and make predictions with detailed reasoning

### Key Features

- **RAG-Powered Context**: Searches for similar historical performances before making predictions
- **Comprehensive Analysis**: Considers current form, matchup difficulty, injuries, weather, and more
- **Transparent Reasoning**: Every prediction includes detailed reasoning and confidence scores
- **Real-time Data**: Fetches live props from PrizePicks, player stats from ESPN
- **Historical Tracking**: Stores predictions and outcomes for accuracy analysis

## Architecture

```
┌─────────────────┐
│  PrizePicks API │──► Props (Over/Under Lines)
└─────────────────┘

┌─────────────────┐
│    ESPN API     │──► Player Stats, Game Logs
└─────────────────┘

         │
         ▼
┌─────────────────┐
│   PostgreSQL    │──► Structured Data (Players, Games, Stats)
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ RAG Narrative   │──► Generate Rich Game Narratives
│    Service      │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  OpenAI Embed   │──► Convert to 3072-dim Vectors
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Qdrant Vector  │──► Store & Search Semantic Similarity
│   Database      │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   Prediction    │──► Orchestrate Full Flow:
│    Endpoint     │     1. Get prop + current stats
└─────────────────┘     2. RAG search for similar games
         │              3. Gather matchup context
         ▼              4. Send to Claude
┌─────────────────┐
│  Claude 3.5     │──► AI Analysis with Reasoning
│    Sonnet       │
└─────────────────┘
         │
         ▼
    Prediction
  (OVER/UNDER +
   Reasoning +
   Confidence)
```

## Tech Stack

### Backend
- **FastAPI** - Async Python web framework
- **PostgreSQL** - Structured data storage
- **Qdrant** - Vector database for RAG
- **Redis** - Caching layer
- **SQLAlchemy 2.0** - Async ORM
- **Alembic** - Database migrations

### AI/ML
- **Claude 3.5 Sonnet** - Prediction generation with reasoning
- **OpenAI text-embedding-3-large** - 3072-dimension embeddings
- **Qdrant** - Vector similarity search

### Infrastructure
- **Docker Compose** - Container orchestration
- **Uvicorn** - ASGI server
- **Structlog** - Structured logging

## Project Structure

```
nfl-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   └── predictions.py    # Prediction endpoint
│   │   │   └── router.py              # API router
│   │   ├── core/
│   │   │   ├── config.py              # Configuration
│   │   │   └── database.py            # Database connection
│   │   ├── models/
│   │   │   └── nfl.py                 # Database models
│   │   ├── services/
│   │   │   ├── claude_prediction.py   # Claude AI service
│   │   │   ├── embeddings.py          # OpenAI embeddings
│   │   │   ├── vector_store.py        # Qdrant vector DB
│   │   │   ├── rag_narrative.py       # Narrative generation
│   │   │   └── espn_game_stats.py     # ESPN data fetching
│   │   └── main.py                    # FastAPI application
│   ├── alembic/
│   │   ├── versions/                  # Database migrations
│   │   └── env.py                     # Alembic config
│   └── scripts/
│       ├── seed_teams.py              # Seed NFL teams
│       ├── backfill_player_stats.py   # Backfill historical stats
│       └── db_utils.py                # Database utilities
├── requirements/
│   ├── base.txt                       # Core dependencies
│   └── dev.txt                        # Development dependencies
├── docker-compose.yml                 # Docker services
├── .env                               # Environment variables
└── README.md                          # This file
```

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- API Keys:
  - Anthropic API key (for Claude)
  - OpenAI API key (for embeddings)

### 1. Clone and Setup

```bash
cd nfl-ai
cp .env.example .env
# Edit .env and add your API keys
```

### 2. Start Infrastructure

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

Services will be available at:
- **API**: http://localhost:8002
- **API Docs**: http://localhost:8002/docs
- **PostgreSQL**: localhost:5433
- **Qdrant**: http://localhost:6334
- **Redis**: localhost:6380

### 3. Run Database Migrations

```bash
cd backend
alembic upgrade head
```

### 4. Seed Initial Data

```bash
# Seed NFL teams (all 32 teams)
python -m scripts.seed_teams

# Backfill player stats from ESPN
python -m scripts.backfill_player_stats --season 2024 --active-only
```

### 5. Test the API

```bash
# Check health
curl http://localhost:8002/health

# Make a prediction
curl -X POST http://localhost:8002/api/v1/predictions/predict \
  -H "Content-Type: application/json" \
  -d '{
    "player_name": "Patrick Mahomes",
    "stat_type": "passing_yards",
    "line_score": 275.5,
    "opponent": "BUF"
  }'
```

## Database Schema

### Core Tables

#### Players
- Unified player database across platforms
- Links to ESPN, Sleeper, PrizePicks

#### Player Game Stats
- Game-by-game historical statistics
- **Critical for RAG** - used to find similar situations

#### Games
- NFL games with scores, weather, Vegas lines

#### PrizePicks Projections
- Current props available for betting

#### Predictions
- AI-generated predictions with reasoning
- Tracks accuracy over time

## AI Prediction Flow

1. **Receive Request** - Player name, stat type, line score, opponent

2. **Gather Structured Data**:
   - Current season stats
   - Recent game performance (last 5 games)
   - Matchup context (opponent defense rank, Vegas lines, weather)
   - Injury status

3. **RAG Search**:
   - Generate query embedding: "Looking for {player} {stat_type} performances in similar situations"
   - Search Qdrant for top 10 most similar historical games
   - Return game narratives with similarity scores

4. **Send to Claude**:
   - Comprehensive prompt with all context
   - Request: prediction (OVER/UNDER), confidence (0-100), reasoning

5. **Return Prediction**:
   ```json
   {
     "prediction": "OVER",
     "confidence": 72,
     "projected_value": 285.3,
     "reasoning": "Mahomes averages 290 yards in last 3 vs BUF...",
     "key_factors": ["Strong recent form", "Favorable matchup"],
     "similar_situations_count": 8
   }
   ```

## Scripts & Utilities

### Database Utilities

```bash
# Check database status
python -m scripts.db_utils status

# Count all records
python -m scripts.db_utils count

# Show sample data
python -m scripts.db_utils sample

# Clear all data (WARNING: destructive!)
python -m scripts.db_utils clear --confirm
```

### Data Backfill

```bash
# Backfill all players for 2024
python -m scripts.backfill_player_stats --season 2024

# Backfill specific player
python -m scripts.backfill_player_stats --season 2024 --player-id "123456"

# Backfill multiple seasons
python -m scripts.backfill_player_stats --seasons 2023 2024 2025

# Active players only
python -m scripts.backfill_player_stats --season 2024 --active-only
```

### Seed Teams

```bash
# Seed all 32 NFL teams
python -m scripts.seed_teams
```

## Configuration

All configuration is done via environment variables in `.env`:

```bash
# Database
POSTGRES_USER=nfl_user
POSTGRES_PASSWORD=nfl_password
POSTGRES_DB=nfl_analytics
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# AI APIs
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...

# Vector DB
QDRANT_URL=http://qdrant:6333

# Redis
REDIS_URL=redis://redis:6379/0
```

## API Endpoints

### Health Check
```
GET /health
```

### Predictions
```
POST /api/v1/predictions/predict
```

**Request Body:**
```json
{
  "player_name": "Patrick Mahomes",
  "stat_type": "passing_yards",
  "line_score": 275.5,
  "opponent": "BUF"
}
```

**Response:**
```json
{
  "prediction": "OVER",
  "confidence": 72,
  "projected_value": 285.3,
  "reasoning": "Detailed AI analysis...",
  "key_factors": ["Strong recent form", "Favorable matchup"],
  "risk_factors": ["Away game", "Cold weather"],
  "similar_situations_count": 8,
  "comparable_game": "Week 11, 2024 vs KC: 298 yards",
  "model": "claude-3-5-sonnet-20241022",
  "generated_at": "2025-10-26T12:00:00Z"
}
```

## Cost Estimates

### Per Prediction
- **Claude API**: ~$0.01-0.02 (input + output tokens)
- **OpenAI Embeddings**: ~$0.0001 (query embedding)
- **Total**: ~$0.01-0.02 per prediction

### Monthly (100 predictions/day)
- **Claude**: ~$30-60/month
- **OpenAI**: ~$0.30/month
- **Infrastructure**: ~$20-40/month (if using cloud hosting)
- **Total**: **~$50-100/month**

## Development

### Running Locally

```bash
# Install dependencies
cd backend
pip install -r requirements/dev.txt

# Run locally (without Docker)
uvicorn app.main:app --reload --port 8002

# Run tests
pytest

# Format code
black .
ruff check .
```

### Adding New Features

1. Create feature branch
2. Add models to `app/models/nfl.py`
3. Create migration: `alembic revision --autogenerate -m "description"`
4. Add business logic to `app/services/`
5. Add API endpoints to `app/api/endpoints/`
6. Update router in `app/api/router.py`
7. Write tests
8. Submit PR

## Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Restart service
docker-compose restart postgres
```

### Qdrant Connection Issues
```bash
# Check Qdrant status
curl http://localhost:6334/collections

# View logs
docker-compose logs qdrant
```

### API Errors
```bash
# View API logs
docker-compose logs api

# Check health endpoint
curl http://localhost:8002/health
```

## Next Steps

1. **Load Historical Data**: Run backfill scripts to populate player_game_stats
2. **Generate Narratives**: Create embeddings for all historical games
3. **Test Predictions**: Make test predictions and verify RAG is working
4. **Track Accuracy**: Monitor prediction accuracy over time
5. **Optimize**: Fine-tune prompts and RAG search parameters

## Important Notes

- **Duplicate Migration File**: Remove `backend/alembic/versions/001_initial_schema.py` (keep only `001_create_core_schema.py`)
- **Docker Path Update**: Docker configuration has been updated to use `backend/` instead of `src/`
- **Structlog Added**: Added structlog to requirements (was missing)

## License

MIT

## Support

For issues and questions, see documentation in `/docs` directory.
