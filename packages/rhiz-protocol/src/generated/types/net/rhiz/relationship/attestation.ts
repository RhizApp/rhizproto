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
const id = 'net.rhiz.relationship.attestation'

export interface Record {
  $type: 'net.rhiz.relationship.attestation'
  /** AT URI of the relationship being attested (e.g., at://did:plc:alice/net.rhiz.relationship.record/{tid}) */
  targetRelationship: string
  /** DID of the entity making this attestation */
  attester: string
  /** Type of attestation: verify (confirms relationship), dispute (denies relationship), strengthen (suggests higher strength), weaken (suggests lower strength) */
  attestationType: 'verify' | 'dispute' | 'strengthen' | 'weaken'
  /** Attester's confidence in this attestation (0-100) */
  confidence: number
  /** Optional textual evidence supporting this attestation */
  evidence?: string
  /** For strengthen/weaken types: suggested relationship strength value */
  suggestedStrength?: number
  /** Specific relationship fields being attested (if not attesting whole relationship) */
  targetFields?: ('strength' | 'type' | 'context' | 'verification')[]
  /** Timestamp when attestation was created */
  createdAt: string
  stake?: StakeInfo
  [k: string]: unknown
}

const hashRecord = 'main'

export function isRecord<V>(v: V) {
  return is$typed(v, id, hashRecord)
}

export function validateRecord<V>(v: V) {
  return validate<Record & V>(v, id, hashRecord, true)
}

/** Economic staking information for attestation (Phase 3 feature) */
export interface StakeInfo {
  $type?: 'net.rhiz.relationship.attestation#stakeInfo'
  /** Amount of tokens staked */
  amount: number
  /** Token symbol (e.g., 'RHIZ') */
  token: string
  /** Timestamp when stake can be withdrawn */
  lockedUntil?: string
  /** Percentage of stake at risk if attestation proven false (0-100) */
  slashingRisk?: number
  /** Whether this stake has been slashed */
  slashed: boolean
}

const hashStakeInfo = 'stakeInfo'

export function isStakeInfo<V>(v: V) {
  return is$typed(v, id, hashStakeInfo)
}

export function validateStakeInfo<V>(v: V) {
  return validate<StakeInfo & V>(v, id, hashStakeInfo)
}
