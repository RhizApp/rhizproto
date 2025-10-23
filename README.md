# Rhiz Protocol - The Relationship Layer of the Web

**The Relationship Protocol for the Internet**

**Protocol Standard | AT Protocol Native | User-Owned Data**

Rhiz Protocol is a decentralized protocol for creating, verifying, and querying machine-readable relationships. Relationships are first-class data structures with quantified trust, temporal dynamics, and network verification.

> **What is Rhiz?** A protocol specification for verifiable relationships and trust, with a production-ready implementation on AT Protocol. Think OAuth for relationships, not just another social network.

## 🎯 What is Rhiz Protocol?

Rhiz Protocol defines standard primitives for relationships, attestations, and trust - enabling any application to build on verifiable relationship data.

### Core Primitives

1. **Entity** - Any person, organization, or agent (identified by DID)
2. **Relationship** - Quantified connection between entities (strength 0-100)
3. **Attestation** - Third-party validation of relationships
4. **Trust Metrics** - Calculated scores based on network consensus

### Key Innovations

- ✅ **Relationships as First-Class Data** - Not just graph edges, but rich data structures
- ✅ **Network Verification** - Attestations create conviction scores (0-100)
- ✅ **Trust Quantification** - Transparent algorithms, reproducible results
- ✅ **Cryptographic Verification** - All relationships require signatures from participants
- ✅ **User Ownership** - Data lives in user repositories, not centralized databases
- ✅ **Federation-Ready** - Multiple services can index the same relationship data

---

## 📦 Repository Contents

### Protocol Specification

- **[Protocol Specification](PROTOCOL_SPECIFICATION.md)** - Complete formal specification (chain-agnostic)
- **[AT Protocol Implementation Guide](AT_PROTOCOL_IMPLEMENTATION_GUIDE.md)** - Reference implementation on AT Protocol
- **[Protocol Roadmap](RHIZ_PROTOCOL_ROADMAP.md)** - 3-year development plan

### AT Protocol Implementation (Reference)

| Package | Description | Status |
|---------|-------------|--------|
| `@atproto/rhiz-protocol` | Core protocol: Lexicons, types, identity, signing, repo operations | ✅ Production |
| `@atproto/rhiz-sdk` | TypeScript SDK with DID-based operations and AT Protocol support | ✅ Production |
| `@atproto/rhiz-sdk-py` | Python SDK for Rhiz Protocol API | 🔄 In Progress |

### Rhiz Services

| Service | Description | Tech |
|---------|-------------|------|
| `rhiz-api` | FastAPI backend with graph queries, trust engine, DID-native endpoints | Python 3.11 |
| `rhiz-atproto` | Firehose indexer, feed generator, labeler for AT Protocol integration | TypeScript |
| `fundrhiz` | Flagship app for founder-investor warm introductions | Next.js |

### AT Protocol Base Packages (Included)

This repo includes the full AT Protocol stack for development:

| Package | Description |
|---------|-------------|
| `@atproto/api` | AT Protocol client library |
| `@atproto/identity` | DID and handle resolution |
| `@atproto/lexicon` | Schema definition language |
| `@atproto/repo` | Data storage structure (MST) |
| `@atproto/crypto` | Cryptographic signing |
| `@atproto/xrpc` | Client/server HTTP helpers |

Plus `pds`, `bsky`, and other AT Protocol services for testing and development.

### Lexicons

- **`net.rhiz.*`** - Rhiz Protocol schemas (11 lexicons) in `./lexicons/net/rhiz/`
- **`com.atproto.*`** - AT Protocol core schemas
- **`app.bsky.*`** - Bluesky application schemas

### Interoperability Test Data

Test files in `./interop-test-files/` include:
- **Rhiz Protocol tests** - `rhiz/` directory with valid record examples
- **AT Protocol tests** - Syntax and crypto validation files

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- pnpm 8.15.9+
- Docker & Docker Compose
- PostgreSQL 14+

### Installation

