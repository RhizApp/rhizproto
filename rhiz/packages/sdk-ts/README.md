# @rhiz/sdk

Official TypeScript SDK for Rhiz Protocol API.

## Installation

```bash
npm install @rhiz/sdk
# or
pnpm add @rhiz/sdk
```

## Quick Start

```typescript
import { RhizClient } from '@rhiz/sdk';

// Initialize client
const client = new RhizClient({
  apiUrl: 'http://localhost:8000',
  apiKey: 'your-api-key', // optional
});

// Find path between entities
const path = await client.graph.findPath({
  from: 'entity_1',
  to: 'entity_2',
  max_hops: 6,
  min_strength: 0.5,
});

// Get entity neighbors
const neighbors = await client.graph.getNeighbors('entity_1');

// Get trust metrics
const metrics = await client.analytics.getTrustMetrics('entity_1');
```

## API Reference

### Graph Operations

```typescript
// Find shortest path
const path = await client.graph.findPath({
  from: 'entity_1',
  to: 'entity_2',
  max_hops: 6,
  min_strength: 0.5,
  relationship_types: ['professional'],
  exclude_entities: ['entity_3'],
});

// Get neighbors
const neighbors = await client.graph.getNeighbors('entity_1', {
  min_strength: 0.7,
});
```

### Entity Operations

```typescript
// Create entity
const entity = await client.entities.create({
  id: 'entity_1',
  type: 'person',
  name: 'Alice',
  bio: 'Founder at StartupX',
});

// Get entity
const entity = await client.entities.get('entity_1');

// Update entity
const updated = await client.entities.update('entity_1', {
  name: 'Alice Smith',
  bio: 'CEO at StartupX',
});
```

### Analytics Operations

```typescript
// Get trust health
const health = await client.analytics.getTrustHealth('entity_1');

// Get trust metrics
const metrics = await client.analytics.getTrustMetrics('entity_1');

// Get network stats
const stats = await client.analytics.getNetworkStats();
```

## Configuration

```typescript
const client = new RhizClient({
  apiUrl: 'https://api.rhiz.network', // API base URL
  apiKey: 'your-api-key', // Optional API key
  timeout: 30000, // Request timeout in ms
  retries: 3, // Number of retries on failure
});
```

## Error Handling

```typescript
try {
  const path = await client.graph.findPath({
    from: 'entity_1',
    to: 'entity_2',
  });
} catch (error) {
  if (error instanceof RhizError) {
    console.error(`Rhiz API Error: ${error.message}`);
    console.error(`Status: ${error.statusCode}`);
  }
}
```

## TypeScript Support

Full TypeScript support with type definitions for all API operations.

```typescript
import type {
  GraphPath,
  Entity,
  TrustMetrics,
  GraphQueryRequest,
} from '@rhiz/sdk';
```

## License

MIT

