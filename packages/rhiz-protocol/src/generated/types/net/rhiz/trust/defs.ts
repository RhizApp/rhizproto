/**
 * GENERATED CODE - DO NOT MODIFY
 */
import { type ValidationResult, BlobRef } from '@atproto/lexicon'
import { CID } from 'multiformats/cid'
import { validate as _validate } from '../../../../lexicons'
import {
  type $Typed,
  is$typed as _is$typed,
  type OmitKey,
} from '../../../../util'

const is$typed = _is$typed,
  validate = _validate
const id = 'net.rhiz.trust.defs'

/** Trust metrics for an entity */
export interface TrustMetrics {
  $type?: 'net.rhiz.trust.defs#trustMetrics'
  /** DID of the entity these metrics describe */
  entityDid: string
  /** Overall trust score (0-100, scaled from 0.0-1.0) */
  trustScore: number
  /** Reputation score based on network consensus (0-100) */
  reputation: number
  /** Reciprocity score for mutual relationships (0-100) */
  reciprocity: number
  /** Consistency score for stable relationships (0-100) */
  consistency: number
  /** Total number of relationships */
  relationshipCount: number
  /** Number of verified relationships */
  verifiedRelationshipCount: number
  /** When these metrics were last calculated */
  lastCalculated: string
}

const hashTrustMetrics = 'trustMetrics'

export function isTrustMetrics<V>(v: V) {
  return is$typed(v, id, hashTrustMetrics)
}

export function validateTrustMetrics<V>(v: V) {
  return validate<TrustMetrics & V>(v, id, hashTrustMetrics)
}
