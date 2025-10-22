# Intuition Protocol → Rhiz Protocol: Synthesis Summary

## TL;DR

**Intuition's Core Innovation:** Attestation-based consensus with economic staking creates verifiable truth.

**Rhiz's Adaptation:** Apply attestation model to relationships, maintaining AT Protocol's user-owned, federated architecture.

**Result:** Transform Rhiz from "dual-signed relationships" to "network-verified relationships with conviction scores."

---

## What We're Building

### The Upgrade Path

```
Current: Alice + Bob sign relationship
  ↓
Phase 2A: Alice + Bob sign + 15 people attest = 90% conviction
  ↓
Phase 2B: Relationship decomposed to triples, each independently attested
  ↓
Phase 2C: Expertise, credentials, events all attestable
  ↓
Phase 3: Economic staking adds skin-in-the-game to attestations
```

---

## Documents Created

### 1. INTUITION_INTEGRATION_ANALYSIS.md (Main Document)

**Purpose:** Comprehensive analysis of applicable concepts

**Contents:**
- Understanding Intuition Protocol
- Rhiz's current strengths
- 10 applicable concepts with priority levels
- Implementation roadmap (Phase 2A → Phase 3B)
- Technical architecture details
- Success metrics
- Key insights

**When to use:** Strategic planning, understanding the full vision

---

### 2. PHASE_2A_IMPLEMENTATION_GUIDE.md (Tactical Guide)

**Purpose:** Step-by-step implementation instructions for first phase

**Contents:**
- Week-by-week task breakdown
- Code samples for all components
- Database migrations
- API endpoints
- SDK methods
- UI components
- Testing strategy
- Deployment plan

**When to use:** Actually building Phase 2A (start immediately)

---

### 3. Lexicon Schemas (Implementation Artifacts)

**Created files:**
- `lexicons/net/rhiz/relationship/attestation.json`
- `lexicons/net/rhiz/conviction/defs.json`
- `lexicons/net/rhiz/conviction/getScore.json`
- `lexicons/net/rhiz/conviction/listAttestations.json`

**Purpose:** AT Protocol schemas for attestation records and queries

**Next step:** Run `pnpm run codegen` to generate TypeScript types

---

## Immediate Next Actions

### This Week

1. ✅ **Review analysis** - Read INTUITION_INTEGRATION_ANALYSIS.md, validate approach
2. ✅ **Validate schemas** - Review lexicon files, ensure they match requirements
3. **Generate types** - Run `cd packages/rhiz-protocol && pnpm run codegen`
4. **Review types** - Check generated TypeScript types look correct

### Next Week

5. **Database migration** - Create and run attestations table migration
6. **Conviction algorithm** - Implement conviction calculator in Python
7. **Unit tests** - Test conviction calculation edge cases
8. **Prototype** - Build minimal attestation endpoint

### Weeks 3-8

9. **Follow Phase 2A guide** - Implement full attestation system
10. **Beta test** - Internal team testing
11. **Launch** - Release to users
12. **Measure** - Track adoption and quality metrics

---

## Key Decisions Made

### ✅ Decision 1: Start Without Economics

**Rationale:** Prove social attestation model works before adding token complexity.

**Implication:** Phase 2A has no staking, Phase 3A adds it later if validated.

---

### ✅ Decision 2: AT Protocol Storage, Not Blockchain

**Rationale:** AT Protocol is better for social data (no gas fees, user ownership, scalability).

**Implication:** Attestations live in user repos, indexed by AppView. Optional blockchain bridge in Phase 3.

---

### ✅ Decision 3: Conviction = 0-100 Integer

**Rationale:** Consistent with Rhiz's trust scores, AT Protocol compliant (no floats).

**Implication:** All conviction scores are integers 0-100, like strength scores.

---

### ✅ Decision 4: Reputation-Weighted Attestations

**Rationale:** Prevent Sybil attacks, give more weight to trusted attesters.

**Implication:** Conviction calculator uses attester's trust_score as multiplier (0.5x to 2.0x).

---

### ✅ Decision 5: Temporal Decay

**Rationale:** Old attestations become less relevant over time.

