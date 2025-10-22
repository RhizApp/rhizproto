# Intuition Protocol Integration Analysis for Rhiz Protocol

## Executive Summary

This document analyzes the Intuition protocol's architecture and identifies concrete concepts that can enhance Rhiz Protocol. Intuition's attestation-based knowledge graph system offers powerful primitives that align with Rhiz's trust-weighted relationship intelligence.

**Key Takeaway:** Intuition's triple-based attestations + economic staking can transform Rhiz from "relationships exist" to "relationships are continuously validated by the network with skin in the game."

---

## Understanding Intuition Protocol

### Core Concepts

**1. Triple-Based Knowledge Graph**
- Subject-Predicate-Object structure for all claims
- Example: `Alice -> knows -> Bob` or `Alice -> trustScore -> 85`
- Composable, machine-readable statements about the world

**2. Attestation System**
- Anyone can attest to (validate) or dispute a triple
- Attestations are on-chain with cryptographic signatures
- Creates a "consensus layer" over factual claims

**3. Economic Staking**
- Attesters stake tokens when validating claims
- Correct attestations earn rewards
- False attestations lose stake (slashing)
- Creates economic incentive for truth

**4. Identity Vaults**
- Each entity has a vault (identity container)
- Stores all triples where entity is the subject
- Queryable, portable, owned by the entity

**5. Conviction Scores**
- Aggregate measure of network confidence in a claim
- Based on: number of attestations, stake amounts, attester reputation
- Dynamically updated as new attestations arrive

---

## What Rhiz Currently Has (Strengths to Build On)

| Capability | Current Implementation | AT Protocol Native |
|------------|------------------------|-------------------|
| **Identity** | DIDs as primary keys | ✅ Yes |
| **Relationships** | Dual-signature records in repos | ✅ Yes |
| **Trust Metrics** | Calculated scores (0-100) | ✅ Yes |
| **Verification** | Cryptographic signatures | ✅ Yes |
| **Federation** | Firehose indexing, AppView pattern | ✅ Yes |
| **Pathfinding** | Trust-weighted graph algorithms | ✅ Yes |
| **Portability** | Data in user repos | ✅ Yes |

**Gap:** Rhiz currently lacks **continuous validation**, **economic incentives**, and **network consensus mechanisms** for trust scores.

---

## Applicable Concepts from Intuition

### 🎯 Priority 1: High-Value, Low-Friction Integration

#### 1. Attestation Layer for Relationships

**Concept from Intuition:** Anyone can attest to the validity/strength of a claim.

**Applied to Rhiz:**
```typescript
// Current: Only the two participants sign a relationship
at://did:plc:alice/net.rhiz.relationship.record/3jx7ytmdwej2k
{
  participants: ['did:plc:alice', 'did:plc:bob'],
  strength: 85,
  signatures: [
    { did: 'did:plc:alice', signature: '...' },
    { did: 'did:plc:bob', signature: '...' }
  ]
}

// Enhanced: Third-party attestations validate the relationship
at://did:plc:carol/net.rhiz.relationship.attestation/3jx8abcdef123
{
  targetRelationship: 'at://did:plc:alice/net.rhiz.relationship.record/3jx7ytmdwej2k',
  attester: 'did:plc:carol',
  attestationType: 'verify' | 'dispute' | 'strengthen' | 'weaken',
  evidence: 'I worked with both Alice and Bob at TechCo for 2 years',
  confidence: 90,  // How confident is the attester (0-100)
  timestamp: '2025-10-22T10:00:00Z',
  signature: '...'
}
```

**Benefits:**
- **Network validation** - Relationships gain credibility from third-party attestations
- **Fraud detection** - Disputed relationships flagged automatically
- **Dynamic trust** - Relationship strength updates based on community input
- **Reputation building** - Attesters build reputation through accurate validation

**Implementation:**
1. New lexicon schema: `net.rhiz.relationship.attestation` (record)
2. Attestations stored in attester's repo (user-owned)
3. AppView indexes attestations and updates relationship conviction scores
4. Query API: `getAttestations(relationshipUri)` returns all attestations for a relationship

---

#### 2. Conviction Scores for Trust Metrics

**Concept from Intuition:** Aggregate network confidence in a claim based on attestations.

