# Rhiz Protocol Specification v1.0

**The Relationship Protocol for the Internet**

---

## Abstract

Rhiz Protocol is a decentralized protocol for creating, verifying, and querying machine-readable relationships between entities. Built natively on AT Protocol, Rhiz enables cryptographically verifiable, user-owned relationship data with trust scoring and network attestation.

**Core Innovation:** Relationships are first-class data structures with quantified trust, temporal dynamics, and network verification - not just social graph edges.

---

## 1. Introduction

### 1.1 Motivation

Social networks today model connections as binary (follow/unfollow) or implicit (likes, comments). This fails to capture:

- **Relationship strength** - How well do two people know each other?
- **Relationship context** - Why are they connected?
- **Relationship verification** - Can others attest to this connection?
- **Trust dynamics** - How has trust evolved over time?

Rhiz Protocol solves this by making relationships **quantified, contextual, and verifiable**.

### 1.2 Design Principles

1. **User Ownership** - Relationship data lives in user repositories, not centralized databases
2. **Cryptographic Verification** - All relationships require signatures from both parties
3. **Network Attestation** - Third parties can verify and attest to relationships
4. **Trust Quantification** - Transparent algorithms calculate trust scores
5. **Temporal Awareness** - Relationships evolve over time
6. **Federation-Ready** - Multiple services can index the same data
7. **Privacy-First** - Granular control over relationship visibility

### 1.3 Use Cases

- **Warm Introductions** - Find trusted paths between people
- **Professional Networking** - Verified relationships with context
- **Trust-Weighted Graphs** - Pathfinding algorithms using trust scores
- **Reputation Systems** - Network-verified identity and credentials
- **Community Mapping** - Visualize relationship networks

---

## 2. Core Primitives

### 2.1 Entity

An **Entity** is any person, organization, or agent in the protocol.

**Identifier:** AT Protocol DID (e.g., `did:plc:abc123xyz`)

**Properties:**
- `did` (string, required) - Decentralized identifier
- `name` (string, required) - Display name
- `type` (enum, required) - `person | organization | agent`
- `handle` (string, optional) - Human-readable handle (e.g., `alice.bsky.social`)
- `attributes` (object, optional) - Extensible metadata

**Storage:** `at://did:plc:alice/net.rhiz.entity.profile/self`

**Example:**
```json
{
  "$type": "net.rhiz.entity.profile",
  "did": "did:plc:abc123",
  "name": "Alice Chen",
  "type": "person",
  "handle": "alice.bsky.social",
  "attributes": {
    "bio": "Co-founder @TechCo",
    "location": "San Francisco",
    "domains": ["artificial_intelligence", "startups"]
  }
}
```

---

### 2.2 Relationship

A **Relationship** represents a connection between two or more entities with quantified trust and context.

**Identifier:** AT URI + TID (e.g., `at://did:plc:alice/net.rhiz.relationship.record/3jx7ytm`)

**Core Properties:**
- `participants` (array<string>, required) - DIDs of participants (2+ entities)
- `type` (enum, required) - Relationship category
- `strength` (integer 0-100, required) - Quantified relationship strength
- `context` (string, optional) - Why this relationship exists
- `signatures` (array, required) - Cryptographic signatures from all participants

**Relationship Types:**
- `professional` - Work, business, or career relationships
- `personal` - Friends, family, social connections
- `academic` - Research, education, mentorship
- `transactional` - Business transactions, contracts
- `organizational` - Membership, affiliation

**Trust Properties:**
- `verification` - Mutual verification status
- `privacy` - Visibility controls
- `temporal` - Time-based dynamics

**Storage:** Stored in the repository of the relationship creator
- Example: `at://did:plc:alice/net.rhiz.relationship.record/3jx7ytm`

