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
const id = 'net.rhiz.entity.defs'

/** Type of entity in the Rhiz network */
export type EntityType = 'person' | 'organization' | 'agent' | (string & {})

/** Public view of an entity */
export interface EntityView {
  $type?: 'net.rhiz.entity.defs#entityView'
  /** Decentralized identifier */
  did: string
  /** Human-readable handle */
  handle: string
  /** Display name */
  displayName: string
  entityType?: EntityType
  /** Biography or description */
  bio?: string
  /** Avatar image URL */
  avatarUrl?: string
  /** Whether entity is verified */
  verified: boolean
  createdAt: string
  updatedAt?: string
}

const hashEntityView = 'entityView'

export function isEntityView<V>(v: V) {
  return is$typed(v, id, hashEntityView)
}

export function validateEntityView<V>(v: V) {
  return validate<EntityView & V>(v, id, hashEntityView)
}