**Applied to Rhiz:**
```typescript
// Current: Trust scores are calculated, but not network-validated
{
  trustScore: 88,
  reputation: 91,
  reciprocity: 85
}

// Enhanced: Conviction-backed trust with network consensus
{
  trustScore: 88,
  conviction: {
    score: 87,  // Network's confidence in this trust score (0-100)
    attestationCount: 15,  // Number of attestations supporting this
    lastUpdated: '2025-10-22T10:00:00Z',
    trend: 'increasing' | 'stable' | 'decreasing'
  },
  reputation: 91,
  reputationConviction: {
    score: 93,
    attestationCount: 42,
    lastUpdated: '2025-10-22T10:00:00Z',
    trend: 'stable'
  }
}
```

**Benefits:**
- **Trust the trust** - Meta-level confidence in trust scores
- **Gaming resistance** - Hard to fake when network validates
- **Temporal awareness** - Conviction trends show trust momentum
- **Quality signal** - High conviction = highly reliable metric

**Implementation:**
1. Extend `net.rhiz.trust.metrics` schema with conviction fields
2. Calculate conviction scores from attestations during indexing
3. Weight attestations by attester reputation (recursive trust)
4. Display conviction in UI: "85 trust (92% network confidence)"

---

#### 3. Triple-Based Relationship Claims

**Concept from Intuition:** Subject-Predicate-Object structure for all knowledge.

**Applied to Rhiz:**
```typescript
// Current: Relationships are complex objects
{
  participants: ['did:plc:alice', 'did:plc:bob'],
  type: 'professional',
  strength: 85,
  context: 'Co-founded TechCo'
}

// Enhanced: Decompose into atomic triples for composability
Triples:
1. did:plc:alice -> net.rhiz.relationship.hasRelationship -> did:plc:bob
2. did:plc:alice -> net.rhiz.relationship.strength -> 85 (context: did:plc:bob)
3. did:plc:alice -> net.rhiz.relationship.type -> "professional" (context: did:plc:bob)
4. did:plc:alice -> net.rhiz.relationship.context -> "Co-founded TechCo" (context: did:plc:bob)

// Each triple can be independently attested
Attestation 1: did:plc:carol attests triple #1 with confidence 95
Attestation 2: did:plc:david attests triple #2 but suggests strength 90
Attestation 3: did:plc:eve disputes triple #3, suggests "personal" instead
```

**Benefits:**
- **Granular validation** - Attest specific claims, not whole relationships
- **Composability** - Triples are universal primitives
- **Queryability** - "Show all did:plc:alice -> strength -> >80"
- **Interoperability** - Standard RDF/semantic web integration

**Implementation:**
1. New schema: `net.rhiz.triple.claim` for atomic statements
2. Link triples to parent relationship record (for backwards compatibility)
3. Query engine supports triple pattern matching
4. UI shows conviction per triple: "Strength: 85 (90% confidence)"

---

#### 4. Identity Vaults → Entity Profiles

**Concept from Intuition:** Each identity has a vault storing all claims where they're the subject.

**Applied to Rhiz:**
```typescript
// Current: Entity profiles are basic
at://did:plc:alice/net.rhiz.entity.profile/self
{
  did: 'did:plc:alice',
  name: 'Alice Chen',
  type: 'person',
  attributes: { bio: '...', skills: [...] }
}

// Enhanced: Profile includes all triples + attestations about this entity
at://did:plc:alice/net.rhiz.entity.profile/self
{
  did: 'did:plc:alice',
  name: 'Alice Chen',
  type: 'person',

  // Aggregate view of all knowledge about Alice
  vault: {
    relationships: 47,  // Count of hasRelationship triples
    attestationsReceived: 312,  // Third-party validations
    convictionScore: 92,  // Network confidence in Alice's data

    // Queryable triples where Alice is subject
    triples: {
      'net.rhiz.relationship.hasRelationship': 47,
      'net.rhiz.trust.score': 1,
      'net.rhiz.expertise.domain': 5,
      'net.rhiz.credential.verified': 8
    }
  }
}
```

**Benefits:**
- **Comprehensive identity** - All knowledge about an entity in one place
- **Reputation aggregate** - Vault conviction = overall trustworthiness
- **Portable** - Export entire vault to move between services
- **Queryable** - "Show me all engineers (expertise.domain = 'engineering') with conviction > 80"

**Implementation:**
1. Extend `net.rhiz.entity.profile` with vault metadata
2. AppView maintains vault index per entity
3. API endpoint: `getVault(did)` returns aggregated view
4. Real-time vault updates via firehose

---

### 🎯 Priority 2: Medium-Term Value (Phase 2-3)

