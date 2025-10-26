# NFL RAG+AI System Architecture

> Clean Architecture with Separation of Concerns

## Architectural Principles

1. **Separation of Concerns** - Each module has a single, well-defined responsibility
2. **Dependency Inversion** - High-level modules don't depend on low-level modules
3. **Interface Segregation** - Each data source has its own accessor interface
4. **Testability** - Every component can be tested in isolation
5. **Documentation** - Every module, class, and function is documented
6. **Type Safety** - Full type hints throughout codebase

---

## Layered Architecture

```
┌─────────────────────────────────────────────┐
│          API Layer (FastAPI)                │
│  - REST endpoints                            │
│  - Request validation (Pydantic)            │
│  - Response formatting                       │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│       Business Logic Layer                   │
│  - Prediction Engine                         │
│  - Confidence Scoring                        │
│  - Rule Engine                               │
│  - RAG Orchestrator                          │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│         Service Layer                        │
│  - RAG Engine (Retrieval + Claude)          │
│  - Narrative Generator                       │
│  - Embedding Service                         │
│  - Data Orchestrator                         │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│      Data Access Layer                       │
│  - Data Source Accessors (one per source)   │
│  - Repository Pattern                        │
│  - Database Clients                          │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│       External Systems                       │
│  - ESPN API                                  │
│  - Sleeper API                               │
│  - Claude API                                │
│  - Qdrant Vector DB                          │
│  - PostgreSQL                                │
└─────────────────────────────────────────────┘
```

---

## Directory Structure

