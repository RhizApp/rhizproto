/**
 * GENERATED CODE - DO NOT MODIFY
 */
import {
  type LexiconDoc,
  Lexicons,
  ValidationError,
  type ValidationResult,
} from '@atproto/lexicon'
import { type $Typed, is$typed, maybe$typed } from './util.js'

export const schemaDict = {
  NetRhizConvictionDefs: {
    lexicon: 1,
    id: 'net.rhiz.conviction.defs',
    defs: {
      convictionScore: {
        type: 'object',
        description:
          'Network consensus score for a claim based on attestations',
        required: ['score', 'attestationCount', 'lastUpdated'],
        properties: {
          score: {
            type: 'integer',
            minimum: 0,
            maximum: 100,
            description:
              'Network confidence score (0-100). Higher = more network consensus.',
          },
          attestationCount: {
            type: 'integer',
            minimum: 0,
            description: 'Total number of attestations received',
          },
          verifyCount: {
            type: 'integer',
            minimum: 0,
            description: 'Number of verify attestations',
          },
          disputeCount: {
            type: 'integer',
            minimum: 0,
            description: 'Number of dispute attestations',
          },
          lastUpdated: {
            type: 'string',
            format: 'datetime',
            description: 'When conviction score was last recalculated',
          },
          trend: {
            type: 'string',
            enum: ['increasing', 'stable', 'decreasing'],
            description: 'Conviction trend over last 30 days',
          },
          topAttesterReputation: {
            type: 'integer',
            minimum: 0,
            maximum: 100,
            description:
              'Reputation score of highest-reputation attester (for quality signal)',
          },
        },
      },
      attestationSummary: {
        type: 'object',
        description: 'Summary of attestations for a target URI',
        required: ['targetUri', 'conviction'],
        properties: {
          targetUri: {
            type: 'string',
            format: 'at-uri',
            description: 'URI of the attested record',
          },
          conviction: {
            type: 'ref',
            ref: 'lex:net.rhiz.conviction.defs#convictionScore',
          },
          recentAttestations: {
            type: 'array',
            description: 'Most recent attestations (limited to 10)',
            maxLength: 10,
            items: {
              type: 'ref',
              ref: 'lex:net.rhiz.conviction.defs#attestationRef',
            },
          },
        },
      },
      attestationRef: {
        type: 'object',
        description: 'Reference to an attestation',
        required: ['uri', 'attester', 'type', 'confidence', 'createdAt'],
        properties: {
          uri: {
            type: 'string',
            format: 'at-uri',
            description: 'AT URI of the attestation record',
          },
          attester: {
            type: 'string',
            format: 'did',
            description: 'DID of attester',
          },
          type: {
            type: 'string',
            enum: ['verify', 'dispute', 'strengthen', 'weaken'],
          },
          confidence: {
            type: 'integer',
            minimum: 0,
            maximum: 100,
          },
          createdAt: {
            type: 'string',
            format: 'datetime',
          },
        },
      },
    },
  },
  NetRhizConvictionGetScore: {
    lexicon: 1,
    id: 'net.rhiz.conviction.getScore',
    defs: {
      main: {
        type: 'query',
        description:
          'Get the conviction score for any attested record (relationship, trust metric, expertise claim, etc.)',
        parameters: {
          type: 'params',
          required: ['uri'],
          properties: {
            uri: {
              type: 'string',
              format: 'at-uri',
              description: 'AT URI of the record to get conviction for',
            },
          },
        },
        output: {
          encoding: 'application/json',
          schema: {
            type: 'object',
            required: ['uri', 'conviction'],
            properties: {
              uri: {
                type: 'string',
                format: 'at-uri',
                description: 'URI of the attested record',
              },
              conviction: {
                type: 'ref',
                ref: 'lex:net.rhiz.conviction.defs#convictionScore',
              },
              attestations: {
                type: 'array',
                description: 'All attestations for this record',
                items: {
                  type: 'ref',
                  ref: 'lex:net.rhiz.conviction.defs#attestationRef',
                },
              },
            },
          },
        },
        errors: [
          {
            name: 'RecordNotFound',
            description:
              'The specified URI does not exist or has no attestations',
          },
        ],
      },
    },
  },
  NetRhizConvictionListAttestations: {
    lexicon: 1,
    id: 'net.rhiz.conviction.listAttestations',
    defs: {
      main: {
        type: 'query',
        description:
          'List attestations for a specific record, with optional filtering',
        parameters: {
          type: 'params',
          required: ['uri'],
          properties: {
            uri: {
              type: 'string',
              format: 'at-uri',
              description: 'AT URI of the record to list attestations for',
            },
            type: {
              type: 'string',
              enum: ['verify', 'dispute', 'strengthen', 'weaken'],
              description: 'Filter by attestation type',
            },
            minConfidence: {
              type: 'integer',
              minimum: 0,
              maximum: 100,
              description: 'Minimum confidence threshold (0-100)',
            },
            limit: {
              type: 'integer',
              minimum: 1,
              maximum: 100,
              default: 50,
              description: 'Number of attestations to return',
            },
            cursor: {
              type: 'string',
              description: 'Pagination cursor',
            },
          },
        },
        output: {
          encoding: 'application/json',
          schema: {
            type: 'object',
            required: ['attestations'],
            properties: {
              attestations: {
                type: 'array',
                items: {
                  type: 'ref',
                  ref: 'lex:net.rhiz.conviction.listAttestations#attestationView',
                },
              },
              cursor: {
                type: 'string',
                description: 'Pagination cursor for next page',
              },
            },
          },
        },
      },
      attestationView: {
        type: 'object',
        description: 'Full attestation with attester profile',
        required: ['uri', 'record', 'attester'],
        properties: {
          uri: {
            type: 'string',
            format: 'at-uri',
          },
          cid: {
            type: 'string',
            format: 'cid',
          },
          record: {
            type: 'ref',
            ref: 'lex:net.rhiz.relationship.attestation',
          },
          attester: {
            type: 'ref',
            ref: 'lex:net.rhiz.entity.defs#entityProfile',
            description: 'Profile of the attester',
          },
          attesterReputation: {
            type: 'integer',
            minimum: 0,
            maximum: 100,
            description:
              "Attester's reputation score (affects conviction weight)",
          },
        },
      },
    },
  },
  NetRhizEntityDefs: {
    lexicon: 1,
    id: 'net.rhiz.entity.defs',
    defs: {
      entityType: {
        type: 'string',
        description: 'Type of entity in the Rhiz network',
        knownValues: ['person', 'organization', 'agent'],
      },
      entityView: {
        type: 'object',
        description: 'Public view of an entity',
        required: ['did', 'handle', 'displayName', 'verified', 'createdAt'],
        properties: {
          did: {
            type: 'string',
            format: 'did',
            description: 'Decentralized identifier',
          },
          handle: {
            type: 'string',
            format: 'handle',
            description: 'Human-readable handle',
          },
          displayName: {
            type: 'string',
            maxLength: 200,
            description: 'Display name',
          },
          entityType: {
            type: 'ref',
            ref: 'lex:net.rhiz.entity.defs#entityType',
          },
          bio: {
            type: 'string',
            maxLength: 1000,
            description: 'Biography or description',
          },
          avatarUrl: {
            type: 'string',
            format: 'uri',
            description: 'Avatar image URL',
          },
          verified: {
            type: 'boolean',
            description: 'Whether entity is verified',
          },
          createdAt: {
            type: 'string',
            format: 'datetime',
          },
          updatedAt: {
            type: 'string',
            format: 'datetime',
          },
        },
      },
    },
  },
  NetRhizEntityProfile: {
    lexicon: 1,
    id: 'net.rhiz.entity.profile',
    defs: {
      main: {
        type: 'record',
        description:
          'Entity profile record in Rhiz Protocol. Stores identity and metadata for people, organizations, and agents.',
        key: 'literal:self',
        record: {
          type: 'object',
          required: ['displayName', 'entityType', 'createdAt'],
          properties: {
            displayName: {
              type: 'string',
              maxLength: 200,
              description: 'Display name for this entity',
            },
            entityType: {
              type: 'ref',
              ref: 'lex:net.rhiz.entity.defs#entityType',
              description: 'Type of entity',
            },
            bio: {
              type: 'string',
              maxLength: 1000,
              description: 'Biography or description',
            },
            avatarUrl: {
              type: 'string',
              format: 'uri',
              description: 'Avatar image URL',
            },
            verified: {
              type: 'boolean',
              default: false,
              description: 'Whether this entity is verified',
            },
            metadata: {
              type: 'unknown',
              description: 'Additional metadata (flexible JSON object)',
            },
            createdAt: {
              type: 'string',
              format: 'datetime',
            },
          },
        },
      },
    },
  },
  NetRhizGraphDefs: {
    lexicon: 1,
    id: 'net.rhiz.graph.defs',
    defs: {
      graphHop: {
        type: 'object',
        description: 'A single hop in a graph path',
        required: ['from', 'to', 'relationshipUri', 'strength'],
        properties: {
          from: {
            type: 'string',
            format: 'did',
            description: 'Source entity DID',
          },
          to: {
            type: 'string',
            format: 'did',
            description: 'Destination entity DID',
          },
          relationshipUri: {
            type: 'string',
            format: 'at-uri',
            description: 'AT URI of the relationship record',
          },
          relationshipCid: {
            type: 'string',
            format: 'cid',
            description: 'CID of the relationship record',
          },
          strength: {
            type: 'integer',
            minimum: 0,
            maximum: 100,
            description: 'Relationship strength (0-100, scaled from 0.0-1.0)',
          },
        },
      },
      graphPath: {
        type: 'object',
        description:
          'A path between two entities through the relationship graph',
        required: ['from', 'to', 'hops', 'totalStrength', 'distance'],
        properties: {
          from: {
            type: 'string',
            format: 'did',
            description: 'Start entity DID',
          },
          to: {
            type: 'string',
            format: 'did',
            description: 'End entity DID',
          },
          hops: {
            type: 'array',
            items: {
              type: 'ref',
              ref: 'lex:net.rhiz.graph.defs#graphHop',
            },
            description: 'Sequence of hops connecting the entities',
          },
          totalStrength: {
            type: 'integer',
            minimum: 0,
            maximum: 100,
            description: 'Weighted product of hop strengths (0-100)',
          },
          distance: {
            type: 'integer',
            minimum: 1,
            description: 'Number of hops',
          },
        },
      },
    },
  },
  NetRhizGraphFindPath: {
    lexicon: 1,
    id: 'net.rhiz.graph.findPath',
    defs: {
      main: {
        type: 'query',
        description:
          'Find the shortest path between two entities through the relationship graph. Uses trust-weighted pathfinding algorithms.',
        parameters: {
          type: 'params',
          required: ['from', 'to'],
          properties: {
            from: {
              type: 'string',
              format: 'did',
              description: 'Start entity DID',
            },
            to: {
              type: 'string',
              format: 'did',
              description: 'Target entity DID',
            },
            maxHops: {
              type: 'integer',
              minimum: 1,
              maximum: 10,
              default: 6,
              description: 'Maximum number of hops to search',
            },
            minStrength: {
              type: 'integer',
              minimum: 0,
              maximum: 100,
              default: 50,
              description:
                'Minimum relationship strength to consider (0-100, default 50)',
            },
            relationshipTypes: {
              type: 'array',
              items: {
                type: 'string',
              },
              description:
                'Optional filter by relationship types (professional, personal, etc)',
            },
            excludeDids: {
              type: 'array',
              items: {
                type: 'string',
                format: 'did',
              },
              description: 'Optional DIDs to exclude from path',
            },
          },
        },
        output: {
          encoding: 'application/json',
          schema: {
            type: 'object',
            required: ['paths'],
            properties: {
              paths: {
                type: 'array',
                items: {
                  type: 'ref',
                  ref: 'lex:net.rhiz.graph.defs#graphPath',
                },
                description: 'List of paths found, sorted by strength',
              },
            },
          },
        },
      },
    },
  },
  NetRhizGraphGetNeighbors: {
    lexicon: 1,
    id: 'net.rhiz.graph.getNeighbors',
    defs: {
      main: {
        type: 'query',
        description:
          'Get all direct relationships (neighbors) for an entity in the relationship graph.',
        parameters: {
          type: 'params',
          required: ['did'],
          properties: {
            did: {
              type: 'string',
              format: 'did',
              description: 'Entity DID to get neighbors for',
            },
            minStrength: {
              type: 'integer',
              minimum: 0,
              maximum: 100,
              default: 0,
              description: 'Minimum relationship strength to include (0-100)',
            },
            relationshipTypes: {
              type: 'array',
              items: {
                type: 'string',
              },
              description:
                'Optional filter by relationship types (professional, personal, etc)',
            },
            limit: {
              type: 'integer',
              minimum: 1,
              maximum: 100,
              default: 50,
              description: 'Maximum number of neighbors to return',
            },
            cursor: {
              type: 'string',
              description: 'Pagination cursor',
            },
          },
        },
        output: {
          encoding: 'application/json',
          schema: {
            type: 'ref',
            ref: 'lex:net.rhiz.graph.getNeighbors#neighborsList',
          },
        },
      },
      neighborsList: {
        type: 'object',
        required: ['neighbors'],
        properties: {
          neighbors: {
            type: 'array',
            items: {
              type: 'ref',
              ref: 'lex:net.rhiz.graph.getNeighbors#neighborItem',
            },
          },
          cursor: {
            type: 'string',
            description: 'Pagination cursor for next page',
          },
        },
      },
      neighborItem: {
        type: 'object',
        required: ['entity', 'relationshipUri', 'strength'],
        properties: {
          entity: {
            type: 'ref',
            ref: 'lex:net.rhiz.entity.defs#entityView',
          },
          relationshipUri: {
            type: 'string',
            format: 'at-uri',
          },
          relationshipCid: {
            type: 'string',
            format: 'cid',
          },
          strength: {
            type: 'integer',
            minimum: 0,
            maximum: 100,
            description: 'Relationship strength (0-100)',
          },
          type: {
            type: 'string',
            description: 'Relationship type',
          },
        },
      },
    },
  },
  NetRhizIntroDefs: {
    lexicon: 1,
    id: 'net.rhiz.intro.defs',
    defs: {
      introStatus: {
        type: 'string',
        description: 'Status of an introduction request',
        knownValues: [
          'pending',
          'accepted',
          'declined',
          'completed',
          'cancelled',
        ],
      },
      agentIntent: {
        type: 'string',
        description: 'Intent of an agent message',
        knownValues: [
          'intro_request',
          'pitch',
          'evaluation',
          'negotiation',
          'info',
        ],
      },
    },
  },
  NetRhizIntroRequest: {
    lexicon: 1,
    id: 'net.rhiz.intro.request',
    defs: {
      main: {
        type: 'record',
        description:
          'Introduction request record. Used to request warm introductions through the relationship graph.',
        key: 'tid',
        record: {
          type: 'object',
          required: [
            'requester',
            'target',
            'context',
            'message',
            'status',
            'createdAt',
          ],
          properties: {
            requester: {
              type: 'string',
              format: 'did',
              description: 'DID of entity requesting introduction',
            },
            target: {
              type: 'string',
              format: 'did',
              description: 'DID of entity to be introduced to',
            },
            intermediary: {
              type: 'string',
              format: 'did',
              description: 'Optional suggested intermediary DID',
            },
            context: {
              type: 'string',
              maxLength: 500,
              description: 'Context for the introduction',
            },
            message: {
              type: 'string',
              maxLength: 2000,
              description: 'Introduction request message',
            },
            status: {
              type: 'ref',
              ref: 'lex:net.rhiz.intro.defs#introStatus',
            },
            pathRef: {
              type: 'string',
              format: 'at-uri',
              description:
                'Reference to the path record that suggested this intro',
            },
            createdAt: {
              type: 'string',
              format: 'datetime',
            },
            updatedAt: {
              type: 'string',
              format: 'datetime',
            },
          },
        },
      },
    },
  },
  NetRhizRelationshipAttestation: {
    lexicon: 1,
    id: 'net.rhiz.relationship.attestation',
    defs: {
      main: {
        type: 'record',
        description:
          'Third-party attestation validating or disputing a relationship record. Enables network consensus on relationship authenticity and strength.',
        key: 'tid',
        record: {
          type: 'object',
          required: [
            'targetRelationship',
            'attester',
            'attestationType',
            'confidence',
            'createdAt',
          ],
          properties: {
            targetRelationship: {
              type: 'string',
              format: 'at-uri',
              description:
                'AT URI of the relationship being attested (e.g., at://did:plc:alice/net.rhiz.relationship.record/{tid})',
            },
            attester: {
              type: 'string',
              format: 'did',
              description: 'DID of the entity making this attestation',
            },
            attestationType: {
              type: 'string',
              enum: ['verify', 'dispute', 'strengthen', 'weaken'],
              description:
                'Type of attestation: verify (confirms relationship), dispute (denies relationship), strengthen (suggests higher strength), weaken (suggests lower strength)',
            },
            confidence: {
              type: 'integer',
              minimum: 0,
              maximum: 100,
              description: "Attester's confidence in this attestation (0-100)",
            },
            evidence: {
              type: 'string',
              maxLength: 1000,
              description:
                'Optional textual evidence supporting this attestation',
            },
            suggestedStrength: {
              type: 'integer',
              minimum: 0,
              maximum: 100,
              description:
                'For strengthen/weaken types: suggested relationship strength value',
            },
            targetFields: {
              type: 'array',
              description:
                'Specific relationship fields being attested (if not attesting whole relationship)',
              items: {
                type: 'string',
                enum: ['strength', 'type', 'context', 'verification'],
              },
            },
            createdAt: {
              type: 'string',
              format: 'datetime',
              description: 'Timestamp when attestation was created',
            },
            stake: {
              type: 'ref',
              ref: 'lex:net.rhiz.relationship.attestation#stakeInfo',
              description:
                'Optional economic stake on this attestation (Phase 3)',
            },
          },
        },
      },
      stakeInfo: {
        type: 'object',
        description:
          'Economic staking information for attestation (Phase 3 feature)',
        required: ['amount', 'token'],
        properties: {
          amount: {
            type: 'integer',
            minimum: 0,
            description: 'Amount of tokens staked',
          },
          token: {
            type: 'string',
            description: "Token symbol (e.g., 'RHIZ')",
          },
          lockedUntil: {
            type: 'string',
            format: 'datetime',
            description: 'Timestamp when stake can be withdrawn',
          },
          slashingRisk: {
            type: 'integer',
            minimum: 0,
            maximum: 100,
            description:
              'Percentage of stake at risk if attestation proven false (0-100)',
          },
          slashed: {
            type: 'boolean',
            default: false,
            description: 'Whether this stake has been slashed',
          },
        },
      },
    },
  },
  NetRhizRelationshipDefs: {
    lexicon: 1,
    id: 'net.rhiz.relationship.defs',
    defs: {
      signatureData: {
        type: 'object',
        description: 'Cryptographic signature from a participant',
        required: ['did', 'signature'],
        properties: {
          did: {
            type: 'string',
            format: 'did',
          },
          signature: {
            type: 'string',
            description: 'Base64-encoded signature',
          },
        },
      },
      relationshipType: {
        type: 'string',
        description: 'Type of relationship',
        knownValues: [
          'professional',
          'personal',
          'family',
          'social',
          'civic',
          'educational',
        ],
      },
      visibility: {
        type: 'string',
        description: 'Visibility level for relationship data',
        knownValues: ['public', 'network', 'private'],
      },
      consentLevel: {
        type: 'string',
        description: 'Consent level for data usage',
        knownValues: ['full', 'limited', 'anonymous'],
      },
      verification: {
        type: 'object',
        description: 'Verification data for a relationship',
        required: [
          'consensusScore',
          'verifierCount',
          'confidence',
          'lastVerified',
        ],
        properties: {
          consensusScore: {
            type: 'integer',
            minimum: 0,
            maximum: 100,
            description:
              'Consensus score from verifiers (0-100, scaled from 0.0-1.0)',
          },
          verifierCount: {
            type: 'integer',
            minimum: 0,
            description: 'Number of entities that verified this relationship',
          },
          confidence: {
            type: 'integer',
            minimum: 0,
            maximum: 100,
            description:
              'Confidence level in verification (0-100, scaled from 0.0-1.0)',
          },
          lastVerified: {
            type: 'string',
            format: 'datetime',
            description: 'When relationship was last verified',
          },
          verifiers: {
            type: 'array',
            items: {
              type: 'string',
              format: 'did',
            },
            description: 'DIDs of entities that verified this relationship',
          },
        },
      },
      privacy: {
        type: 'object',
        description: 'Privacy settings for a relationship',
        required: ['visibility', 'consent'],
        properties: {
          visibility: {
            type: 'ref',
            ref: 'lex:net.rhiz.relationship.defs#visibility',
          },
          consent: {
            type: 'ref',
            ref: 'lex:net.rhiz.relationship.defs#consentLevel',
          },
        },
      },
      strengthHistoryPoint: {
        type: 'object',
        description: 'Historical strength data point',
        required: ['timestamp', 'strength'],
        properties: {
          timestamp: {
            type: 'string',
            format: 'datetime',
          },
          strength: {
            type: 'integer',
            minimum: 0,
            maximum: 100,
            description: 'Strength score (0-100, scaled from 0.0-1.0)',
          },
          event: {
            type: 'string',
            maxLength: 500,
            description: 'Optional description of what changed',
          },
        },
      },
      temporal: {
        type: 'object',
        description: 'Temporal data for a relationship',
        required: ['start', 'lastInteraction'],
        properties: {
          start: {
            type: 'string',
            format: 'datetime',
            description: 'When relationship started',
          },
          lastInteraction: {
            type: 'string',
            format: 'datetime',
            description: 'Most recent interaction',
          },
          history: {
            type: 'array',
            items: {
              type: 'ref',
              ref: 'lex:net.rhiz.relationship.defs#strengthHistoryPoint',
            },
            description: 'Historical strength data points',
          },
        },
      },
    },
  },
  NetRhizRelationshipRecord: {
    lexicon: 1,
    id: 'net.rhiz.relationship.record',
    defs: {
      main: {
        type: 'record',
        description:
          "Core relationship record in Rhiz Protocol. Represents a verified trust relationship between two entities. Stored in the initiator's repository.",
        key: 'tid',
        record: {
          type: 'object',
          required: [
            'participants',
            'type',
            'strength',
            'context',
            'verification',
            'privacy',
            'temporal',
            'createdAt',
          ],
          properties: {
            participants: {
              type: 'array',
              minLength: 2,
              maxLength: 2,
              items: {
                type: 'string',
                format: 'did',
              },
              description: 'The two entities in this relationship (as DIDs)',
            },
            type: {
              type: 'ref',
              ref: 'lex:net.rhiz.relationship.defs#relationshipType',
              description: 'Type of relationship',
            },
            strength: {
              type: 'integer',
              minimum: 0,
              maximum: 100,
              description:
                'Normalized trust score (0-100, scaled from 0.0-1.0)',
            },
            context: {
              type: 'string',
              maxLength: 500,
              description: 'Domain or project context for this relationship',
            },
            verification: {
              type: 'ref',
              ref: 'lex:net.rhiz.relationship.defs#verification',
              description: 'Verification data',
            },
            privacy: {
              type: 'ref',
              ref: 'lex:net.rhiz.relationship.defs#privacy',
              description: 'Privacy settings',
            },
            temporal: {
              type: 'ref',
              ref: 'lex:net.rhiz.relationship.defs#temporal',
              description: 'Temporal data',
            },
            signatures: {
              type: 'array',
              items: {
                type: 'ref',
                ref: 'lex:net.rhiz.relationship.defs#signatureData',
              },
              description: 'Cryptographic signatures from participants',
            },
            createdAt: {
              type: 'string',
              format: 'datetime',
            },
          },
        },
      },
    },
  },
  NetRhizTrustDefs: {
    lexicon: 1,
    id: 'net.rhiz.trust.defs',
    defs: {
      trustMetrics: {
        type: 'object',
        description: 'Trust metrics for an entity',
        required: [
          'entityDid',
          'trustScore',
          'reputation',
          'reciprocity',
          'consistency',
          'relationshipCount',
          'verifiedRelationshipCount',
          'lastCalculated',
        ],
        properties: {
          entityDid: {
            type: 'string',
            format: 'did',
            description: 'DID of the entity these metrics describe',
          },
          trustScore: {
            type: 'integer',
            minimum: 0,
            maximum: 100,
            description: 'Overall trust score (0-100, scaled from 0.0-1.0)',
          },
          reputation: {
            type: 'integer',
            minimum: 0,
            maximum: 100,
            description: 'Reputation score based on network consensus (0-100)',
          },
          reciprocity: {
            type: 'integer',
            minimum: 0,
            maximum: 100,
            description: 'Reciprocity score for mutual relationships (0-100)',
          },
          consistency: {
            type: 'integer',
            minimum: 0,
            maximum: 100,
            description: 'Consistency score for stable relationships (0-100)',
          },
          relationshipCount: {
            type: 'integer',
            minimum: 0,
            description: 'Total number of relationships',
          },
          verifiedRelationshipCount: {
            type: 'integer',
            minimum: 0,
            description: 'Number of verified relationships',
          },
          lastCalculated: {
            type: 'string',
            format: 'datetime',
            description: 'When these metrics were last calculated',
          },
        },
      },
    },
  },
  NetRhizTrustMetrics: {
    lexicon: 1,
    id: 'net.rhiz.trust.metrics',
    defs: {
      main: {
        type: 'record',
        description:
          'Trust metrics record for an entity. Calculated periodically and stored for historical analysis.',
        key: 'tid',
        record: {
          type: 'object',
          required: [
            'trustScore',
            'reputation',
            'reciprocity',
            'consistency',
            'relationshipCount',
            'verifiedRelationshipCount',
            'calculatedAt',
          ],
          properties: {
            trustScore: {
              type: 'integer',
              minimum: 0,
              maximum: 100,
              description: 'Overall trust score (0-100, scaled from 0.0-1.0)',
            },
            reputation: {
              type: 'integer',
              minimum: 0,
              maximum: 100,
              description: 'Reputation score (0-100)',
            },
            reciprocity: {
              type: 'integer',
              minimum: 0,
              maximum: 100,
              description: 'Reciprocity score (0-100)',
            },
            consistency: {
              type: 'integer',
              minimum: 0,
              maximum: 100,
              description: 'Consistency score (0-100)',
            },
            relationshipCount: {
              type: 'integer',
              minimum: 0,
              description: 'Total relationships',
            },
            verifiedRelationshipCount: {
              type: 'integer',
              minimum: 0,
              description: 'Verified relationships',
            },
            calculatedAt: {
              type: 'string',
              format: 'datetime',
            },
          },
        },
      },
    },
  },
} as const satisfies Record<string, LexiconDoc>
export const schemas = Object.values(schemaDict) satisfies LexiconDoc[]
export const lexicons: Lexicons = new Lexicons(schemas)

