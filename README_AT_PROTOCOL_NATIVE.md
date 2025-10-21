# Rhiz Protocol - AT Protocol Native Implementation

> The Relationship Layer of the Internet

**Status**: ✅ AT Protocol Native | 🚀 Federation-Ready | 🔒 User-Owned Data

---

## Overview

Rhiz Protocol is a **truly AT Protocol-native** relationship intelligence system that enables trust-weighted social graphs, warm introductions, and multi-agent coordination. Built on AT Protocol primitives from the ground up, Rhiz provides the missing relationship layer for decentralized social networks.

### Key Differentiator

Rhiz is not just "using AT Protocol" — **Rhiz IS AT Protocol native**:
- ✅ DIDs as primary identifiers
- ✅ Relationship records stored in user repos
- ✅ Content-addressed with AT URIs + CIDs
- ✅ Firehose indexer for real-time updates
- ✅ Federation-ready architecture
- ✅ User data ownership

---

## What is Rhiz Protocol?

Rhiz Protocol establishes a universal schema for representing, verifying, and measuring trust between people, organizations, and agents. It's built entirely on AT Protocol infrastructure.

### Core Capabilities

1. **Trust-Weighted Graphs** - Find paths between entities weighted by verified relationship strength
2. **Warm Introductions** - AI agents facilitate introductions through trusted intermediaries
3. **Relationship Intelligence** - Quantified trust metrics with transparency
4. **Federation** - Multiple services can index and serve the same relationship data
5. **User Ownership** - Relationships stored in user's AT Protocol repos

---

## Architecture

### AT Protocol Native Stack

```
┌─────────────────────────────────────────────────────────────┐
│                     User AT Protocol Repos                   │
│  at://did:plc:alice/net.rhiz.relationship.record/{tid}     │
│  SOURCE OF TRUTH - User owns data                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   AT Protocol Firehose                       │
│  Broadcasts all repo commits                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Rhiz AppView (Indexer)                          │
│  Subscribes to net.rhiz.* records                           │
│  Indexes into PostgreSQL for fast queries                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                Query API (PostgreSQL)                        │
│  Fast graph traversal, trust metrics, analytics            │
│  QUERY INDEX - Not source of truth                         │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

- **Lexicon Schemas** (`lexicons/net/rhiz/`) - Protocol definitions
- **Identity Resolution** - DID/handle resolution via AT Protocol
- **Repo Writer** - Creates records in user repos
- **Firehose Indexer** - Subscribes to relationship records
- **Graph API** - Path-finding and network analysis
- **Trust Engine** - Calculates trust metrics
- **Agent Coordination** - Multi-agent negotiation system

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/rhiz/rhizproto.git
cd rhizproto

# Install dependencies
pnpm install

# Generate types from lexicons
cd packages/rhiz-protocol
pnpm run codegen

# Build all packages
cd ../..
pnpm build

# Run database migration
cd services/rhiz-api
alembic upgrade head

# Start services
docker-compose up -d
```

### Usage Example

```typescript
import { RhizClient } from '@atproto/rhiz-sdk';

// Initialize client with AT Protocol support
const client = new RhizClient({
  apiUrl: 'https://api.rhiz.network',
  atproto: {
    service: 'https://bsky.social',
  },
});

// Login with AT Protocol credentials
await client.login('alice.bsky.social', 'app-password');

// Create entity profile (stored in your AT Protocol repo)
const alice = await client.entities.create({
  did: 'did:plc:abc123def456',
  name: 'Alice Chen',
  type: 'person',
  bio: 'Founder @ TechCo',
});

// Create relationship (stored in your repo, indexed by firehose)
const relationship = await client.repo.createRelationship(
  'did:plc:alice123',
  {
    participants: ['did:plc:alice123', 'did:plc:bob456'],
    type: 'professional',
    strength: 0.85,
    context: 'Co-founded startup together',
    verification: {
      consensusScore: 0.9,
      verifierCount: 5,
      confidence: 0.95,
      lastVerified: new Date().toISOString(),
    },
    privacy: { visibility: 'network', consent: 'limited' },
    temporal: {
      start: '2020-01-15T00:00:00Z',
      lastInteraction: new Date().toISOString(),
    },
    createdAt: new Date().toISOString(),
  }
);

console.log(relationship.uri);
// at://did:plc:alice123/net.rhiz.relationship.record/3jx7ytmdwej2k

// Find path between entities
const paths = await client.graph.findPath({
  from: 'did:plc:alice',
  to: 'did:plc:investor',
  maxHops: 6,
  minStrength: 0.5,
});
```

---

## Package Structure

### TypeScript Packages

| Package | Description | Status |
|---------|-------------|--------|
| `@atproto/rhiz-protocol` | Core protocol schemas, types, and AT Protocol integration | ✅ Complete |
| `@atproto/rhiz-sdk` | TypeScript SDK with AT Protocol repo support | ✅ Complete |

### Services

| Service | Description | Status |
|---------|-------------|--------|
| `rhiz-api` | FastAPI backend with DID-native endpoints | ✅ Complete |
| `rhiz-atproto` | Firehose indexer and AT Protocol services | ✅ Complete |
| `fundrhiz` | Flagship app for founder-investor introductions | 🔄 Updating |

### Lexicons

All protocol schemas are defined as proper Lexicon JSON files:

```
lexicons/net/rhiz/
├── entity/         # Entity profiles
├── relationship/   # Relationship records
├── trust/          # Trust metrics
├── intro/          # Introduction requests
└── graph/          # Graph query APIs
```

---

## Features

### 1. DID-Native Identity

All entities are identified by AT Protocol DIDs:

