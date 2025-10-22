/**
 * Relationship Indexer
 * Subscribes to AT Protocol firehose and indexes net.rhiz.* records
 */

import { Firehose } from '@atproto/sync'
import { AtUri } from '@atproto/syntax'
import { cborDecode } from '@atproto/common'

/**
 * Indexed relationship data
 */
export interface IndexedRelationship {
  uri: string
  cid: string
  did: string // Owner of the record
  participants: [string, string]
  type: string
  strength: number
  context: string
  createdAt: string
  indexedAt: string
}

/**
 * Indexed attestation data
 */
export interface IndexedAttestation {
  uri: string
  cid: string
  attesterDid: string
  targetRelationship: string
  attestationType: string
  confidence: number
  evidence?: string
  suggestedStrength?: number
  createdAt: string
  indexedAt: string
}

/**
 * Indexer callbacks
 */
export interface IndexerCallbacks {
  onRelationshipCreated: (relationship: IndexedRelationship) => Promise<void>
  onRelationshipUpdated: (relationship: IndexedRelationship) => Promise<void>
  onRelationshipDeleted: (uri: string) => Promise<void>
  onAttestationCreated: (attestation: IndexedAttestation) => Promise<void>
  onAttestationUpdated: (attestation: IndexedAttestation) => Promise<void>
  onAttestationDeleted: (uri: string) => Promise<void>
  onProfileCreated: (profile: {
    uri: string
    cid: string
    did: string
    displayName: string
    entityType: string
    bio?: string
    createdAt: string
  }) => Promise<void>
  onError: (error: Error) => void
}

/**
 * Relationship indexer that subscribes to the firehose
 */
export class RelationshipIndexer {
  private firehose: Firehose
  private isRunning = false

  constructor(
    private firehoseUrl: string,
    private callbacks: IndexerCallbacks,
  ) {
    this.firehose = new Firehose({
      filterCollections: [
        'net.rhiz.relationship.record',
        'net.rhiz.relationship.attestation',
        'net.rhiz.entity.profile',
        'net.rhiz.trust.metrics',
        'net.rhiz.intro.request',
      ],
      handleEvent: this.handleEvent.bind(this),
      onError: callbacks.onError,
    })
  }

  /**
   * Start indexing from the firehose
   */
  async start(cursor?: number): Promise<void> {
    if (this.isRunning) {
      throw new Error('Indexer is already running')
    }

    console.log('Starting Rhiz relationship indexer...')
    console.log(`Firehose URL: ${this.firehoseUrl}`)

    this.isRunning = true
    await this.firehose.start(this.firehoseUrl, cursor)
  }

  /**
   * Stop indexing
   */
  stop(): void {
    if (!this.isRunning) {
      return
    }

    console.log('Stopping Rhiz relationship indexer...')
    this.firehose.destroy()
    this.isRunning = false
  }

  /**
   * Handle a firehose event
   */
  private async handleEvent(event: any): Promise<void> {
    if (event.$type !== 'commit') {
      return
    }

    const { repo, ops } = event

    for (const op of ops) {
      try {
        await this.handleOp(repo, op)
      } catch (error) {
        this.callbacks.onError(
          new Error(
            `Failed to handle op: ${error instanceof Error ? error.message : String(error)}`,
          ),
        )
      }
    }
  }

  /**
   * Handle a single operation
   */
  private async handleOp(repo: string, op: any): Promise<void> {
    const { action, path, cid } = op

    // Parse collection and rkey from path
    const uri = `at://${repo}/${path}`
    const atUri = new AtUri(uri)
    const collection = atUri.collection

    if (action === 'create' && collection === 'net.rhiz.relationship.record') {
      await this.handleRelationshipCreate(uri, cid, repo, op.record)
    } else if (
      action === 'update' &&
      collection === 'net.rhiz.relationship.record'
    ) {
      await this.handleRelationshipUpdate(uri, cid, repo, op.record)
    } else if (
      action === 'delete' &&
      collection === 'net.rhiz.relationship.record'
    ) {
      await this.handleRelationshipDelete(uri)
    } else if (action === 'create' && collection === 'net.rhiz.relationship.attestation') {
      await this.handleAttestationCreate(uri, cid, repo, op.record)
    } else if (action === 'update' && collection === 'net.rhiz.relationship.attestation') {
      await this.handleAttestationUpdate(uri, cid, repo, op.record)
    } else if (action === 'delete' && collection === 'net.rhiz.relationship.attestation') {
      await this.handleAttestationDelete(uri)
    } else if (action === 'create' && collection === 'net.rhiz.entity.profile') {
      await this.handleProfileCreate(uri, cid, repo, op.record)
    }
  }

