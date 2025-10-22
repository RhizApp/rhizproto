# Start Here: Rhiz Protocol Documentation Index

**Welcome to Rhiz Protocol!** This guide helps you navigate the documentation.

---

## What is Rhiz Protocol?

Rhiz Protocol is **the relationship protocol for the internet** - a specification for machine-readable, verifiable relationships with quantified trust.

**Think of it like:**
- OAuth for relationships
- W3C DID for connections
- A protocol standard, not a single platform

---

## 🎯 Choose Your Path

### I want to understand the protocol

**Read:** [PROTOCOL_SPECIFICATION.md](PROTOCOL_SPECIFICATION.md)

This is the formal specification defining:
- Core primitives (Entity, Relationship, Attestation, Trust)
- Data structures (chain-agnostic)
- Cryptographic requirements
- Trust algorithms
- Protocol operations

**Time:** 45 minutes
**Outcome:** You understand what Rhiz Protocol defines

---

### I want to implement Rhiz

**Read:** [AT_PROTOCOL_IMPLEMENTATION_GUIDE.md](AT_PROTOCOL_IMPLEMENTATION_GUIDE.md)

This documents our reference implementation on AT Protocol:
- Architecture patterns
- Lexicon schema design decisions
- Repository operations
- Firehose indexing
- Trust calculation implementation
- Performance optimizations
- Lessons learned

**Time:** 1 hour
**Outcome:** You know how to implement Rhiz on any tech stack

---

### I want to build on Rhiz