#### 5. Economic Staking for Attestations

**Concept from Intuition:** Attesters stake tokens; correct attestations earn rewards, false ones get slashed.

**Applied to Rhiz:**
```typescript
// Attestation with economic commitment
at://did:plc:carol/net.rhiz.relationship.attestation/3jx8abcdef123
{
  targetRelationship: 'at://...',
  attester: 'did:plc:carol',
  attestationType: 'verify',
  confidence: 90,

  // Economic layer
  stake: {
    amount: 100,  // Tokens staked on this attestation
    token: 'RHIZ',  // Native protocol token
    lockedUntil: '2025-11-22T10:00:00Z',  // Time lock period
    slashingRisk: 0.2  // 20% if proven false
  }
}

// Slashing event if attestation proven false
{
  event: 'attestation_slashed',
  attestation: 'at://did:plc:carol/net.rhiz.relationship.attestation/3jx8abcdef123',
  reason: 'Relationship proven fraudulent',
  slashedAmount: 20,  // 20% of 100
  beneficiaries: [
    { did: 'did:plc:alice', amount: 10 },  // Original victim
    { did: 'did:plc:david', amount: 10 }   // Reporter of fraud
  ]
}
```

**Benefits:**
- **Skin in the game** - Attesters economically committed to truth
- **Sybil resistance** - Expensive to create fake attestations at scale
- **Quality incentive** - Earn rewards for accurate validation
- **Network security** - Economic cost to attack the trust layer

**Implementation Considerations:**
- **Token design** - RHIZ token for staking (ERC-20 on Base or native AT Protocol asset)
- **Slashing rules** - Clear criteria for false attestations
- **Reward distribution** - How to split fees/rewards
- **Time locks** - Attestation challenge period before unstaking
- **Bootstrap** - No-stake version first, add staking in Phase 3

**⚠️ Complexity:** High - requires token economics, smart contracts, dispute resolution.

**🔮 Timeline:** Phase 3 (after core attestation system proven)

---

#### 6. Expertise/Skill Attestations

**Concept from Intuition:** Not just relationships, but any attribute can be attested.

**Applied to Rhiz:**
```typescript
// Alice claims expertise in AI/ML
at://did:plc:alice/net.rhiz.expertise.claim/3jx9mlskills
{
  subject: 'did:plc:alice',
  domain: 'artificial_intelligence',
  subdomains: ['machine_learning', 'nlp', 'computer_vision'],
  level: 'expert',  // beginner | intermediate | advanced | expert
  selfAssessed: true
}

// Bob attests to Alice's AI expertise
at://did:plc:bob/net.rhiz.expertise.attestation/3jx9attestml
{
  targetClaim: 'at://did:plc:alice/net.rhiz.expertise.claim/3jx9mlskills',
  attester: 'did:plc:bob',
  attestationType: 'verify',
  evidence: 'Worked with Alice on ML project for 2 years, she led architecture',
  confidence: 95,
  domains: ['machine_learning', 'nlp']  // Specific subdomains Bob can vouch for
}

// Network conviction for Alice's AI expertise
{
  domain: 'artificial_intelligence',
  claimedLevel: 'expert',
  conviction: {
    score: 91,  // Network agrees with 91% confidence
    attestationCount: 23,
    expertAttestations: 8,  // Attestations from other AI experts (weighted higher)
    lastUpdated: '2025-10-22T10:00:00Z'
  }
}
```

**Benefits:**
- **Verified skills** - Not self-reported, network-validated
- **Context matching** - Find intros based on verified expertise
- **Anti-resume fraud** - Can't claim skills without attestations
- **Dynamic CVs** - Skills gain/lose conviction over time

**Use Cases:**
- **FundRhiz:** Match founders to investors by verified domain expertise
- **Hiring:** Verify candidate skills through network attestations
- **Collaboration:** Find experts for projects based on conviction scores

**Implementation:**
1. New schemas: `net.rhiz.expertise.claim` and `net.rhiz.expertise.attestation`
2. Taxonomy of domains/subdomains (using industry standards)
3. Expert attestations weighted higher (recursive trust)
4. Search API: `findExperts({ domain: 'AI', minConviction: 80 })`

---

#### 7. Credential/Achievement Attestations

**Concept from Intuition:** Facts about entities can be attested (degrees, certifications, achievements).

