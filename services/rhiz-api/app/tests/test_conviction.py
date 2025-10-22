"""Unit tests for conviction calculator"""

import pytest
from datetime import datetime, timedelta
from app.services.conviction import ConvictionCalculator, Attestation


class MockEntity:
    """Mock entity for testing"""
    def __init__(self, did: str, name: str, type: str, trust_score: int = 75):
        self.did = did
        self.name = name
        self.type = type
        self.trust_score = trust_score


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
    assert result['trend'] == 'stable'


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
    
    entity = MockEntity(did='did:plc:alice', name='Alice', type='person', trust_score=80)
    
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
    
    entity = MockEntity(did='did:plc:alice', name='Alice', type='person', trust_score=75)
    
    db = MockDB({'default': entity})
    
    result = calc.calculate_conviction(
        'at://test/relationship/1',
        [verify, dispute],
        db
    )
    
    # Dispute weighted 1.5x, should dominate
    assert result['score'] < 50, "Dispute should lower conviction below neutral"
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
    
    entity = MockEntity(did='did:plc:alice', name='Alice', type='person', trust_score=75)
    
    db = MockDB({'default': entity})
    
    result_recent = calc.calculate_conviction('at://test/1', [recent], db)
    result_old = calc.calculate_conviction('at://test/2', [old], db)
    
    assert result_recent['score'] > result_old['score'], \
        "Recent attestations should have higher conviction than old ones"


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
    high_rep = MockEntity(did='did:plc:alice', name='Alice', type='person', trust_score=95)
    
    # Low reputation attester
    low_rep = MockEntity(did='did:plc:alice', name='Alice', type='person', trust_score=30)
    
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
    
    entity = MockEntity(did='did:plc:alice', name='Alice', type='person', trust_score=80)
    
    db = MockDB({'default': entity})
    
    result = calc.calculate_conviction('at://test/relationship/1', attestations, db)
    
    assert result['score'] >= 70, "Multiple verifications should give high conviction"
    assert result['attestation_count'] == 5
    assert result['verify_count'] == 5
    assert result['dispute_count'] == 0


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
    
    entity = MockEntity(did='did:plc:alice', name='Alice', type='person', trust_score=80)
    
    db = MockDB({'default': entity})
    
    result = calc.calculate_conviction(
        'at://test/relationship/1',
        recent_attestations,
        db
    )
    
    assert result['trend'] in ['increasing', 'stable', 'decreasing']
    assert result['attestation_count'] == 5


def test_conviction_confidence_scaling():
    """Confidence level affects conviction weight"""
    calc = ConvictionCalculator()
    
    high_confidence = Attestation(
        uri='at://test/attestation/1',
        attester_did='did:plc:alice',
        attestation_type='verify',
        confidence=100,
        created_at=datetime.utcnow()
    )
    
    low_confidence = Attestation(
        uri='at://test/attestation/2',
        attester_did='did:plc:bob',
        attestation_type='verify',
        confidence=50,
        created_at=datetime.utcnow()
    )
    
    entity = MockEntity(did='did:plc:alice', name='Alice', type='person', trust_score=80)
    
    db = MockDB({'default': entity})
    
    result_high = calc.calculate_conviction('at://test/1', [high_confidence], db)
    result_low = calc.calculate_conviction('at://test/2', [low_confidence], db)
    
    assert result_high['score'] > result_low['score'], \
        "High confidence attestations should have more weight"


def test_conviction_mixed_types():
    """Mix of attestation types aggregates correctly"""
    calc = ConvictionCalculator()
    
    attestations = [
        Attestation(
            uri='at://test/attestation/1',
            attester_did='did:plc:user1',
            attestation_type='verify',
            confidence=90,
            created_at=datetime.utcnow()
        ),
        Attestation(
            uri='at://test/attestation/2',
            attester_did='did:plc:user2',
            attestation_type='verify',
            confidence=85,
            created_at=datetime.utcnow()
        ),
        Attestation(
            uri='at://test/attestation/3',
            attester_did='did:plc:user3',
            attestation_type='strengthen',
            confidence=80,
            created_at=datetime.utcnow()
        )
    ]
    
    entity = MockEntity(did='did:plc:alice', name='Alice', type='person', trust_score=75)
    
    db = MockDB({'default': entity})
    
    result = calc.calculate_conviction('at://test/relationship/1', attestations, db)
    
    assert result['score'] > 50, "Net positive attestations should give positive conviction"
    assert result['verify_count'] == 2
    assert result['strengthen_count'] == 1
    assert result['attestation_count'] == 3

