/**
 * Zod validators for Rhiz Protocol types
 */

import { z } from 'zod';
import {
  RelationshipType,
  Visibility,
  ConsentLevel,
  EntityType,
} from './types';

// Base validators
export const EntityIdSchema = z.string().min(1);
export const RelationshipIdSchema = z.string().min(1);
export const ISO8601Schema = z.string().datetime();

// Enum validators
export const RelationshipTypeSchema = z.nativeEnum(RelationshipType);
export const VisibilitySchema = z.nativeEnum(Visibility);
export const ConsentLevelSchema = z.nativeEnum(ConsentLevel);
export const EntityTypeSchema = z.nativeEnum(EntityType);

// Complex validators
export const VerificationSchema = z.object({
  consensus_score: z.number().min(0).max(1),
  verifier_count: z.number().int().min(0),
  confidence: z.number().min(0).max(1),
  last_verified: ISO8601Schema,
});

export const PrivacySchema = z.object({
  visibility: VisibilitySchema,
  consent: ConsentLevelSchema,
});

export const StrengthHistoryPointSchema = z.object({
  timestamp: ISO8601Schema,
  strength: z.number().min(0).max(1),
  event: z.string().optional(),
});

export const TemporalSchema = z.object({
  start: ISO8601Schema,
  last_interaction: ISO8601Schema,
  history: z.array(StrengthHistoryPointSchema),
});

export const ProtocolMetadataSchema = z.object({
  contributors: z.array(EntityIdSchema),
  version: z.string(),
  updated: ISO8601Schema,
});

export const RelationshipRecordSchema = z.object({
  id: RelationshipIdSchema,
  participants: z.tuple([EntityIdSchema, EntityIdSchema]),
  type: RelationshipTypeSchema,
  strength: z.number().min(0).max(1),
  context: z.string().min(1),
  verification: VerificationSchema,
  privacy: PrivacySchema,
  temporal: TemporalSchema,
  protocol: ProtocolMetadataSchema,
});

export const EntitySchema = z.object({
  id: EntityIdSchema,
  type: EntityTypeSchema,
  did: z.string().optional(),
  handle: z.string().optional(),
  name: z.string().min(1),
  bio: z.string().optional(),
  avatar_url: z.string().url().optional(),
  verified: z.boolean(),
  created_at: ISO8601Schema,
  updated_at: ISO8601Schema,
});

export const TrustMetricsSchema = z.object({
  entity_id: EntityIdSchema,
  trust_score: z.number().min(0).max(1),
  reputation: z.number().min(0).max(1),
  reciprocity: z.number().min(0).max(1),
  consistency: z.number().min(0).max(1),
  relationship_count: z.number().int().min(0),
  verified_relationship_count: z.number().int().min(0),
  last_calculated: ISO8601Schema,
});

export const GraphHopSchema = z.object({
  from: EntityIdSchema,
  to: EntityIdSchema,
  relationship_id: RelationshipIdSchema,
  strength: z.number().min(0).max(1),
});

export const GraphPathSchema = z.object({
  from: EntityIdSchema,
  to: EntityIdSchema,
  hops: z.array(GraphHopSchema),
  total_strength: z.number().min(0).max(1),
  distance: z.number().int().min(1),
});

export const GraphQuerySchema = z.object({
  from: EntityIdSchema,
  to: EntityIdSchema,
  max_hops: z.number().int().min(1).max(10).optional().default(6),
  min_strength: z.number().min(0).max(1).optional().default(0.5),
  relationship_types: z.array(RelationshipTypeSchema).optional(),
  exclude_entities: z.array(EntityIdSchema).optional(),
});

export const IntroRequestSchema = z.object({
  id: z.string(),
  requester: EntityIdSchema,
  target: EntityIdSchema,
  intermediary: EntityIdSchema.optional(),
  context: z.string().min(1),
  message: z.string().min(1),
  status: z.enum(['pending', 'accepted', 'declined', 'completed']),
  created_at: ISO8601Schema,
  updated_at: ISO8601Schema,
});

export const AgentMessageSchema = z.object({
  id: z.string(),
  from: EntityIdSchema,
  to: EntityIdSchema,
  content: z.string().min(1),
  intent: z.enum(['intro_request', 'pitch', 'evaluation', 'negotiation', 'info']),
  thread_id: z.string().optional(),
  created_at: ISO8601Schema,
});

/**
 * Validation helper functions
 */

export type ValidationResult<T> =
  | { success: true; data: T }
  | { success: false; errors: z.ZodError };

export function validateRelationship(
  data: unknown
): ValidationResult<z.infer<typeof RelationshipRecordSchema>> {
  const result = RelationshipRecordSchema.safeParse(data);
  if (result.success) {
    return { success: true, data: result.data };
  }
  return { success: false, errors: result.error };
}

export function validateEntity(
  data: unknown
): ValidationResult<z.infer<typeof EntitySchema>> {
  const result = EntitySchema.safeParse(data);
  if (result.success) {
    return { success: true, data: result.data };
  }
  return { success: false, errors: result.error };
}

export function validateTrustMetrics(
  data: unknown
): ValidationResult<z.infer<typeof TrustMetricsSchema>> {
  const result = TrustMetricsSchema.safeParse(data);
  if (result.success) {
    return { success: true, data: result.data };
  }
  return { success: false, errors: result.error };
}

export function validateGraphQuery(
  data: unknown
): ValidationResult<z.infer<typeof GraphQuerySchema>> {
  const result = GraphQuerySchema.safeParse(data);
  if (result.success) {
    return { success: true, data: result.data };
  }
  return { success: false, errors: result.error };
}

