# API Overview

The Rhiz Protocol API provides RESTful endpoints for relationship intelligence operations.

## Base URL

```
http://localhost:8000/api/v1
```

Production: `https://api.rhiz.network/api/v1`

## Authentication

API requests can optionally include an API key:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.rhiz.network/api/v1/graph/find-path
```

## Endpoints

### Graph Operations
- `POST /graph/find-path` - Find trust-weighted path between entities
- `GET /graph/neighbors/{entity_id}` - Get entity's direct connections

### Entity Operations
- `POST /entities/` - Create a new entity
- `GET /entities/{entity_id}` - Get entity details
- `PATCH /entities/{entity_id}` - Update entity
- `DELETE /entities/{entity_id}` - Delete entity

### Analytics Operations
- `GET /analytics/trust-health/{entity_id}` - Trust health metrics
- `GET /analytics/trust-metrics/{entity_id}` - Detailed trust metrics
- `GET /analytics/network-stats` - Network statistics

## Response Format

All API responses follow this format:

**Success Response:**
```json
{
  "data": { ... },
  "status": "success"
}
```

**Error Response:**
```json
{
  "detail": "Error message",
  "status_code": 400
}
```

## Rate Limiting

- **Default**: 100 requests per minute
- **Authenticated**: 1000 requests per minute

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1640000000
```

## SDKs

Use our official SDKs for easier integration:

- [TypeScript SDK](../sdks/typescript)
- [Python SDK](../sdks/python)

## Interactive Documentation

Explore the API interactively at:
```
http://localhost:8000/docs
```

This provides:
- Complete API reference
- Request/response examples
- Try-it-out functionality
- Schema definitions