**Applied to Rhiz:**
```typescript
// Alice claims she has Stanford CS degree
at://did:plc:alice/net.rhiz.credential.claim/3jx9stanford
{
  subject: 'did:plc:alice',
  credentialType: 'degree',
  institution: 'Stanford University',
  field: 'Computer Science',
  level: 'bachelor',
  graduationYear: 2018,
  selfReported: true
}

// Stanford (official DID) attests to the degree
at://did:plc:stanford/net.rhiz.credential.attestation/3jx9verify
{
  targetClaim: 'at://did:plc:alice/net.rhiz.credential.claim/3jx9stanford',
  attester: 'did:plc:stanford',  // Official institutional DID
  attestationType: 'verify',
  official: true,  // This is an authoritative source
  verificationMethod: 'registrar_database',
  confidence: 100,
  timestamp: '2025-10-22T10:00:00Z',
  signature: '...'  // Signed by Stanford's institutional key
}

// Network conviction is 100% because official source
{
  credentialType: 'degree',
  conviction: {
    score: 100,
    attestationCount: 1,
    officialAttestation: true,  // Authoritative source verified
    lastUpdated: '2025-10-22T10:00:00Z'
  }
}
```

**Benefits:**
- **Zero-knowledge credentials** - Prove claims without exposing PII
- **Official verification** - Institutions can attest directly
- **Fraud prevention** - Can't fake degrees/certs with official attestations
- **Interoperability** - Integrate with W3C Verifiable Credentials

**Use Cases:**
- **Professional networking** - Verified credentials in profiles
- **Background checks** - Query conviction for claimed credentials
- **Alumni networks** - Schools attest to graduate DIDs

**Implementation:**
1. New schemas: `net.rhiz.credential.claim` and `net.rhiz.credential.attestation`
2. Registry of official institutional DIDs (universities, companies, governments)
3. Official attestations weighted as authoritative (conviction = 100)
4. Integration with W3C VC standard for interop

---

#### 8. Event/Interaction Attestations

**Concept from Intuition:** Specific events can be attested (meetings, collaborations, transactions).

**Applied to Rhiz:**
```typescript
// Alice claims she met Bob at TechConf 2024
at://did:plc:alice/net.rhiz.event.claim/3jx9techconf
{
  subject: 'did:plc:alice',
  eventType: 'in_person_meeting',
  participants: ['did:plc:alice', 'did:plc:bob'],
  eventName: 'TechConf 2024',
  location: 'San Francisco, CA',
  date: '2024-06-15',
  context: 'Met at AI panel, discussed collaboration'
}

// Bob confirms the meeting
at://did:plc:bob/net.rhiz.event.attestation/3jx9confirm
{
  targetClaim: 'at://did:plc:alice/net.rhiz.event.claim/3jx9techconf',
  attester: 'did:plc:bob',
  attestationType: 'verify',
  confidence: 100,
  note: 'Yes, we discussed potential partnership'
}

// Carol also saw them together
at://did:plc:carol/net.rhiz.event.attestation/3jx9witness
{
  targetClaim: 'at://did:plc:alice/net.rhiz.event.claim/3jx9techconf',
  attester: 'did:plc:carol',
  attestationType: 'verify',
  confidence: 95,
  evidence: 'I saw them talking at the conference reception'
}

// Conviction is high (100) because participant confirmed
{
  eventType: 'in_person_meeting',
  conviction: {
    score: 100,
    attestationCount: 2,
    participantConfirmed: true,  // Bob confirmed
    witnessCount: 1,  // Carol witnessed
    lastUpdated: '2025-10-22T10:00:00Z'
  }
}
```

**Benefits:**
- **Relationship history** - Verified timeline of interactions
- **Context building** - Rich background for introductions
- **Trust decay modeling** - Recent interactions strengthen trust
- **Dispute resolution** - Timestamped, attested events for conflicts

**Use Cases:**
- **Introduction context** - "Alice and Bob met at TechConf 2024 (verified)"
- **Relationship freshness** - "Last interaction 3 months ago (attested)"
- **Network analytics** - "Alice has 15 in-person meetings this year (verified)"

**Implementation:**
1. New schemas: `net.rhiz.event.claim` and `net.rhiz.event.attestation`
2. Event taxonomy (meeting, collaboration, transaction, introduction, etc.)
3. Participant attestations weighted highest
4. Timeline view in UI showing attested events

---

### 🎯 Priority 3: Future Innovation (Phase 3-4)

#### 9. Reputation Markets

**Concept from Intuition:** Conviction scores create markets for reputation.