**Implication:** 180-day half-life (attestations lose 50% weight every 6 months).

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  User Repositories (AT Protocol)                            │
│  - Relationship records (existing)                          │
│  - Attestation records (NEW)                                │
│  - User owns all data                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  AT Protocol Firehose                                        │
│  - Real-time stream of all commits                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Rhiz AppView (Indexer)                                      │
│  - Index attestations                                        │
│  - Calculate conviction scores (NEW)                         │
│  - Update relationship conviction (NEW)                      │
│  - Cache conviction in PostgreSQL                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Query API                                                   │
│  - GET /conviction/getScore (NEW)                            │
│  - GET /conviction/listAttestations (NEW)                    │
│  - Existing relationship endpoints (enhanced with conviction)│
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Applications                                                │
│  - FundRhiz: Show conviction badges                          │
│  - SDK: attestRelationship() method                          │
│  - UI: Attestation buttons, conviction displays              │
└─────────────────────────────────────────────────────────────┘
```

---

## Example User Flow

### Alice Creates Relationship

```typescript
// Alice creates relationship with Bob
const relationship = await client.relationships.create({
  participants: ['did:plc:alice', 'did:plc:bob'],
  type: 'professional',
  strength: 85,
  context: 'Co-founded TechCo'
})
// URI: at://did:plc:alice/net.rhiz.relationship.record/3jx7ytmdwej2k
// Initial conviction: 0 (no attestations yet)
```

### Carol Attests the Relationship

```typescript
// Carol knows both Alice and Bob, attests their relationship
await client.attestRelationship({
  targetRelationship: 'at://did:plc:alice/net.rhiz.relationship.record/3jx7ytmdwej2k',
  attestationType: 'verify',
  confidence: 90,
  evidence: 'I worked with both at TechCo for 2 years'
})
// Attestation stored in Carol's repo
// URI: at://did:plc:carol/net.rhiz.relationship.attestation/3jx8abc123
```

### Conviction Updates

```typescript
// Firehose picks up Carol's attestation
// Indexer recalculates conviction for Alice-Bob relationship

// Before: conviction = 0
// After: conviction = 72 (based on Carol's attestation, weighted by her reputation)

// Relationship now shows:
{
  uri: 'at://did:plc:alice/net.rhiz.relationship.record/3jx7ytmdwej2k',
  participants: ['did:plc:alice', 'did:plc:bob'],
  strength: 85,
  conviction: {
    score: 72,
    attestationCount: 1,
    verifyCount: 1,
    disputeCount: 0,
    trend: 'stable'
  }
}
```

### David Also Attests

```typescript
// David attests too
await client.attestRelationship({
  targetRelationship: 'at://did:plc:alice/net.rhiz.relationship.record/3jx7ytmdwej2k',
  attestationType: 'verify',
  confidence: 95,
  evidence: 'I know them both from Stanford'
})

// Conviction increases
// Before: 72
// After: 85 (two attestations, both verify, both high confidence)
```

### UI Shows Conviction

```tsx
<RelationshipCard relationship={aliceBob}>
  <ConvictionBadge
    score={85}
    attestationCount={2}
    trend="stable"
  />
  {/* Shows: "85% verified • 2 attestations • →" */}

  <AttestationButton
    relationshipUri={aliceBob.uri}
    onAttested={() => refetch()}
  />
