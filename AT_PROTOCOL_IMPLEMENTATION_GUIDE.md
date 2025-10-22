# AT Protocol Implementation Guide

**How to Implement Rhiz Protocol on AT Protocol**

---

## Overview

This guide documents Rhiz Protocol's AT Protocol implementation as the reference implementation. It covers architecture decisions, implementation patterns, and lessons learned that can inform future implementations.

---

## 1. Architecture Overview

### 1.1 AT Protocol Integration

**Core Principle:** Rhiz is AT Protocol-native, not AT Protocol-adjacent.

```
User AT Protocol Repository (Source of Truth)
  ├── net.rhiz.entity.profile/self
  ├── net.rhiz.relationship.record/{tid}
  ├── net.rhiz.relationship.attestation/{tid}
  ├── net.rhiz.trust.metrics/{tid}
  └── net.rhiz.intro.request/{tid}
          ↓ (commits broadcast via)
    AT Protocol Firehose
          ↓ (subscribed by)
    Rhiz Indexer Service
          ↓ (processes and stores in)
    PostgreSQL Database
          ↓ (queried via)
    Rhiz API (XRPC)
          ↓ (consumed by)
    Applications (FundRhiz, etc.)
```

---

### 1.2 Data Flow

**Creating a Relationship:**
1. User A initiates relationship via SDK
2. SDK creates record in User A's AT Protocol repo
3. Record includes space for User B's signature
4. User B retrieves, validates, and signs
5. Both signatures stored in the record
6. Firehose broadcasts commit
7. Indexer picks up commit, validates signatures
8. Relationship indexed in PostgreSQL for fast queries
9. Trust metrics calculated and cached

**Attesting to a Relationship:**
1. User C discovers relationship (via API query)
2. User C creates attestation record in their repo
3. Attestation references relationship by AT URI
4. Firehose broadcasts attestation commit
5. Indexer picks up attestation
6. Conviction score recalculated
7. Conviction cache updated
8. Relationship conviction updated

---

## 2. Lexicon Schemas

### 2.1 Design Principles

**Type Safety:**
- All records have `$type` field
- Strict validation via JSON schemas
- Generated TypeScript types
- No runtime type errors

**Versioning:**
- Semantic versioning for schemas
- Backwards compatibility required
- Deprecation process defined
- Migration paths documented

**Extensibility:**
- Optional fields for future features
- Metadata objects for custom data
- Union types for polymorphism
- Reference types for links

---

### 2.2 Entity Profile Schema

**File:** `lexicons/net/rhiz/entity/profile.json`

**Key Design Decisions:**

1. **Single Profile Per User**
   - Key: `literal:self` (only one profile per repo)
   - Rationale: Simplicity, clear canonical profile
   - Alternative considered: Multiple personas (rejected for v1)

2. **Minimal Required Fields**
   - Required: `did`, `name`, `type`
   - Optional: Everything else
   - Rationale: Easy onboarding, user control

3. **Extensible Attributes**
   - `attributes` object for custom fields
   - No schema enforcement on attributes
   - Rationale: Flexibility for different use cases

**Example:**
```json
{
  "lexicon": 1,
  "id": "net.rhiz.entity.profile",
  "defs": {
    "main": {
      "type": "record",
      "key": "literal:self",
      "record": {
        "type": "object",
        "required": ["did", "name", "type"],
        "properties": {
          "did": {
            "type": "string",
            "format": "did"
          },
          "name": {
            "type": "string",
            "maxLength": 100
          },
          "type": {
            "type": "string",
            "enum": ["person", "organization", "agent"]
          },
          "attributes": {
            "type": "object"
          }
        }
      }
    }
  }
}
```

---

### 2.3 Relationship Record Schema

**File:** `lexicons/net/rhiz/relationship/record.json`

**Key Design Decisions:**

1. **TID as Record Key**
   - Key: `tid` (Timestamp Identifier)
   - Rationale: Unique, sortable, no collisions
   - AT Protocol standard for user-generated records