**Applied to Rhiz:**
- **Reputation NFTs** - High-conviction entities can mint reputation tokens
- **Trust as collateral** - Borrow against your network trust score
- **Attestation services** - High-reputation users charge fees for attestations
- **Trust insurance** - Insure against trust score drops

**⚠️ Complexity:** Very high - requires mature token economics and DeFi integration.

---

#### 10. Dispute Resolution Mechanism

**Concept from Intuition:** When attestations conflict, there's a resolution process.

**Applied to Rhiz:**
```typescript
// Alice claims relationship strength is 85
// Bob disputes, says it's only 60
// Dispute resolution via multi-party attestations

{
  dispute: {
    originalClaim: 'at://did:plc:alice/net.rhiz.relationship.record/3jx7ytmdwej2k',
    disputedField: 'strength',
    originalValue: 85,
    disputedValue: 60,
    disputant: 'did:plc:bob',

    resolution: {
      method: 'attestation_vote',
      attestations: [
        { attester: 'did:plc:carol', suggestedValue: 70, weight: 1.2 },
        { attester: 'did:plc:david', suggestedValue: 65, weight: 1.0 },
        { attester: 'did:plc:eve', suggestedValue: 80, weight: 1.5 }
      ],
      resolvedValue: 72,  // Weighted average
      conviction: 85,  // Network confidence in resolution
      finalized: '2025-10-23T10:00:00Z'
    }
  }
}
```

**Benefits:**
- **Conflict resolution** - Disagreements resolved by network
- **Gaming resistance** - Can't unilaterally claim false strengths
- **Fairness** - Weighted by attester reputation
- **Transparency** - All dispute history visible

---

## Implementation Roadmap

### Phase 2A: Core Attestation System (Q1 2026)

**Goal:** Enable third-party attestations on relationships without economic layer.

**Tasks:**
1. ✅ Design lexicon schemas
   - `net.rhiz.relationship.attestation`
   - `net.rhiz.trust.attestation`
2. ✅ Implement conviction score calculation
3. ✅ Update AppView to index attestations
4. ✅ API endpoints for attestations
5. ✅ UI for viewing/submitting attestations
6. ✅ Tests and validation

**Deliverables:**
- Users can attest to relationships
- Conviction scores visible in UI
- API returns attestation counts + conviction

**Metrics:**
- Attestation adoption rate
- Conviction score accuracy vs. self-reported
- Fraud detection rate (disputes vs. verifications)

---

### Phase 2B: Triple-Based Claims (Q2 2026)

**Goal:** Decompose relationships into atomic triples for granular attestation.

**Tasks:**
1. ✅ Design `net.rhiz.triple.claim` schema
2. ✅ Implement triple pattern matching
3. ✅ Migrate existing relationships to triple representation
4. ✅ Update UI for triple-level attestations
5. ✅ Query engine for triple searches

**Deliverables:**
- Relationships represented as composable triples
- Attestations at triple level (not just whole relationships)
- Query: "Find all did:plc:alice -> strength -> >80"

---

### Phase 2C: Expertise & Credentials (Q3 2026)

**Goal:** Extend attestations to skills, credentials, achievements.

**Tasks:**
1. ✅ Design expertise/credential schemas
2. ✅ Build domain taxonomy
3. ✅ Integrate with institutional DIDs
4. ✅ Context-aware matching using expertise
5. ✅ Search by verified skills

**Deliverables:**
- Users can claim and attest to expertise
- Institutional credential verification
- FundRhiz uses expertise for investor matching

---

### Phase 3A: Economic Staking (Q1 2027)

**Goal:** Add economic layer to attestations with staking and slashing.

**Tasks:**
1. ✅ Design RHIZ token economics
2. ✅ Smart contract for staking (Base L2)
3. ✅ Slashing mechanism
4. ✅ Reward distribution
5. ✅ Bridge AT Protocol ↔ on-chain

**Deliverables:**
- RHIZ token deployed
- Attesters can stake on claims
- Slashing for false attestations
- Economic security guarantees

---

### Phase 3B: Reputation Markets (Q2 2027)

**Goal:** Enable reputation-based financial primitives.

**Tasks:**
1. ✅ Reputation NFTs
2. ✅ Trust-based collateral
3. ✅ Attestation marketplace
4. ✅ Trust insurance products

**Deliverables:**
- Reputation tradable/usable as collateral
- Market for high-value attestations
- Trust-based DeFi primitives

---

## Technical Architecture

### Lexicon Schema Additions