</RelationshipCard>
```

---

## Success Criteria

### Phase 2A (6 months)

- ✅ **Adoption:** 30% of relationships have ≥1 attestation
- ✅ **Quality:** 80%+ conviction correlation with manual validation
- ✅ **Fraud:** 90%+ of fake relationships have conviction <40
- ✅ **Performance:** <100ms conviction calculation, <200ms API latency

### Phase 2B (12 months)

- ✅ **Triples:** 90%+ of relationships decomposed to triples
- ✅ **Granularity:** 40%+ of attestations target specific triples
- ✅ **Queryability:** Triple pattern queries <100ms

### Phase 2C (18 months)

- ✅ **Expertise:** Top 100 domains have 1000+ claimed experts
- ✅ **Credentials:** 50+ institutions attest credentials
- ✅ **Matching:** Expertise-based intros 50%+ more successful

---

## Competitive Moat

### What Makes This Hard to Copy

1. **Network effects** - More attestations = more valuable
2. **AT Protocol native** - Deep integration with federation
3. **Reputation system** - Recursive trust (attesters have reputation)
4. **Conviction algorithm** - Proprietary weighting formula
5. **Data portability** - Users own attestations, lock-in is feature quality

**Result:** First-mover advantage in AT Protocol relationship attestations.

---

## FAQs

### Q: Why not just use Intuition directly?

**A:** Intuition is Ethereum-based (gas fees, blockchain storage). Rhiz is AT Protocol-native (free, user-owned repos, federated). Better fit for social data.

---

### Q: Do we need a token?

**A:** Not immediately. Phase 2A proves attestation model without economics. If successful, Phase 3A adds optional RHIZ token for staking.

---

### Q: Can users fake attestations?

**A:** Hard. Each attestation is:
1. Signed by attester (cryptographic proof)
2. Weighted by attester reputation (low-rep = low weight)
3. Subject to disputes (others can challenge)
4. Visible in attester's repo (public audit trail)

---

### Q: What if two people disagree on relationship strength?

**A:** Conviction algorithm aggregates all attestations. If Alice says 85, Bob says 60, and 5 others attest, conviction reflects weighted consensus (not just Alice's claim).

---

### Q: How does this help FundRhiz?

**A:**
- **Trust signal** - High-conviction relationships prioritized for intros
- **Fraud prevention** - Fake connections have low conviction
- **Network quality** - Attestations incentivize authentic relationships
- **Matching** - Expertise attestations enable smarter investor matching

---

## Technical Risks & Mitigation

### Risk: Conviction calculation too slow

**Mitigation:**
- Cache conviction scores in database
- Only recalculate on new attestation
- Use incremental updates, not full recalc

### Risk: Low adoption

**Mitigation:**
- Gamification (top attesters leaderboard)
- Incentives (high conviction = higher search ranking)
- Onboarding prompts
- Social proof ("15 people attested this relationship")

### Risk: Gaming/spam

**Mitigation:**
- Reputation weighting (low-rep attestations count less)
- Rate limiting (max attestations per day)
- Dispute mechanism (flag bad attestations)
- Sybil detection (ML to catch suspicious patterns)

---

## Next Steps Checklist

- [ ] Read INTUITION_INTEGRATION_ANALYSIS.md (strategic context)
- [ ] Read PHASE_2A_IMPLEMENTATION_GUIDE.md (tactical execution)
- [ ] Review lexicon schemas (validate structure)
- [ ] Generate TypeScript types (`pnpm run codegen`)
- [ ] Create database migration (attestations + conviction_scores tables)
- [ ] Implement conviction calculator (Python)
- [ ] Write unit tests (conviction algorithm)
- [ ] Build API endpoints (/conviction/getScore, /conviction/listAttestations)
- [ ] Update firehose indexer (index attestations)
- [ ] Build SDK methods (attestRelationship, getConviction)
- [ ] Create UI components (ConvictionBadge, AttestationButton)
- [ ] Integration testing (end-to-end attestation flow)
- [ ] Beta testing (internal team)
- [ ] Public launch (all users)
- [ ] Monitor metrics (adoption, quality, performance)
- [ ] Plan Phase 2B (triples) based on learnings

---

## Resources

### Documentation
- **INTUITION_INTEGRATION_ANALYSIS.md** - Full analysis and roadmap
- **PHASE_2A_IMPLEMENTATION_GUIDE.md** - Implementation guide for Phase 2A
- **INTUITION_SYNTHESIS_SUMMARY.md** - This document (quick reference)

### Schemas
- `lexicons/net/rhiz/relationship/attestation.json` - Attestation record
- `lexicons/net/rhiz/conviction/*.json` - Conviction definitions and queries

### Implementation Files (To Be Created)
- `services/rhiz-api/app/services/conviction.py` - Conviction calculator
- `services/rhiz-api/app/routers/conviction.py` - API endpoints
- `services/rhiz-atproto/src/indexer.ts` - Updated indexer
- `packages/rhiz-sdk/src/client.ts` - SDK methods
- `services/fundrhiz/components/ConvictionBadge.tsx` - UI component

---

## Questions?

**Strategic questions:** Review INTUITION_INTEGRATION_ANALYSIS.md
**Implementation questions:** Review PHASE_2A_IMPLEMENTATION_GUIDE.md
**Technical support:** rhiz-protocol@rhiz.network

---

**Status:** Ready to implement Phase 2A
**Timeline:** 6-8 weeks to launch
**Expected impact:** Transform trust model from dual-signed to network-verified

Let's build the conviction layer. 🚀

---

**Document:** INTUITION_SYNTHESIS_SUMMARY.md
**Version:** 1.0
**Date:** October 22, 2025
**Author:** Rhiz Protocol Team

