# Phase 2A: Attestation System - Progress Tracker

**Sprint:** 8 weeks (October 22 - December 17, 2025)
**Goal:** Launch network-verified relationships with conviction scores
**Status:** 🟡 Not Started → 🟢 In Progress → ✅ Complete

---

## Week 1: Foundation Layer (Oct 22-28)

### Day 1-2: Type Generation ⬜
- [ ] Generate TypeScript types from lexicons
  ```bash
  cd packages/rhiz-protocol && pnpm run codegen
  ```
- [ ] Verify attestation.ts generated
- [ ] Verify conviction types generated
- [ ] Build package successfully
- [ ] No compilation errors

**Deliverable:** Generated types in `packages/rhiz-protocol/src/generated/`

---

### Day 3-5: Database Migration ⬜
- [ ] Create migration file `002_attestation_tables.py`
- [ ] Define attestations table schema
- [ ] Define conviction_scores table schema
- [ ] Add conviction columns to relationships table
- [ ] Run migration: `alembic upgrade head`
- [ ] Verify tables exist in database

**Deliverable:** Database tables ready for attestations

**SQL Verification:**
```sql
\dt attestations
\dt conviction_scores
\d relationships
```

---

### Week 1 Checkpoint ⬜
**Criteria for proceeding:**
- ✅ All types generated without errors
- ✅ Database migration successful
- ✅ Tables have correct indexes

**If blocked:** Review `QUICK_START_GUIDE.md` troubleshooting section

---

## Week 2: Conviction Algorithm (Oct 29 - Nov 4)

### Day 6-10: ConvictionCalculator ⬜
- [ ] Create `app/services/conviction.py`
- [ ] Implement `calculate_conviction()` method
- [ ] Add reputation weighting (0.5x to 2.0x)
- [ ] Add temporal decay (180-day half-life)
- [ ] Add confidence scaling
- [ ] Implement trend calculation
- [ ] Add comprehensive logging

**Deliverable:** Working conviction calculator

**Test manually:**
```python
from app.services.conviction import ConvictionCalculator

calc = ConvictionCalculator()
result = calc.calculate_conviction(...)
print(result['score'])  # Should be 0-100
```

---

### Day 11-12: Unit Tests ⬜
- [ ] Create `app/tests/test_conviction.py`
- [ ] Test: Zero attestations → 0 conviction
- [ ] Test: Single verify → positive conviction
- [ ] Test: Dispute lowers score
- [ ] Test: Temporal decay works
- [ ] Test: Reputation weighting works
- [ ] Test: Multiple attestations aggregate
- [ ] Test: Trend calculation works
- [ ] All 8+ tests passing

**Deliverable:** Comprehensive test coverage

**Run tests:**
```bash
cd services/rhiz-api
pytest app/tests/test_conviction.py -v
```

**Success:** All tests green ✅

---

### Week 2 Checkpoint ⬜
**Criteria for proceeding:**
- ✅ ConvictionCalculator implemented
- ✅ All unit tests passing
- ✅ Algorithm handles edge cases correctly

**Metrics:**
- Test coverage: >90%
- Calculation time: <50ms for 100 attestations

---

## Week 3: API Layer (Nov 5-11)

### Day 13-15: Conviction Endpoints ⬜
- [ ] Create `app/api/conviction.py`
- [ ] Implement `GET /xrpc/net.rhiz.conviction.getScore`
- [ ] Implement `GET /xrpc/net.rhiz.conviction.listAttestations`
- [ ] Add query parameter validation
- [ ] Add pagination support
- [ ] Add caching logic

**Deliverable:** Working API endpoints

**Test endpoints:**
```bash
# Test getScore
curl "http://localhost:8000/xrpc/net.rhiz.conviction.getScore?uri=at://test/uri"

# Test listAttestations
curl "http://localhost:8000/xrpc/net.rhiz.conviction.listAttestations?uri=at://test/uri&limit=10"
```

---

