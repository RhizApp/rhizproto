# Rhiz Protocol Attestation System: Execution Plan

**Version:** 1.0
**Date:** October 22, 2025
**Status:** Ready to Execute
**Timeline:** 8 weeks to launch

---

## Executive Summary

This plan executes Phase 2A: Core Attestation System for Rhiz Protocol, integrating Intuition Protocol's conviction-based validation into our AT Protocol-native architecture. We transform relationships from "dual-signed" to "network-verified with conviction scores."

**Goal:** Enable third-party attestations on relationships, calculate conviction scores, and display network confidence in relationship claims.

**Strategic Rationale:** Prove social attestation model works before adding economic complexity (Phase 3). This de-risks token economics by validating organic adoption first.

---

## Current State Assessment

### ✅ Completed
- **Lexicon schemas** - attestation.json and conviction/*.json exist
- **AT Protocol foundation** - DID-native architecture complete
- **Database** - PostgreSQL with relationship/entity tables
- **API infrastructure** - FastAPI with entities/graph endpoints
- **Firehose indexer** - Basic TypeScript indexer operational
- **SDK** - TypeScript SDK with DID operations

### ❌ Phase 2A Gaps (What We'll Build)
- Conviction calculation algorithm
- Database tables: `attestations`, `conviction_scores`
- API endpoints: `/xrpc/net.rhiz.conviction.*`
- Firehose: Attestation record indexing
- SDK: `attestRelationship()` method
- UI: ConvictionBadge, AttestationButton components
- Tests: Unit tests for conviction algorithm

---

## Success Criteria

### Technical Metrics
- ✅ **Performance:** Conviction calculation <100ms for 100 attestations
- ✅ **Latency:** API responses <200ms p95
- ✅ **Firehose lag:** <5 seconds commit-to-indexed
- ✅ **Uptime:** 99.9% availability

### Adoption Metrics
- 🎯 **Week 8:** 10% of relationships have ≥1 attestation
- 🎯 **Month 3:** 30% of relationships have ≥1 attestation
- 🎯 **Month 6:** 50% of relationships have ≥3 attestations

### Quality Metrics
- 🎯 **Accuracy:** 80%+ conviction correlation with manual validation
- 🎯 **Fraud detection:** 90%+ of fake relationships have conviction <40
- 🎯 **User trust:** 70%+ say conviction scores are helpful

---

## 8-Week Implementation Sprint

### Week 1-2: Foundation Layer

#### Week 1: Type Generation & Database Schema

**Day 1-2: Type Generation**
```bash
# Generate TypeScript types from lexicons
cd /Users/israelwilson/Developer/rhizproto/packages/rhiz-protocol
pnpm run codegen

# Verify generated files
ls -la src/generated/types/net/rhiz/relationship/
ls -la src/generated/types/net/rhiz/conviction/

# Build package
pnpm run build
```

**Verification:**
- `RelationshipAttestation` type exists
- `ConvictionScore` type exists
- No compilation errors

**Day 3-5: Database Migration**

Create: `services/rhiz-api/alembic/versions/002_attestation_tables.py`

```python
"""Add attestation and conviction tables

Revision ID: 002_attestation_tables
Revises: 001_did_migration
Create Date: 2025-10-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Attestations table
    op.create_table(
        'attestations',
        sa.Column('uri', sa.Text(), primary_key=True),
        sa.Column('attester_did', sa.Text(), nullable=False),
        sa.Column('target_uri', sa.Text(), nullable=False),
        sa.Column('attestation_type', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Integer(), nullable=False),
        sa.Column('evidence', sa.Text(), nullable=True),
        sa.Column('suggested_strength', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('indexed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('cid', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['attester_did'], ['entities.did'], ondelete='CASCADE'),
    )

    # Indexes for fast queries
    op.create_index('idx_attestations_target', 'attestations', ['target_uri'])
    op.create_index('idx_attestations_attester', 'attestations', ['attester_did'])
    op.create_index('idx_attestations_type', 'attestations', ['attestation_type'])
    op.create_index('idx_attestations_created', 'attestations', ['created_at'])

    # Conviction scores cache
    op.create_table(
        'conviction_scores',
        sa.Column('target_uri', sa.Text(), primary_key=True),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('attestation_count', sa.Integer(), nullable=False),
        sa.Column('verify_count', sa.Integer(), nullable=False),
        sa.Column('dispute_count', sa.Integer(), nullable=False),
        sa.Column('strengthen_count', sa.Integer(), nullable=False),
        sa.Column('weaken_count', sa.Integer(), nullable=False),
        sa.Column('last_updated', sa.DateTime(timezone=True), nullable=False),
        sa.Column('trend', sa.Text(), nullable=True),
        sa.Column('top_attester_reputation', sa.Integer(), nullable=True),
    )

    op.create_index('idx_conviction_score', 'conviction_scores', ['score'])
    op.create_index('idx_conviction_updated', 'conviction_scores', ['last_updated'])

    # Add conviction columns to relationships
    op.add_column('relationships', sa.Column('conviction_score', sa.Integer(), nullable=True))
    op.add_column('relationships', sa.Column('attestation_count', sa.Integer(), server_default='0'))

    op.create_index('idx_relationships_conviction', 'relationships', ['conviction_score'])

def downgrade():
    op.drop_index('idx_relationships_conviction')
    op.drop_column('relationships', 'attestation_count')
    op.drop_column('relationships', 'conviction_score')

    op.drop_index('idx_conviction_updated')
    op.drop_index('idx_conviction_score')
    op.drop_table('conviction_scores')

    op.drop_index('idx_attestations_created')
    op.drop_index('idx_attestations_type')
    op.drop_index('idx_attestations_attester')
    op.drop_index('idx_attestations_target')
    op.drop_table('attestations')
```

**Execute migration:**
```bash
cd services/rhiz-api
alembic upgrade head
```

**Verification:**
```sql
-- Verify tables exist
\dt attestations
\dt conviction_scores

-- Check indexes
\di idx_attestations_*
\di idx_conviction_*

-- Verify columns added to relationships
\d relationships
```

---

#### Week 2: Conviction Algorithm Core

**Day 6-10: Conviction Calculator Implementation**

Create: `services/rhiz-api/app/services/conviction.py`

```python
"""
Conviction score calculation algorithm.

This module calculates network confidence in attested records based on:
- Attestation types (verify, dispute, strengthen, weaken)
- Attester reputation (trust_score weighting)
- Temporal decay (old attestations matter less)
- Confidence levels (attester's stated confidence)

Conviction scores: 0-100 (integer, AT Protocol compliant)
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.entity import Entity

import logging

logger = logging.getLogger(__name__)


class Attestation:
    """Attestation data model for conviction calculation"""
    def __init__(
        self,
        uri: str,
        attester_did: str,
        attestation_type: str,
        confidence: int,
        created_at: datetime
    ):
        self.uri = uri
        self.attester_did = attester_did
        self.attestation_type = attestation_type
        self.confidence = confidence
        self.created_at = created_at


class ConvictionCalculator:
    """
    Calculate network conviction scores for attested records.

    Algorithm:
    1. Weight attestations by type (verify +1.0, dispute -1.5, etc.)
    2. Scale by attester reputation (0.5x to 2.0x)
    3. Apply temporal decay (180-day half-life)
    4. Scale by confidence (0-100)
    5. Normalize to 0-100 score
    """

    # Base weights by attestation type
    VERIFY_WEIGHT = 1.0
    DISPUTE_WEIGHT = -1.5  # Disputes weighted higher (fraud prevention)
    STRENGTHEN_WEIGHT = 0.5
    WEAKEN_WEIGHT = -0.5

    # Reputation multiplier bounds
    MIN_REPUTATION_MULTIPLIER = 0.5  # Even low-rep attestations have 50% weight
    MAX_REPUTATION_MULTIPLIER = 2.0  # High-rep attestations count 2x

    # Temporal decay
    DECAY_HALF_LIFE_DAYS = 180  # Attestations lose 50% weight every 6 months

    def calculate_conviction(
        self,
        target_uri: str,
        attestations: List[Attestation],
        db: Session
    ) -> Dict:
        """
        Calculate conviction score for a target record.

        Args:
            target_uri: AT URI of record being attested
            attestations: List of attestation objects
            db: Database session for attester lookups

        Returns:
            {
                'score': int (0-100),
                'attestation_count': int,
                'verify_count': int,
                'dispute_count': int,
                'strengthen_count': int,
                'weaken_count': int,
                'trend': str ('increasing' | 'stable' | 'decreasing'),
                'top_attester_reputation': int
            }
        """
        if not attestations:
            return self._empty_conviction()

        # Initialize counters
        counts = {
            'verify': 0,
            'dispute': 0,
            'strengthen': 0,
            'weaken': 0
        }

        weighted_sum = 0.0
        total_weight = 0.0
        attester_reputations = []
        now = datetime.utcnow()

        for attestation in attestations:
            # Fetch attester entity
            attester = db.query(Entity).filter(
                Entity.did == attestation.attester_did
            ).first()

            # Reputation score (0-100) normalized to 0-1
            attester_reputation = (attester.trust_score / 100.0) if attester else 0.5

            # Reputation multiplier (0.5x to 2.0x)
            reputation_multiplier = (
                self.MIN_REPUTATION_MULTIPLIER +
                attester_reputation * (
                    self.MAX_REPUTATION_MULTIPLIER - self.MIN_REPUTATION_MULTIPLIER
                )
            )

            # Temporal decay (exponential decay with 180-day half-life)
            age_days = (now - attestation.created_at).days
            decay_factor = 0.5 ** (age_days / self.DECAY_HALF_LIFE_DAYS)

            # Base weight by attestation type
            if attestation.attestation_type == 'verify':
                base_weight = self.VERIFY_WEIGHT
                counts['verify'] += 1
            elif attestation.attestation_type == 'dispute':
                base_weight = self.DISPUTE_WEIGHT
                counts['dispute'] += 1
            elif attestation.attestation_type == 'strengthen':
                base_weight = self.STRENGTHEN_WEIGHT
                counts['strengthen'] += 1
            elif attestation.attestation_type == 'weaken':
                base_weight = self.WEAKEN_WEIGHT
                counts['weaken'] += 1
            else:
                logger.warning(f"Unknown attestation type: {attestation.attestation_type}")
                base_weight = 0.0

            # Confidence scaling (0-100 scales weight)
            confidence_factor = attestation.confidence / 100.0

            # Final weight = base * reputation * decay * confidence
            final_weight = (
                base_weight *
                reputation_multiplier *
                decay_factor *
                confidence_factor
            )

            weighted_sum += final_weight
            total_weight += abs(final_weight)

            if attester:
                attester_reputations.append(attester.trust_score)

        # Normalize to 0-100 score
        if total_weight == 0:
            conviction_score = 50  # Neutral if no meaningful attestations
        else:
            # Map weighted sum to 0-100
            # Positive sum = high conviction, negative = low conviction
            normalized = weighted_sum / total_weight
            conviction_score = int(50 + (normalized * 50))
            conviction_score = max(0, min(100, conviction_score))

        # Calculate trend
        trend = self._calculate_trend(attestations, now)

        return {
            'score': conviction_score,
            'attestation_count': len(attestations),
            'verify_count': counts['verify'],
            'dispute_count': counts['dispute'],
            'strengthen_count': counts['strengthen'],
            'weaken_count': counts['weaken'],
            'trend': trend,
            'top_attester_reputation': max(attester_reputations) if attester_reputations else 0
        }

    def _calculate_trend(self, attestations: List[Attestation], now: datetime) -> str:
        """
        Calculate conviction trend: increasing, stable, or decreasing.

        Compares last 30 days vs previous 30 days.
        """
        thirty_days_ago = now - timedelta(days=30)
        sixty_days_ago = now - timedelta(days=60)

        recent = [a for a in attestations if a.created_at >= thirty_days_ago]
        previous = [a for a in attestations if sixty_days_ago <= a.created_at < thirty_days_ago]

        # Net positive attestations
        recent_net = sum(1 if a.attestation_type == 'verify' else -1 for a in recent)
        previous_net = sum(1 if a.attestation_type == 'verify' else -1 for a in previous)

        if len(recent) < 3:
            return 'stable'

        if recent_net > previous_net * 1.5:
            return 'increasing'
        elif recent_net < previous_net * 0.5:
            return 'decreasing'
        else:
            return 'stable'

    def _empty_conviction(self) -> Dict:
        """Return structure for records with no attestations"""
        return {
            'score': 0,
            'attestation_count': 0,
            'verify_count': 0,
            'dispute_count': 0,
            'strengthen_count': 0,
            'weaken_count': 0,
            'trend': 'stable',
            'top_attester_reputation': 0
        }
```

**Day 11-12: Unit Tests**

Create: `services/rhiz-api/app/tests/test_conviction.py`

```python
"""Unit tests for conviction calculator"""

import pytest
from datetime import datetime, timedelta
from app.services.conviction import ConvictionCalculator, Attestation
from app.models.entity import Entity


class MockDB:
    """Mock database session for testing"""
    def __init__(self, entities: dict):
        self.entities = entities

    def query(self, model):
        return self

    def filter(self, condition):
        return self

    def first(self):
        # Return mock entity based on test data
        return self.entities.get('default')


def test_conviction_no_attestations():
    """Zero conviction with no attestations"""
    calc = ConvictionCalculator()
    result = calc.calculate_conviction('at://test/uri', [], None)

    assert result['score'] == 0
    assert result['attestation_count'] == 0
    assert result['verify_count'] == 0
    assert result['dispute_count'] == 0


def test_conviction_single_verify():
    """Single verify attestation gives positive conviction"""
    calc = ConvictionCalculator()

    attestation = Attestation(
        uri='at://test/attestation/1',
        attester_did='did:plc:alice',
        attestation_type='verify',
        confidence=90,
        created_at=datetime.utcnow()
    )

    entity = Entity(did='did:plc:alice', name='Alice', type='person')
    entity.trust_score = 80

    db = MockDB({'default': entity})

    result = calc.calculate_conviction('at://test/relationship/1', [attestation], db)

    assert result['score'] > 50, "Verify should give positive conviction"
    assert result['attestation_count'] == 1
    assert result['verify_count'] == 1
    assert result['dispute_count'] == 0


def test_conviction_dispute_lowers_score():
    """Dispute attestations lower conviction"""
    calc = ConvictionCalculator()

    verify = Attestation(
        uri='at://test/attestation/1',
        attester_did='did:plc:alice',
        attestation_type='verify',
        confidence=80,
        created_at=datetime.utcnow()
    )

    dispute = Attestation(
        uri='at://test/attestation/2',
        attester_did='did:plc:bob',
        attestation_type='dispute',
        confidence=95,
        created_at=datetime.utcnow()
    )

    entity = Entity(did='did:plc:alice', name='Alice', type='person')
    entity.trust_score = 75

    db = MockDB({'default': entity})

    result = calc.calculate_conviction(
        'at://test/relationship/1',
        [verify, dispute],
        db
    )

    # Dispute weighted 1.5x, should dominate
    assert result['score'] < 50, "Dispute should lower conviction"
    assert result['dispute_count'] == 1
    assert result['verify_count'] == 1


def test_conviction_temporal_decay():
    """Old attestations have less weight"""
    calc = ConvictionCalculator()

    recent = Attestation(
        uri='at://test/attestation/1',
        attester_did='did:plc:alice',
        attestation_type='verify',
        confidence=90,
        created_at=datetime.utcnow()
    )

    old = Attestation(
        uri='at://test/attestation/2',
        attester_did='did:plc:bob',
        attestation_type='verify',
        confidence=90,
        created_at=datetime.utcnow() - timedelta(days=365)
    )

    entity = Entity(did='did:plc:alice', name='Alice', type='person')
    entity.trust_score = 75

    db = MockDB({'default': entity})

    result_recent = calc.calculate_conviction('at://test/1', [recent], db)
    result_old = calc.calculate_conviction('at://test/2', [old], db)

    assert result_recent['score'] > result_old['score'], \
        "Recent attestations should have higher conviction"


def test_conviction_reputation_weighting():
    """High-reputation attesters have more weight"""
    calc = ConvictionCalculator()

    attestation = Attestation(
        uri='at://test/attestation/1',
        attester_did='did:plc:alice',
        attestation_type='verify',
        confidence=90,
        created_at=datetime.utcnow()
    )

    # High reputation attester
    high_rep = Entity(did='did:plc:alice', name='Alice', type='person')
    high_rep.trust_score = 95

    # Low reputation attester
    low_rep = Entity(did='did:plc:alice', name='Alice', type='person')
    low_rep.trust_score = 30

    result_high = calc.calculate_conviction(
        'at://test/1',
        [attestation],
        MockDB({'default': high_rep})
    )

    result_low = calc.calculate_conviction(
        'at://test/2',
        [attestation],
        MockDB({'default': low_rep})
    )

    assert result_high['score'] > result_low['score'], \
        "High-reputation attesters should have more impact"


def test_conviction_multiple_attestations():
    """Multiple verifications increase conviction"""
    calc = ConvictionCalculator()

    attestations = [
        Attestation(
            uri=f'at://test/attestation/{i}',
            attester_did=f'did:plc:user{i}',
            attestation_type='verify',
            confidence=85,
            created_at=datetime.utcnow()
        )
        for i in range(5)
    ]

    entity = Entity(did='did:plc:alice', name='Alice', type='person')
    entity.trust_score = 80

    db = MockDB({'default': entity})

    result = calc.calculate_conviction('at://test/relationship/1', attestations, db)

    assert result['score'] >= 70, "Multiple verifications should give high conviction"
    assert result['attestation_count'] == 5
    assert result['verify_count'] == 5


def test_conviction_trend_calculation():
    """Trend detection works correctly"""
    calc = ConvictionCalculator()

    now = datetime.utcnow()

    # Recent attestations
    recent_attestations = [
        Attestation(
            uri=f'at://test/attestation/recent{i}',
            attester_did=f'did:plc:user{i}',
            attestation_type='verify',
            confidence=85,
            created_at=now - timedelta(days=i)
        )
        for i in range(5)
    ]

    entity = Entity(did='did:plc:alice', name='Alice', type='person')
    entity.trust_score = 80

    db = MockDB({'default': entity})

    result = calc.calculate_conviction(
        'at://test/relationship/1',
        recent_attestations,
        db
    )

    assert result['trend'] in ['increasing', 'stable', 'decreasing']
```

**Run tests:**
```bash
cd services/rhiz-api
pytest app/tests/test_conviction.py -v
```

**Success Criteria:**
- All tests pass ✅
- Conviction algorithm handles edge cases
- Temporal decay works correctly
- Reputation weighting validated

---

### Week 3-4: API & Indexer Integration

#### Week 3: API Endpoints

**Day 13-15: Conviction API Routes**

Create: `services/rhiz-api/app/api/conviction.py`

```python
"""Conviction API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.services.conviction import ConvictionCalculator, Attestation
from app.models.entity import Entity

router = APIRouter(prefix="/xrpc/net.rhiz.conviction", tags=["conviction"])


@router.get("/getScore")
async def get_conviction_score(
    uri: str = Query(..., description="AT URI of attested record"),
    db: Session = Depends(get_db)
):
    """
    Get conviction score for any attested record.

    Returns cached score if available, calculates fresh if not.
    """
    # Check if cached
    cached = db.execute(
        "SELECT * FROM conviction_scores WHERE target_uri = :uri",
        {"uri": uri}
    ).first()

    if cached:
        return {
            "uri": uri,
            "conviction": {
                "score": cached.score,
                "attestationCount": cached.attestation_count,
                "verifyCount": cached.verify_count,
                "disputeCount": cached.dispute_count,
                "strengthenCount": cached.strengthen_count,
                "weakenCount": cached.weaken_count,
                "lastUpdated": cached.last_updated.isoformat(),
                "trend": cached.trend,
                "topAttesterReputation": cached.top_attester_reputation
            }
        }

    # Calculate fresh
    attestation_rows = db.execute(
        "SELECT * FROM attestations WHERE target_uri = :uri",
        {"uri": uri}
    ).fetchall()

    if not attestation_rows:
        raise HTTPException(status_code=404, detail="No attestations found")

    # Convert to Attestation objects
    attestations = [
        Attestation(
            uri=row.uri,
            attester_did=row.attester_did,
            attestation_type=row.attestation_type,
            confidence=row.confidence,
            created_at=row.created_at
        )
        for row in attestation_rows
    ]

    calc = ConvictionCalculator()
    conviction = calc.calculate_conviction(uri, attestations, db)

    return {
        "uri": uri,
        "conviction": {
            "score": conviction['score'],
            "attestationCount": conviction['attestation_count'],
            "verifyCount": conviction['verify_count'],
            "disputeCount": conviction['dispute_count'],
            "strengthenCount": conviction['strengthen_count'],
            "weakenCount": conviction['weaken_count'],
            "lastUpdated": datetime.utcnow().isoformat(),
            "trend": conviction['trend'],
            "topAttesterReputation": conviction['top_attester_reputation']
        }
    }


@router.get("/listAttestations")
async def list_attestations(
    uri: str = Query(..., description="AT URI of attested record"),
    type: Optional[str] = Query(None, description="Filter by attestation type"),
    minConfidence: Optional[int] = Query(None, description="Minimum confidence level"),
    limit: int = Query(50, le=100),
    cursor: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all attestations for a record"""

    query = "SELECT * FROM attestations WHERE target_uri = :uri"
    params = {"uri": uri}

    if type:
        query += " AND attestation_type = :type"
        params["type"] = type

    if minConfidence:
        query += " AND confidence >= :min_confidence"
        params["min_confidence"] = minConfidence

    query += " ORDER BY created_at DESC"

    if cursor:
        query += " AND created_at < :cursor"
        params["cursor"] = cursor

    query += " LIMIT :limit"
    params["limit"] = limit + 1

    attestation_rows = db.execute(query, params).fetchall()

    has_more = len(attestation_rows) > limit
    if has_more:
        attestation_rows = attestation_rows[:limit]
        next_cursor = attestation_rows[-1].created_at.isoformat()
    else:
        next_cursor = None

    # Fetch attester profiles
    result = []
    for row in attestation_rows:
        attester = db.query(Entity).filter(
            Entity.did == row.attester_did
        ).first()

        result.append({
            "uri": row.uri,
            "cid": row.cid,
            "record": {
                "targetRelationship": row.target_uri,
                "attester": row.attester_did,
                "attestationType": row.attestation_type,
                "confidence": row.confidence,
                "evidence": row.evidence,
                "createdAt": row.created_at.isoformat()
            },
            "attester": {
                "did": attester.did,
                "name": attester.name,
                "type": attester.type
            } if attester else None,
            "attesterReputation": attester.trust_score if attester else 0
        })

    return {
        "attestations": result,
        "cursor": next_cursor
    }
```

**Day 16-17: Register Routes**

Update: `services/rhiz-api/app/main.py`

```python
from app.api import conviction

# Add to app
app.include_router(conviction.router)
```

**Test endpoints:**
```bash
# Start API server
cd services/rhiz-api
uvicorn app.main:app --reload

# Test getScore endpoint (should 404 - no attestations yet)
curl "http://localhost:8000/xrpc/net.rhiz.conviction.getScore?uri=at://did:plc:test/net.rhiz.relationship.record/123"

# Test listAttestations endpoint
curl "http://localhost:8000/xrpc/net.rhiz.conviction.listAttestations?uri=at://did:plc:test/net.rhiz.relationship.record/123"
```

---

#### Week 4: Firehose Indexer

**Day 18-21: Update Indexer**

Update: `services/rhiz-atproto/src/indexer.ts`

```typescript
import { Firehose } from '@atproto/sync'
import { Database } from './db'

export class RhizIndexer {
  private db: Database

  async indexCommit(commit: Commit) {
    // Existing logic for relationships, entities, etc.

    // NEW: Index attestation records
    if (commit.collection === 'net.rhiz.relationship.attestation') {
      await this.indexAttestation(commit)
    }
  }

  async indexAttestation(commit: Commit) {
    const record = commit.record as RelationshipAttestation

    console.log(`Indexing attestation: ${commit.uri}`)

    // Store attestation
    await this.db.query(`
      INSERT INTO attestations (
        uri, attester_did, target_uri, attestation_type,
        confidence, evidence, suggested_strength,
        created_at, indexed_at, cid
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
      ON CONFLICT (uri) DO UPDATE SET
        attestation_type = EXCLUDED.attestation_type,
        confidence = EXCLUDED.confidence,
        evidence = EXCLUDED.evidence,
        indexed_at = EXCLUDED.indexed_at
    `, [
      commit.uri,
      record.attester,
      record.targetRelationship,
      record.attestationType,
      record.confidence,
      record.evidence || null,
      record.suggestedStrength || null,
      record.createdAt,
      new Date(),
      commit.cid
    ])

    // Trigger conviction recalculation
    await this.recalculateConviction(record.targetRelationship)

    console.log(`✓ Indexed attestation for ${record.targetRelationship}`)
  }

  async recalculateConviction(targetUri: string) {
    console.log(`Recalculating conviction for ${targetUri}`)

    // Call conviction API to recalculate
    const response = await fetch(
      `http://localhost:8000/xrpc/net.rhiz.conviction.getScore?uri=${encodeURIComponent(targetUri)}`
    )

    if (!response.ok) {
      console.error(`Failed to calculate conviction: ${response.statusText}`)
      return
    }

    const data = await response.json()
    const conviction = data.conviction

    // Update conviction_scores cache
    await this.db.query(`
      INSERT INTO conviction_scores (
        target_uri, score, attestation_count,
        verify_count, dispute_count, strengthen_count, weaken_count,
        last_updated, trend, top_attester_reputation
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
      ON CONFLICT (target_uri) DO UPDATE SET
        score = EXCLUDED.score,
        attestation_count = EXCLUDED.attestation_count,
        verify_count = EXCLUDED.verify_count,
        dispute_count = EXCLUDED.dispute_count,
        strengthen_count = EXCLUDED.strengthen_count,
        weaken_count = EXCLUDED.weaken_count,
        last_updated = EXCLUDED.last_updated,
        trend = EXCLUDED.trend,
        top_attester_reputation = EXCLUDED.top_attester_reputation
    `, [
      targetUri,
      conviction.score,
      conviction.attestationCount,
      conviction.verifyCount,
      conviction.disputeCount,
      conviction.strengthenCount,
      conviction.weakenCount,
      new Date(),
      conviction.trend,
      conviction.topAttesterReputation
    ])

    // If target is a relationship, update relationship table
    if (targetUri.includes('net.rhiz.relationship.record')) {
      await this.db.query(`
        UPDATE relationships
        SET conviction_score = $1, attestation_count = $2
        WHERE uri = $3
      `, [conviction.score, conviction.attestationCount, targetUri])
    }

    console.log(`✓ Updated conviction: ${conviction.score}/100 (${conviction.attestationCount} attestations)`)
  }
}
```

**Day 22: Test Indexer**

```bash
# Start indexer
cd services/rhiz-atproto
pnpm run ingest

# Monitor logs for attestation indexing
tail -f logs/indexer.log
```

---

### Week 5-6: SDK & UI Layer

#### Week 5: SDK Methods

**Day 23-26: SDK Implementation**

Update: `packages/rhiz-sdk/src/client.ts`

```typescript
import { Agent } from '@atproto/api'

export class RhizClient {
  private agent: Agent

  /**
   * Attest to a relationship record
   */
  async attestRelationship(params: {
    targetRelationship: string  // AT URI
    attestationType: 'verify' | 'dispute' | 'strengthen' | 'weaken'
    confidence: number  // 0-100
    evidence?: string
    suggestedStrength?: number
  }): Promise<{ uri: string; cid: string }> {
    const record = {
      $type: 'net.rhiz.relationship.attestation',
      targetRelationship: params.targetRelationship,
      attester: this.agent.session?.did,
      attestationType: params.attestationType,
      confidence: params.confidence,
      evidence: params.evidence,
      suggestedStrength: params.suggestedStrength,
      createdAt: new Date().toISOString()
    }

    // Write to user's repo
    const result = await this.agent.com.atproto.repo.createRecord({
      repo: this.agent.session!.did,
      collection: 'net.rhiz.relationship.attestation',
      record
    })

    return {
      uri: result.uri,
      cid: result.cid
    }
  }

  /**
   * Get conviction score for a record
   */
  async getConviction(uri: string): Promise<ConvictionScore> {
    const response = await fetch(
      `${this.apiUrl}/xrpc/net.rhiz.conviction.getScore?uri=${encodeURIComponent(uri)}`
    )

    if (!response.ok) {
      throw new Error(`Failed to get conviction: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * List attestations for a record
   */
  async listAttestations(params: {
    uri: string
    type?: 'verify' | 'dispute' | 'strengthen' | 'weaken'
    minConfidence?: number
    limit?: number
    cursor?: string
  }): Promise<{ attestations: Attestation[]; cursor?: string }> {
    const queryParams = new URLSearchParams({
      uri: params.uri,
      ...(params.type && { type: params.type }),
      ...(params.minConfidence && { minConfidence: params.minConfidence.toString() }),
      ...(params.limit && { limit: params.limit.toString() }),
      ...(params.cursor && { cursor: params.cursor })
    })

    const response = await fetch(
      `${this.apiUrl}/xrpc/net.rhiz.conviction.listAttestations?${queryParams}`
    )

    if (!response.ok) {
      throw new Error(`Failed to list attestations: ${response.statusText}`)
    }

    return response.json()
  }
}

export interface ConvictionScore {
  uri: string
  conviction: {
    score: number
    attestationCount: number
    verifyCount: number
    disputeCount: number
    lastUpdated: string
    trend: 'increasing' | 'stable' | 'decreasing'
    topAttesterReputation: number
  }
}

export interface Attestation {
  uri: string
  cid: string
  record: {
    targetRelationship: string
    attester: string
    attestationType: string
    confidence: number
    evidence?: string
    createdAt: string
  }
  attester?: {
    did: string
    name: string
    type: string
  }
  attesterReputation: number
}
```

**Day 27: SDK Tests**

Create: `packages/rhiz-sdk/src/__tests__/attestations.test.ts`

```typescript
import { describe, it, expect, beforeAll } from 'vitest'
import { RhizClient } from '../client'

describe('Attestation SDK', () => {
  let client: RhizClient

  beforeAll(async () => {
    client = new RhizClient({
      apiUrl: 'http://localhost:8000',
      atproto: {
        service: 'https://bsky.social'
      }
    })

    // Login with test account
    await client.login('test.bsky.social', 'password')
  })

  it('should create attestation', async () => {
    const result = await client.attestRelationship({
      targetRelationship: 'at://did:plc:test/net.rhiz.relationship.record/123',
      attestationType: 'verify',
      confidence: 90,
      evidence: 'I know both parties personally'
    })

    expect(result.uri).toMatch(/^at:\/\//)
    expect(result.cid).toBeTruthy()
  })

  it('should get conviction score', async () => {
    const conviction = await client.getConviction(
      'at://did:plc:test/net.rhiz.relationship.record/123'
    )

    expect(conviction.conviction.score).toBeGreaterThanOrEqual(0)
    expect(conviction.conviction.score).toBeLessThanOrEqual(100)
  })

  it('should list attestations', async () => {
    const result = await client.listAttestations({
      uri: 'at://did:plc:test/net.rhiz.relationship.record/123',
      limit: 10
    })

    expect(Array.isArray(result.attestations)).toBe(true)
  })
})
```

---

#### Week 6: UI Components

**Day 28-31: React Components**

Create: `services/fundrhiz/components/ConvictionBadge.tsx`

```typescript
import React from 'react'
import { Badge } from '@/components/ui/badge'

interface ConvictionBadgeProps {
  score: number
  attestationCount: number
  trend?: 'increasing' | 'stable' | 'decreasing'
  className?: string
}

export function ConvictionBadge({
  score,
  attestationCount,
  trend = 'stable',
  className = ''
}: ConvictionBadgeProps) {
  // Color based on score
  const getVariant = (score: number) => {
    if (score >= 80) return 'success'
    if (score >= 60) return 'warning'
    if (score >= 40) return 'default'
    return 'destructive'
  }

  // Trend icon
  const trendIcon = {
    increasing: '↗',
    stable: '→',
    decreasing: '↘'
  }[trend]

  return (
    <Badge
      variant={getVariant(score)}
      className={`flex items-center gap-2 ${className}`}
    >
      <span className="font-bold">{score}%</span>
      <span className="text-xs">verified</span>
      <span className="text-xs opacity-75">{trendIcon}</span>
      <span className="text-xs opacity-75">
        {attestationCount} {attestationCount === 1 ? 'attestation' : 'attestations'}
      </span>
    </Badge>
  )
}
```

Create: `services/fundrhiz/components/AttestationButton.tsx`

```typescript
'use client'

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Slider } from '@/components/ui/slider'
import { Textarea } from '@/components/ui/textarea'
import { RhizClient } from '@atproto/rhiz-sdk'
import { useSession } from 'next-auth/react'

interface AttestationButtonProps {
  relationshipUri: string
  onAttested?: () => void
}

export function AttestationButton({ relationshipUri, onAttested }: AttestationButtonProps) {
  const { data: session } = useSession()
  const [showForm, setShowForm] = useState(false)
  const [type, setType] = useState<'verify' | 'dispute'>('verify')
  const [confidence, setConfidence] = useState(80)
  const [evidence, setEvidence] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async () => {
    if (!session) {
      alert('Please log in to attest')
      return
    }

    setSubmitting(true)

    try {
      const client = new RhizClient({
        apiUrl: process.env.NEXT_PUBLIC_RHIZ_API_URL!,
        atproto: {
          service: 'https://bsky.social'
        }
      })

      // Use session credentials
      await client.attestRelationship({
        targetRelationship: relationshipUri,
        attestationType: type,
        confidence,
        evidence: evidence.trim() || undefined
      })

      setShowForm(false)
      setEvidence('')
      onAttested?.()

      alert('Attestation submitted successfully!')
    } catch (error) {
      console.error('Failed to submit attestation:', error)
      alert('Failed to submit attestation. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <>
      <Button
        onClick={() => setShowForm(true)}
        variant="outline"
        size="sm"
      >
        Attest to this relationship
      </Button>

      <Dialog open={showForm} onOpenChange={setShowForm}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Attest to Relationship</DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Attestation Type</Label>
              <RadioGroup value={type} onValueChange={(v) => setType(v as any)}>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="verify" id="verify" />
                  <Label htmlFor="verify" className="font-normal">
                    Verify - I confirm this relationship exists
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="dispute" id="dispute" />
                  <Label htmlFor="dispute" className="font-normal">
                    Dispute - I don't believe this relationship is accurate
                  </Label>
                </div>
              </RadioGroup>
            </div>

            <div className="space-y-2">
              <Label>Confidence: {confidence}%</Label>
              <Slider
                value={[confidence]}
                onValueChange={([v]) => setConfidence(v)}
                min={0}
                max={100}
                step={5}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="evidence">Evidence (optional)</Label>
              <Textarea
                id="evidence"
                value={evidence}
                onChange={(e) => setEvidence(e.target.value)}
                placeholder="e.g., 'I worked with both of them at TechCo for 2 years'"
                maxLength={1000}
                rows={3}
              />
              <p className="text-xs text-muted-foreground">
                {evidence.length}/1000 characters
              </p>
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setShowForm(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={submitting}>
              {submitting ? 'Submitting...' : 'Submit Attestation'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}
```

**Day 32-34: Integrate Components**

Update: `services/fundrhiz/app/relationships/[id]/page.tsx`

```typescript
import { ConvictionBadge } from '@/components/ConvictionBadge'
import { AttestationButton } from '@/components/AttestationButton'

export default async function RelationshipPage({ params }: { params: { id: string } }) {
  const relationship = await getRelationship(params.id)
  const conviction = await getConviction(relationship.uri)

  return (
    <div>
      <h1>{relationship.participants.map(p => p.name).join(' ↔ ')}</h1>

      <div className="flex items-center gap-4 mt-4">
        <ConvictionBadge
          score={conviction.conviction.score}
          attestationCount={conviction.conviction.attestationCount}
          trend={conviction.conviction.trend}
        />

        <AttestationButton
          relationshipUri={relationship.uri}
          onAttested={() => revalidatePath(`/relationships/${params.id}`)}
        />
      </div>

      {/* Rest of relationship display */}
    </div>
  )
}
```

---

### Week 7-8: Testing & Launch

#### Week 7: Integration Testing

**Day 35-38: End-to-End Tests**

Create: `services/rhiz-api/app/tests/test_integration.py`

```python
"""Integration tests for full attestation flow"""

import pytest
from datetime import datetime
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_full_attestation_flow():
    """Test complete attestation flow from creation to conviction"""

    # 1. Create attestation via firehose (simulated)
    attestation_data = {
        'uri': 'at://did:plc:test/net.rhiz.relationship.attestation/abc123',
        'attester_did': 'did:plc:alice',
        'target_uri': 'at://did:plc:bob/net.rhiz.relationship.record/xyz789',
        'attestation_type': 'verify',
        'confidence': 90,
        'evidence': 'I know both parties',
        'created_at': datetime.utcnow().isoformat(),
        'cid': 'bafy123...'
    }

    # Simulate indexer inserting attestation
    # (In real flow, this comes from firehose)

    # 2. Query conviction score
    response = client.get(
        f"/xrpc/net.rhiz.conviction.getScore",
        params={'uri': attestation_data['target_uri']}
    )

    assert response.status_code == 200
    data = response.json()
    assert data['conviction']['attestationCount'] >= 1

    # 3. List attestations
    response = client.get(
        f"/xrpc/net.rhiz.conviction.listAttestations",
        params={'uri': attestation_data['target_uri']}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data['attestations']) >= 1


def test_multiple_attestations_aggregate():
    """Multiple attestations correctly aggregate into conviction"""

    target_uri = 'at://did:plc:test/net.rhiz.relationship.record/multi123'

    # Create 5 verify attestations
    # (In real flow, these come from different users via firehose)

    # Query conviction
    response = client.get(
        f"/xrpc/net.rhiz.conviction.getScore",
        params={'uri': target_uri}
    )

    assert response.status_code == 200
    data = response.json()

    # With 5 verifications, conviction should be high
    assert data['conviction']['score'] >= 70
    assert data['conviction']['verifyCount'] == 5
    assert data['conviction']['disputeCount'] == 0


def test_dispute_lowers_conviction():
    """Dispute attestations lower conviction score"""

    target_uri = 'at://did:plc:test/net.rhiz.relationship.record/dispute123'

    # Create 1 verify, 1 dispute
    # Dispute weighted 1.5x should dominate

    response = client.get(
        f"/xrpc/net.rhiz.conviction.getScore",
        params={'uri': target_uri}
    )

    assert response.status_code == 200
    data = response.json()

    # Conviction should be below neutral
    assert data['conviction']['score'] < 50
    assert data['conviction']['disputeCount'] >= 1
```

**Run integration tests:**
```bash
cd services/rhiz-api
pytest app/tests/test_integration.py -v
```

**Day 39-41: Load Testing**

```python
"""Load tests for conviction system"""

import pytest
from locust import HttpUser, task, between


class ConvictionLoadTest(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_conviction_score(self):
        uri = 'at://did:plc:test/net.rhiz.relationship.record/load123'
        self.client.get(f"/xrpc/net.rhiz.conviction.getScore?uri={uri}")

    @task(1)
    def list_attestations(self):
        uri = 'at://did:plc:test/net.rhiz.relationship.record/load123'
        self.client.get(f"/xrpc/net.rhiz.conviction.listAttestations?uri={uri}&limit=50")
```

**Run load tests:**
```bash
locust -f app/tests/load_test.py --host http://localhost:8000 --users 100 --spawn-rate 10
```

**Performance targets:**
- Conviction calculation: <100ms for 100 attestations ✅
- API p95 latency: <200ms ✅
- Throughput: 1000 req/s ✅

---

#### Week 8: Launch Preparation

**Day 42-44: Documentation**

Create launch docs:
- API endpoint documentation
- SDK usage examples
- UI component library
- Deployment guide
- Monitoring setup

**Day 45-47: Beta Testing**

- Deploy to staging environment
- Invite 20 internal beta testers
- Monitor for bugs and UX issues
- Gather feedback on conviction algorithm
- Validate conviction accuracy

**Day 48-49: Production Deployment**

```bash
# Build all packages
cd /Users/israelwilson/Developer/rhizproto
pnpm build

# Run database migration
cd services/rhiz-api
alembic upgrade head

# Deploy services
docker-compose -f docker-compose.rhiz.yml up -d

# Start firehose indexer
cd services/rhiz-atproto
pm2 start dist/indexer.js --name rhiz-indexer

# Start API server
cd services/rhiz-api
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name rhiz-api

# Deploy FundRhiz UI
cd services/fundrhiz
vercel --prod
```

**Day 50: Launch** 🚀

- Public announcement
- Monitor metrics dashboard
- Track adoption rates
- Respond to issues

---

## Risk Mitigation

### Technical Risks

**Risk:** Conviction calculation too slow with many attestations
**Mitigation:**
- Cache conviction scores in database
- Recalculate only on new attestation (incremental)
- Optimize SQL queries with proper indexes
- Background job for batch recalculation if needed

**Risk:** Firehose indexing lag
**Mitigation:**
- Monitor lag metrics (<5 seconds target)
- Scale indexer horizontally if needed
- Use Redis pub/sub for real-time updates

**Risk:** Database bottleneck
**Mitigation:**
- PostgreSQL connection pooling
- Read replicas for query load
- Materialized views for complex queries

### Adoption Risks

**Risk:** Users don't attest organically
**Mitigation:**
- Gamification: Top attesters leaderboard
- Incentives: High conviction = higher search ranking
- Onboarding prompts: "Help verify 3 relationships"
- Social proof: "15 people attested this"

**Risk:** Low-quality attestations (spam)
**Mitigation:**
- Reputation weighting (low-rep = low impact)
- Rate limiting (max 50 attestations/day)
- Dispute mechanism (flag bad attestations)
- ML-based spam detection

### Security Risks

**Risk:** Sybil attacks (fake attestations)
**Mitigation:**
- Reputation multiplier (new accounts have 0.5x weight)
- Require minimum trust_score to attest
- Graph analysis to detect suspicious patterns
- Human review for disputed high-value relationships

**Risk:** Collusion (coordinated false attestations)
**Mitigation:**
- Diversity bonus (attestations from different clusters count more)
- Temporal analysis (sudden spikes flagged)
- Social graph analysis (detect coordinated accounts)

---

## Monitoring & Metrics

### Technical Metrics

**System Health:**
```
- API latency p50/p95/p99
- Conviction calculation time
- Firehose indexing lag
- Database query performance
- Error rates by endpoint
```

**Dashboards:**
- Grafana for real-time metrics
- DataDog for APM
- Sentry for error tracking

### Business Metrics

**Adoption:**
```
- Attestations created per day
- % of relationships with ≥1 attestation
- Active attesters (DAU/MAU)
- Attestations per user (distribution)
```

**Quality:**
```
- Average conviction score
- Distribution of conviction scores
- Verify vs dispute ratio
- Attestation confidence levels
```

**Engagement:**
```
- Time to first attestation (new users)
- Attestation completion rate
- Return rate (users who attest again)
```

---

## Post-Launch: Phase 2B Planning

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

### Phase 2B: Triple-Based Claims (Months 4-6)

**Next features:**
1. Decompose relationships into atomic triples
2. Attest specific relationship fields (not whole relationships)
3. Triple pattern matching queries
4. Granular conviction per field

**Preparation:**
- Design `net.rhiz.triple.claim` lexicon
- Plan triple indexing strategy
- Prototype triple query engine

### Phase 2C: Expertise & Credentials (Months 7-9)

**Next features:**
1. Expertise claims and attestations
2. Credential verification by institutions
3. Context-aware matching using expertise
4. Domain taxonomy and search

---

## Success Playbook

### If Adoption is Low (<10% by Week 8)

**Actions:**
1. Add onboarding flow with attestation prompts
2. Gamify: "Earn Trust Badge - Attest 10 relationships"
3. Send notifications: "Your relationship needs verification"
4. Show social proof: "Be the first to attest"
5. Add incentives: High conviction relationships rank higher

### If Conviction Accuracy is Low (<70%)

**Actions:**
1. Adjust conviction algorithm weights
2. Increase dispute weight (penalize bad relationships more)
3. Add temporal decay tweaking
4. Improve reputation multiplier formula
5. Manual validation of sample set

### If Performance is Slow (>200ms p95)

**Actions:**
1. Add Redis caching layer
2. Optimize SQL queries with EXPLAIN ANALYZE
3. Add database indexes on hot paths
4. Batch conviction recalculations
5. Scale API horizontally (load balancer)

---

## Resources & Dependencies

### Team Requirements

**Engineering:**
- 1 Backend engineer (Python/FastAPI) - conviction algorithm, API
- 1 Full-stack engineer (TypeScript) - SDK, firehose indexer
- 1 Frontend engineer (React) - UI components
- 0.5 DevOps - deployment, monitoring

**Product:**
- 0.5 PM - coordination, user testing
- 0.5 Designer - UI/UX for conviction badges

### Infrastructure

**Required services:**
- PostgreSQL 14+ (existing)
- Redis 7+ (for caching)
- AT Protocol firehose access (existing)
- Monitoring (Grafana + Prometheus)

**Estimated costs:**
- Database: $50/month (upgraded tier)
- Redis: $30/month
- Monitoring: $20/month
- Total: ~$100/month additional

---

## Timeline Summary

| Week | Focus | Deliverables |
|------|-------|-------------|
| 1 | Foundation | Type generation, database migration |
| 2 | Algorithm | Conviction calculator, unit tests |
| 3 | API | Conviction endpoints, routing |
| 4 | Indexer | Firehose attestation indexing |
| 5 | SDK | Client methods for attestations |
| 6 | UI | React components (badges, buttons) |
| 7 | Testing | Integration tests, load tests |
| 8 | Launch | Beta testing, production deployment |

---

## Key Decision Points

### Week 2 Checkpoint
**Decision:** Proceed with current conviction algorithm or adjust weights?
**Criteria:** Unit test results, edge case handling

### Week 4 Checkpoint
**Decision:** Indexer performance acceptable or needs optimization?
**Criteria:** <5 second lag, no errors, handles 100 attestations/min

### Week 6 Checkpoint
**Decision:** UI components ready for production or need redesign?
**Criteria:** User testing feedback, accessibility, mobile support

### Week 8 Checkpoint
**Decision:** Launch publicly or extend beta testing?
**Criteria:** No critical bugs, performance targets met, positive feedback

---

## Appendix

### Lexicon Schemas Location
```
lexicons/net/rhiz/
  relationship/attestation.json ✅
  conviction/defs.json ✅
  conviction/getScore.json ✅
  conviction/listAttestations.json ✅
```

### Generated Types Location
```
packages/rhiz-protocol/src/generated/types/net/rhiz/
  relationship/attestation.ts (to be generated)
  conviction/defs.ts (to be generated)
```

### Database Tables
```sql
attestations (uri, attester_did, target_uri, attestation_type, confidence, ...)
conviction_scores (target_uri, score, attestation_count, verify_count, ...)
relationships (+ conviction_score, + attestation_count)
```

### API Endpoints
```
GET  /xrpc/net.rhiz.conviction.getScore?uri={uri}
GET  /xrpc/net.rhiz.conviction.listAttestations?uri={uri}&type={type}&...
```

### SDK Methods
```typescript
client.attestRelationship({ targetRelationship, attestationType, confidence, ... })
client.getConviction(uri)
client.listAttestations({ uri, type, minConfidence, limit, cursor })
```

---

## Execution Checklist

### Pre-Work
- [ ] Review INTUITION_INTEGRATION_ANALYSIS.md
- [ ] Review PHASE_2A_IMPLEMENTATION_GUIDE.md
- [ ] Validate lexicon schemas exist
- [ ] Ensure development environment ready

### Week 1-2: Foundation
- [ ] Generate TypeScript types from lexicons
- [ ] Create database migration
- [ ] Run migration in dev environment
- [ ] Implement conviction calculator
- [ ] Write unit tests
- [ ] All tests pass

### Week 3-4: Integration
- [ ] Create conviction API endpoints
- [ ] Register routes in main.py
- [ ] Test API endpoints locally
- [ ] Update firehose indexer
- [ ] Test attestation indexing
- [ ] Verify conviction recalculation

### Week 5-6: SDK & UI
- [ ] Implement SDK methods
- [ ] Write SDK tests
- [ ] Create React components
- [ ] Integrate components into FundRhiz
- [ ] Test end-to-end UI flow

### Week 7-8: Launch
- [ ] Run integration tests
- [ ] Run load tests
- [ ] Write documentation
- [ ] Deploy to staging
- [ ] Beta test (20 users)
- [ ] Fix critical bugs
- [ ] Deploy to production
- [ ] Launch announcement
- [ ] Monitor metrics

### Post-Launch
- [ ] Week 1: Daily monitoring
- [ ] Week 2: First metrics review
- [ ] Week 4: Iteration based on feedback
- [ ] Week 8: Phase 2A evaluation
- [ ] Month 3: Phase 2B planning

---

**Status:** Ready to Execute
**Timeline:** 8 weeks to production
**Confidence:** High (schemas ready, architecture proven, team capable)

Let's build the conviction layer. 🚀

