import { describe, it, expect } from 'vitest';
import {
  validateRelationship,
  validateEntity,
  validateTrustMetrics,
  validateGraphQuery,
} from '../validators';
import { RelationshipType, EntityType, Visibility, ConsentLevel } from '../types';

describe('Protocol Validators', () => {
  describe('validateRelationship', () => {
    it('should validate a complete relationship record', () => {
      const validRelationship = {
        id: 'rel_123',
        participants: ['entity_1', 'entity_2'] as [string, string],
        type: RelationshipType.PROFESSIONAL,
        strength: 0.85,
        context: 'co-founded startup together',
        verification: {
          consensus_score: 0.9,
          verifier_count: 5,
          confidence: 0.92,
          last_verified: '2024-01-01T00:00:00Z',
        },
        privacy: {
          visibility: Visibility.NETWORK,
          consent: ConsentLevel.FULL,
        },
        temporal: {
          start: '2020-01-01T00:00:00Z',
          last_interaction: '2024-01-01T00:00:00Z',
          history: [],
        },
        protocol: {
          contributors: ['entity_1'],
          version: '0.1.0',
          updated: '2024-01-01T00:00:00Z',
        },
      };

      const result = validateRelationship(validRelationship);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.id).toBe('rel_123');
      }
    });

    it('should reject invalid strength values', () => {
      const invalidRelationship = {
        id: 'rel_123',
        participants: ['entity_1', 'entity_2'],
        type: RelationshipType.PROFESSIONAL,
        strength: 1.5, // Invalid: > 1
        context: 'test',
        verification: {
          consensus_score: 0.9,
          verifier_count: 5,
          confidence: 0.92,
          last_verified: '2024-01-01T00:00:00Z',
        },
        privacy: {
          visibility: Visibility.NETWORK,
          consent: ConsentLevel.FULL,
        },
        temporal: {
          start: '2020-01-01T00:00:00Z',
          last_interaction: '2024-01-01T00:00:00Z',
          history: [],
        },
        protocol: {
          contributors: ['entity_1'],
          version: '0.1.0',
          updated: '2024-01-01T00:00:00Z',
        },
      };

      const result = validateRelationship(invalidRelationship);
      expect(result.success).toBe(false);
    });
  });

  describe('validateEntity', () => {
    it('should validate a complete entity record', () => {
      const validEntity = {
        id: 'entity_1',
        type: EntityType.PERSON,
        did: 'did:plc:test123',
        handle: 'alice.bsky.social',
        name: 'Alice',
        bio: 'Test bio',
        avatar_url: 'https://example.com/avatar.jpg',
        verified: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      const result = validateEntity(validEntity);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.name).toBe('Alice');
      }
    });

    it('should require name field', () => {
      const invalidEntity = {
        id: 'entity_1',
        type: EntityType.PERSON,
        verified: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        // Missing name
      };

      const result = validateEntity(invalidEntity);
      expect(result.success).toBe(false);
    });
  });

  describe('validateTrustMetrics', () => {
    it('should validate trust metrics', () => {
      const validMetrics = {
        entity_id: 'entity_1',
        trust_score: 0.85,
        reputation: 0.9,
        reciprocity: 0.8,
        consistency: 0.87,
        relationship_count: 50,
        verified_relationship_count: 45,
        last_calculated: '2024-01-01T00:00:00Z',
      };

      const result = validateTrustMetrics(validMetrics);
      expect(result.success).toBe(true);
    });

    it('should reject negative counts', () => {
      const invalidMetrics = {
        entity_id: 'entity_1',
        trust_score: 0.85,
        reputation: 0.9,
        reciprocity: 0.8,
        consistency: 0.87,
        relationship_count: -5, // Invalid
        verified_relationship_count: 45,
        last_calculated: '2024-01-01T00:00:00Z',
      };

      const result = validateTrustMetrics(invalidMetrics);
      expect(result.success).toBe(false);
    });
  });

  describe('validateGraphQuery', () => {
    it('should validate graph query with defaults', () => {
      const validQuery = {
        from: 'entity_1',
        to: 'entity_2',
      };

      const result = validateGraphQuery(validQuery);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.max_hops).toBe(6);
        expect(result.data.min_strength).toBe(0.5);
      }
    });

    it('should validate query with custom parameters', () => {
      const validQuery = {
        from: 'entity_1',
        to: 'entity_2',
        max_hops: 4,
        min_strength: 0.7,
        relationship_types: [RelationshipType.PROFESSIONAL],
        exclude_entities: ['entity_3'],
      };

      const result = validateGraphQuery(validQuery);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.max_hops).toBe(4);
        expect(result.data.min_strength).toBe(0.7);
      }
    });
  });
});