**Example:**
```json
{
  "$type": "net.rhiz.relationship.record",
  "participants": [
    "did:plc:alice",
    "did:plc:bob"
  ],
  "type": "professional",
  "strength": 85,
  "context": "Co-founded TechCo in 2020, worked together for 3 years",
  "verification": {
    "consensusScore": 0,
    "mutuallyVerified": true,
    "verifierCount": 0
  },
  "privacy": {
    "visibility": "public",
    "allowDiscovery": true,
    "allowAttestation": true
  },
  "temporal": {
    "start": "2020-01-15T00:00:00Z",
    "lastInteraction": "2025-10-20T14:30:00Z",
    "history": [
      {
        "timestamp": "2020-01-15T00:00:00Z",
        "strength": 70,
        "event": "Started collaboration"
      },
      {
        "timestamp": "2023-03-15T00:00:00Z",
        "strength": 85,
        "event": "Series A raised"
      }
    ]
  },
  "signatures": [
    {
      "did": "did:plc:alice",
      "signature": "base64encodedSignature1...",
      "signedAt": "2025-10-22T10:00:00Z"
    },
    {
      "did": "did:plc:bob",
      "signature": "base64encodedSignature2...",
      "signedAt": "2025-10-22T10:05:00Z"
    }
  ],
  "createdAt": "2025-10-22T10:00:00Z"
}
```

---

### 2.3 Attestation

An **Attestation** is a third-party validation of a relationship or claim.

**Identifier:** AT URI (e.g., `at://did:plc:carol/net.rhiz.relationship.attestation/3jx8abc`)

**Properties:**
- `targetRelationship` (string, required) - AT URI of relationship being attested
- `attester` (string, required) - DID of the attester
- `attestationType` (enum, required) - Type of attestation
- `confidence` (integer 0-100, required) - Attester's confidence level
- `evidence` (string, optional) - Supporting evidence or explanation
- `createdAt` (string, required) - ISO 8601 timestamp

**Attestation Types:**
- `verify` - Confirms the relationship exists as stated
- `dispute` - Questions the accuracy of the relationship
- `strengthen` - Suggests relationship is stronger than stated
- `weaken` - Suggests relationship is weaker than stated

**Storage:** Stored in attester's repository
- Example: `at://did:plc:carol/net.rhiz.relationship.attestation/3jx8abc`

**Example:**
```json
{
  "$type": "net.rhiz.relationship.attestation",
  "targetRelationship": "at://did:plc:alice/net.rhiz.relationship.record/3jx7ytm",
  "attester": "did:plc:carol",
  "attestationType": "verify",
  "confidence": 90,
  "evidence": "I worked with both Alice and Bob at TechCo for 2 years",
  "createdAt": "2025-10-22T11:00:00Z"
}
```

---

### 2.4 Trust Metrics

**Trust metrics** quantify the reliability and strength of relationships and entities.

**Entity-Level Metrics:**
- `trustScore` (0-100) - Overall trustworthiness of the entity
- `reputation` (0-100) - Network consensus on reliability
- `reciprocity` (0-100) - Mutual relationship strength
- `consistency` (0-100) - Stability over time
- `relationshipCount` - Total number of relationships
- `verifiedRelationshipCount` - Relationships with attestations

**Relationship-Level Metrics:**
- `strength` (0-100) - Self-reported relationship strength
- `convictionScore` (0-100) - Network confidence in relationship
- `attestationCount` - Number of third-party attestations
- `verifyCount` - Number of verify attestations
- `disputeCount` - Number of dispute attestations

**Storage:** Trust metrics can be cached in `at://did:plc:alice/net.rhiz.trust.metrics/{tid}`

**Example:**
```json
{
  "$type": "net.rhiz.trust.metrics",
  "subject": "did:plc:alice",
  "trustScore": 88,
  "reputation": 91,
  "reciprocity": 85,
  "consistency": 89,
  "relationshipCount": 47,
  "verifiedRelationshipCount": 42,
  "calculatedAt": "2025-10-22T12:00:00Z"
}
```

---

## 3. Protocol Operations

### 3.1 Creating a Relationship

