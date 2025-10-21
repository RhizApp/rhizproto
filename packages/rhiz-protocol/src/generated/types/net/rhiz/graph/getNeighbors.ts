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
import type * as NetRhizEntityDefs from '../entity/defs.js'

const is$typed = _is$typed,
  validate = _validate
const id = 'net.rhiz.graph.getNeighbors'

export type QueryParams = {
  /** Entity DID to get neighbors for */
  did: string
  /** Minimum relationship strength to include (0-100) */
  minStrength?: number
  /** Optional filter by relationship types (professional, personal, etc) */
  relationshipTypes?: string[]
  /** Maximum number of neighbors to return */
  limit?: number
  /** Pagination cursor */
  cursor?: string
}
export type InputSchema = undefined
export type OutputSchema = NeighborsList

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

export interface NeighborsList {
  $type?: 'net.rhiz.graph.getNeighbors#neighborsList'
  neighbors: NeighborItem[]
  /** Pagination cursor for next page */
  cursor?: string
}

const hashNeighborsList = 'neighborsList'

export function isNeighborsList<V>(v: V) {
  return is$typed(v, id, hashNeighborsList)
}

export function validateNeighborsList<V>(v: V) {
  return validate<NeighborsList & V>(v, id, hashNeighborsList)
}

export interface NeighborItem {
  $type?: 'net.rhiz.graph.getNeighbors#neighborItem'
  entity: NetRhizEntityDefs.EntityView
  relationshipUri: string
  relationshipCid?: string
  /** Relationship strength (0-100) */
  strength: number
  /** Relationship type */
  type?: string
}

const hashNeighborItem = 'neighborItem'

export function isNeighborItem<V>(v: V) {
  return is$typed(v, id, hashNeighborItem)
}

export function validateNeighborItem<V>(v: V) {
  return validate<NeighborItem & V>(v, id, hashNeighborItem)
}