2. **Array of Participants**
   - 2+ entities can be in a relationship
   - Future: Group relationships (3+ people)
   - Current: Most are binary (2 people)

3. **Integer Strength (0-100)**
   - Not float (0.0-1.0)
   - Rationale: AT Protocol lexicons don't support floats
   - Better UX: "85 strength" vs "0.85 strength"
   - Avoids float comparison issues

4. **Nested Objects for Organization**
   - `verification` object groups verification fields
   - `privacy` object groups privacy controls
   - `temporal` object groups time-based data
   - Rationale: Clear structure, extensible

5. **Dual Signatures Required**
   - Both participants must sign
   - Prevents fake relationships
   - Cryptographic proof of consent
   - Audit trail

**Example:**
```json
{
  "lexicon": 1,
  "id": "net.rhiz.relationship.record",
  "defs": {
    "main": {
      "type": "record",
      "key": "tid",
      "record": {
        "type": "object",
        "required": ["participants", "type", "strength", "signatures", "createdAt"],
        "properties": {
          "participants": {
            "type": "array",
            "items": { "type": "string", "format": "did" },
            "minLength": 2
          },
          "type": {
            "type": "string",
            "knownValues": ["professional", "personal", "academic", "transactional", "organizational"]
          },
          "strength": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
          },
          "context": {
            "type": "string",
            "maxLength": 2000
          },
          "verification": {
            "type": "ref",
            "ref": "net.rhiz.relationship.defs#verification"
          },
          "privacy": {
            "type": "ref",
            "ref": "net.rhiz.relationship.defs#privacy"
          },
          "temporal": {
            "type": "ref",
            "ref": "net.rhiz.relationship.defs#temporal"
          },
          "signatures": {
            "type": "array",
            "items": { "type": "ref", "ref": "#signature" }
          },
          "createdAt": {
            "type": "string",
            "format": "datetime"
          }
        }
      }
    },
    "signature": {
      "type": "object",
      "required": ["did", "signature", "signedAt"],
      "properties": {
        "did": {
          "type": "string",
          "format": "did"
        },
        "signature": {
          "type": "string"
        },
        "signedAt": {
          "type": "string",
          "format": "datetime"
        }
      }
    }
  }
}
```

---

### 2.4 Attestation Schema

**File:** `lexicons/net/rhiz/relationship/attestation.json`

**Key Design Decisions:**

1. **Target by AT URI**
   - `targetRelationship` is full AT URI
   - Rationale: Unambiguous reference, content-addressed
   - Works across repos and services

2. **Attester Always in Signature**
   - `attester` field = record creator's DID
   - Redundant but explicit
   - Easier validation and queries

3. **Four Attestation Types**
   - `verify` - Confirms relationship
   - `dispute` - Questions relationship
   - `strengthen` - Suggests higher strength
   - `weaken` - Suggests lower strength
   - Rationale: Cover all trust scenarios

4. **Confidence as Percentage**
   - 0-100 integer
   - Allows nuanced attestations
   - "I'm 60% sure" vs "I'm 100% sure"

5. **Optional Evidence**
   - Free-text explanation
   - Max 1000 characters
   - Not required but encouraged

**Example:**
```json
{
  "lexicon": 1,
  "id": "net.rhiz.relationship.attestation",
  "defs": {
    "main": {
      "type": "record",
      "key": "tid",
      "record": {
        "type": "object",
        "required": ["targetRelationship", "attester", "attestationType", "confidence", "createdAt"],
        "properties": {
          "targetRelationship": {
            "type": "string",
            "format": "at-uri"
          },
          "attester": {
            "type": "string",
            "format": "did"
          },
          "attestationType": {
            "type": "string",
            "enum": ["verify", "dispute", "strengthen", "weaken"]
          },
          "confidence": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
          },
          "evidence": {
            "type": "string",
            "maxLength": 1000
          },
          "suggestedStrength": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
          },
          "createdAt": {
            "type": "string",
            "format": "datetime"
          }
        }
      }
    }
  }
}
```