### Day 16-17: Route Registration ⬜
- [ ] Update `app/main.py` to import conviction router
- [ ] Register conviction routes
- [ ] Test all endpoints respond
- [ ] Add API documentation
- [ ] Test error handling (404, 500)

**Deliverable:** Fully integrated API

**Verification:**
```bash
# Should list conviction endpoints
curl http://localhost:8000/docs
```

---

### Week 3 Checkpoint ⬜
**Criteria for proceeding:**
- ✅ Both API endpoints working
- ✅ Endpoints return correct JSON structure
- ✅ Error handling works properly
- ✅ Response time <200ms

---

## Week 4: Firehose Indexer (Nov 12-18)

### Day 18-21: Indexer Update ⬜
- [ ] Update `services/rhiz-atproto/src/indexer.ts`
- [ ] Add `indexAttestation()` method
- [ ] Handle `net.rhiz.relationship.attestation` collection
- [ ] Store attestation in database
- [ ] Trigger conviction recalculation
- [ ] Update conviction_scores table
- [ ] Update relationships table conviction fields

**Deliverable:** Attestations indexed from firehose

**Test:**
```bash
# Start indexer
cd services/rhiz-atproto
pnpm run ingest

# Monitor logs
tail -f logs/indexer.log | grep attestation
```

---

### Day 22: Integration Testing ⬜
- [ ] Create test attestation record in AT Protocol repo
- [ ] Verify firehose picks it up
- [ ] Verify attestation inserted into database
- [ ] Verify conviction recalculated
- [ ] Verify conviction_scores updated
- [ ] Verify relationships table updated

**Deliverable:** End-to-end attestation flow working

**Success Criteria:**
- Attestation created → indexed within 5 seconds
- Conviction recalculated correctly
- Database tables all updated

---

### Week 4 Checkpoint ⬜
**Criteria for proceeding:**
- ✅ Indexer handles attestations
- ✅ Conviction updates in real-time
- ✅ Firehose lag <5 seconds
- ✅ No errors in logs

---

## Week 5: SDK Layer (Nov 19-25)

### Day 23-26: SDK Methods ⬜
- [ ] Update `packages/rhiz-sdk/src/client.ts`
- [ ] Implement `attestRelationship()` method
- [ ] Implement `getConviction()` method
- [ ] Implement `listAttestations()` method
- [ ] Add TypeScript interfaces
- [ ] Add JSDoc documentation

**Deliverable:** SDK methods for attestations

**Test:**
```typescript
const client = new RhizClient(...)
await client.login(...)

// Create attestation
const result = await client.attestRelationship({
  targetRelationship: 'at://...',
  attestationType: 'verify',
  confidence: 90
})

// Get conviction
const conviction = await client.getConviction('at://...')
console.log(conviction.conviction.score)
```

---

### Day 27: SDK Tests ⬜
- [ ] Create `packages/rhiz-sdk/src/__tests__/attestations.test.ts`
- [ ] Test attestRelationship() creates record
- [ ] Test getConviction() returns score
- [ ] Test listAttestations() returns list
- [ ] Test error handling
- [ ] All tests passing

**Deliverable:** Tested SDK methods

---

### Week 5 Checkpoint ⬜
**Criteria for proceeding:**
- ✅ All SDK methods implemented
- ✅ SDK tests passing
- ✅ Methods work end-to-end
- ✅ Documentation complete

---

## Week 6: UI Layer (Nov 26 - Dec 2)

### Day 28-31: React Components ⬜
- [ ] Create `services/fundrhiz/components/ConvictionBadge.tsx`
- [ ] Implement conviction score display
- [ ] Add color coding (green/yellow/red)
- [ ] Add trend indicator (↗→↘)
- [ ] Create `services/fundrhiz/components/AttestationButton.tsx`
- [ ] Implement attestation form
- [ ] Add type selection (verify/dispute)
- [ ] Add confidence slider
- [ ] Add evidence textarea

**Deliverable:** Reusable UI components

**Preview:**
```bash
cd services/fundrhiz
pnpm run dev
# Navigate to relationship page
# See conviction badge and attestation button
```

