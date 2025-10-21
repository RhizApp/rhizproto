# Quickstart

Get up and running with Rhiz Protocol in 10 minutes.

## 1. Start Services

```bash
# Start database and Redis
make docker-up

# In separate terminals:
# Terminal 1: API
cd apps/api
poetry run uvicorn app.main:app --reload

# Terminal 2: Frontend
cd apps/web
pnpm dev

# Terminal 3: Docs
cd apps/docs
pnpm start
```

## 2. Create Your First Entity

Using the API directly:

```bash
curl -X POST http://localhost:8000/api/v1/entities/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": "founder_alice",
    "type": "person",
    "name": "Alice",
    "bio": "Founder of StartupX"
  }'
```

Or using the TypeScript SDK:

```typescript
import { RhizClient } from '@rhiz/sdk';

const client = new RhizClient({
  apiUrl: 'http://localhost:8000',
});

const alice = await client.entities.create({
  id: 'founder_alice',
  type: 'person',
  name: 'Alice',
  bio: 'Founder of StartupX',
});
```

## 3. Create a Relationship

Create a second entity and establish a relationship through the database:

```typescript
const bob = await client.entities.create({
  id: 'investor_bob',
  type: 'person',
  name: 'Bob',
  bio: 'Angel Investor',
});

// Relationship creation endpoint coming soon
// For now, use direct database access
```

## 4. Find a Path

Once you have a graph, find paths between entities:

```typescript
const path = await client.graph.findPath({
  from: 'founder_alice',
  to: 'investor_bob',
  max_hops: 6,
  min_strength: 0.5,
});

console.log(`Path found with ${path.distance} hops`);
console.log(`Total strength: ${path.total_strength}`);
```

## 5. Get Trust Metrics

Analyze trust metrics for an entity:

```typescript
const health = await client.analytics.getTrustHealth('founder_alice');

console.log(`Trust Level: ${health.trust_level}`);
console.log(`Trust Score: ${health.trust_score}`);
console.log(`Network Size: ${health.network_size}`);
```

## 6. Explore the UI

Visit the web app to explore visually:

```bash
open http://localhost:3000
```

Features:
- Dashboard with trust metrics
- Network visualization
- Introduction requests
- Relationship management

## Next Steps

- [Protocol Specification](../protocol/overview)
- [API Reference](../api/overview)
- [Local Development Guide](../guides/local-development)

## Common Issues

### Database Connection Error
Make sure PostgreSQL is running:
```bash
docker ps | grep rhiz-postgres
```

### Port Already in Use
Change ports in configuration:
- API: `API_PORT` in `.env`
- Frontend: `PORT` in `apps/web/.env.local`

### Module Not Found
Rebuild protocol package:
```bash
cd packages/protocol
pnpm build
```