---

## 3. Repository Operations

### 3.1 Creating Records

**Implementation:** `packages/rhiz-protocol/src/repo.ts`

**Key Pattern: RhizRepoWriter**

```typescript
export class RhizRepoWriter {
  constructor(private agent: Agent) {}

  async createRelationship(
    repo: string,
    record: RelationshipRecord
  ): Promise<{ uri: string; cid: string }> {
    // Validate record structure
    validateRelationshipRecord(record)
    
    // Create record in user's repo
    const result = await this.agent.com.atproto.repo.createRecord({
      repo,
      collection: 'net.rhiz.relationship.record',
      record: {
        $type: 'net.rhiz.relationship.record',
        ...record
      }
    })
    
    return {
      uri: result.uri,
      cid: result.cid
    }
  }
}
```

**Design Decisions:**

1. **Agent-Based Operations**
   - Use AT Protocol Agent class
   - Handles authentication automatically
   - Session management built-in

2. **Validation Before Write**
   - Client-side validation first
   - Catches errors early
   - Better UX (immediate feedback)

3. **Return URI + CID**
   - URI for referencing
   - CID for content verification
   - Both needed for completeness

---

### 3.2 Signature Flow

**Challenge:** Relationships need two signatures, but AT Protocol repos are single-user.

**Solution:** Progressive signature collection

**Flow:**
```typescript
// Step 1: Alice creates relationship
const relationship = await client.createRelationship({
  participants: ['did:plc:alice', 'did:plc:bob'],
  type: 'professional',
  strength: 85,
  context: 'Co-founders',
  signatures: [
    {
      did: 'did:plc:alice',
      signature: await signRecord(relationship, aliceKey),
      signedAt: new Date().toISOString()
    }
    // Bob's signature placeholder
  ]
})

// Step 2: Bob retrieves relationship
const rel = await client.getRelationship(relationship.uri)

// Step 3: Bob validates and signs
const bobSignature = {
  did: 'did:plc:bob',
  signature: await signRecord(rel, bobKey),
  signedAt: new Date().toISOString()
}

// Step 4: Update record with both signatures
await client.updateRelationship(relationship.uri, {
  ...rel,
  signatures: [...rel.signatures, bobSignature]
})
```

**Alternative Considered:** Out-of-band signature exchange
- Rejected: Too complex, not AT Protocol-native
- Current approach: Simple, works with existing infrastructure

---

## 4. Firehose Indexing

### 4.1 Subscription Pattern

**Implementation:** `services/rhiz-atproto/src/indexer.ts`

**Key Pattern: Collection-Based Filtering**

```typescript
export class RhizFirehoseIndexer {
  private firehose: Firehose

  async start() {
    this.firehose = new Firehose({
      service: 'wss://bsky.network',
      handleEvent: (evt) => this.handleEvent(evt)
    })
    
    await this.firehose.start()
  }

  async handleEvent(evt: CommitEvent) {
    // Filter for Rhiz collections only
    if (!evt.ops) return
    
    for (const op of evt.ops) {
      if (op.action !== 'create' && op.action !== 'update') continue
      
      // Route to appropriate handler
      switch (op.collection) {
        case 'net.rhiz.entity.profile':
          await this.indexEntity(op)
          break
        case 'net.rhiz.relationship.record':
          await this.indexRelationship(op)
          break
        case 'net.rhiz.relationship.attestation':
          await this.indexAttestation(op)
          break
      }
    }
  }
}
```

---

### 4.2 Indexing Relationships

**Key Steps:**

1. **Deserialize Record**
   ```typescript
   const record = op.record as RelationshipRecord
   ```

2. **Validate Signatures**
   ```typescript
   for (const sig of record.signatures) {
     const didDoc = await resolveDidDocument(sig.did)
     const isValid = await verifySignature(record, sig, didDoc)
     if (!isValid) {
       console.warn('Invalid signature:', sig.did)
       return // Skip invalid relationships
     }
   }
   ```

