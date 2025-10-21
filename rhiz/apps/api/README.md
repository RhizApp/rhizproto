# Rhiz API

FastAPI backend for Rhiz Protocol - the relationship intelligence layer.

## Features

- **Graph API**: Find trust-weighted paths between entities
- **Agent Coordination**: Multi-agent task routing and negotiation
- **Forums**: Collaborative discussion and due diligence
- **Enrichment**: Automatic contact and relationship data enhancement
- **Analytics**: Trust health metrics and network analysis
- **AT Protocol**: DID mapping and Firehose integration

## Quick Start

```bash
# Install dependencies
poetry install

# Set up database
docker-compose up -d postgres redis
poetry run alembic upgrade head

# Run development server
poetry run uvicorn app.main:app --reload

# API docs at http://localhost:8000/docs
```

## Architecture

```
app/
├── main.py                 # FastAPI application
├── config.py               # Configuration and settings
├── database.py             # Database setup and session
├── models/                 # SQLAlchemy models
├── schemas/                # Pydantic schemas
├── api/                    # API routes
│   ├── graph.py
│   ├── agent.py
│   ├── forum.py
│   ├── enrichment.py
│   └── analytics.py
├── services/               # Business logic
│   ├── trust_engine.py
│   ├── pathfinder.py
│   └── agent_coordinator.py
└── tests/                  # Test suite
```

## Environment Variables

See `.env.example` in project root.

Required:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `API_SECRET_KEY`: JWT secret key

Optional:
- `OPENAI_API_KEY`: For agent coordination
- `ATPROTO_DID`: AT Protocol identity
- `LOG_LEVEL`: Logging level (default: info)

## Testing

```bash
# Run all tests
poetry run pytest

# With coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_graph.py
```

## API Endpoints

### Graph
- `POST /api/v1/graph/find-path` - Find trust-weighted path between entities
- `GET /api/v1/graph/neighbors` - Get entity's direct connections

### Agent
- `POST /api/v1/agent/coordinate` - Coordinate multi-agent tasks
- `GET /api/v1/agent/status/{task_id}` - Check task status

### Forum
- `POST /api/v1/forum/create` - Create discussion forum
- `GET /api/v1/forum/{forum_id}` - Get forum details
- `POST /api/v1/forum/{forum_id}/message` - Post message

### Enrichment
- `POST /api/v1/enrichment/contact` - Enrich contact data
- `POST /api/v1/enrichment/relationship` - Enrich relationship data

### Analytics
- `GET /api/v1/analytics/trust-health/{entity_id}` - Trust health metrics
- `GET /api/v1/analytics/network-stats` - Network statistics

## Development

```bash
# Format code
poetry run black .
poetry run ruff check --fix .

# Type checking
poetry run mypy .

# Create migration
poetry run alembic revision --autogenerate -m "description"

# Run migration
poetry run alembic upgrade head
```

## License

MIT