```
nfl-ai/
│
├── README.md                           # Project overview
├── MASTER_PLAN.md                      # Complete project plan
├── ARCHITECTURE.md                     # This file
├── CONTRIBUTING.md                     # Contribution guidelines
├── .gitignore
├── .env.example                        # Environment variables template
│
├── docs/                               # 📚 Documentation
│   ├── api/                            # API documentation
│   │   ├── endpoints.md                # REST API reference
│   │   └── examples.md                 # Usage examples
│   ├── architecture/                   # Architecture docs
│   │   ├── layers.md                   # Layer responsibilities
│   │   ├── data_flow.md                # Data flow diagrams
│   │   └── decisions.md                # Architecture decision records
│   ├── sources/                        # Data source documentation
│   │   ├── README.md                   # Overview of all sources
│   │   ├── ESPN_API.md
│   │   ├── SLEEPER_API.md
│   │   └── ...
│   ├── setup/                          # Setup & deployment
│   │   ├── local_development.md
│   │   ├── docker_setup.md
│   │   └── production_deploy.md
│   └── guides/                         # Developer guides
│       ├── adding_data_source.md       # How to add new data source
│       ├── testing.md                  # Testing guidelines
│       └── monitoring.md               # Monitoring setup
│
├── samples/                            # 📊 Sample API responses
│   ├── espn/
│   │   ├── player_stats.json
│   │   ├── injury_report.json
│   │   └── README.md                   # What each sample represents
│   ├── sleeper/
│   ├── odds/
│   └── ...
│
├── src/                                # 💻 Source code
│   ├── __init__.py
│   │
│   ├── api/                            # 🌐 API Layer
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI app
│   │   ├── dependencies.py             # Dependency injection
│   │   ├── middleware.py               # Request/response middleware
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── props.py                # Prop analysis endpoints
│   │   │   ├── players.py              # Player data endpoints
│   │   │   ├── health.py               # Health check endpoints
│   │   │   └── data.py                 # Data status endpoints
│   │   └── models/                     # Pydantic request/response models
│   │       ├── __init__.py
│   │       ├── requests.py             # Request models
│   │       └── responses.py            # Response models
│   │
│   ├── core/                           # ⚙️ Core Business Logic
│   │   ├── __init__.py
│   │   ├── config.py                   # Configuration management
│   │   ├── exceptions.py               # Custom exceptions
│   │   ├── logging.py                  # Logging configuration
│   │   ├── prediction/                 # Prediction engine
│   │   │   ├── __init__.py
│   │   │   ├── engine.py               # Main prediction engine
│   │   │   ├── rule_engine.py          # Rule-based predictions
│   │   │   ├── rag_predictor.py        # RAG+Claude predictions
│   │   │   ├── confidence_scorer.py    # Confidence calculation
│   │   │   └── models.py               # Prediction domain models
│   │   └── analysis/                   # Analysis logic
│   │       ├── __init__.py
│   │       ├── matchup_analyzer.py
│   │       ├── trend_analyzer.py
│   │       └── edge_calculator.py
│   │
│   ├── services/                       # 🔧 Service Layer
│   │   ├── __init__.py
│   │   ├── rag/                        # RAG Engine
│   │   │   ├── __init__.py
│   │   │   ├── retriever.py            # Vector DB retrieval
│   │   │   ├── claude_client.py        # Claude API client
│   │   │   ├── prompt_builder.py       # Prompt construction
│   │   │   ├── response_parser.py      # Claude response parsing
│   │   │   └── templates/              # Prompt templates
│   │   │       ├── base_prompt.txt
│   │   │       ├── prop_analysis.txt
│   │   │       └── ...
│   │   ├── narrative/                  # Narrative Generation
│   │   │   ├── __init__.py
│   │   │   ├── generator.py            # Main narrative generator
│   │   │   ├── templates.py            # Template-based generation
│   │   │   ├── llm_enricher.py         # LLM-powered enrichment
│   │   │   └── embedder.py             # Generate embeddings
│   │   ├── orchestration/              # Data Orchestration
│   │   │   ├── __init__.py
│   │   │   ├── scheduler.py            # APScheduler jobs
│   │   │   ├── coordinator.py          # Coordinate data collection
│   │   │   ├── validator.py            # Data validation
│   │   │   └── merger.py               # Merge data from sources
│   │   └── monitoring/                 # Monitoring Services
│   │       ├── __init__.py
│   │       ├── data_freshness.py       # Track data staleness
│   │       ├── accuracy_tracker.py     # Track prediction accuracy
│   │       ├── cost_monitor.py         # Track API costs
│   │       └── alerting.py             # Alert on issues
│   │
│   ├── data/                           # 💾 Data Access Layer
│   │   ├── __init__.py
│   │   ├── accessors/                  # Data Source Accessors
│   │   │   ├── __init__.py
│   │   │   ├── base.py                 # Base accessor interface
│   │   │   ├── espn/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── accessor.py         # ESPN accessor implementation
│   │   │   │   ├── client.py           # HTTP client
│   │   │   │   ├── parser.py           # Response parsing
│   │   │   │   ├── models.py           # ESPN-specific models
│   │   │   │   └── cache.py            # Caching logic
│   │   │   ├── sleeper/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── accessor.py
│   │   │   │   ├── client.py
│   │   │   │   ├── parser.py
│   │   │   │   └── models.py
│   │   │   ├── odds/
│   │   │   ├── twitter/
│   │   │   ├── weather/
│   │   │   ├── nfl_official/
│   │   │   ├── pff/
│   │   │   ├── nextgen/
│   │   │   └── ...                     # One directory per source
│   │   ├── repositories/               # Repository Pattern
│   │   │   ├── __init__.py
│   │   │   ├── base.py                 # Base repository
│   │   │   ├── player_repository.py
│   │   │   ├── game_repository.py
│   │   │   ├── injury_repository.py
│   │   │   ├── narrative_repository.py
│   │   │   └── prediction_repository.py
│   │   └── clients/                    # Database Clients
│   │       ├── __init__.py
│   │       ├── postgres.py             # PostgreSQL client
│   │       ├── qdrant.py               # Qdrant client
│   │       └── redis.py                # Redis client
│   │
│   ├── models/                         # 📋 Domain Models
│   │   ├── __init__.py
│   │   ├── player.py                   # Player domain model
│   │   ├── game.py                     # Game domain model
│   │   ├── injury.py                   # Injury domain model
│   │   ├── narrative.py                # Narrative domain model
│   │   ├── prop.py                     # Prop domain model
│   │   ├── prediction.py               # Prediction domain model
│   │   └── enums.py                    # Shared enums
│   │
│   └── utils/                          # 🛠️ Utilities
│       ├── __init__.py
│       ├── retry.py                    # Retry logic
│       ├── rate_limit.py               # Rate limiting
│       ├── datetime.py                 # DateTime utilities
│       ├── text.py                     # Text processing
│       └── validators.py               # Validation helpers
│
├── tests/                              # 🧪 Tests
│   ├── __init__.py
│   ├── conftest.py                     # Pytest fixtures
│   ├── unit/                           # Unit tests
│   │   ├── __init__.py
│   │   ├── data/                       # Data layer tests
│   │   │   ├── test_espn_accessor.py
│   │   │   ├── test_sleeper_accessor.py
│   │   │   └── ...
│   │   ├── services/                   # Service layer tests
│   │   │   ├── test_rag_retriever.py
│   │   │   ├── test_claude_client.py
│   │   │   └── ...
│   │   └── core/                       # Core logic tests
│   │       ├── test_prediction_engine.py
│   │       └── ...
│   ├── integration/                    # Integration tests
│   │   ├── __init__.py
│   │   ├── test_data_pipeline.py
│   │   ├── test_rag_engine.py
│   │   └── test_prediction_flow.py
│   ├── e2e/                            # End-to-end tests
│   │   ├── __init__.py
│   │   └── test_prop_analysis.py
│   └── fixtures/                       # Test data fixtures
│       ├── espn_responses.json
│       ├── sleeper_responses.json
│       └── ...
│
├── scripts/                            # 📜 Utility Scripts
│   ├── research/                       # Research scripts
│   │   ├── test_espn_api.py
│   │   ├── test_sleeper_api.py
│   │   └── ...
│   ├── setup/                          # Setup scripts
│   │   ├── init_db.py
│   │   ├── create_indexes.py
│   │   └── seed_data.py
│   └── maintenance/                    # Maintenance scripts
│       ├── backfill_data.py
│       ├── rebuild_embeddings.py
│       └── cleanup_old_data.py
│
├── migrations/                         # 🗄️ Database Migrations
│   └── alembic/                        # Alembic migrations
│
├── docker/                             # 🐳 Docker Configuration
│   ├── Dockerfile.api                  # API service
│   ├── Dockerfile.worker              # Background workers
│   ├── docker-compose.yml
│   └── docker-compose.dev.yml
│
├── .github/                            # GitHub Configuration
│   └── workflows/
│       ├── tests.yml                   # CI/CD tests
│       └── lint.yml                    # Linting
│
├── requirements/                       # 📦 Python Dependencies
│   ├── base.txt                        # Core dependencies
│   ├── dev.txt                         # Development dependencies
│   ├── test.txt                        # Testing dependencies
│   └── prod.txt                        # Production dependencies
│
├── pyproject.toml                      # Python project config
├── setup.py                            # Package setup
└── pytest.ini                          # Pytest configuration
```

