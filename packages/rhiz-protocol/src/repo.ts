/**
 * AT Protocol Repo Operations for Rhiz Records
 * Handles storage and retrieval of relationship records in user repositories
 */

import { AtpAgent } from '@atproto/api'
import { TID } from '@atproto/common'
import { AtUri } from '@atproto/syntax'

/**
 * Record reference with AT URI and CID
 */
export interface RecordRef {
  uri: string // at://did:plc:alice/net.rhiz.relationship.record/tid
  cid: string // Content ID
}

/**
 * Relationship record for storage in repo
 */
export interface RelationshipRecordData {
  participants: [string, string]
  type: string
  strength: number
  context: string
  verification: {
    consensusScore: number
    verifierCount: number
    confidence: number
    lastVerified: string
  }
  privacy: {
    visibility: string
    consent: string
  }
  temporal: {
    start: string
    lastInteraction: string
    history?: Array<{
      timestamp: string
      strength: number
      event?: string
    }>
  }
  signatures?: Array<{
    did: string
    signature: string
  }>
  createdAt: string
}

/**
 * Repo writer for Rhiz records
 */
export class RhizRepoWriter {
  constructor(private agent: AtpAgent) {}

  /**
   * Create a new relationship record in a user's repo
   */
  async createRelationship(
    initiatorDid: string,
    record: RelationshipRecordData,
  ): Promise<RecordRef> {
    const response = await this.agent.com.atproto.repo.createRecord({
      repo: initiatorDid,
      collection: 'net.rhiz.relationship.record',
      record,
    })

    return {
      uri: response.data.uri,
      cid: response.data.cid,
    }
  }

  /**
   * Update an existing relationship record
   */
  async updateRelationship(
    uri: string,
    record: RelationshipRecordData,
  ): Promise<RecordRef> {
    const atUri = new AtUri(uri)

    const response = await this.agent.com.atproto.repo.putRecord({
      repo: atUri.hostname,
      collection: atUri.collection,
      rkey: atUri.rkey,
      record,
    })

    return {
      uri: response.data.uri,
      cid: response.data.cid,
    }
  }

  /**
   * Delete a relationship record
   */
  async deleteRelationship(uri: string): Promise<void> {
    const atUri = new AtUri(uri)

    await this.agent.com.atproto.repo.deleteRecord({
      repo: atUri.hostname,
      collection: atUri.collection,
      rkey: atUri.rkey,
    })
  }

  /**
   * Get a relationship record by URI
   */
  async getRelationship(uri: string): Promise<{
    record: RelationshipRecordData
    cid: string
  }> {
    const atUri = new AtUri(uri)

    const response = await this.agent.com.atproto.repo.getRecord({
      repo: atUri.hostname,
      collection: atUri.collection,
      rkey: atUri.rkey,
    })

    return {
      record: response.data.value as RelationshipRecordData,
      cid: response.data.cid || '',
    }
  }

  /**
   * List all relationships for a DID
   */
  async listRelationships(did: string, limit = 100): Promise<Array<{
    uri: string
    cid: string
    record: RelationshipRecordData
  }>> {
    const response = await this.agent.com.atproto.repo.listRecords({
      repo: did,
      collection: 'net.rhiz.relationship.record',
      limit,
    })

    return response.data.records.map((r) => ({
      uri: r.uri,
      cid: r.cid,
      record: r.value as RelationshipRecordData,
    }))
  }

  /**
   * Create an entity profile record
   */
  async createProfile(
    did: string,
    profile: {
      displayName: string
      entityType: string
      bio?: string
      avatarUrl?: string
      verified?: boolean
      createdAt: string
    },
  ): Promise<RecordRef> {
    const response = await this.agent.com.atproto.repo.createRecord({
      repo: did,
      collection: 'net.rhiz.entity.profile',
      rkey: 'self',
      record: profile,
    })

    return {
      uri: response.data.uri,
      cid: response.data.cid,
    }
  }

  /**
   * Get an entity profile
   */
  async getProfile(did: string): Promise<{
    record: any
    cid: string
  }> {
    const response = await this.agent.com.atproto.repo.getRecord({
      repo: did,
      collection: 'net.rhiz.entity.profile',
      rkey: 'self',
    })

    return {
      record: response.data.value,
      cid: response.data.cid || '',
    }
  }

  /**
   * Create a trust metrics record
   */
  async createTrustMetrics(
    did: string,
    metrics: {
      trustScore: number
      reputation: number
      reciprocity: number
      consistency: number
      relationshipCount: number
      verifiedRelationshipCount: number
      calculatedAt: string
    },
  ): Promise<RecordRef> {
    const tid = TID.nextStr()

    const response = await this.agent.com.atproto.repo.createRecord({
      repo: did,
      collection: 'net.rhiz.trust.metrics',
      rkey: tid,
      record: metrics,
    })

    return {
      uri: response.data.uri,
      cid: response.data.cid,
    }
  }

  /**
   * Create an introduction request record
   */
  async createIntroRequest(
    requesterDid: string,
    request: {
      requester: string
      target: string
      intermediary?: string
      context: string
      message: string
      status: string
      createdAt: string
      updatedAt: string
    },
  ): Promise<RecordRef> {
    const tid = TID.nextStr()

    const response = await this.agent.com.atproto.repo.createRecord({
      repo: requesterDid,
      collection: 'net.rhiz.intro.request',
      rkey: tid,
      record: request,
    })

    return {
      uri: response.data.uri,
      cid: response.data.cid,
    }
  }
}

/**
 * Create a repo writer for a given agent
 */
export function createRepoWriter(agent: AtpAgent): RhizRepoWriter {
  return new RhizRepoWriter(agent)
}