```
lexicons/net/rhiz/
  relationship/
    attestation.json          [NEW] Third-party validation of relationships
  trust/
    attestation.json          [NEW] Validation of trust metrics
  triple/
    claim.json                [NEW] Atomic subject-predicate-object statements
    attestation.json          [NEW] Validation of triple claims
  expertise/
    claim.json                [NEW] Skill/domain expertise claims
    attestation.json          [NEW] Validation of expertise
  credential/
    claim.json                [NEW] Degree/certification claims
    attestation.json          [NEW] Validation of credentials
  event/
    claim.json                [NEW] Meeting/interaction claims
    attestation.json          [NEW] Validation of events
  conviction/
    defs.json                 [NEW] Conviction score definitions
  stake/
    record.json               [NEW] Economic staking records
    defs.json                 [NEW] Staking parameters
```

### Database Schema Additions

```sql
-- Attestations table
CREATE TABLE attestations (
  uri TEXT PRIMARY KEY,
  attester_did TEXT NOT NULL,
  target_uri TEXT NOT NULL,
  attestation_type TEXT NOT NULL,  -- verify | dispute | strengthen | weaken
  confidence INTEGER NOT NULL,  -- 0-100
  evidence TEXT,
  created_at TIMESTAMP NOT NULL,
  indexed_at TIMESTAMP NOT NULL,

  -- Economic fields (Phase 3)
  stake_amount NUMERIC,
  token TEXT,
  locked_until TIMESTAMP,
  slashed BOOLEAN DEFAULT FALSE,

  FOREIGN KEY (attester_did) REFERENCES entities(did)
);

CREATE INDEX idx_attestations_target ON attestations(target_uri);
CREATE INDEX idx_attestations_attester ON attestations(attester_did);
CREATE INDEX idx_attestations_type ON attestations(attestation_type);

-- Conviction scores cache
CREATE TABLE conviction_scores (
  target_uri TEXT PRIMARY KEY,
  score INTEGER NOT NULL,  -- 0-100
  attestation_count INTEGER NOT NULL,
  verify_count INTEGER NOT NULL,
  dispute_count INTEGER NOT NULL,
  last_updated TIMESTAMP NOT NULL,
  trend TEXT  -- increasing | stable | decreasing
);

-- Triples table
CREATE TABLE triples (
  uri TEXT PRIMARY KEY,
  subject_did TEXT NOT NULL,
  predicate TEXT NOT NULL,
  object TEXT NOT NULL,
  context_uri TEXT,  -- Optional: links to parent record
  created_at TIMESTAMP NOT NULL,
  conviction_score INTEGER,

  FOREIGN KEY (subject_did) REFERENCES entities(did)
);

CREATE INDEX idx_triples_subject ON triples(subject_did);
CREATE INDEX idx_triples_predicate ON triples(predicate);
CREATE INDEX idx_triples_pattern ON triples(subject_did, predicate);

-- Expertise claims
CREATE TABLE expertise_claims (
  uri TEXT PRIMARY KEY,
  subject_did TEXT NOT NULL,
  domain TEXT NOT NULL,
  level TEXT NOT NULL,  -- beginner | intermediate | advanced | expert
  self_assessed BOOLEAN DEFAULT TRUE,
  conviction_score INTEGER,
  attestation_count INTEGER DEFAULT 0,

  FOREIGN KEY (subject_did) REFERENCES entities(did)
);

CREATE INDEX idx_expertise_domain ON expertise_claims(domain);
CREATE INDEX idx_expertise_conviction ON expertise_claims(conviction_score DESC);
```

### API Endpoint Additions

```typescript
// Attestation endpoints
POST   /xrpc/net.rhiz.relationship.attestation.create
GET    /xrpc/net.rhiz.relationship.attestation.get
GET    /xrpc/net.rhiz.relationship.attestation.list
POST   /xrpc/net.rhiz.relationship.attestation.delete

// Conviction queries
GET    /xrpc/net.rhiz.conviction.getScore?uri=at://...
GET    /xrpc/net.rhiz.conviction.getTrend?uri=at://...
GET    /xrpc/net.rhiz.conviction.getAttestations?uri=at://...

// Triple operations
POST   /xrpc/net.rhiz.triple.create
GET    /xrpc/net.rhiz.triple.query
  // Pattern matching: { subject?, predicate?, object? }

// Expertise
POST   /xrpc/net.rhiz.expertise.claim.create
POST   /xrpc/net.rhiz.expertise.attestation.create
GET    /xrpc/net.rhiz.expertise.search
  // Search by domain, min conviction, etc.

// Staking (Phase 3)
POST   /xrpc/net.rhiz.stake.create
POST   /xrpc/net.rhiz.stake.withdraw
GET    /xrpc/net.rhiz.stake.getBalance
```