```bash
# Install dependencies
pnpm install

# Generate types from Rhiz lexicons
cd packages/rhiz-protocol
pnpm run codegen

# Build all packages
cd ../..
pnpm build

# Start database and Redis
docker-compose up -d postgres redis

# Run database migration
cd services/rhiz-api
alembic upgrade head

# Start API server
uvicorn app.main:app --reload

# In another terminal, start firehose indexer
cd services/rhiz-atproto
pnpm run ingest

# In another terminal, start FundRhiz frontend
cd services/fundrhiz
pnpm dev
```

### Usage Example

```typescript
import { RhizClient } from '@atproto/rhiz-sdk';

const client = new RhizClient({
  apiUrl: 'http://localhost:3000',
  atproto: { service: 'https://bsky.social' }
});

await client.login('alice.bsky.social', 'password');

// Create entity with DID
const entity = await client.entities.create({
  did: 'did:plc:abc123',
  name: 'Alice Chen',
  type: 'person'
});

// Create relationship (stored in AT Protocol repo)
const rel = await client.repo.createRelationship('did:plc:alice', {
  participants: ['did:plc:alice', 'did:plc:bob'],
  type: 'professional',
  strength: 85,
  context: 'Co-founded TechCo',
  // ... full relationship data
});

// Find path between entities
const paths = await client.graph.findPath({
  from: 'did:plc:founder',
  to: 'did:plc:investor',
  maxHops: 6,
  minStrength: 50
});
```

### Development Commands

```bash
# Run all tests
pnpm test

# Lint and format
pnpm lint
pnpm format

# Build specific package
pnpm build --filter @atproto/rhiz-protocol

# Run dev environment (AT Protocol services)
make run-dev-env
```

## 🌐 Architecture

### AT Protocol Native Foundation

Rhiz is built **natively** on AT Protocol - not bolted on, but integrated from the ground up:

```
User AT Protocol Repo → Firehose → Rhiz AppView → Applications
(Source of Truth)        (Sync)     (Index)        (FundRhiz, etc)
```

**Key Principles:**
- DIDs as primary identifiers (not arbitrary IDs)
- Relationships stored in user repos (`at://did:plc:alice/net.rhiz.relationship.record/*`)
- Content-addressed with AT URIs + CIDs
- Cryptographically signed by both participants
- Database indexes for fast queries, repos are source of truth

### Protocol Specifications

