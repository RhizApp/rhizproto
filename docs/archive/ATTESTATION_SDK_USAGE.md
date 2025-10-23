# Attestation SDK Usage Guide

Quick reference for using the Rhiz SDK attestation features.

---

## Installation

```bash
pnpm add @atproto/rhiz-sdk
```

---

## Basic Setup

```typescript
import { RhizClient } from '@atproto/rhiz-sdk'

const client = new RhizClient({
  apiUrl: 'https://api.rhiz.network',
  atproto: {
    service: 'https://bsky.social'
  }
})

// Login to AT Protocol
await client.login('alice.bsky.social', 'password')
```

---

## Attesting to a Relationship

```typescript
// Attest to verify a relationship
const attestation = await client.conviction.attestRelationship({
  targetRelationship: 'at://did:plc:alice/net.rhiz.relationship.record/abc123',
  attestationType: 'verify',
  confidence: 90,
  evidence: 'I worked with both Alice and Bob at TechCo for 2 years'
})

console.log('Attestation created:', attestation.uri)
// at://did:plc:carol/net.rhiz.relationship.attestation/xyz789
```

### Attestation Types

- **`verify`** - Confirms the relationship exists as stated
- **`dispute`** - Questions the accuracy of the relationship
- **`strengthen`** - Suggests relationship is stronger than stated
- **`weaken`** - Suggests relationship is weaker than stated

### Example: Dispute a Relationship

```typescript
await client.conviction.attestRelationship({
  targetRelationship: 'at://did:plc:alice/net.rhiz.relationship.record/abc123',
  attestationType: 'dispute',
  confidence: 85,
  evidence: 'I know both parties and they barely know each other'
})
```

### Example: Suggest Stronger Relationship

```typescript
await client.conviction.attestRelationship({
  targetRelationship: 'at://did:plc:alice/net.rhiz.relationship.record/abc123',
  attestationType: 'strengthen',
  confidence: 80,
  evidence: 'They worked together for 5 years, not 2',
  suggestedStrength: 95  // Suggest strength should be 95 instead of stated value
})
```

---

## Getting Conviction Scores

```typescript
// Get conviction score for a relationship
const conviction = await client.conviction.getConviction(
  'at://did:plc:alice/net.rhiz.relationship.record/abc123'
)

console.log(`Conviction: ${conviction.conviction.score}/100`)
console.log(`Attestations: ${conviction.conviction.attestationCount}`)
console.log(`Verifications: ${conviction.conviction.verifyCount}`)
console.log(`Disputes: ${conviction.conviction.disputeCount}`)
console.log(`Trend: ${conviction.conviction.trend}`)

// Example output:
// Conviction: 87/100
// Attestations: 15
// Verifications: 14
// Disputes: 1
// Trend: increasing
```

---

## Listing Attestations

```typescript
// Get all attestations for a relationship
const result = await client.conviction.listAttestations({
  uri: 'at://did:plc:alice/net.rhiz.relationship.record/abc123',
  limit: 50
})

for (const attestation of result.attestations) {
  console.log(`${attestation.record.attestationType} by ${attestation.attester?.name}`)
  console.log(`  Confidence: ${attestation.record.confidence}%`)
  console.log(`  Evidence: ${attestation.record.evidence}`)
  console.log(`  Attester reputation: ${attestation.attesterReputation}/100`)
}
```

### Filter Attestations

```typescript
// Get only verify attestations with high confidence
const verifications = await client.conviction.listAttestations({
  uri: 'at://did:plc:alice/net.rhiz.relationship.record/abc123',
  type: 'verify',
  minConfidence: 80,
  limit: 20
})
```

### Pagination

```typescript
let cursor: string | undefined = undefined
const allAttestations = []

do {
  const result = await client.conviction.listAttestations({
    uri: 'at://did:plc:alice/net.rhiz.relationship.record/abc123',
    limit: 50,
    cursor
  })

  allAttestations.push(...result.attestations)
  cursor = result.cursor
} while (cursor)

console.log(`Total attestations: ${allAttestations.length}`)
```

---

## Batch Operations

```typescript
// Get conviction for multiple relationships at once
const uris = [
  'at://did:plc:alice/net.rhiz.relationship.record/abc123',
  'at://did:plc:alice/net.rhiz.relationship.record/def456',
  'at://did:plc:alice/net.rhiz.relationship.record/ghi789',
]

const convictions = await client.conviction.getConvictionBatch(uris)

for (const conviction of convictions) {
  console.log(`${conviction.uri}: ${conviction.conviction.score}/100`)
}
```

---

## Complete Example: Relationship with Attestations

