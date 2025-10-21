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
const id = 'net.rhiz.intro.defs'

/** Status of an introduction request */
export type IntroStatus =
  | 'pending'
  | 'accepted'
  | 'declined'
  | 'completed'
  | 'cancelled'
  | (string & {})
/** Intent of an agent message */
export type AgentIntent =
  | 'intro_request'
  | 'pitch'
  | 'evaluation'
  | 'negotiation'
  | 'info'
  | (string & {})
