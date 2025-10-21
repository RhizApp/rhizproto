# Installation

This guide will help you set up Rhiz Protocol for local development.

## Prerequisites

Make sure you have the following installed:

- **Node.js** 20+ ([Download](https://nodejs.org/))
- **Python** 3.11+ ([Download](https://www.python.org/))
- **Docker** ([Download](https://www.docker.com/))
- **pnpm** 8+ (`npm install -g pnpm`)
- **Poetry** ([Install](https://python-poetry.org/docs/#installation))

## Clone Repository

```bash
git clone https://github.com/rhiz/rhiz.git
cd rhiz
```

## Install Dependencies

### JavaScript/TypeScript Dependencies

```bash
pnpm install
```

This will install dependencies for:
- Protocol package (@rhiz/protocol)
- TypeScript SDK (@rhiz/sdk)
- Frontend (Next.js app)
- AT Protocol services
- Documentation site

### Python Dependencies

```bash
# API backend
cd apps/api
poetry install

# Python SDK
cd ../../packages/sdk-py
poetry install
```

## Start Infrastructure

Start PostgreSQL and Redis using Docker Compose:

```bash
make docker-up
```

This will start:
- **PostgreSQL 16** with pgvector extension on port 5432
- **Redis 7** on port 6379

## Database Setup

Run migrations to create database tables:

```bash
cd apps/api
poetry run alembic upgrade head
```

Optionally, seed with demo data:

```bash
make seed
```

## Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your configuration. Key variables:

```env
# Database
DATABASE_URL=postgresql://rhiz:rhiz@localhost:5432/rhiz

# Redis
REDIS_URL=redis://localhost:6379/0

# API
API_SECRET_KEY=your-secret-key-here

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Verify Installation

Run the test suite to verify everything is set up correctly:

```bash
make test
```

## Next Steps

- [Quickstart Guide](quickstart) - Build your first integration
- [Local Development](../guides/local-development) - Development workflow
- [API Reference](../api/overview) - Explore the API

