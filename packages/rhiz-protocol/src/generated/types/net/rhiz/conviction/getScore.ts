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
import type * as NetRhizConvictionDefs from './defs.js'

const is$typed = _is$typed,
  validate = _validate
const id = 'net.rhiz.conviction.getScore'

export type QueryParams = {
  /** AT URI of the record to get conviction for */
  uri: string
}
export type InputSchema = undefined

export interface OutputSchema {
  /** URI of the attested record */
  uri: string
  conviction: NetRhizConvictionDefs.ConvictionScore
  /** All attestations for this record */
  attestations?: NetRhizConvictionDefs.AttestationRef[]
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

export class RecordNotFoundError extends XRPCError {
  constructor(src: XRPCError) {
    super(src.status, src.error, src.message, src.headers, { cause: src })
  }
}

export function toKnownErr(e: any) {
  if (e instanceof XRPCError) {
    if (e.error === 'RecordNotFound') return new RecordNotFoundError(e)
  }

  return e
}