3. **Store in Database**
   ```typescript
   await db.query(`
     INSERT INTO relationships (
       uri, cid, participants, type, strength,
       context, created_at, indexed_at
     ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
     ON CONFLICT (uri) DO UPDATE SET
       strength = EXCLUDED.strength,
       indexed_at = EXCLUDED.indexed_at
   `, [
     op.uri,
     op.cid,
     record.participants,
     record.type,
     record.strength,
     record.context,
     record.createdAt,
     new Date()
   ])
   ```

4. **Update Graph Index**
   ```typescript
   // Create edges for fast graph queries
   for (const participant of record.participants) {
     await db.query(`
       INSERT INTO graph_edges (
         from_did, to_did, relationship_uri, strength
       ) VALUES ($1, $2, $3, $4)
     `, [
       participant,
       otherParticipants,
       op.uri,
       record.strength
     ])
   }
   ```

---

## 5. Identity Resolution

### 5.1 DID Resolution

**Implementation:** `packages/rhiz-protocol/src/identity.ts`

**Key Pattern: Cached Resolution**

```typescript
import { DidResolver } from '@atproto-labs/did-resolver'
import { LRUCache } from 'lru-cache'

export class RhizIdentityResolver {
  private resolver: DidResolver
  private cache: LRUCache<string, DidDocument>

  constructor() {
    this.resolver = new DidResolver({
      plcUrl: 'https://plc.directory',
      timeout: 3000
    })
    
    this.cache = new LRUCache({
      max: 10000,
      ttl: 1000 * 60 * 60 // 1 hour
    })
  }

  async resolveDid(did: string): Promise<DidDocument> {
    // Check cache first
    const cached = this.cache.get(did)
    if (cached) return cached
    
    // Resolve from PLC directory
    const didDoc = await this.resolver.resolve(did)
    
    // Cache result
    this.cache.set(did, didDoc)
    
    return didDoc
  }
}
```

**Design Decisions:**

1. **LRU Cache**
   - 10,000 entry limit
   - 1-hour TTL
   - Significantly reduces PLC lookups

2. **Handle Resolution**
   - Convert handle → DID via DNS lookup
   - Cache handle→DID mappings separately
   - Handles can change, DIDs don't

3. **Error Handling**
   - Retry failed resolutions (3 attempts)
   - Fallback to cached if PLC down
   - Log resolution failures

---

## 6. Trust Calculation

### 6.1 Trust Score Algorithm

**Implementation:** `services/rhiz-api/app/services/trust_engine.py`

**Formula:**

```python
def calculate_trust_score(entity_did: str) -> int:
    """
    Calculate trust score (0-100) for an entity.
    
    Factors:
    - Relationship count (more = higher trust)
    - Mutual relationships (reciprocity)
    - Relationship strength (average)
    - Attestations received (social proof)
    - Account age (older = more trusted)
    """
    
    # Get relationships
    relationships = get_relationships(entity_did)
    
    # Base score from relationship count (0-40 points)
    rel_count_score = min(40, len(relationships) * 2)
    
    # Reciprocity score (0-30 points)
    mutual = count_mutual_relationships(relationships)
    reciprocity_score = (mutual / len(relationships)) * 30 if relationships else 0
    
    # Strength score (0-20 points)
    avg_strength = sum(r.strength for r in relationships) / len(relationships) if relationships else 0
    strength_score = (avg_strength / 100) * 20
    
    # Attestation score (0-10 points)
    attestations = get_attestations_for_entity(entity_did)
    attestation_score = min(10, len(attestations))
    
    # Total (0-100)
    total = rel_count_score + reciprocity_score + strength_score + attestation_score
    
    return int(min(100, total))
```

**Design Decisions:**

1. **Weighted Components**
   - Relationship count: 40% (most important)
   - Reciprocity: 30% (mutual trust matters)
   - Strength: 20% (quality of relationships)
   - Attestations: 10% (social proof)

2. **Integer Output**
   - 0-100 range
   - No floats (AT Protocol compatibility)
   - Easy to understand ("85 trust")

3. **Cached Results**
   - Trust scores cached in database
   - Recalculated when relationships change
   - Max age: 24 hours

---

## 7. API Design

### 7.1 XRPC Endpoints

**AT Protocol Standard:** XRPC (Cross-Protocol RPC)

**Implementation:** `services/rhiz-api/app/api/`

**Key Endpoints:**

1. **Graph Queries**
   ```
   POST /xrpc/net.rhiz.graph.findPath
   GET  /xrpc/net.rhiz.graph.getNeighbors
   ```

2. **Entity Operations**
   ```
   GET  /xrpc/net.rhiz.entity.getProfile
   GET  /xrpc/net.rhiz.entity.resolve
   ```

3. **Conviction Queries**
   ```
   GET  /xrpc/net.rhiz.conviction.getScore
   GET  /xrpc/net.rhiz.conviction.listAttestations
   ```

**Pattern:**
```python
@router.post("/xrpc/net.rhiz.graph.findPath")
async def find_path(
    request: FindPathRequest,
    db: Session = Depends(get_db)
):
    """Find trust-weighted paths between entities"""
    
    # Validate inputs
    validate_did(request.from_did)
    validate_did(request.to_did)
    
    # Find paths
    paths = await pathfinder.find_paths(
        from_did=request.from_did,
        to_did=request.to_did,
        max_hops=request.max_hops or 6,
        min_strength=request.min_strength or 0
    )
    
    return {
        "paths": paths,
        "count": len(paths)
    }
```

---

## 8. Performance Optimizations

### 8.1 Database Indexing

**Key Indexes:**

```sql
-- Entity lookups
CREATE INDEX idx_entities_did ON entities(did);
CREATE INDEX idx_entities_handle ON entities(handle);

-- Relationship queries
CREATE INDEX idx_relationships_participants ON relationships USING gin(participants);
CREATE INDEX idx_relationships_created ON relationships(created_at DESC);

-- Graph traversal
CREATE INDEX idx_graph_edges_from ON graph_edges(from_did);
CREATE INDEX idx_graph_edges_to ON graph_edges(to_did);
CREATE INDEX idx_graph_edges_strength ON graph_edges(strength);

-- Attestation lookups
CREATE INDEX idx_attestations_target ON attestations(target_uri);
CREATE INDEX idx_attestations_attester ON attestations(attester_did);
```

---

### 8.2 Caching Strategy

**Layers:**

1. **Application Cache (Redis)**
   - Trust scores (1 hour TTL)
   - Conviction scores (5 minute TTL)
   - DID documents (1 hour TTL)

2. **Query Cache (PostgreSQL)**
   - Materialized views for complex queries
   - Refresh every 15 minutes

3. **CDN Cache**
   - Static assets (lexicon schemas)
   - Public profiles (1 hour TTL)

---

## 9. Testing

### 9.1 Unit Tests

**Pattern: Interop Test Files**

`interop-test-files/rhiz/relationship-record-valid.json`:
```json
{
  "$type": "net.rhiz.relationship.record",
  "participants": ["did:plc:test1", "did:plc:test2"],
  "type": "professional",
  "strength": 85,
  "signatures": [...]
}
```

**Validation:**
```typescript
test('valid relationship record', async () => {
  const record = require('./relationship-record-valid.json')
  const isValid = await validateRecord(record, schema)
  expect(isValid).toBe(true)
})
```

---

### 9.2 Integration Tests

**Pattern: End-to-End Flows**

```typescript
test('full relationship creation flow', async () => {
  // 1. Create entity profiles
  const alice = await client.entities.create({
    did: 'did:plc:alice',
    name: 'Alice',
    type: 'person'
  })
  
  // 2. Create relationship
  const rel = await client.createRelationship({
    participants: ['did:plc:alice', 'did:plc:bob'],
    type: 'professional',
    strength: 85
  })
  
  // 3. Verify indexed
  await waitForIndexing()
  
  // 4. Query relationship
  const queried = await client.getRelationship(rel.uri)
  expect(queried.strength).toBe(85)
  
  // 5. Create attestation
  const attestation = await client.attestRelationship({
    targetRelationship: rel.uri,
    attestationType: 'verify',
    confidence: 90
  })
  
  // 6. Verify conviction updated
  await waitForIndexing()
  const conviction = await client.getConviction(rel.uri)
  expect(conviction.score).toBeGreaterThan(0)
})
```

---

## 10. Lessons Learned

### 10.1 What Worked Well

1. **DIDs as Primary Keys**
   - Clean architecture
   - No UUID mapping needed
   - Cryptographically verifiable

2. **Integer Scores**
   - AT Protocol compatible
   - Better UX than floats
   - No comparison issues

3. **Firehose Indexing**
   - Real-time updates
   - Scales well
   - AT Protocol standard pattern

4. **Lexicon-First Development**
   - Generated types prevent errors
   - Single source of truth
   - Clear contracts

---

### 10.2 Challenges Overcome

1. **Dual Signatures**
   - Challenge: Two signatures in single-user repo
   - Solution: Progressive signature collection
   - Works but requires coordination

2. **Float Limitations**
   - Challenge: Lexicons don't support floats
   - Solution: Integer 0-100 scale everywhere
   - Actually better UX

3. **Graph Query Performance**
   - Challenge: Multi-hop queries slow on large graphs
   - Solution: Pre-computed edges, aggressive caching
   - Sub-second queries for 6 hops

---

### 10.3 Future Improvements

1. **Signature Negotiation**
   - Better UX for multi-party signatures
   - Push notifications for signature requests
   - Time-limited signature windows

2. **Advanced Caching**
   - Predict which paths users will query
   - Pre-compute popular paths
   - Cache warming strategies

3. **Batch Operations**
   - Create multiple relationships at once
   - Batch attestations
   - Bulk import from other platforms

---

## 11. Migration Guide

### 11.1 From Centralized Database

**If you have existing relationship data:**

1. **Generate DIDs for Entities**
   ```python
   for entity in old_entities:
       did = create_did(entity.email)
       entity.did = did
   ```

2. **Transform Relationships**
   ```python
   for rel in old_relationships:
       new_rel = {
           'participants': [
               entity_did_map[rel.user1_id],
               entity_did_map[rel.user2_id]
           ],
           'type': map_type(rel.type),
           'strength': rel.strength,
           'context': rel.description
       }
   ```

3. **Create AT Protocol Records**
   ```python
   for rel in new_relationships:
       await client.createRelationship(rel)
   ```

---

## 12. Deployment

### 12.1 Production Checklist

- [ ] Lexicon schemas validated
- [ ] Types generated from lexicons
- [ ] Database migrations run
- [ ] Indexes created
- [ ] Firehose indexer running
- [ ] API endpoints tested
- [ ] SDK published
- [ ] Monitoring set up
- [ ] Backup strategy in place
- [ ] Rate limiting configured

---

### 12.2 Monitoring

**Key Metrics:**
- Firehose lag (target: <5 seconds)
- API latency (target: <200ms p95)
- Trust calculation time (target: <100ms)
- Indexer throughput (target: 100+ records/sec)
- Error rate (target: <0.1%)

---

## Conclusion

This implementation guide captures the key patterns, decisions, and lessons from building Rhiz Protocol on AT Protocol. The architecture leverages AT Protocol's strengths (user-owned repos, federation, cryptographic verification) while adding relationship intelligence on top.

**Key Takeaways:**
- AT Protocol-native design from ground up
- DIDs as primary identifiers throughout
- Integer scores for AT Protocol compatibility
- Firehose indexing for real-time updates
- Trust algorithms that scale
- Developer experience matters

This serves as the reference implementation for Rhiz Protocol. Future implementations on other chains can learn from these patterns while adapting to their specific constraints.

---

**Guide Version:** 1.0  
**Date:** October 22, 2025  
**Maintained by:** Rhiz Protocol Team