  /**
   * Handle relationship record creation
   */
  private async handleRelationshipCreate(
    uri: string,
    cid: string,
    did: string,
    record: any,
  ): Promise<void> {
    const indexed: IndexedRelationship = {
      uri,
      cid,
      did,
      participants: record.participants,
      type: record.type,
      strength: record.strength,
      context: record.context,
      createdAt: record.createdAt,
      indexedAt: new Date().toISOString(),
    }

    await this.callbacks.onRelationshipCreated(indexed)
  }

  /**
   * Handle relationship record update
   */
  private async handleRelationshipUpdate(
    uri: string,
    cid: string,
    did: string,
    record: any,
  ): Promise<void> {
    const indexed: IndexedRelationship = {
      uri,
      cid,
      did,
      participants: record.participants,
      type: record.type,
      strength: record.strength,
      context: record.context,
      createdAt: record.createdAt,
      indexedAt: new Date().toISOString(),
    }

    await this.callbacks.onRelationshipUpdated(indexed)
  }

  /**
   * Handle relationship record deletion
   */
  private async handleRelationshipDelete(uri: string): Promise<void> {
    await this.callbacks.onRelationshipDeleted(uri)
  }

  /**
   * Handle attestation record creation
   */
  private async handleAttestationCreate(
    uri: string,
    cid: string,
    did: string,
    record: any,
  ): Promise<void> {
    const indexed: IndexedAttestation = {
      uri,
      cid,
      attesterDid: record.attester,
      targetRelationship: record.targetRelationship,
      attestationType: record.attestationType,
      confidence: record.confidence,
      evidence: record.evidence,
      suggestedStrength: record.suggestedStrength,
      createdAt: record.createdAt,
      indexedAt: new Date().toISOString(),
    }

    console.log(`📝 Indexing attestation: ${uri}`)
    console.log(`   Target: ${record.targetRelationship}`)
    console.log(`   Type: ${record.attestationType} (confidence: ${record.confidence})`)

    await this.callbacks.onAttestationCreated(indexed)
  }

  /**
   * Handle attestation record update
   */
  private async handleAttestationUpdate(
    uri: string,
    cid: string,
    did: string,
    record: any,
  ): Promise<void> {
    const indexed: IndexedAttestation = {
      uri,
      cid,
      attesterDid: record.attester,
      targetRelationship: record.targetRelationship,
      attestationType: record.attestationType,
      confidence: record.confidence,
      evidence: record.evidence,
      suggestedStrength: record.suggestedStrength,
      createdAt: record.createdAt,
      indexedAt: new Date().toISOString(),
    }

    await this.callbacks.onAttestationUpdated(indexed)
  }

  /**
   * Handle attestation record deletion
   */
  private async handleAttestationDelete(uri: string): Promise<void> {
    console.log(`🗑️  Deleting attestation: ${uri}`)
    await this.callbacks.onAttestationDeleted(uri)
  }

  /**
   * Handle profile creation
   */
  private async handleProfileCreate(
    uri: string,
    cid: string,
    did: string,
    record: any,
  ): Promise<void> {
    await this.callbacks.onProfileCreated({
      uri,
      cid,
      did,
      displayName: record.displayName,
      entityType: record.entityType,
      bio: record.bio,
      createdAt: record.createdAt,
    })
  }
}

/**
 * Create and start a relationship indexer
 */
export async function createRelationshipIndexer(
  firehoseUrl: string,
  callbacks: IndexerCallbacks,
  cursor?: number,
): Promise<RelationshipIndexer> {
  const indexer = new RelationshipIndexer(firehoseUrl, callbacks)
  await indexer.start(cursor)
  return indexer
}

