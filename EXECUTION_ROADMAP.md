# Rhiz Protocol: Attestation System Execution Roadmap

**Mission:** Transform Rhiz from "dual-signed relationships" to "network-verified relationships with conviction scores"

**Timeline:** 8 weeks (October 22 - December 17, 2025)
**Status:** Ready to Execute

---

## 📋 Document Navigation

This roadmap synthesizes all planning documents into an actionable execution plan.

### Planning Documents Created

1. **INTUITION_INTEGRATION_ANALYSIS.md** (1,042 lines)
   - Strategic analysis of Intuition Protocol concepts
   - 10 applicable concepts with priorities
   - Full implementation roadmap (Phase 2A → Phase 3B)
   - **Use for:** Understanding the vision and strategic decisions

2. **PHASE_2A_IMPLEMENTATION_GUIDE.md** (1,028 lines)
   - Step-by-step tactical implementation guide
   - Week-by-week breakdown with code samples
   - Database migrations, API endpoints, UI components
   - **Use for:** Detailed implementation instructions

3. **INTUITION_SYNTHESIS_SUMMARY.md** (449 lines)
   - Quick reference guide
   - TL;DR of core concepts
   - FAQs and key decisions
   - **Use for:** Quick lookups and team onboarding

4. **RHIZ_ATTESTATION_IMPLEMENTATION_PLAN.md** (THIS DOCUMENT)
   - Comprehensive 8-week execution plan
   - Risk mitigation strategies
   - Success criteria and monitoring
   - **Use for:** Sprint planning and execution

5. **QUICK_START_GUIDE.md**
   - Get started in 30 minutes
   - Fast-track commands
   - Troubleshooting guide
   - **Use for:** Immediate execution

6. **PHASE_2A_PROGRESS_TRACKER.md**
   - Week-by-week task tracking
   - Metrics dashboard
   - Blocker management
   - **Use for:** Daily progress tracking

---

## 🎯 What We're Building

### The Transformation

```
BEFORE (Current State):
Alice + Bob sign relationship
└─ Dual-signature verification
└─ No third-party validation
└─ Trust score calculated but not verified

AFTER (Phase 2A):
Alice + Bob sign relationship
   ↓
15 people attest = 90% conviction
   ↓
Network-verified trust
   ↓
High-conviction relationships prioritized
```

### Core Innovation

**Attestation:** Third-party validation of relationships
- Types: verify, dispute, strengthen, weaken
- Stored in attester's AT Protocol repo
- Cryptographically signed

**Conviction:** Network confidence score (0-100)
- Weighted by attester reputation
- Temporal decay (old attestations matter less)
- Real-time updates via firehose

**Result:** "Trust the trust" - meta-level confidence in relationship claims

---

## 🚀 8-Week Sprint Overview

### Phase Breakdown

| Week | Focus | Key Deliverables | Confidence |
|------|-------|------------------|------------|
| 1-2 | Foundation | Types, DB migration, conviction algorithm | 🟢 High |
| 3-4 | Integration | API endpoints, firehose indexer | 🟢 High |
| 5-6 | SDK & UI | Client methods, React components | 🟡 Medium |
| 7 | Testing | E2E tests, load tests | 🟢 High |
| 8 | Launch | Beta testing, production deployment | 🟡 Medium |

### Critical Path

```
Week 1: Types & DB
   ↓ (blocks Week 2)
Week 2: Conviction Algorithm
   ↓ (blocks Week 3)
Week 3: API Endpoints
   ↓ (blocks Week 4)
Week 4: Firehose Indexer
   ↓ (blocks Week 5)
Week 5: SDK Methods
   ↓ (blocks Week 6)
Week 6: UI Components
   ↓ (blocks Week 7)
Week 7: Testing
   ↓ (blocks Week 8)
Week 8: Launch
```

**No parallel work possible** - each week depends on previous

---

## 📊 Success Criteria

### Technical Metrics (Week 8)

✅ **Performance:**
- Conviction calculation: <100ms for 100 attestations
- API p95 latency: <200ms
- Firehose lag: <5 seconds
- Test coverage: >90%

✅ **Stability:**
- Error rate: <0.1%
- Uptime: >99.9%
- Zero critical bugs

### Adoption Metrics

🎯 **Week 8 (Launch):**
- 50+ attestations created
- 10%+ of relationships attested
- 20+ active attesters

🎯 **Month 3:**
- 30%+ of relationships attested
- 100+ attestations/day
- Average conviction score: 70+