**Process:**
1. Entity A initiates relationship creation
2. Relationship record created in Entity A's repository
3. Entity B signs the relationship (mutual consent)
4. Relationship becomes active and discoverable
5. Firehose broadcasts the relationship to indexers

**Cryptographic Requirements:**
- Both parties must sign the relationship record
- Signatures use keys from DID documents
- Verification checks both signatures are valid

**AT Protocol Flow:**
```
1. Alice creates relationship record in her repo
   at://did:plc:alice/net.rhiz.relationship.record/3jx7ytm

2. Bob retrieves the record, signs it, and stores signature

3. Both signatures attached to the record

4. Firehose broadcasts commit to indexers

5. Indexers verify signatures and index relationship
```

---

### 3.2 Attesting to a Relationship

**Process:**
1. Attester discovers a relationship (via graph query or direct link)
2. Attester evaluates the relationship
3. Attester creates attestation record in their repository
4. Attestation references target relationship by AT URI
5. Indexers recalculate conviction score for the relationship

**Requirements:**
- Attester must have a Rhiz entity profile
- Attester's reputation affects attestation weight
- Attestation is cryptographically signed

**AT Protocol Flow:**
```
1. Carol finds Alice-Bob relationship
   at://did:plc:alice/net.rhiz.relationship.record/3jx7ytm

2. Carol creates attestation in her repo
   at://did:plc:carol/net.rhiz.relationship.attestation/3jx8abc

3. Firehose broadcasts Carol's attestation

4. Indexer picks up attestation, recalculates conviction

5. Relationship conviction score updates: 0 → 72
```

---

### 3.3 Calculating Conviction Scores

**Conviction Algorithm:**

```
For each attestation:
  1. Get base weight by type:
     - verify: +1.0
     - dispute: -1.5 (weighted higher for fraud prevention)
     - strengthen: +0.5
     - weaken: -0.5

  2. Apply reputation multiplier (0.5x to 2.0x):
     multiplier = 0.5 + (attester_reputation / 100) * 1.5

  3. Apply temporal decay (180-day half-life):
     decay = 0.5 ^ (days_old / 180)

  4. Scale by confidence (0-100):
     weight = base_weight * reputation * decay * (confidence / 100)

Aggregate:
  weighted_sum = sum of all weights
  total_weight = sum of absolute weights

  conviction = 50 + (weighted_sum / total_weight) * 50
  conviction = clamp(conviction, 0, 100)
```

**Result:** Integer score from 0 (low confidence) to 100 (high confidence)

**Properties:**
- High-reputation attesters have more impact
- Disputes weighted 1.5x to penalize fraud
- Old attestations decay over time
- Multiple attestations aggregate

---

### 3.4 Graph Queries

**Find Path Between Entities:**

Query: `net.rhiz.graph.findPath`

```typescript
{
  from: "did:plc:founder",
  to: "did:plc:investor",
  maxHops: 6,
  minStrength: 50
}
```

Response: Array of paths with trust-weighted scores

```typescript
{
  paths: [
    {
      hops: [
        { entity: "did:plc:founder", relationship: "at://..." },
        { entity: "did:plc:cofounder", relationship: "at://..." },
        { entity: "did:plc:investor", relationship: "at://..." }
      ],
      totalStrength: 66,
      hopCount: 2
    }
  ]
}
```

**Get Neighbors:**

Query: `net.rhiz.graph.getNeighbors`

```typescript
{
  did: "did:plc:alice",
  minStrength: 60,
  limit: 50
}
```

Response: Array of connected entities with relationship details

---

## 4. Data Structures

### 4.1 AT Protocol Integration

**Repository Collections:**
- `net.rhiz.entity.profile` - Entity profiles (key: `self`)
- `net.rhiz.relationship.record` - Relationships (key: TID)
- `net.rhiz.relationship.attestation` - Attestations (key: TID)
- `net.rhiz.trust.metrics` - Trust scores (key: TID)
- `net.rhiz.intro.request` - Introduction requests (key: TID)