---

## Layer Responsibilities

### API Layer
**Responsibility**: Handle HTTP requests and responses
- Input validation
- Authentication/authorization
- Response formatting
- Error handling
- Rate limiting

**Does NOT**:
- Contain business logic
- Access databases directly
- Call external APIs directly

### Business Logic Layer (Core)
**Responsibility**: Implement domain logic and business rules
- Prediction algorithms
- Confidence scoring
- Edge calculation
- Domain models

**Does NOT**:
- Know about HTTP
- Access databases directly
- Know about specific data sources

### Service Layer
**Responsibility**: Orchestrate operations and coordinate between layers
- RAG engine
- Narrative generation
- Data orchestration
- Monitoring

**Does NOT**:
- Contain prediction logic
- Know about HTTP

### Data Access Layer
**Responsibility**: Abstract data sources and provide clean interfaces
- Data source accessors (one per source)
- Repositories (database access)
- Database clients

**Does NOT**:
- Contain business logic
- Know about predictions or RAG

---

## Data Source Accessor Pattern

Each data source gets its own isolated module following a standard interface:

```python
# src/data/accessors/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseDataAccessor(ABC):
    """Base interface for all data source accessors"""

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to data source"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to data source"""
        pass

    @abstractmethod
    async def fetch_player_data(self, player_id: int) -> Dict[str, Any]:
        """Fetch player data"""
        pass

    @abstractmethod
    async def validate_response(self, response: Any) -> bool:
        """Validate API response"""
        pass
```

```python
# src/data/accessors/espn/accessor.py
from ..base import BaseDataAccessor
from .client import ESPNClient
from .parser import ESPNParser
from .models import ESPNPlayerData

class ESPNAccessor(BaseDataAccessor):
    """
    ESPN API Accessor

    Responsible for:
    - Making HTTP requests to ESPN API
    - Parsing ESPN-specific response formats
    - Caching ESPN data
    - Rate limiting ESPN requests
    - Validating ESPN data quality

    NOT responsible for:
    - Business logic
    - Combining data from multiple sources
    - Generating narratives
    """

    def __init__(self):
        self.client = ESPNClient()
        self.parser = ESPNParser()
        self.cache = ESPNCache()

    async def fetch_player_data(self, player_id: int) -> ESPNPlayerData:
        # Implementation
        pass
```

