import { describe, it, expect } from 'vitest';
import {
  calculateDecayedStrength,
  getTrustLevel,
  calculatePathStrength,
  calculateTrustScore,
  generateRelationshipId,
  areDirectlyConnected,
  formatTrustScore,
  isValidDID,
  isValidHandle,
  calculateReciprocity,
} from '../utils';
import { RelationshipType } from '../types';

describe('Protocol Utils', () => {
  describe('calculateDecayedStrength', () => {
    it('should calculate decay for recent interaction', () => {
      const relationship = {
        strength: 1.0,
        type: RelationshipType.PROFESSIONAL,
        temporal: {
          start: '2020-01-01T00:00:00Z',
          last_interaction: new Date().toISOString(), // Today
          history: [],
        },
      };

      const decayed = calculateDecayedStrength(relationship);
      expect(decayed).toBeCloseTo(1.0, 2);
    });

    it('should decay strength over time', () => {
      const oneYearAgo = new Date();
      oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);

      const relationship = {
        strength: 1.0,
        type: RelationshipType.PROFESSIONAL,
        temporal: {
          start: '2020-01-01T00:00:00Z',
          last_interaction: oneYearAgo.toISOString(),
          history: [],
        },
      };

      const decayed = calculateDecayedStrength(relationship);
      expect(decayed).toBeLessThan(1.0);
    });
  });

  describe('getTrustLevel', () => {
    it('should categorize trust scores correctly', () => {
      expect(getTrustLevel(0.95)).toBe('very_high');
      expect(getTrustLevel(0.8)).toBe('high');
      expect(getTrustLevel(0.6)).toBe('medium');
      expect(getTrustLevel(0.3)).toBe('low');
      expect(getTrustLevel(0.05)).toBe('very_low');
    });
  });

  describe('calculatePathStrength', () => {
    it('should calculate geometric mean of hop strengths', () => {
      const path = {
        from: 'entity_1',
        to: 'entity_3',
        hops: [
          { from: 'entity_1', to: 'entity_2', relationship_id: 'rel_1', strength: 0.8 },
          { from: 'entity_2', to: 'entity_3', relationship_id: 'rel_2', strength: 0.9 },
        ],
        total_strength: 0,
        distance: 2,
      };

      const strength = calculatePathStrength(path);
      // Geometric mean of 0.8 and 0.9
      expect(strength).toBeCloseTo(0.8485, 2);
    });

    it('should return 0 for empty path', () => {
      const path = {
        from: 'entity_1',
        to: 'entity_1',
        hops: [],
        total_strength: 0,
        distance: 0,
      };

      expect(calculatePathStrength(path)).toBe(0);
    });
  });

  describe('calculateTrustScore', () => {
    it('should calculate weighted trust score', () => {
      const metrics = {
        entity_id: 'entity_1',
        reputation: 0.9,
        reciprocity: 0.8,
        consistency: 0.85,
        relationship_count: 50,
        verified_relationship_count: 45,
        last_calculated: '2024-01-01T00:00:00Z',
      };

      const score = calculateTrustScore(metrics);
      expect(score).toBeGreaterThan(0);
      expect(score).toBeLessThanOrEqual(1);
    });
  });

  describe('generateRelationshipId', () => {
    it('should generate same ID regardless of order', () => {
      const id1 = generateRelationshipId('entity_a', 'entity_b');
      const id2 = generateRelationshipId('entity_b', 'entity_a');
      expect(id1).toBe(id2);
    });

    it('should generate deterministic IDs', () => {
      const id1 = generateRelationshipId('entity_a', 'entity_b');
      const id2 = generateRelationshipId('entity_a', 'entity_b');
      expect(id1).toBe(id2);
    });
  });

  describe('areDirectlyConnected', () => {
    it('should return true for direct connections', () => {
      const path = {
        from: 'entity_1',
        to: 'entity_2',
        hops: [{ from: 'entity_1', to: 'entity_2', relationship_id: 'rel_1', strength: 0.8 }],
        total_strength: 0.8,
        distance: 1,
      };

      expect(areDirectlyConnected(path)).toBe(true);
    });

    it('should return false for indirect connections', () => {
      const path = {
        from: 'entity_1',
        to: 'entity_3',
        hops: [
          { from: 'entity_1', to: 'entity_2', relationship_id: 'rel_1', strength: 0.8 },
          { from: 'entity_2', to: 'entity_3', relationship_id: 'rel_2', strength: 0.9 },
        ],
        total_strength: 0.72,
        distance: 2,
      };

      expect(areDirectlyConnected(path)).toBe(false);
    });
  });

  describe('formatTrustScore', () => {
    it('should format as percentage', () => {
      expect(formatTrustScore(0.85)).toBe('85%');
      expect(formatTrustScore(0.5)).toBe('50%');
      expect(formatTrustScore(1.0)).toBe('100%');
    });
  });

  describe('isValidDID', () => {
    it('should validate DID format', () => {
      expect(isValidDID('did:plc:abc123')).toBe(true);
      expect(isValidDID('did:key:z6Mk...')).toBe(true);
      expect(isValidDID('not-a-did')).toBe(false);
      expect(isValidDID('did:invalid format')).toBe(false);
    });
  });

  describe('isValidHandle', () => {
    it('should validate handle format', () => {
      expect(isValidHandle('alice.bsky.social')).toBe(true);
      expect(isValidHandle('bob.example.com')).toBe(true);
      expect(isValidHandle('invalid handle')).toBe(false);
      expect(isValidHandle('noperiod')).toBe(false);
    });
  });

  describe('calculateReciprocity', () => {
    it('should return 1 for perfect balance', () => {
      expect(calculateReciprocity(10, 10)).toBe(1);
    });

    it('should return 0 for no interactions', () => {
      expect(calculateReciprocity(0, 0)).toBe(0);
    });

    it('should return value between 0-1 for imbalanced interactions', () => {
      const reciprocity = calculateReciprocity(8, 2);
      expect(reciprocity).toBeGreaterThan(0);
      expect(reciprocity).toBeLessThan(1);
      expect(reciprocity).toBeCloseTo(0.4, 1);
    });
  });
});

