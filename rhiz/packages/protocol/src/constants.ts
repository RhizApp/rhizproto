/**
 * Protocol constants and defaults
 */

/**
 * Default values for graph queries
 */
export const DEFAULT_MAX_HOPS = 6;
export const DEFAULT_MIN_STRENGTH = 0.5;

/**
 * Trust scoring thresholds
 */
export const TRUST_THRESHOLDS = {
  VERY_HIGH: 0.9,
  HIGH: 0.75,
  MEDIUM: 0.5,
  LOW: 0.25,
  VERY_LOW: 0.1,
} as const;

/**
 * Relationship strength decay rates (per day)
 */
export const DECAY_RATES = {
  professional: 0.001, // 0.1% per day
  personal: 0.0005, // 0.05% per day
  family: 0.0001, // 0.01% per day
  social: 0.002, // 0.2% per day
  civic: 0.0015, // 0.15% per day
  educational: 0.0012, // 0.12% per day
} as const;

/**
 * Verification thresholds
 */
export const VERIFICATION_THRESHOLDS = {
  MIN_VERIFIERS: 2,
  MIN_CONSENSUS: 0.7,
  MIN_CONFIDENCE: 0.8,
} as const;

/**
 * Rate limits
 */
export const RATE_LIMITS = {
  INTRO_REQUESTS_PER_DAY: 10,
  GRAPH_QUERIES_PER_MINUTE: 60,
  RELATIONSHIP_UPDATES_PER_HOUR: 100,
} as const;

/**
 * Maximum values
 */
export const MAX_VALUES = {
  RELATIONSHIP_CONTEXT_LENGTH: 500,
  INTRO_MESSAGE_LENGTH: 2000,
  AGENT_MESSAGE_LENGTH: 5000,
  ENTITY_BIO_LENGTH: 1000,
} as const;

/**
 * Privacy defaults
 */
export const DEFAULT_PRIVACY = {
  visibility: 'network' as const,
  consent: 'limited' as const,
};

/**
 * API endpoints (relative paths)
 */
export const API_ENDPOINTS = {
  GRAPH_FIND_PATH: '/graph/find-path',
  GRAPH_NEIGHBORS: '/graph/neighbors',
  AGENT_COORDINATE: '/agent/coordinate',
  FORUM_CREATE: '/forum/create',
  ENRICHMENT_CONTACT: '/enrichment/contact',
  ANALYTICS_TRUST_HEALTH: '/analytics/trust-health',
} as const;

