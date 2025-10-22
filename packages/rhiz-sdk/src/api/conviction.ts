/**
 * Conviction API
 * Methods for attestations and conviction scores
 */

import { AxiosInstance } from 'axios'
import { RhizRepoWriter } from '@atproto/rhiz-protocol'

export interface ConvictionScore {
  uri: string
  conviction: {
    score: number
    attestationCount: number
    verifyCount: number
    disputeCount: number
    strengthenCount: number
    weakenCount: number
    lastUpdated: string
    trend: 'increasing' | 'stable' | 'decreasing'
    topAttesterReputation: number
  }
}

export interface Attestation {
  uri: string
  cid: string
  record: {
    targetRelationship: string
    attester: string
    attestationType: 'verify' | 'dispute' | 'strengthen' | 'weaken'
    confidence: number
    evidence?: string
    suggestedStrength?: number
    createdAt: string
  }
  attester?: {
    did: string
    name: string
    type: string
  }
  attesterReputation: number
}

export interface AttestationParams {
  targetRelationship: string
  attestationType: 'verify' | 'dispute' | 'strengthen' | 'weaken'
  confidence: number
  evidence?: string
  suggestedStrength?: number
}

export interface ListAttestationsParams {
  uri: string
  type?: 'verify' | 'dispute' | 'strengthen' | 'weaken'
  minConfidence?: number
  limit?: number
  cursor?: string
}

export interface ListAttestationsResponse {
  attestations: Attestation[]
  cursor?: string
}

export class ConvictionAPI {
  constructor(
    private client: AxiosInstance,
    private repoWriter?: RhizRepoWriter,
  ) {}

  /**
   * Attest to a relationship record
   * Creates an attestation record in the user's AT Protocol repository
   */
  async attestRelationship(params: AttestationParams): Promise<{ uri: string; cid: string }> {
    if (!this.repoWriter) {
      throw new Error('AT Protocol not configured - cannot create attestation record')
    }

    // Get current session
    const session = await this.repoWriter.getAgent().getSession()
    if (!session) {
      throw new Error('Not logged in - call client.login() first')
    }

    // Create attestation record
    const record = {
      $type: 'net.rhiz.relationship.attestation',
      targetRelationship: params.targetRelationship,
      attester: session.did,
      attestationType: params.attestationType,
      confidence: params.confidence,
      evidence: params.evidence,
      suggestedStrength: params.suggestedStrength,
      createdAt: new Date().toISOString(),
    }

    // Write to user's repository
    const result = await this.repoWriter.getAgent().com.atproto.repo.createRecord({
      repo: session.did,
      collection: 'net.rhiz.relationship.attestation',
      record,
    })

    return {
      uri: result.data.uri,
      cid: result.data.cid,
    }
  }

  /**
   * Get conviction score for a record
   */
  async getConviction(uri: string): Promise<ConvictionScore> {
    const response = await this.client.get<ConvictionScore>(
      `/xrpc/net.rhiz.conviction.getScore`,
      {
        params: { uri },
      }
    )
    return response.data
  }

  /**
   * List attestations for a record
   */
  async listAttestations(params: ListAttestationsParams): Promise<ListAttestationsResponse> {
    const response = await this.client.get<ListAttestationsResponse>(
      `/xrpc/net.rhiz.conviction.listAttestations`,
      {
        params: {
          uri: params.uri,
          ...(params.type && { type: params.type }),
          ...(params.minConfidence && { minConfidence: params.minConfidence }),
          ...(params.limit && { limit: params.limit }),
          ...(params.cursor && { cursor: params.cursor }),
        },
      }
    )
    return response.data
  }

  /**
   * Get conviction score for multiple records at once
   */
  async getConvictionBatch(uris: string[]): Promise<ConvictionScore[]> {
    const results = await Promise.all(
      uris.map(uri => this.getConviction(uri).catch(() => null))
    )
    return results.filter((r): r is ConvictionScore => r !== null)
  }
}

