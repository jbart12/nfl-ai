# NFL AI - Makefile for common commands

.PHONY: help
help:  ## Show this help message
	@echo "NFL AI - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: setup
setup:  ## Initial setup - copy .env and install dependencies
	@echo "Setting up NFL AI..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env file"; fi
	@echo "Setup complete! Edit .env with your API keys."

.PHONY: up
up:  ## Start all services
	docker-compose up -d
	@echo ""
	@echo "✅ NFL AI services started!"
	@echo ""
	@echo "Services running on:"
	@echo "  - API:        http://localhost:8002"
	@echo "  - PostgreSQL: localhost:5433"
	@echo "  - Qdrant:     http://localhost:6334"
	@echo "  - Redis:      localhost:6380"
	@echo ""
	@echo "View logs: make logs"

.PHONY: dev
dev:  ## Start services in development mode (with pgAdmin)
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo ""
	@echo "✅ NFL AI services started in DEV mode!"
	@echo ""
	@echo "Services running on:"
	@echo "  - API:        http://localhost:8002"
	@echo "  - PostgreSQL: localhost:5433"
	@echo "  - Qdrant:     http://localhost:6334"
	@echo "  - Redis:      localhost:6380"
	@echo "  - PgAdmin:    http://localhost:5434 (admin@nfl-ai.local / admin)"

.PHONY: down
down:  ## Stop all services
	docker-compose down
	@echo "✅ NFL AI services stopped"

.PHONY: restart
restart:  ## Restart all services
	docker-compose restart
	@echo "✅ NFL AI services restarted"

.PHONY: logs
logs:  ## View logs from all services
	docker-compose logs -f

.PHONY: logs-api
logs-api:  ## View API logs
	docker-compose logs -f api

.PHONY: logs-worker
logs-worker:  ## View worker logs
	docker-compose logs -f worker

.PHONY: ps
ps:  ## Show running services
	docker-compose ps

.PHONY: build
build:  ## Rebuild Docker images
	docker-compose build
	@echo "✅ Docker images rebuilt"

.PHONY: clean
clean:  ## Stop services and remove volumes (WARNING: deletes data)
	@echo "⚠️  This will delete all data! Press Ctrl+C to cancel, Enter to continue"
	@read confirm
	docker-compose down -v
	@echo "✅ Services stopped and volumes removed"

.PHONY: shell-api
shell-api:  ## Open shell in API container
	docker-compose exec api /bin/bash

.PHONY: shell-worker
shell-worker:  ## Open shell in worker container
	docker-compose exec worker /bin/bash

.PHONY: shell-postgres
shell-postgres:  ## Open PostgreSQL shell
	docker-compose exec postgres psql -U nfl_ai_user -d nfl_ai

.PHONY: test
test:  ## Run tests
	docker-compose exec api pytest

.PHONY: test-unit
test-unit:  ## Run unit tests only
	docker-compose exec api pytest -m unit

.PHONY: test-integration
test-integration:  ## Run integration tests
	docker-compose exec api pytest -m integration

.PHONY: test-cov
test-cov:  ## Run tests with coverage
	docker-compose exec api pytest --cov=src --cov-report=html

.PHONY: lint
lint:  ## Run linting
	docker-compose exec api black src/ tests/
	docker-compose exec api ruff check src/ tests/

.PHONY: format
format:  ## Format code
	docker-compose exec api black src/ tests/

.PHONY: migrate
migrate:  ## Run database migrations
	docker-compose exec api alembic upgrade head

.PHONY: migrate-create
migrate-create:  ## Create new migration (use NAME=migration_name)
	docker-compose exec api alembic revision --autogenerate -m "$(NAME)"

.PHONY: seed
seed:  ## Seed database with initial data
	docker-compose exec api python scripts/setup/seed_data.py

.PHONY: research-espn
research-espn:  ## Run ESPN API research script
	docker-compose exec api python scripts/research/test_espn_api.py

.PHONY: research-sleeper
research-sleeper:  ## Run Sleeper API research script
	docker-compose exec api python scripts/research/test_sleeper_api.py

.PHONY: status
status:  ## Show service health status
	@echo "Checking service health..."
	@echo ""
	@echo "PostgreSQL:"
	@docker-compose exec postgres pg_isready -U nfl_ai_user || echo "  ❌ Not responding"
	@echo ""
	@echo "Redis:"
	@docker-compose exec redis redis-cli ping || echo "  ❌ Not responding"
	@echo ""
	@echo "Qdrant:"
	@curl -s http://localhost:6334/healthz > /dev/null && echo "  ✅ Healthy" || echo "  ❌ Not responding"
	@echo ""
	@echo "API:"
	@curl -s http://localhost:8002/health > /dev/null && echo "  ✅ Healthy" || echo "  ❌ Not responding"

.PHONY: ports
ports:  ## Show all used ports
	@echo "NFL AI Port Assignments:"
	@echo "  8002  - FastAPI API"
	@echo "  5433  - PostgreSQL"
	@echo "  6334  - Qdrant HTTP"
	@echo "  6335  - Qdrant gRPC"
	@echo "  6380  - Redis"
	@echo "  5434  - PgAdmin (dev only)"
