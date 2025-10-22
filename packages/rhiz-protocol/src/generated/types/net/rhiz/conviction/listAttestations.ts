/**
 * GENERATED CODE - DO NOT MODIFY
 */
import { HeadersMap, XRPCError } from '@atproto/xrpc'
import { type ValidationResult, BlobRef } from '@atproto/lexicon'
import { CID } from 'multiformats/cid'
import { validate as _validate } from '../../../../lexicons'
import {
  type $Typed,
  is$typed as _is$typed,
  type OmitKey,
} from '../../../../util'
import type * as NetRhizRelationshipAttestation from '../relationship/attestation.js'
import type * as NetRhizEntityDefs from '../entity/defs.js'

const is$typed = _is$typed,
  validate = _validate
const id = 'net.rhiz.conviction.listAttestations'

export type QueryParams = {
  /** AT URI of the record to list attestations for */
  uri: string
  /** Filter by attestation type */
  type?: 'verify' | 'dispute' | 'strengthen' | 'weaken'
  /** Minimum confidence threshold (0-100) */
  minConfidence?: number
  /** Number of attestations to return */
  limit?: number
  /** Pagination cursor */
  cursor?: string
}
export type InputSchema = undefined

export interface OutputSchema {
  attestations: AttestationView[]
  /** Pagination cursor for next page */
  cursor?: string
}

export interface CallOptions {
  signal?: AbortSignal
  headers?: HeadersMap
}

export interface Response {
  success: boolean
  headers: HeadersMap
  data: OutputSchema
}

export function toKnownErr(e: any) {
  return e
}

/** Full attestation with attester profile */
export interface AttestationView {
  $type?: 'net.rhiz.conviction.listAttestations#attestationView'
  uri: string
  cid?: string
  record: NetRhizRelationshipAttestation.Main
  attester: NetRhizEntityDefs.EntityProfile
  /** Attester's reputation score (affects conviction weight) */
  attesterReputation?: number
}

const hashAttestationView = 'attestationView'

export function isAttestationView<V>(v: V) {
  return is$typed(v, id, hashAttestationView)
}

export function validateAttestationView<V>(v: V) {
  return validate<AttestationView & V>(v, id, hashAttestationView)
}