```typescript
// Every entity has a cryptographically verifiable DID
did: "did:plc:abc123def456"

// Handles are optional, human-readable aliases
handle: "alice.bsky.social"
```

### 2. Content-Addressed Relationships

Relationships are stored in user repos and referenced by AT URIs:

```typescript
// AT URI for the relationship record
at://did:plc:alice/net.rhiz.relationship.record/3jx7ytmdwej2k

// CID for content verification
cid: "bafyreihg5xqf2..."
```

### 3. Trust-Weighted Pathfinding

Find the strongest path between any two entities:

```typescript
const path = await client.graph.findPath({
  from: 'did:plc:founder',
  to: 'did:plc:investor',
  maxHops: 6,
  minStrength: 0.5,
});

// Returns path with:
// - Sequence of hops through trusted intermediaries
// - AT URIs for each relationship (verifiable in repos)
// - Total strength (weighted product)
// - Distance in hops
```

### 4. Cryptographic Signatures

All relationships must be signed by both participants:

```typescript
signatures: [
  {
    did: "did:plc:alice",
    signature: "base64_signature_from_alice"
  },
  {
    did: "did:plc:bob",
    signature: "base64_signature_from_bob"
  }
]
```

### 5. Federation-Ready

Multiple services can index and serve the same Rhiz data:

```
User Repo → Firehose → [AppView 1, AppView 2, AppView 3]
                       ↓          ↓          ↓
                    Service A  Service B  Service C
```

Each service independently indexes firehose events and serves queries. Users choose which service to use, but their data remains portable.

---

## API Endpoints

### Entities (DID-Native)

- `POST /api/v1/entities/` - Create entity with DID
- `GET /api/v1/entities/{did:path}` - Get entity by DID
- `GET /api/v1/entities/by-handle/{handle}` - Resolve handle to entity
- `PATCH /api/v1/entities/{did:path}` - Update entity
- `DELETE /api/v1/entities/{did:path}` - Delete entity

### Graph (AT URI References)

- `POST /api/v1/graph/find-path` - Find path between DIDs
- `GET /api/v1/graph/neighbors/{did:path}` - Get direct neighbors

### Analytics

- `GET /api/v1/analytics/trust-health` - Network trust health metrics
- `GET /api/v1/analytics/network-stats` - Network statistics

---

## Development

### Prerequisites

- Node.js 18+
- pnpm
- Docker & Docker Compose
- PostgreSQL 14+
- Redis

### Setup

```bash
# Install dependencies
pnpm install

# Generate types from lexicons
pnpm run codegen

# Build packages
pnpm build

# Start database & Redis
docker-compose up -d postgres redis

# Run migrations
cd services/rhiz-api
alembic upgrade head

# Start API server
uvicorn app.main:app --reload

# In another terminal, start firehose indexer
cd services/rhiz-atproto
pnpm run ingest
```

### Testing

```bash
# Run all tests
pnpm test

# Test specific package
cd packages/rhiz-protocol
pnpm test

# Run Python tests
cd services/rhiz-api
pytest
```

---

## Interoperability

Rhiz Protocol includes interop test files for validation:

```
interop-test-files/rhiz/
├── relationship-record-valid.json
├── entity-profile-valid.json
├── trust-metrics-valid.json
└── intro-request-valid.json
```

These ensure Rhiz records conform to AT Protocol standards and can be consumed by other implementations.

---

## Documentation

- **[AT Protocol Native Migration](AT_PROTOCOL_NATIVE_MIGRATION.md)** - Full migration guide
- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)** - Technical details
- **[Implementation Complete](IMPLEMENTATION_COMPLETE.md)** - Completion report
- **[Lexicon Schemas](lexicons/net/rhiz/)** - Protocol definitions
- **[Interop Tests](interop-test-files/rhiz/)** - Reference implementations

---

## Roadmap

### Phase 1: Foundation ✅ COMPLETE
- Lexicon schema definitions
- DID-native identity
- Content-addressed records
- Firehose indexer
- Database migration

### Phase 2: Intelligence Layer 🔄 NEXT
- Vector embeddings for semantic search
- Temporal trust dynamics
- Multi-hop trust propagation
- Machine learning for trust prediction

### Phase 3: Agent Layer
- Agent-to-agent negotiation protocols
- Emergent behavior patterns
- Coalition formation
- Autonomous introduction facilitation

### Phase 4: Scale & Federation
- Multi-region AppViews
- Performance optimizations
- Full data portability tools
- Cross-protocol bridges

---

## Contributing

We welcome contributions! Please see our contribution guidelines:

1. Open an issue for discussion
2. Fork the repository
3. Create a feature branch
4. Implement changes
5. Add tests
6. Submit pull request

**Important**: All relationship data must be stored in AT Protocol repos, not directly in the database. The database is only for query optimization.

---

## License

Dual-licensed under MIT and Apache 2.0:

- MIT license ([LICENSE-MIT.txt](LICENSE-MIT.txt))
- Apache License 2.0 ([LICENSE-APACHE.txt](LICENSE-APACHE.txt))

Software patent non-aggression pledge applies.

---

## Community

- **Website**: https://rhiz.network
- **Discord**: https://discord.gg/rhiz
- **Twitter**: @rhizprotocol
- **GitHub**: https://github.com/rhiz/rhizproto

---

## Acknowledgments

Built on [AT Protocol](https://atproto.com) by Bluesky Social PBC.

Rhiz Protocol extends AT Protocol with relationship intelligence primitives while maintaining full compatibility with the AT Protocol ecosystem.

---

**Rhiz Protocol** - The Relationship Layer of the Internet

*AT Protocol Native | Federation-Ready | User-Owned Data*