**Content Addressing:**
- All records have AT URIs: `at://did:plc:alice/collection/rkey`
- All records have CIDs for content verification
- Firehose provides real-time updates

**Signatures:**
- ECDSA signatures using secp256k1 keys (AT Protocol standard)
- Signatures verify against DID document public keys
- Multi-party signatures for relationships

---

### 4.2 Trust Score Schema

**Entity Trust Score:**
```typescript
interface TrustMetrics {
  subject: string           // DID
  trustScore: number        // 0-100, overall trust
  reputation: number        // 0-100, network consensus
  reciprocity: number       // 0-100, mutual relationships
  consistency: number       // 0-100, stable over time
  relationshipCount: number
  verifiedRelationshipCount: number
  calculatedAt: string      // ISO 8601
}
```

**Relationship Conviction:**
```typescript
interface ConvictionScore {
  targetUri: string                    // AT URI
  score: number                        // 0-100
  attestationCount: number
  verifyCount: number
  disputeCount: number
  strengthenCount: number
  weakenCount: number
  lastUpdated: string
  trend: 'increasing' | 'stable' | 'decreasing'
  topAttesterReputation: number
}
```

---

## 5. Security & Privacy

### 5.1 Cryptographic Requirements

**Identity:**
- All entities must have valid AT Protocol DIDs
- DID documents must contain valid public keys
- Key rotation supported per AT Protocol standards

**Signatures:**
- Relationships require signatures from all participants
- Attestations signed by attester
- Signature verification using DID document keys

**Verification:**
```typescript
async function verifyRelationship(record: Relationship): Promise<boolean> {
  for (const signature of record.signatures) {
    const didDoc = await resolveDidDocument(signature.did)
    const publicKey = getSigningKey(didDoc)
    const isValid = await verifySignature(record, signature, publicKey)
    if (!isValid) return false
  }
  return true
}
```

---

### 5.2 Privacy Controls

**Visibility Levels:**
- `public` - Discoverable by anyone
- `connections` - Only visible to connected entities
- `private` - Only visible to participants

**Attestation Controls:**
- `allowAttestation` - Whether third parties can attest
- `allowDiscovery` - Whether relationship appears in graph queries
- `blockList` - Specific DIDs blocked from viewing

**Data Minimization:**
- Only required fields stored on-chain
- Sensitive context can be encrypted
- Selective disclosure supported

---

## 6. Implementation Guidelines

### 6.1 AT Protocol Reference Implementation

**Required Components:**
1. **Lexicon Schemas** - Define record types in JSON
2. **Repository Writer** - Create records in user repos
3. **Firehose Indexer** - Subscribe to `net.rhiz.*` collections
4. **Graph Indexer** - Build PostgreSQL index for queries
5. **Trust Engine** - Calculate conviction and trust scores
6. **API Layer** - XRPC endpoints for queries

**Architecture:**
```
User Repo → Firehose → Indexer → PostgreSQL → API → Applications
(source)    (sync)     (process)  (query)     (serve) (consume)
```

**Key Files:**
- `lexicons/net/rhiz/**/*.json` - Schema definitions
- `packages/rhiz-protocol/` - TypeScript types and utilities
- `packages/rhiz-sdk/` - Client SDK
- `services/rhiz-api/` - Python API backend
- `services/rhiz-atproto/` - Firehose indexer

---

### 6.2 Performance Requirements

**Indexing:**
- Firehose lag: <5 seconds from commit to indexed
- Relationship indexing: <100ms per record
- Attestation processing: <200ms including conviction recalculation

**Queries:**
- Entity lookup: <10ms
- Relationship query: <50ms
- Path finding: <500ms for 6-hop max
- Trust score calculation: <100ms for 100 attestations

**Storage:**
- Relationship size: <5KB average
- Attestation size: <2KB average
- Trust metrics cache: <1KB per entity

---

## 7. Extensions & Future Work

### 7.1 Planned Features

**Phase 2A (Q1 2026) - Attestation System:**
- Network conviction scores
- Reputation-weighted attestations
- Temporal decay for old attestations
- UI components for attestation