### Quality Metrics

🎯 **Validation:**
- Conviction accuracy: >80% (vs manual validation)
- Fraud detection: >90% (fake relationships <40 conviction)
- User satisfaction: >70% (conviction scores helpful)

---

## 🛠️ Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────┐
│  User AT Protocol Repo (Source of Truth)            │
│  at://did:plc:alice/net.rhiz.relationship.record/*  │
│  at://did:plc:carol/net.rhiz.relationship.attestation/* │
└─────────────────┬────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  AT Protocol Firehose                                │
│  Real-time broadcast of commits                     │
└─────────────────┬────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  Rhiz Indexer (TypeScript)                           │
│  - Indexes attestation records                      │
│  - Triggers conviction recalculation                │
└─────────────────┬────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  PostgreSQL Database                                 │
│  - attestations table                               │
│  - conviction_scores table (cache)                  │
│  - relationships table (+ conviction columns)       │
└─────────────────┬────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  Conviction Calculator (Python)                      │
│  - Reputation weighting (0.5x to 2.0x)              │
│  - Temporal decay (180-day half-life)               │
│  - Confidence scaling                               │
│  - Trend calculation                                │
└─────────────────┬────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  API Layer (FastAPI)                                 │
│  - GET /xrpc/net.rhiz.conviction.getScore           │
│  - GET /xrpc/net.rhiz.conviction.listAttestations   │
└─────────────────┬────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│  SDK & UI (TypeScript/React)                         │
│  - attestRelationship() method                      │
│  - ConvictionBadge component                        │
│  - AttestationButton component                      │
└─────────────────────────────────────────────────────┘
```

### Data Flow

1. **User creates attestation** → Record in AT Protocol repo
2. **Firehose broadcasts** → Indexer picks up commit
3. **Indexer processes** → Insert into `attestations` table
4. **Trigger calculation** → Call conviction algorithm
5. **Calculate score** → Weight by reputation, decay, confidence
6. **Update cache** → Store in `conviction_scores` table
7. **Update relationships** → Add conviction to relationship record
8. **API serves** → Return conviction to frontend
9. **UI displays** → Show conviction badge to user

---

## 🎨 Key Files to Create

### Week 1-2: Foundation

```
packages/rhiz-protocol/
  src/generated/types/net/rhiz/
    relationship/attestation.ts        ← Generated from lexicon
    conviction/defs.ts                 ← Generated from lexicon
    conviction/getScore.ts             ← Generated from lexicon
    conviction/listAttestations.ts     ← Generated from lexicon

services/rhiz-api/
  alembic/versions/
    002_attestation_tables.py          ← Database migration
  app/services/
    conviction.py                       ← Core algorithm ⭐
  app/tests/
    test_conviction.py                  ← Unit tests
```

### Week 3-4: Integration

```
services/rhiz-api/
  app/api/
    conviction.py                       ← API endpoints ⭐
  app/main.py                           ← Update to register routes

services/rhiz-atproto/
  src/
    indexer.ts                          ← Update for attestations ⭐
```

### Week 5-6: SDK & UI

```
packages/rhiz-sdk/
  src/
    client.ts                           ← Update with attestation methods ⭐
  src/__tests__/
    attestations.test.ts                ← SDK tests

services/fundrhiz/
  components/
    ConvictionBadge.tsx                ← Display conviction ⭐
    AttestationButton.tsx              ← Submit attestation ⭐
  app/relationships/[id]/
    page.tsx                            ← Integrate components
