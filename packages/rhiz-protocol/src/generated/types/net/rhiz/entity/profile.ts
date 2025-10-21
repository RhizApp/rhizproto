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
import type * as NetRhizEntityDefs from './defs.js'

const is$typed = _is$typed,
  validate = _validate
const id = 'net.rhiz.entity.profile'

export interface Record {
  $type: 'net.rhiz.entity.profile'
  /** Display name for this entity */
  displayName: string
  entityType: NetRhizEntityDefs.EntityType
  /** Biography or description */
  bio?: string
  /** Avatar image URL */
  avatarUrl?: string
  /** Whether this entity is verified */
  verified: boolean
  /** Additional metadata (flexible JSON object) */
  metadata?: { [_ in string]: unknown }
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
