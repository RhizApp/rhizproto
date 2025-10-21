/**
 * Core types for Rhiz Protocol
 * These types define the fundamental data structures for relationship intelligence
 */

export type EntityId = string;
export type RelationshipId = string;
export type ISO8601Timestamp = string;

/**
 * Types of relationships supported by the protocol
 */
export enum RelationshipType {
  PROFESSIONAL = 'professional',
  PERSONAL = 'personal',
  FAMILY = 'family',
  SOCIAL = 'social',
  CIVIC = 'civic',
  EDUCATIONAL = 'educational',
}

/**
 * Visibility levels for relationship data
 */
export enum Visibility {
  PUBLIC = 'public', // Visible to anyone
  NETWORK = 'network', // Visible to connected entities
  PRIVATE = 'private', // Only visible to participants
}

/**
 * Consent levels for data usage
 */
export enum ConsentLevel {
  FULL = 'full', // Full data sharing allowed
  LIMITED = 'limited', // Limited to specific contexts
  ANONYMOUS = 'anonymous', // Anonymized data only
}

/**
 * Verification data for a relationship
 */
export interface Verification {
  consensus_score: number; // 0.0-1.0
  verifier_count: number;
  confidence: number; // 0.0-1.0
  last_verified: ISO8601Timestamp;
}

/**
 * Privacy settings for a relationship
 */
export interface Privacy {
  visibility: Visibility;
  consent: ConsentLevel;
}

/**
 * Historical strength data point
 */
export interface StrengthHistoryPoint {
  timestamp: ISO8601Timestamp;
  strength: number;
  event?: string; // Optional description of what changed
}

/**
 * Temporal data for a relationship
 */
export interface Temporal {
  start: ISO8601Timestamp;
  last_interaction: ISO8601Timestamp;
  history: StrengthHistoryPoint[];
}

/**
 * Protocol metadata
 */
export interface ProtocolMetadata {
  contributors: EntityId[]; // Entities that contributed to this record
  version: string;
  updated: ISO8601Timestamp;
}

/**
 * Core relationship record
 */
export interface RelationshipRecord {
  id: RelationshipId;
  participants: [EntityId, EntityId];
  type: RelationshipType;
  strength: number; // 0.0-1.0 normalized trust score
  context: string; // Domain or project context
  verification: Verification;
  privacy: Privacy;
  temporal: Temporal;
  protocol: ProtocolMetadata;
}

/**
 * Entity types
 */
export enum EntityType {
  PERSON = 'person',
  ORGANIZATION = 'organization',
  AGENT = 'agent',
}

/**
 * Entity record
 */
export interface Entity {
  id: EntityId;
  type: EntityType;
  did?: string; // AT Protocol DID
  handle?: string; // AT Protocol handle
  name: string;
  bio?: string;
  avatar_url?: string;
  verified: boolean;
  created_at: ISO8601Timestamp;
  updated_at: ISO8601Timestamp;
}

/**
 * Trust metrics for an entity
 */
export interface TrustMetrics {
  entity_id: EntityId;
  trust_score: number; // 0.0-1.0
  reputation: number; // 0.0-1.0
  reciprocity: number; // 0.0-1.0
  consistency: number; // 0.0-1.0
  relationship_count: number;
  verified_relationship_count: number;
  last_calculated: ISO8601Timestamp;
}

/**
 * Graph path between entities
 */
export interface GraphPath {
  from: EntityId;
  to: EntityId;
  hops: Array<{
    from: EntityId;
    to: EntityId;
    relationship_id: RelationshipId;
    strength: number;
  }>;
  total_strength: number; // Weighted product of hop strengths
  distance: number; // Number of hops
}

/**
 * Query parameters for finding paths
 */
export interface GraphQuery {
  from: EntityId;
  to: EntityId;
  max_hops?: number; // Default: 6
  min_strength?: number; // Minimum edge strength, default: 0.5
  relationship_types?: RelationshipType[];
  exclude_entities?: EntityId[];
}

/**
 * Introduction request
 */
export interface IntroRequest {
  id: string;
  requester: EntityId;
  target: EntityId;
  intermediary?: EntityId; // Suggested by path-finding
  context: string;
  message: string;
  status: 'pending' | 'accepted' | 'declined' | 'completed';
  created_at: ISO8601Timestamp;
  updated_at: ISO8601Timestamp;
}

/**
 * Agent coordination message
 */
export interface AgentMessage {
  id: string;
  from: EntityId;
  to: EntityId;
  content: string;
  intent: 'intro_request' | 'pitch' | 'evaluation' | 'negotiation' | 'info';
  thread_id?: string;
  created_at: ISO8601Timestamp;
}

