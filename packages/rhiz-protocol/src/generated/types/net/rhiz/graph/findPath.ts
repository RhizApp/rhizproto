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
import type * as NetRhizGraphDefs from './defs.js'

const is$typed = _is$typed,
  validate = _validate
const id = 'net.rhiz.graph.findPath'

export type QueryParams = {
  /** Start entity DID */
  from: string
  /** Target entity DID */
  to: string
  /** Maximum number of hops to search */
  maxHops?: number
  /** Minimum relationship strength to consider (0-100, default 50) */
  minStrength?: number
  /** Optional filter by relationship types (professional, personal, etc) */
  relationshipTypes?: string[]
  /** Optional DIDs to exclude from path */
  excludeDids?: string[]
}
export type InputSchema = undefined

export interface OutputSchema {
  /** List of paths found, sorted by strength */
  paths: NetRhizGraphDefs.GraphPath[]
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