**Phase 2B (Q2 2026) - Triple-Based Claims:**
- Decompose relationships to atomic triples
- Attest specific relationship fields
- Granular conviction per field
- RDF/Linked Data compatibility

**Phase 2C (Q3 2026) - Expertise & Credentials:**
- Skill and domain expertise claims
- Credential verification by institutions
- Context-aware matching
- Professional network analysis

---

### 7.2 Research Directions

**Trust Propagation:**
- TidalTrust algorithm implementation
- Appleseed trust propagation
- PageRank-style reputation
- Graph neural networks for trust prediction

**Privacy:**
- Zero-knowledge proofs for attestations
- Selective disclosure of relationship details
- Anonymous attestation protocols
- Encrypted relationship context

**Interoperability:**
- Cross-protocol bridges (future multi-chain)
- W3C Verifiable Credentials integration
- DIDComm messaging for negotiations
- OAuth 2.0 / OIDC integration

---

## 8. Governance

### 8.1 Protocol Evolution

**RFC Process:**
- Rhiz Improvement Proposals (RIPs)
- Community discussion period (14 days minimum)
- Reference implementation required
- Backwards compatibility considered

**Version Control:**
- Semantic versioning (MAJOR.MINOR.PATCH)
- Breaking changes require major version bump
- Lexicon schema versioning
- Migration guides for implementers

---

### 8.2 Standards Alignment

**Existing Standards:**
- AT Protocol (Authenticated Transfer Protocol)
- W3C DID (Decentralized Identifiers)
- JSON Schema
- ISO 8601 (Timestamps)
- OAuth 2.0 (Future authentication)

**Future Alignment:**
- W3C Verifiable Credentials
- JSON-LD / RDF
- ActivityPub (social web)
- OpenID Connect

---

## 9. Compliance & Legal

### 9.1 Data Protection

**GDPR Compliance:**
- Right to erasure (delete records from repo)
- Right to portability (export data in JSON)
- Consent management (signatures = consent)
- Data minimization (only required fields)

**CCPA Compliance:**
- Right to know (query API)
- Right to delete (repo deletion)
- Right to opt-out (privacy controls)

---

### 9.2 Content Moderation

**Labeling System:**
- AT Protocol labeler service
- Label false/misleading relationships
- Report fraudulent attestations
- Community moderation

**Dispute Resolution:**
- Flag relationships for review
- Challenge attestations
- Community arbitration
- Appeals process

---

## 10. Success Metrics

### 10.1 Technical Metrics

- **Performance:** <200ms p95 API latency
- **Reliability:** 99.9% uptime
- **Scalability:** 1M+ relationships supported
- **Security:** Zero critical vulnerabilities

### 10.2 Adoption Metrics

- **Entities:** 10,000+ by end of Year 1
- **Relationships:** 100,000+ by end of Year 1
- **Attestations:** 50,000+ by end of Year 1
- **Applications:** 10+ using Rhiz Protocol

### 10.3 Quality Metrics

- **Trust Accuracy:** 85%+ correlation with manual validation
- **Fraud Detection:** 95%+ of fake relationships detected
- **User Satisfaction:** 80%+ find trust scores helpful

---

## Conclusion

Rhiz Protocol transforms relationships from binary connections to quantified, verifiable, user-owned data structures. By building natively on AT Protocol, Rhiz provides:

- **Decentralization** - User-owned data in personal repositories
- **Verification** - Cryptographic signatures and network attestation
- **Portability** - Data moves with the user across services
- **Composability** - Standard primitives for relationship intelligence

The result is the relationship layer the internet never had - machine-readable, verifiable, and truly owned by users.

---

**Specification Version:** 1.0
**Date:** October 22, 2025
**Status:** Draft for Community Review
**License:** MIT / Apache 2.0

**Maintainers:** Rhiz Protocol Team
**Contact:** protocol@rhiz.network
**Repository:** https://github.com/rhizprotocol/specification