---

### Day 32-34: Integration ⬜
- [ ] Update relationship page to show ConvictionBadge
- [ ] Add AttestationButton to relationship actions
- [ ] Test attestation submission
- [ ] Verify conviction updates after attestation
- [ ] Test on mobile
- [ ] Test accessibility

**Deliverable:** Fully integrated UI

**User Flow:**
1. View relationship
2. See conviction badge (if attestations exist)
3. Click "Attest to this relationship"
4. Fill form (type, confidence, evidence)
5. Submit
6. Conviction badge updates

---

### Week 6 Checkpoint ⬜
**Criteria for proceeding:**
- ✅ UI components working
- ✅ Attestation submission works
- ✅ Conviction updates visible
- ✅ Mobile responsive
- ✅ Accessible (WCAG AA)

---

## Week 7: Integration Testing (Dec 3-9)

### Day 35-38: End-to-End Tests ⬜
- [ ] Create `services/rhiz-api/app/tests/test_integration.py`
- [ ] Test full attestation flow
- [ ] Test multiple attestations aggregate
- [ ] Test disputes lower conviction
- [ ] Test temporal decay
- [ ] Test reputation weighting
- [ ] All integration tests passing

**Deliverable:** Comprehensive E2E tests

---

### Day 39-41: Load Testing ⬜
- [ ] Create load tests with Locust
- [ ] Test conviction calculation performance
- [ ] Test API endpoint throughput
- [ ] Test database under load
- [ ] Identify bottlenecks
- [ ] Optimize as needed

**Deliverable:** Performance validated

**Targets:**
- Conviction calc: <100ms for 100 attestations
- API p95 latency: <200ms
- Throughput: 1000 req/s

---

### Week 7 Checkpoint ⬜
**Criteria for proceeding:**
- ✅ All E2E tests passing
- ✅ Performance targets met
- ✅ No critical bugs found
- ✅ System stable under load

---

## Week 8: Launch (Dec 10-17)

### Day 42-44: Documentation ⬜
- [ ] Write API endpoint docs
- [ ] Write SDK usage examples
- [ ] Write UI component docs
- [ ] Create deployment guide
- [ ] Set up monitoring dashboards

**Deliverable:** Complete documentation

---

### Day 45-47: Beta Testing ⬜
- [ ] Deploy to staging environment
- [ ] Invite 20 beta testers
- [ ] Collect feedback
- [ ] Monitor for bugs
- [ ] Validate conviction accuracy
- [ ] Fix critical issues

**Deliverable:** Beta validated

**Success Metrics:**
- 0 critical bugs
- >80% positive feedback
- Conviction accuracy >75%

---

### Day 48-49: Production Deployment ⬜
- [ ] Build all packages
- [ ] Run database migration on prod
- [ ] Deploy API server
- [ ] Deploy firehose indexer
- [ ] Deploy frontend
- [ ] Smoke test all endpoints
- [ ] Set up monitoring alerts

**Deliverable:** Production live

**Deployment Checklist:**
```bash
# Build
pnpm build

# Migrate DB
alembic upgrade head

# Deploy services
docker-compose up -d

# Verify
curl https://api.rhiz.network/xrpc/net.rhiz.conviction.getScore?uri=...
```

---

### Day 50: Launch Day 🚀 ⬜
- [ ] Public announcement
- [ ] Monitor metrics dashboard
- [ ] Watch for errors
- [ ] Respond to user feedback
- [ ] Celebrate! 🎉

**Deliverable:** Attestation system live

---

## Success Metrics Tracking

### Technical Metrics

**Performance:**
| Metric | Target | Week 4 | Week 6 | Week 8 | Status |
|--------|--------|--------|--------|--------|--------|
| Conviction calc time | <100ms | - | - | - | ⬜ |
| API p95 latency | <200ms | - | - | - | ⬜ |
| Firehose lag | <5s | - | - | - | ⬜ |
| Test coverage | >90% | - | - | - | ⬜ |

