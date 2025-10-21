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
import type * as NetRhizRelationshipDefs from './defs.js'

const is$typed = _is$typed,
  validate = _validate
const id = 'net.rhiz.relationship.record'

export interface Record {
  $type: 'net.rhiz.relationship.record'
  /** The two entities in this relationship (as DIDs) */
  participants: string[]
  type: NetRhizRelationshipDefs.RelationshipType
  /** Normalized trust score (0-100, scaled from 0.0-1.0) */
  strength: number
  /** Domain or project context for this relationship */
  context: string
  verification: NetRhizRelationshipDefs.Verification
  privacy: NetRhizRelationshipDefs.Privacy
  temporal: NetRhizRelationshipDefs.Temporal
  /** Cryptographic signatures from participants */
  signatures?: NetRhizRelationshipDefs.SignatureData[]
  createdAt: string
  [k: string]: unknown
}

const hashRecord = 'main'

export function isRecord<V>(v: V) {
  return is$typed(v, id, hashRecord)
}

export function validateRecord<V>(v: V) {
  return validate<Record & V>(v, id, hashRecord, true)
}
