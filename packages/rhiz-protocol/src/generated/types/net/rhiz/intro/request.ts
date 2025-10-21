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
import type * as NetRhizIntroDefs from './defs.js'

const is$typed = _is$typed,
  validate = _validate
const id = 'net.rhiz.intro.request'

export interface Record {
  $type: 'net.rhiz.intro.request'
  /** DID of entity requesting introduction */
  requester: string
  /** DID of entity to be introduced to */
  target: string
  /** Optional suggested intermediary DID */
  intermediary?: string
  /** Context for the introduction */
  context: string
  /** Introduction request message */
  message: string
  status: NetRhizIntroDefs.IntroStatus
  /** Reference to the path record that suggested this intro */
  pathRef?: string
  createdAt: string
  updatedAt?: string
  [k: string]: unknown
}

const hashRecord = 'main'

export function isRecord<V>(v: V) {
  return is$typed(v, id, hashRecord)
}

export function validateRecord<V>(v: V) {
  return validate<Record & V>(v, id, hashRecord, true)
}
