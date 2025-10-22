# Phase 2A Implementation Guide: Attestation System

## Overview

This guide provides step-by-step instructions for implementing the core attestation system for Rhiz Protocol, inspired by Intuition Protocol's conviction mechanism.

**Goal:** Enable third-party attestations on relationships and calculate network conviction scores.

**Timeline:** 6-8 weeks

**Prerequisites:**
- AT Protocol native foundation (✅ Complete)
- Firehose indexer operational
- PostgreSQL database with relationship records

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  User Repository (Source of Truth)                          │
│                                                               │
│  at://did:plc:alice/net.rhiz.relationship.record/3jx7...    │
│  at://did:plc:carol/net.rhiz.relationship.attestation/3jx8..│
│  at://did:plc:david/net.rhiz.relationship.attestation/3jx9..│
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  AT Protocol Firehose                                        │
│  Real-time stream of commits                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Rhiz AppView (Indexer)                                      │
│  - Indexes net.rhiz.relationship.attestation records        │
│  - Calculates conviction scores                             │
│  - Updates relationship conviction in real-time             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Query API                                                   │
│  - GET /xrpc/net.rhiz.conviction.getScore                   │
│  - GET /xrpc/net.rhiz.conviction.listAttestations           │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 2A Tasks

### Week 1-2: Schema & Database

#### Task 1.1: Lexicon Schemas (✅ Complete)

Created schemas:
- `net.rhiz.relationship.attestation.json` - Attestation record type
- `net.rhiz.conviction.defs.json` - Conviction score definitions
- `net.rhiz.conviction.getScore.json` - Query to get conviction
- `net.rhiz.conviction.listAttestations.json` - List attestations

#### Task 1.2: Generate TypeScript Types

```bash
cd packages/rhiz-protocol
pnpm run codegen
```

This will generate types in `src/client/types/net/rhiz/`:
- `RelationshipAttestation`
- `ConvictionDefs`
- Etc.

#### Task 1.3: Database Migration

Create migration: `services/rhiz-api/alembic/versions/XXX_add_attestations.py`

```python
"""Add attestation tables

Revision ID: add_attestations
Revises: previous_migration
Create Date: 2025-10-22
"""

from alembic import op
import sqlalchemy as sa

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
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('indexed_at', sa.DateTime(), nullable=False),
        sa.Column('cid', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['attester_did'], ['entities.did']),
    )

    op.create_index('idx_attestations_target', 'attestations', ['target_uri'])
    op.create_index('idx_attestations_attester', 'attestations', ['attester_did'])
    op.create_index('idx_attestations_type', 'attestations', ['attestation_type'])
    op.create_index('idx_attestations_created', 'attestations', ['created_at'])

    # Conviction scores cache table
    op.create_table(
        'conviction_scores',
        sa.Column('target_uri', sa.Text(), primary_key=True),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('attestation_count', sa.Integer(), nullable=False),
        sa.Column('verify_count', sa.Integer(), nullable=False),
        sa.Column('dispute_count', sa.Integer(), nullable=False),
        sa.Column('strengthen_count', sa.Integer(), nullable=False),
        sa.Column('weaken_count', sa.Integer(), nullable=False),
        sa.Column('last_updated', sa.DateTime(), nullable=False),
        sa.Column('trend', sa.Text(), nullable=True),
        sa.Column('top_attester_reputation', sa.Integer(), nullable=True),
    )

    op.create_index('idx_conviction_score', 'conviction_scores', ['score'])
    op.create_index('idx_conviction_updated', 'conviction_scores', ['last_updated'])

    # Add conviction fields to relationships table
    op.add_column('relationships', sa.Column('conviction_score', sa.Integer(), nullable=True))
    op.add_column('relationships', sa.Column('attestation_count', sa.Integer(), default=0))

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

Run migration:
```bash
cd services/rhiz-api
alembic upgrade head
```

---

### Week 3-4: Conviction Algorithm

#### Task 2.1: Conviction Calculation Algorithm

Create: `services/rhiz-api/app/services/conviction.py`

```python
from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import Attestation, Entity