- **[Rhiz Lexicons](lexicons/net/rhiz/)** - 11 validated schemas defining `net.rhiz.*` collections
- **[Project Overview](PROJECT_OVERVIEW.md)** - Comprehensive protocol description
- **[Migration Guide](AT_PROTOCOL_NATIVE_MIGRATION.md)** - AT Protocol native architecture details
- **[AT Protocol Docs](https://atproto.com)** - Core AT Protocol specifications

### About AT Protocol

Rhiz Protocol is built on the Authenticated Transfer Protocol ("ATP" or "atproto"), a decentralized social media protocol developed by [Bluesky Social PBC](https://bsky.social).

- [AT Protocol Overview](https://atproto.com/guides/overview)
- [Protocol Specifications](https://atproto.com/specs/atp)
- [Lexicon Spec](https://atproto.com/specs/lexicon)

## 📖 Documentation

### 🌟 Start Here
- **[START_HERE.md](START_HERE.md)** ⭐ - Navigation guide and quick start
- **[STATUS.md](STATUS.md)** - Current implementation status
- **[Protocol Specification](PROTOCOL_SPECIFICATION.md)** - Complete formal spec
- **[Protocol Roadmap](RHIZ_PROTOCOL_ROADMAP.md)** - 3-year development timeline

### 🛠️ Implementation Guides
- **[AT Protocol Implementation Guide](AT_PROTOCOL_IMPLEMENTATION_GUIDE.md)** - How to implement the protocol
- **[AT Protocol Native Migration](AT_PROTOCOL_NATIVE_MIGRATION.md)** - Architecture decisions
- **[Quick Start Guide](QUICK_START_GUIDE.md)** - Get running in 30 minutes

### 🏗️ Project Documentation
- **[Project Overview](PROJECT_OVERVIEW.md)** - System architecture and use cases
- **[Lexicon Schemas](lexicons/net/rhiz/)** - AT Protocol schema definitions
- **[Interop Tests](interop-test-files/rhiz/)** - Test data and validation

### 📋 Additional Resources
- **[Security](SECURITY.md)** - Security policies and responsible disclosure
- **[Contributing](CONTRIBUTORS.md)** - Contributing guidelines
- **[Archive](docs/archive/)** - Historical implementation reports

## 🤝 Contributing

We welcome contributions that follow our architectural principles:

**Core Principles:**
- ✅ Always upgrade, never degrade
- ✅ No redundancies - single source of truth
- ✅ AT Protocol native - use AT Protocol primitives
- ✅ Federation-first - works in federated context
- ✅ User ownership - data in repos, not databases

**Guidelines:**
- Open an issue for discussion before major PRs
- For lexicon changes, get sign-off before implementation
- Follow existing patterns (DID-native, content-addressed)
- Add tests and documentation
- Atomic commits with clear messages

## 🏗️ Building on Rhiz Protocol

Developers can build applications using Rhiz Protocol's relationship intelligence:

```typescript
// Use the Rhiz SDK in your app
import { RhizClient } from '@atproto/rhiz-sdk';

const client = new RhizClient({ apiUrl: 'https://api.rhiz.network' });

// Access trust-weighted relationship graph
const paths = await client.graph.findPath({
  from: 'did:plc:user1',
  to: 'did:plc:user2'
});
```

**Use Cases:**
- Warm introduction platforms
- Trust-based content curation
- Community relationship mapping
- Professional network analysis
- Academic collaboration networks

## 🔒 Security

If you discover security issues in Rhiz Protocol, please email: **security@rhiz.network**

For AT Protocol base infrastructure issues, contact Bluesky: security@bsky.app

See [SECURITY.md](SECURITY.md) for responsible disclosure guidelines.

## License

This project is dual-licensed under MIT and Apache 2.0 terms:

- MIT license ([LICENSE-MIT.txt](https://github.com/bluesky-social/atproto/blob/main/LICENSE-MIT.txt) or http://opensource.org/licenses/MIT)
- Apache License, Version 2.0, ([LICENSE-APACHE.txt](https://github.com/bluesky-social/atproto/blob/main/LICENSE-APACHE.txt) or http://www.apache.org/licenses/LICENSE-2.0)

Downstream projects and end users may chose either license individually, or both together, at their discretion. The motivation for this dual-licensing is the additional software patent assurance provided by Apache 2.0.

Bluesky Social PBC has committed to a software patent non-aggression pledge. For details see [the original announcement](https://bsky.social/about/blog/10-01-2025-patent-pledge).

---

## 🎉 Current Status

### October 2025 - Phase 1 Complete: AT Protocol Native Foundation ✅

Complete architectural refactor to AT Protocol-native implementation:
- **11 Lexicon schemas** validated and generating types
- **DIDs as primary keys** throughout the system
- **Content-addressed records** with AT URIs + CIDs
- **Firehose indexer** for real-time updates
- **Federation-ready** architecture
- **TypeScript + Python SDKs** updated
- **Database migration** for DID-native operations

### Next: Phase 2A - Attestation System (Q1 2026)

Network-verified relationships with conviction scores (0-100):
- Reputation-weighted attestations
- Temporal decay algorithms
- API endpoints and UI components
- 8-week implementation plan ready

**For detailed status:** See [STATUS.md](STATUS.md)

---

## 🌟 Why Rhiz Protocol Matters

**Relationships are invisible infrastructure.** Social networks show connections, but don't understand trust, context, or strength. Rhiz makes relationships **machine-readable** and **verifiable**.

- **For Users:** Own your relationship data, portable across services
- **For Developers:** Build on proven relationship intelligence infrastructure
- **For The Ecosystem:** Missing protocol primitive that enables new applications

**Rhiz Protocol** - The relationship layer the internet never had.

---

**Built on AT Protocol** | **Federation-Ready** | **User-Owned Data**
