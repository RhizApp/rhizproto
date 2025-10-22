# Quick Start: Attestation System Implementation

**TL;DR:** Start building the conviction layer TODAY. This guide gets you executing in 30 minutes.

---

## ⚡ Day 1: Get Started Now

### Step 1: Generate Types (5 minutes)

```bash
cd /Users/israelwilson/Developer/rhizproto/packages/rhiz-protocol
pnpm run codegen
pnpm run build
```

**What this does:** Generates TypeScript types from the attestation lexicons you already created.

**Verify:**
```bash
ls -la src/generated/types/net/rhiz/relationship/
# Should see: attestation.ts

ls -la src/generated/types/net/rhiz/conviction/
# Should see: defs.ts, getScore.ts, listAttestations.ts
```

---

### Step 2: Database Migration (10 minutes)

```bash
cd /Users/israelwilson/Developer/rhizproto/services/rhiz-api
```

Create file: `alembic/versions/002_attestation_tables.py`

Copy the migration code from `RHIZ_ATTESTATION_IMPLEMENTATION_PLAN.md` Week 1, Day 3-5.

Run migration:
```bash
alembic upgrade head
```

**Verify:**
```bash
psql -d rhiz_dev -c "\dt attestations"
psql -d rhiz_dev -c "\dt conviction_scores"
psql -d rhiz_dev -c "\d relationships" | grep conviction
```

---

### Step 3: Conviction Calculator (15 minutes)

```bash
cd /Users/israelwilson/Developer/rhizproto/services/rhiz-api
```

Create file: `app/services/conviction.py`

Copy the `ConvictionCalculator` class from the implementation plan (Week 2, Day 6-10).

**Test it:**
```bash
# Create test file
touch app/tests/test_conviction.py

# Copy tests from implementation plan (Week 2, Day 11-12)

# Run tests
pytest app/tests/test_conviction.py -v
```

---

## 🎯 This Week's Sprint

### Monday: Foundation
- ✅ Generate types
- ✅ Database migration
- ✅ Conviction calculator

### Tuesday: Tests & API
- Write conviction unit tests
- Create API endpoints (`app/api/conviction.py`)
- Register routes in `main.py`

### Wednesday: Indexer
- Update firehose indexer to handle attestations
- Test attestation indexing locally
- Verify conviction recalculation

### Thursday: SDK
- Add SDK methods to `packages/rhiz-sdk`
- Test `attestRelationship()` method
- Test `getConviction()` method

### Friday: Demo
- Create simple test UI
- Submit test attestation
- Verify conviction updates
- Demo to team

---

## 🚀 Fast-Track Commands

### Run Everything Locally

**Terminal 1: Database**
```bash
docker-compose -f docker-compose.rhiz.yml up postgres redis
```

**Terminal 2: API Server**
```bash
cd services/rhiz-api
uvicorn app.main:app --reload --port 8000
```

**Terminal 3: Firehose Indexer**
```bash
cd services/rhiz-atproto
pnpm run ingest
```

**Terminal 4: Frontend (optional)**
```bash
cd services/fundrhiz
pnpm run dev
```

---

## 🧪 Quick Test Flow

### 1. Create Test Relationship
```bash
curl -X POST http://localhost:8000/relationships \
  -H "Content-Type: application/json" \
  -d '{
    "participants": ["did:plc:alice", "did:plc:bob"],
    "type": "professional",
    "strength": 85,
    "context": "Co-founders"
  }'

# Note the URI returned: at://did:plc:alice/net.rhiz.relationship.record/{tid}
```

### 2. Create Test Attestation (Simulated)
```bash
# In production, this happens via AT Protocol repos
# For testing, insert directly to database

psql -d rhiz_dev -c "
INSERT INTO attestations (
  uri, attester_did, target_uri, attestation_type,
  confidence, evidence, created_at, indexed_at, cid
) VALUES (
  'at://did:plc:carol/net.rhiz.relationship.attestation/test123',
  'did:plc:carol',
  'at://did:plc:alice/net.rhiz.relationship.record/{tid}',
  'verify',
  90,
  'I know both parties',
  NOW(),
  NOW(),
  'bafy123'
);
"
```

### 3. Get Conviction Score
```bash
curl "http://localhost:8000/xrpc/net.rhiz.conviction.getScore?uri=at://did:plc:alice/net.rhiz.relationship.record/{tid}"

# Should return:
# {
#   "uri": "at://...",
#   "conviction": {
#     "score": 72,
#     "attestationCount": 1,
#     "verifyCount": 1,
#     "disputeCount": 0,
#     ...
#   }
# }
```

### 4. List Attestations
```bash
curl "http://localhost:8000/xrpc/net.rhiz.conviction.listAttestations?uri=at://did:plc:alice/net.rhiz.relationship.record/{tid}"
```

---

## 📊 Key Files to Create

### Week 1-2
```
services/rhiz-api/
  alembic/versions/
    002_attestation_tables.py          ← Day 1
  app/services/
    conviction.py                       ← Day 1
  app/tests/
    test_conviction.py                  ← Day 2
```

### Week 3-4
```
services/rhiz-api/
  app/api/
    conviction.py                       ← Day 3

services/rhiz-atproto/
  src/
    indexer.ts                          ← Update, Day 4
```

