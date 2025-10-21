# @rhiz/protocol

Core protocol schemas, types, and validators for Rhiz Protocol.

## Installation

```bash
pnpm add @rhiz/protocol
```

## Usage

### TypeScript Types

```typescript
import { RelationshipRecord, Entity, TrustMetrics } from '@rhiz/protocol';

const relationship: RelationshipRecord = {
  id: 'rel_123',
  participants: ['entity_1', 'entity_2'],
  type: 'professional',
  strength: 0.85,
  context: 'co-founded startup together',
  verification: {
    consensus_score: 0.9,
    verifier_count: 5,
    confidence: 0.92,
    last_verified: new Date().toISOString(),
  },
  privacy: {
    visibility: 'network',
    consent: 'full',
  },
  temporal: {
    start: '2020-01-01T00:00:00Z',
    last_interaction: new Date().toISOString(),
    history: [],
  },
  protocol: {
    contributors: ['entity_1'],
    version: '0.1.0',
    updated: new Date().toISOString(),
  },
};
```

### Validation

```typescript
import { validateRelationship, schemas } from '@rhiz/protocol';

const result = validateRelationship(relationship);
if (result.success) {
  console.log('Valid relationship:', result.data);
} else {
  console.error('Validation errors:', result.errors);
}
```

### JSON Schemas

JSON Schema files are available in the `schemas/` directory for validation in other languages.

```json
{
  "$ref": "@rhiz/protocol/schemas/relationship.json"
}
```

## Types

### Core Types

- `RelationshipRecord` - A verified relationship between two entities
- `Entity` - A person, organization, or agent
- `TrustMetrics` - Trust scoring and reputation data
- `GraphQuery` - Query parameters for path-finding
- `IntroRequest` - Request for a warm introduction

### Enums

- `RelationshipType` - professional | personal | family | social | civic | educational
- `Visibility` - public | network | private
- `ConsentLevel` - full | limited | anonymous

## License

MIT