---

## Key Insights & Recommendations

### 1. Start with No-Stake Attestations (Phase 2A)

**Why:** Prove the attestation model works before adding economic complexity.

**Approach:**
- Let users attest relationships/trust for free
- Build conviction score algorithm
- Measure adoption and accuracy
- **Then** add staking layer once proven

**Risk Mitigation:** If attestations aren't adopted without economic incentives, no sense building token economics.

---

### 2. Leverage AT Protocol's Strengths

**Intuition is on-chain (Ethereum). Rhiz is AT Protocol.**

**Advantages:**
- **No gas fees** - Attestations stored in user repos, not blockchain
- **Scalability** - Firehose handles millions of attestations
- **User ownership** - Attestations live in attester's repo
- **Federation** - Multiple AppViews can index attestations

**Hybrid Approach (Best of Both Worlds):**
- **L1 (AT Protocol):** Attestations, conviction, identity, relationships
- **L2 (Optional blockchain):** Economic staking, slashing, token rewards
- **Bridge:** Cross-reference AT URIs ↔ on-chain stakes

---

### 3. Conviction = Anti-Gaming Mechanism

**Problem:** Without attestations, users can inflate their own trust scores.

**Solution:** Conviction scores make self-reported data verifiable.

**Example:**
```
Alice self-reports trust score: 95
Network conviction: 45 (low confidence)
→ UI shows: "Trust: 95 (45% verified)" with warning icon

Bob self-reports trust score: 85
Network conviction: 92 (high confidence)
→ UI shows: "Trust: 85 (92% verified)" with checkmark
```

**User learns:** High conviction is the goal, not high self-reported scores.

---

### 4. Attestations Drive Network Effects

**Mechanic:** The more attestations exist, the more valuable the network.

**Incentive Design:**
- **Early attesters** earn reputation as validators
- **Attested entities** rank higher in searches
- **High-conviction paths** prioritized in introductions

**Viral Loop:**
1. Alice attests Bob's relationship
2. Bob's conviction increases
3. Bob appears higher in search results
4. More people request intros to Bob
5. Bob asks his connections to attest his relationships
6. More attestations = stronger network

---

### 5. Expertise Attestations → Smart Matching

**FundRhiz Use Case:**

```typescript
// Founder searching for investors
findInvestors({
  expertiseRequired: ['artificial_intelligence', 'healthcare'],
  minConviction: 80,  // Only highly-verified expertise
  minTrustPath: 50,   // Must have trust path to founder
  maxHops: 4
})

// Returns investors with:
// 1. Verified AI + healthcare expertise (conviction > 80)
// 2. Warm path to founder (trust-weighted)
// 3. Ranked by: (expertise conviction * path strength)
```

**Result:** Highest-quality investor matches, not just "who has the most connections."

---

### 6. Institutional Attestations = Authority Layer

**Key Insight:** Some attestations are authoritative (universities, companies, governments).

**Implementation:**
1. **Registry of official DIDs** - did:plc:stanford, did:plc:ycombinator, etc.
2. **Official attestations = conviction 100** - Authoritative sources bypass network voting
3. **Credential interop** - Integrate W3C Verifiable Credentials

**Example:**
```typescript
// Stanford attests Alice graduated
{
  attester: 'did:plc:stanford',
  official: true,
  conviction: 100  // Authoritative
}

// vs. Bob attests Alice graduated
{
  attester: 'did:plc:bob',
  official: false,
  conviction: 65  // Hearsay, lower confidence
}
```

---

### 7. Temporal Dynamics + Attestations

**Combine Rhiz's temporal modeling with Intuition's conviction:**

```typescript
{
  temporal: {
    start: '2020-01-01',
    lastInteraction: '2025-10-01',
    history: [
      { timestamp: '2020-01-01', strength: 70, conviction: 60 },
      { timestamp: '2022-06-01', strength: 80, conviction: 75 },
      { timestamp: '2025-10-01', strength: 85, conviction: 92 }
    ]
  }
}
```

**Insights:**
- **Conviction momentum** - Increasing conviction = relationship strengthening
- **Trust decay** - Old attestations lose weight over time
- **Quality signal** - Recent high-conviction attestations most valuable

