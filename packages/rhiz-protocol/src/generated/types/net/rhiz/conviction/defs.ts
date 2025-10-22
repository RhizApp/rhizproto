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
const id = 'net.rhiz.conviction.defs'

/** Network consensus score for a claim based on attestations */
export interface ConvictionScore {
  $type?: 'net.rhiz.conviction.defs#convictionScore'
  /** Network confidence score (0-100). Higher = more network consensus. */
  score: number
  /** Total number of attestations received */
  attestationCount: number
  /** Number of verify attestations */
  verifyCount?: number
  /** Number of dispute attestations */
  disputeCount?: number
  /** When conviction score was last recalculated */
  lastUpdated: string
  /** Conviction trend over last 30 days */
  trend?: 'increasing' | 'stable' | 'decreasing'
  /** Reputation score of highest-reputation attester (for quality signal) */
  topAttesterReputation?: number
}

const hashConvictionScore = 'convictionScore'

export function isConvictionScore<V>(v: V) {
  return is$typed(v, id, hashConvictionScore)
}

export function validateConvictionScore<V>(v: V) {
  return validate<ConvictionScore & V>(v, id, hashConvictionScore)
}

/** Summary of attestations for a target URI */
export interface AttestationSummary {
  $type?: 'net.rhiz.conviction.defs#attestationSummary'
  /** URI of the attested record */
  targetUri: string
  conviction: ConvictionScore
  /** Most recent attestations (limited to 10) */
  recentAttestations?: AttestationRef[]
}

const hashAttestationSummary = 'attestationSummary'

export function isAttestationSummary<V>(v: V) {
  return is$typed(v, id, hashAttestationSummary)
}

export function validateAttestationSummary<V>(v: V) {
  return validate<AttestationSummary & V>(v, id, hashAttestationSummary)
}

/** Reference to an attestation */
export interface AttestationRef {
  $type?: 'net.rhiz.conviction.defs#attestationRef'
  /** AT URI of the attestation record */
  uri: string
  /** DID of attester */
  attester: string
  type: 'verify' | 'dispute' | 'strengthen' | 'weaken'
  confidence: number
  createdAt: string
}

const hashAttestationRef = 'attestationRef'

export function isAttestationRef<V>(v: V) {
  return is$typed(v, id, hashAttestationRef)
}

export function validateAttestationRef<V>(v: V) {
  return validate<AttestationRef & V>(v, id, hashAttestationRef)
}