### Week 5-6
```
packages/rhiz-sdk/
  src/
    client.ts                           ← Update, Day 5

services/fundrhiz/
  components/
    ConvictionBadge.tsx                ← Day 6
    AttestationButton.tsx              ← Day 6
```

---

## 🎓 Understanding the Flow

### Data Flow
```
User's AT Protocol Repo
  ↓ (creates attestation record)
AT Protocol Firehose
  ↓ (broadcasts commit)
Rhiz Indexer (TypeScript)
  ↓ (indexes attestation)
PostgreSQL (attestations table)
  ↓ (triggers recalculation)
Conviction Calculator (Python)
  ↓ (calculates score)
PostgreSQL (conviction_scores table)
  ↓ (caches result)
API Endpoint
  ↓ (returns conviction)
UI (React)
  ↓ (displays badge)
User sees conviction score
```

### Key Concepts

**Attestation:** Third-party validation of a relationship
- Types: verify, dispute, strengthen, weaken
- Confidence: 0-100 (how sure is the attester)
- Evidence: Optional text explanation

**Conviction:** Aggregate network confidence score
- Score: 0-100 (0 = low confidence, 100 = high confidence)
- Weighted by: attester reputation, temporal decay, confidence
- Updated: Real-time when new attestations arrive

**Weights:**
- Verify: +1.0
- Dispute: -1.5 (higher to penalize fraud)
- Strengthen: +0.5
- Weaken: -0.5

**Reputation Multiplier:**
- Low-rep attester (trust_score 30): 0.5x weight
- Mid-rep attester (trust_score 50): 1.0x weight
- High-rep attester (trust_score 90): 1.8x weight

**Temporal Decay:**
- 180-day half-life
- Year-old attestation: ~25% weight
- 2-year-old attestation: ~6% weight

---

## 🐛 Troubleshooting

### Types not generated?
```bash
# Check lexicon files exist
ls -la /Users/israelwilson/Developer/rhizproto/lexicons/net/rhiz/relationship/attestation.json
ls -la /Users/israelwilson/Developer/rhizproto/lexicons/net/rhiz/conviction/*.json

# Regenerate
cd packages/rhiz-protocol
rm -rf src/generated
pnpm run codegen
```

### Database migration fails?
```bash
# Check current version
cd services/rhiz-api
alembic current

# Check migration history
alembic history

# Reset if needed (CAUTION: dev only)
alembic downgrade base
alembic upgrade head
```

### API endpoint not found?
```bash
# Check routes registered
cd services/rhiz-api
grep "conviction" app/main.py

# Should see:
# from app.api import conviction
# app.include_router(conviction.router)

# Restart server
# Ctrl+C and re-run: uvicorn app.main:app --reload
```

### Tests failing?
```bash
# Install test dependencies
cd services/rhiz-api
pip install pytest pytest-asyncio

# Run verbose
pytest app/tests/test_conviction.py -v -s

# Run specific test
pytest app/tests/test_conviction.py::test_conviction_single_verify -v
```

---

## 📞 Need Help?

### Check These First
1. `RHIZ_ATTESTATION_IMPLEMENTATION_PLAN.md` - Full 8-week plan
2. `PHASE_2A_IMPLEMENTATION_GUIDE.md` - Original tactical guide
3. `INTUITION_SYNTHESIS_SUMMARY.md` - High-level overview

### Common Issues

**Issue:** "Attestation type generated incorrectly"
**Fix:** Run `pnpm run codegen` in packages/rhiz-protocol

**Issue:** "Database table doesn't exist"
**Fix:** Run `alembic upgrade head` in services/rhiz-api

**Issue:** "Conviction calculation returns 0"
**Fix:** Check attestations exist in database: `SELECT * FROM attestations;`

**Issue:** "API returns 500 error"
**Fix:** Check logs: `tail -f services/rhiz-api/logs/app.log`

---

## 🎯 Success Criteria (Week 1)

By end of Week 1, you should have:
- ✅ TypeScript types generated from lexicons
- ✅ Database tables created (attestations, conviction_scores)
- ✅ Conviction calculator implemented
- ✅ Unit tests passing (8+ tests)
- ✅ API endpoints responding (even if no data yet)

**Test:** Run this command and get a response (even if 404):
```bash
curl "http://localhost:8000/xrpc/net.rhiz.conviction.getScore?uri=at://test/uri"
```

---

## 📈 What's Next?

### After Week 1
1. **Week 2:** Finish API endpoints + indexer integration
2. **Week 3:** SDK methods + basic UI
3. **Week 4:** Polish + testing
4. **Week 5:** Beta launch

### Immediate Next Steps (Today)
1. ✅ Generate types
2. ✅ Run database migration
3. ✅ Create conviction.py
4. ✅ Run unit tests
5. ✅ Commit progress

```bash
# Commit your progress
git add .
git commit -m "feat: Phase 2A foundation - types, migration, conviction calculator

- Generated TypeScript types from attestation lexicons
- Created attestations and conviction_scores tables
- Implemented ConvictionCalculator with reputation weighting and temporal decay
- Added unit tests for conviction algorithm
- All tests passing

Phase 2A Week 1 complete."

git push origin main
```

---

**Status:** Ready to execute
**Time to first working endpoint:** 30 minutes
**Time to first test attestation:** 2 hours

Let's ship conviction scores! 🚀