---

## Comparison Matrix: Intuition vs. Rhiz (Enhanced)

| Aspect | Intuition | Rhiz (Current) | Rhiz (Enhanced) |
|--------|-----------|----------------|-----------------|
| **Identity** | Ethereum addresses | AT Protocol DIDs | AT Protocol DIDs |
| **Storage** | On-chain (Ethereum) | AT Protocol repos | AT Protocol repos |
| **Data Structure** | Triples | Complex objects | Triples + objects |
| **Validation** | Attestations with stake | Dual signatures | Dual signatures + attestations |
| **Economics** | Token staking | None | Optional staking (Phase 3) |
| **Conviction** | Yes | No | Yes (Phase 2A) |
| **Composability** | RDF triples | AT URIs | Triples + AT URIs |
| **Federation** | No (single chain) | Yes (firehose) | Yes (firehose) |
| **Gas Fees** | Yes (Ethereum) | No (AT Protocol) | No (AT Protocol) |
| **Portability** | Limited | Full (repos) | Full (repos) |
| **Trust Metrics** | Conviction only | Calculated scores | Calculated + convicted |

**Key Takeaway:** Rhiz can adopt Intuition's validation model while keeping AT Protocol's federation + portability advantages.

---

## Success Metrics

### Phase 2A (Attestation System)

- **Adoption:** 30% of relationships have ≥1 attestation within 6 months
- **Quality:** Conviction scores correlate 0.8+ with manual truth validation
- **Fraud:** 95%+ of disputed relationships flagged within 7 days
- **UX:** Attestation flow <30 seconds, 80%+ completion rate

### Phase 2B (Triple-Based)

- **Coverage:** 90%+ of relationships decomposed into triples
- **Queryability:** Triple pattern queries <100ms for 10M triples
- **Granularity:** 40%+ of attestations target specific triples, not whole relationships

### Phase 2C (Expertise)

- **Skill Coverage:** Top 100 domains have 1000+ claimed experts each
- **Conviction:** Average expertise conviction >75 for top domains
- **Matching:** Expertise-based intro success rate 50%+ higher than random

### Phase 3A (Economic Staking)

- **Economic Security:** $1M+ total value staked on attestations
- **Slashing:** <1% false positive slashing rate
- **ROI:** Attesters earn 10%+ APY on staked tokens
- **Participation:** 20%+ of attesters stake tokens

---

## Conclusion

### What to Build First

**Immediate (Start in Q1 2026):**

1. **Attestation schema** - `net.rhiz.relationship.attestation`
2. **Conviction calculation** - Algorithm for scoring network confidence
3. **AppView indexing** - Ingest attestations from firehose
4. **API endpoints** - Create, query, list attestations
5. **UI integration** - Display conviction scores in relationship views

**Why this order:**
- **Low friction** - No tokens, no economics, just social validation
- **High value** - Conviction immediately improves trust signal
- **Fast feedback** - See if users attest relationships organically
- **De-risked** - Prove model before building complex econ layer

### The Big Picture

**Intuition Protocol's core insight:**
*Truth emerges from economic consensus when people stake value on claims.*

**Rhiz Protocol's adaptation:**
*Trust emerges from social consensus when people attest to relationships.*

**The synthesis:**
*AT Protocol's user-owned repos + Intuition's attestation model = **Verifiable, portable, consensus-backed trust intelligence***

This is the evolution from:
- "Alice says she knows Bob" (unverified)
- "Alice and Bob both signed a relationship" (dual-verified)
- "Alice, Bob, and 15 others attest to their strong relationship with 90% conviction" (network-verified)

**That's the upgrade.**

---

## Next Steps

1. **Review this analysis** - Validate priorities and approach
2. **Design attestation lexicon** - Start with `net.rhiz.relationship.attestation.json`
3. **Prototype conviction algorithm** - Test on existing relationship data
4. **User research** - Interview potential attesters about incentives
5. **Build Phase 2A** - Ship attestation system without economics
6. **Measure adoption** - Track attestation rates and conviction accuracy
7. **Iterate** - Adjust algorithm and UX based on real usage
8. **Phase 2B/C** - Expand to triples, expertise, credentials
9. **Phase 3** - Add economic layer only if organic adoption validated

---

**Document Status:** Draft for review
**Author:** AI Analysis based on Intuition whitepaper
**Date:** October 22, 2025
**Version:** 1.0