class ConvictionCalculator:
    """Calculate network conviction scores for attested records"""

    # Weighting parameters
    VERIFY_WEIGHT = 1.0
    DISPUTE_WEIGHT = -1.5  # Disputes weighted higher (fraud prevention)
    STRENGTHEN_WEIGHT = 0.5
    WEAKEN_WEIGHT = -0.5

    # Reputation multiplier (attestations from high-rep users count more)
    MIN_REPUTATION = 0.5  # Even low-rep attestations have 50% weight
    MAX_REPUTATION = 2.0  # High-rep attestations count 2x

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

        # Count by type
        counts = {
            'verify': 0,
            'dispute': 0,
            'strengthen': 0,
            'weaken': 0
        }

        # Weighted score accumulation
        weighted_sum = 0.0
        total_weight = 0.0

        attester_reputations = []
        now = datetime.utcnow()

        for attestation in attestations:
            # Get attester reputation
            attester = db.query(Entity).filter(
                Entity.did == attestation.attester_did
            ).first()

            attester_reputation = attester.trust_score / 100.0 if attester else 0.5

            # Reputation multiplier (0.5x to 2.0x)
            reputation_multiplier = self.MIN_REPUTATION + (
                attester_reputation * (self.MAX_REPUTATION - self.MIN_REPUTATION)
            )

            # Temporal decay
            age_days = (now - attestation.created_at).days
            decay_factor = 0.5 ** (age_days / self.DECAY_HALF_LIFE_DAYS)

            # Base weight by type
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
                base_weight = 0.0

            # Confidence scaling (0-100 confidence scales weight)
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

            attester_reputations.append(int(attester_reputation * 100))

        # Normalize to 0-100 score
        if total_weight == 0:
            conviction_score = 50  # Neutral if no meaningful attestations
        else:
            # Map weighted sum to 0-100
            # Positive = high conviction, negative = low conviction
            normalized = weighted_sum / total_weight
            conviction_score = int(50 + (normalized * 50))
            conviction_score = max(0, min(100, conviction_score))

        # Calculate trend (last 30 days vs previous 30 days)
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
        """Calculate if conviction is increasing, stable, or decreasing"""
        thirty_days_ago = now - timedelta(days=30)
        sixty_days_ago = now - timedelta(days=60)

        recent = [a for a in attestations if a.created_at >= thirty_days_ago]
        previous = [a for a in attestations if sixty_days_ago <= a.created_at < thirty_days_ago]

        recent_net = sum(1 if a.attestation_type == 'verify' else -1 for a in recent)
        previous_net = sum(1 if a.attestation_type == 'verify' else -1 for a in previous)

        if len(recent) < 3:  # Not enough data
            return 'stable'

        if recent_net > previous_net * 1.5:
            return 'increasing'
        elif recent_net < previous_net * 0.5:
            return 'decreasing'
        else:
            return 'stable'
```

#### Task 2.2: Unit Tests for Conviction Algorithm

Create: `services/rhiz-api/app/tests/test_conviction.py`

```python
import pytest
from datetime import datetime, timedelta
from app.services.conviction import ConvictionCalculator
from app.models import Attestation, Entity

def test_conviction_no_attestations():
    """Zero conviction with no attestations"""
    calc = ConvictionCalculator()
    result = calc.calculate_conviction('at://test/uri', [], None)
    assert result['score'] == 0
    assert result['attestation_count'] == 0

def test_conviction_single_verify():
    """Single verify attestation should give positive conviction"""
    calc = ConvictionCalculator()

    attestation = Attestation(
        uri='at://test/attestation/1',
        attester_did='did:plc:alice',
        target_uri='at://test/relationship/1',
        attestation_type='verify',
        confidence=90,
        created_at=datetime.utcnow()
    )

    # Mock database
    class MockDB:
        def query(self, model):
            return self
        def filter(self, condition):
            return self
        def first(self):
            entity = Entity(did='did:plc:alice')
            entity.trust_score = 80
            return entity

    result = calc.calculate_conviction('at://test/relationship/1', [attestation], MockDB())

    assert result['score'] > 50  # Positive conviction
    assert result['attestation_count'] == 1
    assert result['verify_count'] == 1

def test_conviction_dispute_lowers_score():
    """Dispute attestations should lower conviction"""
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

    # Dispute weighted higher, should lower conviction
    result = calc.calculate_conviction(
        'at://test/relationship/1',
        [verify, dispute],
        MockDB()
    )

    assert result['score'] < 50  # Dispute should dominate
    assert result['dispute_count'] == 1