```

---

## 💡 Key Decisions Made

### ✅ Decision 1: Start Without Economics

**Rationale:** Prove attestation model works before adding token complexity.

**Implication:** Phase 2A has no staking. Phase 3A adds economics if validated.

### ✅ Decision 2: AT Protocol Storage, Not Blockchain

**Rationale:** AT Protocol better for social data (no gas fees, user ownership, scalability).

**Implication:** Attestations in user repos. Optional blockchain bridge in Phase 3.

### ✅ Decision 3: Integer Scores (0-100)

**Rationale:** AT Protocol compliant (no floats), better UX, consistent with trust scores.

**Implication:** All conviction scores are integers 0-100.

### ✅ Decision 4: Reputation-Weighted Attestations

**Rationale:** Prevent Sybil attacks, give more weight to trusted attesters.

**Implication:** Low-rep attestations count 0.5x, high-rep count 2.0x.

### ✅ Decision 5: Temporal Decay

**Rationale:** Old attestations become less relevant over time.

**Implication:** 180-day half-life (attestations lose 50% weight every 6 months).

### ✅ Decision 6: Disputes Weighted Higher

**Rationale:** Fraud prevention - easier to verify than dispute.

**Implication:** Disputes have -1.5 weight vs verify +1.0 weight.

---

## ⚡ Quick Start (First 30 Minutes)

### Step 1: Generate Types (5 min)
```bash
cd packages/rhiz-protocol
pnpm run codegen
pnpm run build
```

### Step 2: Database Migration (10 min)
```bash
cd services/rhiz-api
# Create migration file (copy from RHIZ_ATTESTATION_IMPLEMENTATION_PLAN.md)
alembic upgrade head
```

### Step 3: Conviction Calculator (15 min)
```bash
# Create app/services/conviction.py
# Copy ConvictionCalculator class from implementation plan
# Create app/tests/test_conviction.py
pytest app/tests/test_conviction.py -v
```

**Result:** Foundation complete in 30 minutes!

---

## 🐛 Common Issues & Solutions

### Issue: Types not generated
**Solution:**
```bash
cd packages/rhiz-protocol
rm -rf src/generated
pnpm run codegen
```

### Issue: Database migration fails
**Solution:**
```bash
alembic current  # Check current version
alembic history  # Check migration history
# If needed: alembic downgrade base && alembic upgrade head
```

### Issue: Tests failing
**Solution:**
```bash
# Check test dependencies
pip install pytest pytest-asyncio
# Run verbose
pytest app/tests/test_conviction.py -v -s
```

### Issue: API not responding
**Solution:**
```bash
# Check routes registered
grep "conviction" app/main.py
# Restart server
uvicorn app.main:app --reload
```

---

## 📈 Monitoring & Observability

### Metrics to Track

**System Health:**
- API latency (p50, p95, p99)
- Conviction calculation time
- Firehose indexing lag
- Database query performance
- Error rates by endpoint

**Business Metrics:**
- Attestations created per day
- % of relationships with ≥1 attestation
- Active attesters (DAU/MAU)
- Average conviction score
- Verify vs dispute ratio

**Quality Metrics:**
- Conviction accuracy (vs manual validation)
- Fraud detection rate
- User satisfaction (surveys)

### Dashboards

**Grafana:** Real-time system metrics
**DataDog:** Application performance monitoring
**Sentry:** Error tracking and alerts

---

## 🚨 Risk Mitigation

### Risk: Low Adoption

**Probability:** Medium
**Impact:** High

**Mitigation:**
- Gamification: Top attesters leaderboard
- Incentives: High conviction = higher search ranking
- Onboarding: Prompt users to attest relationships
- Social proof: "15 people attested this"

### Risk: Performance Issues

**Probability:** Low
**Impact:** High

**Mitigation:**
- Cache conviction scores in database
- Recalculate only on new attestation (incremental)
- Optimize SQL queries with proper indexes
- Horizontal scaling if needed

### Risk: Sybil Attacks

**Probability:** Medium
**Impact:** Medium

**Mitigation:**
- Reputation weighting (low-rep = low impact)
- Rate limiting (max attestations/day)
- Graph analysis to detect suspicious patterns
- Human review for disputed relationships

---

## 📅 Timeline & Milestones

### Week 1 (Oct 22-28): Foundation
- ✅ Types generated
- ✅ Database migration complete
- ✅ Conviction algorithm implemented
- ✅ Unit tests passing

### Week 2 (Oct 29 - Nov 4): Algorithm
- ✅ Comprehensive test coverage
- ✅ Edge cases handled
- ✅ Performance validated

### Week 3 (Nov 5-11): API
- ✅ Endpoints implemented
- ✅ Routes registered
- ✅ API responding correctly

### Week 4 (Nov 12-18): Indexer
- ✅ Attestations indexed from firehose
- ✅ Conviction recalculated in real-time
- ✅ End-to-end flow working

### Week 5 (Nov 19-25): SDK
- ✅ SDK methods implemented
- ✅ SDK tests passing
- ✅ Documentation complete

### Week 6 (Nov 26 - Dec 2): UI
- ✅ React components created
- ✅ Components integrated
- ✅ UI flow working end-to-end

### Week 7 (Dec 3-9): Testing
- ✅ E2E tests passing
- ✅ Load tests passing
- ✅ Performance validated

### Week 8 (Dec 10-17): Launch
- ✅ Beta testing complete
- ✅ Production deployed
- ✅ Monitoring active
- 🚀 **PUBLIC LAUNCH**

---

## 🎓 Team Onboarding

### For Backend Engineers

**Read:**
1. QUICK_START_GUIDE.md (30 min)
2. RHIZ_ATTESTATION_IMPLEMENTATION_PLAN.md Week 1-4 (1 hour)

**Build:**
- Database migration
- Conviction calculator
- API endpoints
- Indexer update

### For Frontend Engineers

**Read:**
1. QUICK_START_GUIDE.md (30 min)
2. RHIZ_ATTESTATION_IMPLEMENTATION_PLAN.md Week 5-6 (30 min)

**Build:**
- SDK methods
- React components
- UI integration

### For Product/Design

**Read:**
1. INTUITION_SYNTHESIS_SUMMARY.md (20 min)
2. INTUITION_INTEGRATION_ANALYSIS.md (45 min)

**Focus:**
- User flows
- UI/UX for conviction display
- Onboarding strategy
- Adoption tactics

---

## 🔮 Post-Launch: Phase 2B

### Month 3 Evaluation

**Review:**
- Adoption metrics vs targets
- Conviction accuracy validation
- User feedback analysis
- Performance optimization needs

**Decision:** Proceed to Phase 2B if:
- ✅ 30%+ relationships have ≥1 attestation
- ✅ 80%+ conviction accuracy
- ✅ <100ms conviction calculation
- ✅ Positive user feedback

### Phase 2B Preview (Months 4-6)

**Goal:** Triple-based claims with granular attestation

**Features:**
1. Decompose relationships to atomic triples
2. Attest specific fields (not whole relationships)
3. Triple pattern matching queries
4. Granular conviction per field

**Example:**
```typescript
// Current: Attest whole relationship
attestRelationship({ targetRelationship: 'at://...' })

