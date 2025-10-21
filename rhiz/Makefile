.PHONY: help install dev build test clean docker-up docker-down migrate seed

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install all dependencies
	@echo "📦 Installing dependencies..."
	pnpm install
	cd apps/api && poetry install
	cd packages/sdk-py && poetry install
	@echo "✅ Dependencies installed"

dev: docker-up ## Start development environment
	@echo "🚀 Starting development servers..."
	@echo "API will be at http://localhost:8000"
	@echo "Web will be at http://localhost:3000"
	@echo "Docs will be at http://localhost:3001"
	pnpm dev

build: ## Build all packages and apps
	@echo "🏗️  Building all packages..."
	pnpm build
	cd apps/api && poetry build
	@echo "✅ Build complete"

test: ## Run all tests
	@echo "🧪 Running tests..."
	pnpm test
	cd apps/api && poetry run pytest
	cd packages/sdk-py && poetry run pytest
	@echo "✅ Tests complete"

test-coverage: ## Run tests with coverage
	@echo "🧪 Running tests with coverage..."
	pnpm test -- --coverage
	cd apps/api && poetry run pytest --cov=app --cov-report=html
	@echo "✅ Coverage reports generated"

lint: ## Run linters
	@echo "🔍 Running linters..."
	pnpm lint
	cd apps/api && poetry run ruff check .
	cd apps/api && poetry run black --check .
	@echo "✅ Linting complete"

format: ## Format code
	@echo "✨ Formatting code..."
	pnpm format
	cd apps/api && poetry run ruff check --fix .
	cd apps/api && poetry run black .
	@echo "✅ Formatting complete"

typecheck: ## Run type checking
	@echo "🔎 Type checking..."
	pnpm typecheck
	cd apps/api && poetry run mypy .
	@echo "✅ Type checking complete"

clean: ## Clean build artifacts
	@echo "🧹 Cleaning..."
	pnpm clean
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".turbo" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Clean complete"

docker-up: ## Start Docker services (DB, Redis)
	@echo "🐳 Starting Docker services..."
	docker-compose up -d postgres redis
	@echo "⏳ Waiting for services to be ready..."
	@sleep 5
	@echo "✅ Docker services running"

docker-down: ## Stop Docker services
	@echo "🐳 Stopping Docker services..."
	docker-compose down
	@echo "✅ Docker services stopped"

docker-logs: ## Show Docker logs
	docker-compose logs -f

migrate: ## Run database migrations
	@echo "🔄 Running migrations..."
	cd apps/api && poetry run alembic upgrade head
	@echo "✅ Migrations complete"

migrate-create: ## Create a new migration (use NAME=migration_name)
	@echo "📝 Creating migration: $(NAME)"
	cd apps/api && poetry run alembic revision --autogenerate -m "$(NAME)"

seed: ## Seed database with sample data
	@echo "🌱 Seeding database..."
	cd apps/api && poetry run python scripts/seed_data.py
	@echo "✅ Database seeded"

reset-db: docker-down docker-up migrate seed ## Reset database (WARNING: destroys data)
	@echo "⚠️  Database reset complete"

ci: lint typecheck test ## Run all CI checks
	@echo "✅ All CI checks passed"

deploy-prod: ## Deploy to production (requires auth)
	@echo "🚀 Deploying to production..."
	@echo "⚠️  Not yet implemented - add your deployment commands here"

