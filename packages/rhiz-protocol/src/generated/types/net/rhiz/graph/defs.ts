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
const id = 'net.rhiz.graph.defs'

/** A single hop in a graph path */
export interface GraphHop {
  $type?: 'net.rhiz.graph.defs#graphHop'
  /** Source entity DID */
  from: string
  /** Destination entity DID */
  to: string
  /** AT URI of the relationship record */
  relationshipUri: string
  /** CID of the relationship record */
  relationshipCid?: string
  /** Relationship strength (0-100, scaled from 0.0-1.0) */
  strength: number
}

const hashGraphHop = 'graphHop'

export function isGraphHop<V>(v: V) {
  return is$typed(v, id, hashGraphHop)
}

export function validateGraphHop<V>(v: V) {
  return validate<GraphHop & V>(v, id, hashGraphHop)
}

/** A path between two entities through the relationship graph */
export interface GraphPath {
  $type?: 'net.rhiz.graph.defs#graphPath'
  /** Start entity DID */
  from: string
  /** End entity DID */
  to: string
  /** Sequence of hops connecting the entities */
  hops: GraphHop[]
  /** Weighted product of hop strengths (0-100) */
  totalStrength: number
  /** Number of hops */
  distance: number
}

const hashGraphPath = 'graphPath'

export function isGraphPath<V>(v: V) {
  return is$typed(v, id, hashGraphPath)
}

export function validateGraphPath<V>(v: V) {
  return validate<GraphPath & V>(v, id, hashGraphPath)
}