// Phase 2B: Attest specific triple
attestTriple({
  subject: 'did:plc:alice',
  predicate: 'net.rhiz.relationship.strength',
  object: '85',
  context: 'did:plc:bob'
})
```

---

## 🎉 Success Celebration

### Week 8 Launch Checklist

- [ ] Production deployed
- [ ] All smoke tests passing
- [ ] Monitoring dashboards active
- [ ] Documentation published
- [ ] Team briefed
- [ ] Announcement ready
- [ ] 🚀 **GO LIVE**

### What Success Looks Like

**Technical:**
- All systems operational
- Zero critical bugs
- Performance targets met

**User:**
- First 50 attestations created
- Conviction scores displayed
- Positive feedback received

**Team:**
- Everyone proud of the work
- Clean, maintainable code
- Ready for Phase 2B

---

## 📞 Support & Resources

### Documentation
- **Strategic:** INTUITION_INTEGRATION_ANALYSIS.md
- **Tactical:** PHASE_2A_IMPLEMENTATION_GUIDE.md
- **Quick Ref:** INTUITION_SYNTHESIS_SUMMARY.md
- **Execution:** RHIZ_ATTESTATION_IMPLEMENTATION_PLAN.md
- **Quick Start:** QUICK_START_GUIDE.md
- **Tracking:** PHASE_2A_PROGRESS_TRACKER.md

### Key Contacts
- **Technical Lead:** [Your name]
- **Product Lead:** [Product manager]
- **Design Lead:** [Designer]

### External Resources
- Intuition Protocol: https://intuition.systems
- AT Protocol Docs: https://atproto.com
- Rhiz Protocol Docs: https://docs.rhiz.network

---

## ✅ Final Checklist

### Pre-Sprint
- [ ] All planning documents reviewed
- [ ] Team aligned on goals
- [ ] Development environment ready
- [ ] Lexicon schemas validated

### During Sprint
- [ ] Daily standups
- [ ] Weekly progress tracking
- [ ] Blocker escalation
- [ ] Code reviews

### Post-Launch
- [ ] Metrics dashboard active
- [ ] User feedback collected
- [ ] Retrospective scheduled
- [ ] Phase 2B planning started

---

**Status:** Ready to Execute
**Timeline:** 8 weeks to launch
**Confidence:** High (schemas ready, architecture proven)

**Next Action:** Open `QUICK_START_GUIDE.md` and execute Day 1 tasks.

Let's build the conviction layer! 🚀

---

**Document Version:** 1.0
**Last Updated:** October 22, 2025
**Author:** Rhiz Protocol Team

