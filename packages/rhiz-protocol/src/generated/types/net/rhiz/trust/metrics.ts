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
const id = 'net.rhiz.trust.metrics'

export interface Record {
  $type: 'net.rhiz.trust.metrics'
  /** Overall trust score (0-100, scaled from 0.0-1.0) */
  trustScore: number
  /** Reputation score (0-100) */
  reputation: number
  /** Reciprocity score (0-100) */
  reciprocity: number
  /** Consistency score (0-100) */
  consistency: number
  /** Total relationships */
  relationshipCount: number
  /** Verified relationships */
  verifiedRelationshipCount: number
  calculatedAt: string
  [k: string]: unknown
}

const hashRecord = 'main'

export function isRecord<V>(v: V) {
  return is$typed(v, id, hashRecord)
}

export function validateRecord<V>(v: V) {
  return validate<Record & V>(v, id, hashRecord, true)
}