**Benefits**:
- ✅ Easy to test (mock the interface)
- ✅ Easy to swap implementations
- ✅ Clear responsibilities
- ✅ Can add new sources without changing existing code

---

## Testing Strategy

### Unit Tests (Fast, Isolated)
```python
# tests/unit/data/test_espn_accessor.py
import pytest
from src.data.accessors.espn import ESPNAccessor

@pytest.fixture
def mock_espn_client(mocker):
    """Mock HTTP client to avoid real API calls"""
    return mocker.patch('src.data.accessors.espn.client.ESPNClient')

async def test_fetch_player_data(mock_espn_client):
    """Test player data fetching with mocked client"""
    # Arrange
    mock_espn_client.get.return_value = {...}  # Mock response
    accessor = ESPNAccessor()

    # Act
    result = await accessor.fetch_player_data(player_id=123)

    # Assert
    assert result.player_id == 123
    assert result.name == "Tyreek Hill"
    mock_espn_client.get.assert_called_once()
```

### Integration Tests (Real Dependencies)
```python
# tests/integration/test_data_pipeline.py
async def test_espn_to_postgres_flow():
    """Test real ESPN API → PostgreSQL flow"""
    # Use real ESPN API (in test mode)
    # Use real PostgreSQL (test database)
    # Verify data flows correctly
```

### End-to-End Tests (Full System)
```python
# tests/e2e/test_prop_analysis.py
async def test_complete_prop_analysis():
    """Test complete flow from API request to prediction"""
    # Real API call
    # Real data fetching
    # Real RAG retrieval
    # Real Claude API call
    # Verify final prediction
```

---

## Documentation Standards

### Code Documentation
```python
def calculate_confidence(
    our_projection: float,
    market_line: float,
    hit_probability: float,
    historical_accuracy: float
) -> float:
    """
    Calculate confidence score for a prop prediction.

    Args:
        our_projection: Our projected value for the stat (e.g., 95.2 yards)
        market_line: PrizePicks line (e.g., 74.5 yards)
        hit_probability: Probability of hitting OVER (0.0-1.0)
        historical_accuracy: Our historical accuracy on similar props (0.0-1.0)

    Returns:
        Confidence score from 0-100

    Example:
        >>> calculate_confidence(95.2, 74.5, 0.78, 0.68)
        82.5

    Notes:
        - Confidence > 80: High confidence bet
        - Confidence 60-80: Medium confidence
        - Confidence < 60: Low confidence, avoid
    """
    # Implementation
```

### Module Documentation
```python
"""
ESPN Data Accessor

This module provides access to ESPN's NFL API.

Components:
    - ESPNClient: HTTP client for ESPN API
    - ESPNParser: Parses ESPN response formats
    - ESPNAccessor: Main accessor interface
    - ESPNCache: Caches ESPN responses

Usage:
    accessor = ESPNAccessor()
    await accessor.connect()
    player_data = await accessor.fetch_player_data(123)
    await accessor.disconnect()

Rate Limits:
    - 60 requests per minute
    - 1000 requests per day

Data Freshness:
    - Player stats: Updated within 3 minutes during games
    - Injury reports: Updated within 5 minutes of official reports
"""
```

---

## Dependency Management

```toml
# pyproject.toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = "^0.24.0"
sqlalchemy = "^2.0.0"
asyncpg = "^0.29.0"
qdrant-client = "^1.7.0"
anthropic = "^0.8.0"
openai = "^1.3.0"
pydantic = "^2.5.0"
redis = "^5.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-mock = "^3.12.0"
pytest-cov = "^4.1.0"
black = "^23.12.0"
ruff = "^0.1.8"
mypy = "^1.7.0"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

---

## Next Steps

1. ✅ Directory structure created
2. ✅ Architecture documented
3. 🔴 **Next**: Implement first data accessor (ESPN) following this pattern
4. Write comprehensive tests for ESPN accessor
5. Document ESPN accessor completely
6. Repeat for each data source

This architecture ensures:
- **Maintainability**: Easy to understand and modify
- **Testability**: Each component can be tested in isolation
- **Scalability**: Easy to add new data sources and features
- **Quality**: Documentation and tests for everything
