/**
 * Utility functions for protocol operations
 */

import { RelationshipRecord, TrustMetrics, GraphPath } from './types';
import { DECAY_RATES, TRUST_THRESHOLDS } from './constants';

/**
 * Calculate decayed strength based on last interaction
 */
export function calculateDecayedStrength(
  relationship: Pick<RelationshipRecord, 'strength' | 'type' | 'temporal'>
): number {
  const { strength, type, temporal } = relationship;
  const lastInteraction = new Date(temporal.last_interaction);
  const now = new Date();
  const daysSinceInteraction = Math.floor(
    (now.getTime() - lastInteraction.getTime()) / (1000 * 60 * 60 * 24)
  );

  const decayRate = DECAY_RATES[type];
  const decayFactor = Math.exp(-decayRate * daysSinceInteraction);

  return Math.max(0, Math.min(1, strength * decayFactor));
}

/**
 * Calculate trust level from score
 */
export function getTrustLevel(
  score: number
): 'very_high' | 'high' | 'medium' | 'low' | 'very_low' {
  if (score >= TRUST_THRESHOLDS.VERY_HIGH) return 'very_high';
  if (score >= TRUST_THRESHOLDS.HIGH) return 'high';
  if (score >= TRUST_THRESHOLDS.MEDIUM) return 'medium';
  if (score >= TRUST_THRESHOLDS.LOW) return 'low';
  return 'very_low';
}

/**
 * Calculate path strength (weighted product of hop strengths)
 */
export function calculatePathStrength(path: GraphPath): number {
  if (path.hops.length === 0) return 0;

  // Use geometric mean to penalize weak links
  const product = path.hops.reduce((acc, hop) => acc * hop.strength, 1);
  return Math.pow(product, 1 / path.hops.length);
}

/**
 * Calculate composite trust score from metrics
 */
export function calculateTrustScore(metrics: Omit<TrustMetrics, 'trust_score'>): number {
  const weights = {
    reputation: 0.3,
    reciprocity: 0.25,
    consistency: 0.25,
    verification_ratio: 0.2,
  };

  const verificationRatio =
    metrics.relationship_count > 0
      ? metrics.verified_relationship_count / metrics.relationship_count
      : 0;

  return (
    weights.reputation * metrics.reputation +
    weights.reciprocity * metrics.reciprocity +
    weights.consistency * metrics.consistency +
    weights.verification_ratio * verificationRatio
  );
}

/**
 * Generate a deterministic relationship ID from participants
 */
export function generateRelationshipId(entityA: string, entityB: string): string {
  // Sort to ensure same ID regardless of order
  const [first, second] = [entityA, entityB].sort();
  return `rel_${first}_${second}`;
}

/**
 * Check if two entities are directly connected
 */
export function areDirectlyConnected(path: GraphPath): boolean {
  return path.distance === 1;
}

/**
 * Format trust score as percentage
 */
export function formatTrustScore(score: number): string {
  return `${Math.round(score * 100)}%`;
}

/**
 * Validate DID format (basic check)
 */
export function isValidDID(did: string): boolean {
  return /^did:[a-z]+:[a-zA-Z0-9._-]+$/.test(did);
}

/**
 * Validate AT Protocol handle format
 */
export function isValidHandle(handle: string): boolean {
  return /^[a-zA-Z0-9.-]+$/.test(handle) && handle.includes('.');
}

/**
 * Calculate reciprocity between two entities based on interaction patterns
 */
export function calculateReciprocity(
  interactionsAtoB: number,
  interactionsBtoA: number
): number {
  if (interactionsAtoB === 0 && interactionsBtoA === 0) return 0;

  const total = interactionsAtoB + interactionsBtoA;
  const balance = Math.abs(interactionsAtoB - interactionsBtoA);
  const imbalance = balance / total;

  // Reciprocity is 1 - imbalance
  return 1 - imbalance;
}