export function validate<T extends { $type: string }>(
  v: unknown,
  id: string,
  hash: string,
  requiredType: true,
): ValidationResult<T>
export function validate<T extends { $type?: string }>(
  v: unknown,
  id: string,
  hash: string,
  requiredType?: false,
): ValidationResult<T>
export function validate(
  v: unknown,
  id: string,
  hash: string,
  requiredType?: boolean,
): ValidationResult {
  return (requiredType ? is$typed : maybe$typed)(v, id, hash)
    ? lexicons.validate(`${id}#${hash}`, v)
    : {
        success: false,
        error: new ValidationError(
          `Must be an object with "${hash === 'main' ? id : `${id}#${hash}`}" $type property`,
        ),
      }
}

export const ids = {
  NetRhizConvictionDefs: 'net.rhiz.conviction.defs',
  NetRhizConvictionGetScore: 'net.rhiz.conviction.getScore',
  NetRhizConvictionListAttestations: 'net.rhiz.conviction.listAttestations',
  NetRhizEntityDefs: 'net.rhiz.entity.defs',
  NetRhizEntityProfile: 'net.rhiz.entity.profile',
  NetRhizGraphDefs: 'net.rhiz.graph.defs',
  NetRhizGraphFindPath: 'net.rhiz.graph.findPath',
  NetRhizGraphGetNeighbors: 'net.rhiz.graph.getNeighbors',
  NetRhizIntroDefs: 'net.rhiz.intro.defs',
  NetRhizIntroRequest: 'net.rhiz.intro.request',
  NetRhizRelationshipAttestation: 'net.rhiz.relationship.attestation',
  NetRhizRelationshipDefs: 'net.rhiz.relationship.defs',
  NetRhizRelationshipRecord: 'net.rhiz.relationship.record',
  NetRhizTrustDefs: 'net.rhiz.trust.defs',
  NetRhizTrustMetrics: 'net.rhiz.trust.metrics',
} as const