**Stability:**
| Metric | Target | Week 4 | Week 6 | Week 8 | Status |
|--------|--------|--------|--------|--------|--------|
| Error rate | <0.1% | - | - | - | ⬜ |
| Uptime | >99.9% | - | - | - | ⬜ |
| Critical bugs | 0 | - | - | - | ⬜ |

### Adoption Metrics

**Week 8 Targets:**
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Attestations created | 50+ | - | ⬜ |
| Relationships attested | 10%+ | - | ⬜ |
| Active attesters | 20+ | - | ⬜ |

**Month 3 Targets:**
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Relationships attested | 30%+ | - | ⬜ |
| Attestations/day | 100+ | - | ⬜ |
| Avg conviction score | 70+ | - | ⬜ |

### Quality Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Conviction accuracy | >80% | - | ⬜ |
| Fraud detection | >90% | - | ⬜ |
| User satisfaction | >70% | - | ⬜ |

---

## Blockers & Risks

### Current Blockers
| Issue | Impact | Owner | Status |
|-------|--------|-------|--------|
| - | - | - | ⬜ |

### Identified Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Low adoption | Medium | High | Gamification, incentives |
| Performance issues | Low | High | Caching, optimization |
| Sybil attacks | Medium | Medium | Reputation weighting |

---

## Weekly Standup Notes

### Week 1 (Oct 22-28)
**Completed:**
-

**Blockers:**
-

**Next:**
-

---

### Week 2 (Oct 29 - Nov 4)
**Completed:**
-

**Blockers:**
-

**Next:**
-

---

### Week 3 (Nov 5-11)
**Completed:**
-

**Blockers:**
-

**Next:**
-

---

### Week 4 (Nov 12-18)
**Completed:**
-

**Blockers:**
-

**Next:**
-

---

### Week 5 (Nov 19-25)
**Completed:**
-

**Blockers:**
-

**Next:**
-

---

### Week 6 (Nov 26 - Dec 2)
**Completed:**
-

**Blockers:**
-

**Next:**
-

---

### Week 7 (Dec 3-9)
**Completed:**
-

**Blockers:**
-

**Next:**
-

---

### Week 8 (Dec 10-17)
**Completed:**
-

**Blockers:**
-

**Next:**
-

---

## Team Velocity

| Week | Planned Tasks | Completed | Velocity |
|------|--------------|-----------|----------|
| 1 | 8 | - | -% |
| 2 | 10 | - | -% |
| 3 | 8 | - | -% |
| 4 | 9 | - | -% |
| 5 | 8 | - | -% |
| 6 | 10 | - | -% |
| 7 | 12 | - | -% |
| 8 | 14 | - | -% |

---

## Post-Launch Checklist

### Week 9: Monitor & Iterate
- [ ] Daily metrics review
- [ ] Respond to user feedback
- [ ] Fix minor bugs
- [ ] Optimize hot paths

### Week 10: First Retrospective
- [ ] What went well?
- [ ] What could be better?
- [ ] Lessons learned
- [ ] Adjust for Phase 2B

### Month 3: Phase 2A Evaluation
- [ ] Review adoption metrics
- [ ] Validate conviction accuracy
- [ ] User satisfaction survey
- [ ] Go/no-go for Phase 2B

---

## Phase 2B Preview

**Timeline:** Months 4-6
**Goal:** Triple-based claims with granular attestation

**Prerequisites:**
- ✅ Phase 2A adoption >30%
- ✅ Conviction accuracy >80%
- ✅ Performance targets met

**Key Features:**
1. Decompose relationships to triples
2. Attest specific fields
3. Triple pattern matching
4. Granular conviction per field

**Preparation:**
- Design `net.rhiz.triple.claim` lexicon
- Plan triple indexing strategy
- Prototype triple query engine

---

**Last Updated:** October 22, 2025
**Sprint Progress:** 0% → Target: 100% by Dec 17
**Status:** 🟡 Not Started

Let's ship this! 🚀