**Read:** [Project Overview](PROJECT_OVERVIEW.md) then [Quick Start](#quick-start)

This explains the system architecture and gets you coding:
- What's built already
- How to run locally
- SDK usage examples
- API endpoints
- Common patterns

**Time:** 30 minutes
**Outcome:** You're building an application using Rhiz

---

### I want to know the roadmap

**Read:** [RHIZ_PROTOCOL_ROADMAP.md](RHIZ_PROTOCOL_ROADMAP.md)

This shows our 3-year plan:
- Year 1: Foundation + Attestation system
- Year 2: Scale + Ecosystem growth
- Year 3: Maturity + Sustainability
- Next 90 days (detailed)

**Time:** 20 minutes
**Outcome:** You know where we're going

---

### I want to contribute

**Read:** [Contributing](#contributing) section below

---

## 📚 Document Structure

### Protocol Level (Chain-Agnostic)

| Document | Purpose | Audience |
|----------|---------|----------|
| [PROTOCOL_SPECIFICATION.md](PROTOCOL_SPECIFICATION.md) | Formal protocol spec | Protocol designers, implementers |
| [RHIZ_PROTOCOL_ROADMAP.md](RHIZ_PROTOCOL_ROADMAP.md) | Development roadmap | Contributors, stakeholders |

### Implementation Level (AT Protocol)

| Document | Purpose | Audience |
|----------|---------|----------|
| [AT_PROTOCOL_IMPLEMENTATION_GUIDE.md](AT_PROTOCOL_IMPLEMENTATION_GUIDE.md) | Reference implementation | Developers, implementers |
| [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) | System architecture | Developers building on Rhiz |
| [README.md](README.md) | Quick start guide | First-time visitors |

### Technical Details

| Document | Purpose | Audience |
|----------|---------|----------|
| [Lexicon Schemas](lexicons/net/rhiz/) | AT Protocol schema definitions | Protocol implementers |
| [Interop Tests](interop-test-files/rhiz/) | Test data and validation | Developers, QA |
| [AT_PROTOCOL_NATIVE_MIGRATION.md](AT_PROTOCOL_NATIVE_MIGRATION.md) | Architecture decisions | Technical deep dive |

---

## Quick Start

### Prerequisites
- Node.js 18+
- pnpm 8.15.9+
- Docker & Docker Compose
- PostgreSQL 14+

### Installation

```bash
# Clone repository
git clone https://github.com/rhizprotocol/rhizproto
cd rhizproto

# Install dependencies
pnpm install

# Generate types from lexicons
cd packages/rhiz-protocol
pnpm run codegen

# Build packages
cd ../..
pnpm build

# Start infrastructure
docker-compose up -d postgres redis

# Run database migration
cd services/rhiz-api
alembic upgrade head

# Start API server
uvicorn app.main:app --reload

# In another terminal: Start firehose indexer
cd services/rhiz-atproto
pnpm run ingest

# In another terminal: Start frontend
cd services/fundrhiz
pnpm dev
```

### Your First Relationship

```typescript
import { RhizClient } from '@atproto/rhiz-sdk'

const client = new RhizClient({
  apiUrl: 'http://localhost:3000',
  atproto: { service: 'https://bsky.social' }
})

// Login
await client.login('alice.bsky.social', 'password')

// Create entity
const alice = await client.entities.create({
  did: 'did:plc:abc123',
  name: 'Alice Chen',
  type: 'person'
})

// Create relationship
const relationship = await client.repo.createRelationship('did:plc:alice', {
  participants: ['did:plc:alice', 'did:plc:bob'],
  type: 'professional',
  strength: 85,
  context: 'Co-founded TechCo'
})

console.log('Created:', relationship.uri)
// at://did:plc:alice/net.rhiz.relationship.record/3jx7ytm
```

---

## Current Status

### ✅ Completed (October 2025)

**AT Protocol Native Foundation:**
- 11 Lexicon schemas validated
- DID-native architecture
- Content-addressed records
- Firehose indexer operational
- Database migration complete
- TypeScript + Python SDKs

**Documentation:**
- Protocol specification
- Implementation guide
- 3-year roadmap

### 🔄 In Progress (Q4 2025 - Q1 2026)

**Attestation System (Phase 2A):**
- Network conviction mechanism
- Reputation-weighted validation
- API endpoints for attestations
- UI components (badges, buttons)
- 8-week implementation plan ready

See [RHIZ_ATTESTATION_IMPLEMENTATION_PLAN.md](RHIZ_ATTESTATION_IMPLEMENTATION_PLAN.md) for details.

### 🔮 Planned (Q2 2026+)

**Relationship Quality:**
- Rich context structures
- Relationship analytics
- Advanced trust metrics
- Smart recommendations

**Developer Experience:**
- Improved SDK
- Interactive documentation
- Developer tools (CLI, visualizer)
- Integration guides

See [RHIZ_PROTOCOL_ROADMAP.md](RHIZ_PROTOCOL_ROADMAP.md) for full timeline.

---

## Key Concepts

### Entity
Any person, organization, or agent. Identified by a DID.

```json
{
  "did": "did:plc:abc123",
  "name": "Alice Chen",
  "type": "person"
}
```

### Relationship
Quantified connection between entities with context and signatures.

```json
{
  "participants": ["did:plc:alice", "did:plc:bob"],
  "type": "professional",
  "strength": 85,
  "context": "Co-founded TechCo",
  "signatures": [...]
}
```

### Attestation
Third-party validation of a relationship.

```json
{
  "targetRelationship": "at://...",
  "attester": "did:plc:carol",
  "attestationType": "verify",
  "confidence": 90,
  "evidence": "I worked with both"
}
```

### Trust Metrics
Calculated scores based on network consensus.

```json
{
  "trustScore": 88,      // Overall trust (0-100)
  "reputation": 91,      // Network consensus
  "reciprocity": 85,     // Mutual relationships
  "consistency": 89      // Stable over time
}
```

### Conviction Score
Network confidence in a relationship (0-100), based on attestations.

```json
{
  "score": 87,
  "attestationCount": 15,
  "verifyCount": 14,
  "disputeCount": 1,
  "trend": "increasing"
}
```

---

## Architecture

### High-Level Flow

```
User AT Protocol Repo (Source of Truth)
  ↓ commits via
AT Protocol Firehose (Real-time sync)
  ↓ subscribed by
Rhiz Indexer (Process & validate)
  ↓ stores in
PostgreSQL Database (Fast queries)
  ↓ served by
Rhiz API (XRPC endpoints)
  ↓ consumed by
Applications (FundRhiz, etc.)
```

### Key Design Decisions

1. **DIDs as Primary Keys**
   - Not UUIDs or arbitrary IDs
   - Cryptographically verifiable
   - Cross-platform compatible

2. **Integer Scores (0-100)**
   - Not floats
   - AT Protocol compatible
   - Better UX

3. **Dual Signatures**
   - Both participants must sign
   - Prevents fake relationships
   - Cryptographic proof

4. **Firehose Indexing**
   - Real-time updates
   - AT Protocol standard
   - Scales well

5. **User-Owned Data**
   - Records in user repos
   - Not centralized database
   - Portable across services

---

## FAQ

### Is Rhiz Protocol blockchain-specific?

No. The protocol specification is chain-agnostic. Our reference implementation uses AT Protocol, but the primitives (Entity, Relationship, Attestation, Trust) can be implemented on any tech stack.

### Can I use Rhiz without AT Protocol?

Yes. You can implement Rhiz on NEAR, Ethereum, or any other chain. Follow the [PROTOCOL_SPECIFICATION.md](PROTOCOL_SPECIFICATION.md) and adapt storage/identity layers.

### Is there a token?

Not yet. Phase 1-2 focus on proving the protocol works without economic incentives. A token might be introduced in Year 3 (2027-2028) if organic adoption validates the need.

### How do I integrate Rhiz into my app?

Install the SDK (`pnpm add @atproto/rhiz-sdk`), initialize a client, and use the relationship APIs. See [Quick Start](#quick-start) above.

### Can I run my own Rhiz AppView?

Yes! The reference implementation is open-source. Run the firehose indexer and API server to operate your own AppView. Multiple AppViews can index the same user data (federation).

### What about privacy?

Relationships have granular privacy controls:
- `public` - Discoverable by anyone
- `connections` - Only visible to connected entities
- `private` - Only visible to participants

Users control visibility for each relationship.

### How accurate are trust scores?

Current target: 85%+ correlation with manual validation. Trust algorithms are transparent and reproducible. Attestations improve accuracy through network consensus.

---

## Contributing

We welcome contributions! Here's how to get started:

### 1. Choose What to Work On

**Protocol Level:**
- Improve specification clarity
- Add test cases
- Document edge cases
- Propose protocol improvements (RIP process)

**Implementation Level:**
- Fix bugs in AT Protocol implementation
- Optimize performance
- Improve developer experience
- Add features from roadmap

**Ecosystem Level:**
- Build applications on Rhiz
- Create tutorials and guides
- Integrate with other AT Protocol apps
- Spread awareness

### 2. Development Setup

Follow [Quick Start](#quick-start) to get the development environment running.

### 3. Contribution Guidelines

- Open an issue before starting work on major changes
- Follow existing code style and patterns
- Add tests for new features
- Update documentation
- Atomic commits with clear messages
- No breaking changes without discussion

### 4. Areas Needing Help

**High Priority:**
- [ ] Attestation system implementation (Phase 2A)
- [ ] Performance optimization (database indexes)
- [ ] Developer documentation improvements
- [ ] Test coverage expansion

**Medium Priority:**
- [ ] Additional SDK features
- [ ] UI component library
- [ ] Integration examples
- [ ] Video tutorials

**Future:**
- [ ] Advanced trust algorithms
- [ ] Privacy features (ZK proofs)
- [ ] Cross-chain bridges
- [ ] Academic research validation

---

## Support

### Technical Questions
- GitHub Issues: https://github.com/rhizprotocol/rhizproto/issues
- Discord: https://discord.gg/rhiz (coming soon)

### Protocol Discussions
- GitHub Discussions: https://github.com/rhizprotocol/rhizproto/discussions
- RIP proposals: TBD

### Security Issues
- Email: security@rhiz.network
- Responsible disclosure policy in [SECURITY.md](SECURITY.md)

---

## License

Dual-licensed under MIT and Apache 2.0:
- MIT license ([LICENSE-MIT.txt](LICENSE-MIT.txt))
- Apache License 2.0 ([LICENSE-APACHE.txt](LICENSE-APACHE.txt))

Following Bluesky's model for maximum flexibility and patent protection.

---

## Next Steps

1. **Read the spec:** [PROTOCOL_SPECIFICATION.md](PROTOCOL_SPECIFICATION.md)
2. **Understand the roadmap:** [RHIZ_PROTOCOL_ROADMAP.md](RHIZ_PROTOCOL_ROADMAP.md)
3. **Run it locally:** Follow [Quick Start](#quick-start)
4. **Build something:** Use the SDK to create relationships
5. **Join the community:** Contribute to the protocol

**Ready?** Pick a document from [Choose Your Path](#-choose-your-path) and dive in!

---

**Document:** START_HERE.md
**Version:** 1.0
**Date:** October 22, 2025
**Maintained by:** Rhiz Protocol Team

**We're building the relationship layer the internet never had.**