```typescript
import { RhizClient } from '@atproto/rhiz-sdk'

async function main() {
  // Initialize client
  const client = new RhizClient({
    apiUrl: 'https://api.rhiz.network',
    atproto: { service: 'https://bsky.social' }
  })

  // Login
  await client.login('alice.bsky.social', 'password')

  // Create relationship
  const relationship = await client.repo.createRelationship('did:plc:alice', {
    participants: ['did:plc:alice', 'did:plc:bob'],
    type: 'professional',
    strength: 85,
    context: 'Co-founded TechCo in 2020',
    // ... other fields
  })

  console.log('Relationship created:', relationship.uri)

  // Get initial conviction (should be 0 - no attestations yet)
  try {
    const conviction = await client.conviction.getConviction(relationship.uri)
    console.log('Initial conviction:', conviction.conviction.score)
  } catch (e) {
    console.log('No attestations yet')
  }

  // Login as another user to attest
  await client.login('carol.bsky.social', 'password')

  // Attest to the relationship
  await client.conviction.attestRelationship({
    targetRelationship: relationship.uri,
    attestationType: 'verify',
    confidence: 90,
    evidence: 'I know both Alice and Bob from TechCo'
  })

  // Wait a moment for indexing
  await new Promise(resolve => setTimeout(resolve, 2000))

  // Get updated conviction
  const updatedConviction = await client.conviction.getConviction(relationship.uri)
  console.log('Updated conviction:', updatedConviction.conviction.score)
  // Should be > 0 now

  // List all attestations
  const attestations = await client.conviction.listAttestations({
    uri: relationship.uri
  })

  console.log(`Attestations: ${attestations.attestations.length}`)
  for (const att of attestations.attestations) {
    console.log(`- ${att.record.attestationType} by ${att.attester?.name} (${att.record.confidence}%)`)
  }
}

main().catch(console.error)
```

---

## Error Handling

```typescript
try {
  const conviction = await client.conviction.getConviction(uri)
} catch (error) {
  if (error.statusCode === 404) {
    console.log('No attestations found for this relationship')
  } else {
    console.error('Error fetching conviction:', error.message)
  }
}
```

---

## TypeScript Types

All types are fully typed for autocomplete and type safety:

```typescript
import type {
  ConvictionScore,
  Attestation,
  AttestationParams
} from '@atproto/rhiz-sdk'

// ConvictionScore includes:
// - uri: string
// - conviction: { score, attestationCount, verifyCount, etc. }

// Attestation includes:
// - uri, cid
// - record: { targetRelationship, attester, attestationType, confidence, evidence }
// - attester: { did, name, type }
// - attesterReputation: number

// AttestationParams for creating:
// - targetRelationship: string
// - attestationType: 'verify' | 'dispute' | 'strengthen' | 'weaken'
// - confidence: number (0-100)
// - evidence?: string
// - suggestedStrength?: number
```

---

## Best Practices

### 1. Use High Confidence for Strong Evidence

```typescript
// You witnessed it directly → high confidence
await client.conviction.attestRelationship({
  targetRelationship: uri,
  attestationType: 'verify',
  confidence: 95,
  evidence: 'I saw them work together every day for 2 years'
})

// You heard about it → lower confidence
await client.conviction.attestRelationship({
  targetRelationship: uri,
  attestationType: 'verify',
  confidence: 60,
  evidence: 'I heard from a mutual friend they worked together'
})
```

### 2. Always Provide Evidence

```typescript
// Good - explains why
await client.conviction.attestRelationship({
  targetRelationship: uri,
  attestationType: 'verify',
  confidence: 90,
  evidence: 'Worked with both at TechCo 2020-2023'
})

// Bad - no context
await client.conviction.attestRelationship({
  targetRelationship: uri,
  attestationType: 'verify',
  confidence: 90
  // No evidence - less valuable to others
})
```

### 3. Check Conviction Before Important Actions

```typescript
// Before facilitating an introduction
const conviction = await client.conviction.getConviction(relationshipUri)

if (conviction.conviction.score >= 80) {
  console.log('High-conviction relationship - safe to introduce')
  await facilitateIntroduction()
} else if (conviction.conviction.score < 40) {
  console.log('Low-conviction relationship - verify before introducing')
  await requestAdditionalVerification()
}
```

---

## Next Steps

- Read [PROTOCOL_SPECIFICATION.md](PROTOCOL_SPECIFICATION.md) for protocol details
- Check [RHIZ_PROTOCOL_ROADMAP.md](RHIZ_PROTOCOL_ROADMAP.md) for upcoming features
- See [AT_PROTOCOL_IMPLEMENTATION_GUIDE.md](AT_PROTOCOL_IMPLEMENTATION_GUIDE.md) for implementation patterns

---

**SDK Version:** 0.1.0 (with attestation support)
**Protocol Version:** 1.0
**Last Updated:** October 22, 2025

