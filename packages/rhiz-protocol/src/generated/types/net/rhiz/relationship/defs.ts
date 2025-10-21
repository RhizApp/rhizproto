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
const id = 'net.rhiz.relationship.defs'

/** Cryptographic signature from a participant */
export interface SignatureData {
  $type?: 'net.rhiz.relationship.defs#signatureData'
  did: string
  /** Base64-encoded signature */
  signature: string
}

const hashSignatureData = 'signatureData'

export function isSignatureData<V>(v: V) {
  return is$typed(v, id, hashSignatureData)
}

export function validateSignatureData<V>(v: V) {
  return validate<SignatureData & V>(v, id, hashSignatureData)
}

/** Type of relationship */
export type RelationshipType =
  | 'professional'
  | 'personal'
  | 'family'
  | 'social'
  | 'civic'
  | 'educational'
  | (string & {})
/** Visibility level for relationship data */
export type Visibility = 'public' | 'network' | 'private' | (string & {})
/** Consent level for data usage */
export type ConsentLevel = 'full' | 'limited' | 'anonymous' | (string & {})

/** Verification data for a relationship */
export interface Verification {
  $type?: 'net.rhiz.relationship.defs#verification'
  /** Consensus score from verifiers (0-100, scaled from 0.0-1.0) */
  consensusScore: number
  /** Number of entities that verified this relationship */
  verifierCount: number
  /** Confidence level in verification (0-100, scaled from 0.0-1.0) */
  confidence: number
  /** When relationship was last verified */
  lastVerified: string
  /** DIDs of entities that verified this relationship */
  verifiers?: string[]
}

const hashVerification = 'verification'

export function isVerification<V>(v: V) {
  return is$typed(v, id, hashVerification)
}

export function validateVerification<V>(v: V) {
  return validate<Verification & V>(v, id, hashVerification)
}

/** Privacy settings for a relationship */
export interface Privacy {
  $type?: 'net.rhiz.relationship.defs#privacy'
  visibility: Visibility
  consent: ConsentLevel
}

const hashPrivacy = 'privacy'

export function isPrivacy<V>(v: V) {
  return is$typed(v, id, hashPrivacy)
}

export function validatePrivacy<V>(v: V) {
  return validate<Privacy & V>(v, id, hashPrivacy)
}

/** Historical strength data point */
export interface StrengthHistoryPoint {
  $type?: 'net.rhiz.relationship.defs#strengthHistoryPoint'
  timestamp: string
  /** Strength score (0-100, scaled from 0.0-1.0) */
  strength: number
  /** Optional description of what changed */
  event?: string
}

const hashStrengthHistoryPoint = 'strengthHistoryPoint'

export function isStrengthHistoryPoint<V>(v: V) {
  return is$typed(v, id, hashStrengthHistoryPoint)
}

export function validateStrengthHistoryPoint<V>(v: V) {
  return validate<StrengthHistoryPoint & V>(v, id, hashStrengthHistoryPoint)
}

/** Temporal data for a relationship */
export interface Temporal {
  $type?: 'net.rhiz.relationship.defs#temporal'
  /** When relationship started */
  start: string
  /** Most recent interaction */
  lastInteraction: string
  /** Historical strength data points */
  history?: StrengthHistoryPoint[]
}

const hashTemporal = 'temporal'

export function isTemporal<V>(v: V) {
  return is$typed(v, id, hashTemporal)
}

export function validateTemporal<V>(v: V) {
  return validate<Temporal & V>(v, id, hashTemporal)
}