def test_conviction_temporal_decay():
    """Old attestations should have less weight"""
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
        created_at=datetime.utcnow() - timedelta(days=365)  # 1 year old
    )

    result_recent = calc.calculate_conviction('at://test/1', [recent], MockDB())
    result_old = calc.calculate_conviction('at://test/2', [old], MockDB())

    assert result_recent['score'] > result_old['score']  # Recent should have higher conviction
```

---

### Week 5-6: API Endpoints & Indexer

#### Task 3.1: API Endpoints

Create: `services/rhiz-api/app/routers/conviction.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import Attestation, ConvictionScore, Relationship
from app.services.conviction import ConvictionCalculator

router = APIRouter(prefix="/xrpc/net.rhiz.conviction", tags=["conviction"])

@router.get("/getScore")
async def get_conviction_score(
    uri: str,
    db: Session = Depends(get_db)
):
    """Get conviction score for any attested record"""

    # Check if cached
    cached = db.query(ConvictionScore).filter(
        ConvictionScore.target_uri == uri
    ).first()

    if cached:
        return {
            "uri": uri,
            "conviction": {
                "score": cached.score,
                "attestationCount": cached.attestation_count,
                "verifyCount": cached.verify_count,
                "disputeCount": cached.dispute_count,
                "lastUpdated": cached.last_updated.isoformat(),
                "trend": cached.trend,
                "topAttesterReputation": cached.top_attester_reputation
            }
        }

    # Calculate if not cached
    attestations = db.query(Attestation).filter(
        Attestation.target_uri == uri
    ).all()

    if not attestations:
        raise HTTPException(status_code=404, detail="No attestations found for this URI")

    calc = ConvictionCalculator()
    conviction = calc.calculate_conviction(uri, attestations, db)

    return {
        "uri": uri,
        "conviction": {
            "score": conviction['score'],
            "attestationCount": conviction['attestation_count'],
            "verifyCount": conviction['verify_count'],
            "disputeCount": conviction['dispute_count'],
            "lastUpdated": datetime.utcnow().isoformat(),
            "trend": conviction['trend'],
            "topAttesterReputation": conviction['top_attester_reputation']
        }
    }

