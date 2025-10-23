/**
 * @rhiz/sdk
 * TypeScript SDK for Rhiz Protocol API
 */

export { RhizClient, RhizError } from './client';
export type { RhizClientConfig } from './client';

// Re-export protocol types
export type {
  Entity,
  EntityType,
  RelationshipRecord,
  RelationshipType,
  TrustMetrics,
  GraphPath,
  GraphQuery,
  IntroRequest,
  Visibility,
  ConsentLevel,
} from '@atproto/rhiz-protocol';

// Export API-specific types
export type { CreateEntityRequest, UpdateEntityRequest } from './api/entities';
export type { TrustHealthResponse, NetworkStatsResponse } from './api/analytics';
export type {
  ConvictionScore,
  Attestation,
  AttestationParams,
  ListAttestationsParams,
  ListAttestationsResponse
} from './api/conviction';