@router.get("/listAttestations")
async def list_attestations(
    uri: str,
    type: Optional[str] = None,
    minConfidence: Optional[int] = None,
    limit: int = 50,
    cursor: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all attestations for a record"""

    query = db.query(Attestation).filter(Attestation.target_uri == uri)

    if type:
        query = query.filter(Attestation.attestation_type == type)

    if minConfidence:
        query = query.filter(Attestation.confidence >= minConfidence)

    query = query.order_by(Attestation.created_at.desc())

    if cursor:
        # Pagination logic (cursor = last created_at timestamp)
        query = query.filter(Attestation.created_at < cursor)

    attestations = query.limit(limit + 1).all()

    has_more = len(attestations) > limit
    if has_more:
        attestations = attestations[:limit]
        next_cursor = attestations[-1].created_at.isoformat()
    else:
        next_cursor = None

    # Fetch attester profiles
    result = []
    for attestation in attestations:
        attester = db.query(Entity).filter(
            Entity.did == attestation.attester_did
        ).first()

        result.append({
            "uri": attestation.uri,
            "cid": attestation.cid,
            "record": {
                "targetRelationship": attestation.target_uri,
                "attester": attestation.attester_did,
                "attestationType": attestation.attestation_type,
                "confidence": attestation.confidence,
                "evidence": attestation.evidence,
                "createdAt": attestation.created_at.isoformat()
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

#### Task 3.2: Firehose Indexer Update

Update: `services/rhiz-atproto/src/indexer.ts`

```typescript
import { Firehose } from '@atproto/sync'
import { Database } from './db'

export class RhizIndexer {
  async indexCommit(commit: Commit) {
    // Existing logic for relationships, entities, etc.

    // New: Index attestations
    if (commit.collection === 'net.rhiz.relationship.attestation') {
      await this.indexAttestation(commit)
    }
  }

  async indexAttestation(commit: Commit) {
    const record = commit.record as RelationshipAttestation

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
  }

  async recalculateConviction(targetUri: string) {
    // Call conviction calculator
    const attestations = await this.db.query(`
      SELECT * FROM attestations WHERE target_uri = $1
    `, [targetUri])

    const calc = new ConvictionCalculator()
    const conviction = calc.calculate(targetUri, attestations.rows)

    // Update conviction_scores table
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

    // If target is a relationship, update relationship.conviction_score
    if (targetUri.includes('net.rhiz.relationship.record')) {
      await this.db.query(`
        UPDATE relationships
        SET conviction_score = $1, attestation_count = $2
        WHERE uri = $3
      `, [conviction.score, conviction.attestationCount, targetUri])
    }
  }
}
```

---

### Week 7-8: SDK & UI

#### Task 4.1: SDK Methods

Update: `packages/rhiz-sdk/src/client.ts`

```typescript
export class RhizClient {
  // Existing methods...

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
      attester: this.session.did,
      attestationType: params.attestationType,
      confidence: params.confidence,
      evidence: params.evidence,
      suggestedStrength: params.suggestedStrength,
      createdAt: new Date().toISOString()
    }

    // Write to user's repo
    const result = await this.agent.com.atproto.repo.createRecord({
      repo: this.session.did,
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
    const response = await this.apiClient.get('/xrpc/net.rhiz.conviction.getScore', {
      params: { uri }
    })

    return response.data
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
    const response = await this.apiClient.get('/xrpc/net.rhiz.conviction.listAttestations', {
      params
    })

    return response.data
  }
}
```

#### Task 4.2: UI Components (FundRhiz)

Create: `services/fundrhiz/components/ConvictionBadge.tsx`

```typescript
interface ConvictionBadgeProps {
  score: number
  attestationCount: number
  trend?: 'increasing' | 'stable' | 'decreasing'
}

export function ConvictionBadge({ score, attestationCount, trend }: ConvictionBadgeProps) {
  const getColor = (score: number) => {
    if (score >= 80) return 'green'
    if (score >= 60) return 'yellow'
    if (score >= 40) return 'orange'
    return 'red'
  }

  const color = getColor(score)

  const trendIcon = {
    increasing: '↗️',
    stable: '→',
    decreasing: '↘️'
  }[trend || 'stable']

  return (
    <div className={`conviction-badge conviction-${color}`}>
      <span className="score">{score}%</span>
      <span className="label">verified</span>
      {trend && <span className="trend">{trendIcon}</span>}
      <span className="count">{attestationCount} attestations</span>
    </div>
  )
}
```

Create: `services/fundrhiz/components/AttestationButton.tsx`

```typescript
'use client'

import { useState } from 'react'
import { RhizClient } from '@atproto/rhiz-sdk'

interface AttestationButtonProps {
  relationshipUri: string
  onAttested?: () => void
}

export function AttestationButton({ relationshipUri, onAttested }: AttestationButtonProps) {
  const [showForm, setShowForm] = useState(false)
  const [type, setType] = useState<'verify' | 'dispute'>('verify')
  const [confidence, setConfidence] = useState(80)
  const [evidence, setEvidence] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async () => {
    setSubmitting(true)

    try {
      const client = new RhizClient(/* ... */)
      await client.attestRelationship({
        targetRelationship: relationshipUri,
        attestationType: type,
        confidence,
        evidence
      })

      setShowForm(false)
      onAttested?.()
    } catch (error) {
      console.error('Failed to submit attestation:', error)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div>
      <button onClick={() => setShowForm(true)}>
        Attest to this relationship
      </button>

      {showForm && (
        <div className="attestation-form">
          <h3>Attest to Relationship</h3>

          <div>
            <label>Type:</label>
            <select value={type} onChange={(e) => setType(e.target.value as any)}>
              <option value="verify">Verify (I confirm this relationship exists)</option>
              <option value="dispute">Dispute (I don't believe this relationship is accurate)</option>
            </select>
          </div>

          <div>
            <label>Confidence (0-100):</label>
            <input
              type="range"
              min="0"
              max="100"
              value={confidence}
              onChange={(e) => setConfidence(parseInt(e.target.value))}
            />
            <span>{confidence}%</span>
          </div>

          <div>
            <label>Evidence (optional):</label>
            <textarea
              value={evidence}
              onChange={(e) => setEvidence(e.target.value)}
              placeholder="e.g., 'I worked with both of them at TechCo for 2 years'"
              maxLength={1000}
            />
          </div>

          <button onClick={handleSubmit} disabled={submitting}>
            {submitting ? 'Submitting...' : 'Submit Attestation'}
          </button>
          <button onClick={() => setShowForm(false)}>Cancel</button>
        </div>
      )}
    </div>
  )
}
```

---

## Testing Strategy

### Unit Tests

1. **Conviction Algorithm** (✅ see Task 2.2)
   - Zero attestations → 0 conviction
   - Single verify → positive conviction
   - Disputes lower conviction
   - Temporal decay works correctly
   - Reputation weighting works

2. **API Endpoints**
   - GET /conviction/getScore returns correct format
   - GET /conviction/listAttestations filters correctly
   - Pagination works

3. **SDK Methods**
   - attestRelationship creates valid record
   - getConviction returns typed response
   - listAttestations handles pagination

### Integration Tests

1. **End-to-End Attestation Flow**
   - User creates relationship
   - Third party attests relationship
   - Firehose picks up attestation
   - Conviction score updates in database
   - API returns updated conviction

2. **Multi-Attester Scenario**
   - Multiple users attest same relationship
   - Conviction aggregates correctly
   - Disputes are weighted properly

3. **Temporal Scenarios**
   - Old attestations have less weight
   - Trend calculation works (increasing/stable/decreasing)

### Load Tests

- 1000 attestations/second ingestion
- Conviction calculation <100ms for 100 attestations
- Query API <200ms p95 latency

---

## Success Metrics

### Adoption Metrics

- **Week 8:** 10% of relationships have ≥1 attestation
- **Month 3:** 30% of relationships have ≥1 attestation
- **Month 6:** 50% of relationships have ≥3 attestations

### Quality Metrics

- **Conviction accuracy:** 80%+ correlation with manual validation
- **Fraud detection:** 90%+ of fake relationships have conviction <40
- **User trust:** 70%+ of users say conviction scores are helpful

### Performance Metrics

- **Firehose lag:** <5 seconds from commit to indexed
- **Conviction calc:** <100ms for 100 attestations
- **API latency:** <200ms p95

---

## Deployment

### Phase 1: Internal Testing (Week 8)

- Deploy to staging environment
- Team tests attestation flow
- Validate conviction calculations
- Fix bugs

### Phase 2: Beta Launch (Week 10)

- Deploy to production
- Invite 50 beta testers
- Monitor metrics daily
- Gather feedback

### Phase 3: Public Launch (Week 12)

- Open to all Rhiz users
- Announce attestation feature
- Monitor adoption
- Plan Phase 2B (triples)

---

## Risks & Mitigation

### Risk 1: Low Adoption

**Problem:** Users don't attest relationships organically.

**Mitigation:**
- Gamification: "Top attesters" leaderboard
- Incentives: Higher conviction = higher search ranking
- Onboarding: Prompt users to attest existing relationships
- Social proof: Show which relationships need attestations

### Risk 2: Gaming/Spam

**Problem:** Users create fake attestations to boost conviction.

**Mitigation:**
- Reputation weighting (low-rep users have less impact)
- Dispute mechanism (bad attestations can be reported)
- Rate limiting (max attestations per day)
- Sybil detection (flag accounts with suspicious patterns)

### Risk 3: Performance Issues

**Problem:** Conviction calculation too slow with many attestations.

**Mitigation:**
- Cache conviction scores (recalc only on new attestation)
- Batch processing (update convictions async)
- Database indexing (optimize queries)
- Horizontal scaling (multiple AppView instances)

---

## Post-Launch: Phase 2B Planning

Once Phase 2A is stable (Month 3), begin Phase 2B:

1. **Triple-based claims** - Decompose relationships into atomic triples
2. **Expertise attestations** - Attest to skills/domains
3. **Credential attestations** - Verify degrees/certifications

See `INTUITION_INTEGRATION_ANALYSIS.md` for details.

---

## Questions?

Contact: rhiz-protocol@rhiz.network

---

**Document Status:** Implementation Guide
**Version:** 1.0
**Last Updated:** October 22, 2025

