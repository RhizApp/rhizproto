/**
 * GENERATED CODE - DO NOT MODIFY
 */
import {
  XrpcClient,
  type FetchHandler,
  type FetchHandlerOptions,
} from '@atproto/xrpc'
import { schemas } from './lexicons.js'
import { CID } from 'multiformats/cid'
import { type OmitKey, type Un$Typed } from './util.js'
import * as NetRhizEntityDefs from './types/net/rhiz/entity/defs.js'
import * as NetRhizEntityProfile from './types/net/rhiz/entity/profile.js'
import * as NetRhizGraphDefs from './types/net/rhiz/graph/defs.js'
import * as NetRhizGraphFindPath from './types/net/rhiz/graph/findPath.js'
import * as NetRhizGraphGetNeighbors from './types/net/rhiz/graph/getNeighbors.js'
import * as NetRhizIntroDefs from './types/net/rhiz/intro/defs.js'
import * as NetRhizIntroRequest from './types/net/rhiz/intro/request.js'
import * as NetRhizRelationshipDefs from './types/net/rhiz/relationship/defs.js'
import * as NetRhizRelationshipRecord from './types/net/rhiz/relationship/record.js'
import * as NetRhizTrustDefs from './types/net/rhiz/trust/defs.js'
import * as NetRhizTrustMetrics from './types/net/rhiz/trust/metrics.js'

export * as NetRhizEntityDefs from './types/net/rhiz/entity/defs.js'
export * as NetRhizEntityProfile from './types/net/rhiz/entity/profile.js'
export * as NetRhizGraphDefs from './types/net/rhiz/graph/defs.js'
export * as NetRhizGraphFindPath from './types/net/rhiz/graph/findPath.js'
export * as NetRhizGraphGetNeighbors from './types/net/rhiz/graph/getNeighbors.js'
export * as NetRhizIntroDefs from './types/net/rhiz/intro/defs.js'
export * as NetRhizIntroRequest from './types/net/rhiz/intro/request.js'
export * as NetRhizRelationshipDefs from './types/net/rhiz/relationship/defs.js'
export * as NetRhizRelationshipRecord from './types/net/rhiz/relationship/record.js'
export * as NetRhizTrustDefs from './types/net/rhiz/trust/defs.js'
export * as NetRhizTrustMetrics from './types/net/rhiz/trust/metrics.js'

export class AtpBaseClient extends XrpcClient {
  net: NetNS

  constructor(options: FetchHandler | FetchHandlerOptions) {
    super(options, schemas)
    this.net = new NetNS(this)
  }

  /** @deprecated use `this` instead */
  get xrpc(): XrpcClient {
    return this
  }
}

export class NetNS {
  _client: XrpcClient
  rhiz: NetRhizNS

  constructor(client: XrpcClient) {
    this._client = client
    this.rhiz = new NetRhizNS(client)
  }
}

export class NetRhizNS {
  _client: XrpcClient
  entity: NetRhizEntityNS
  graph: NetRhizGraphNS
  intro: NetRhizIntroNS
  relationship: NetRhizRelationshipNS
  trust: NetRhizTrustNS

  constructor(client: XrpcClient) {
    this._client = client
    this.entity = new NetRhizEntityNS(client)
    this.graph = new NetRhizGraphNS(client)
    this.intro = new NetRhizIntroNS(client)
    this.relationship = new NetRhizRelationshipNS(client)
    this.trust = new NetRhizTrustNS(client)
  }
}

export class NetRhizEntityNS {
  _client: XrpcClient
  profile: NetRhizEntityProfileRecord

  constructor(client: XrpcClient) {
    this._client = client
    this.profile = new NetRhizEntityProfileRecord(client)
  }
}

export class NetRhizEntityProfileRecord {
  _client: XrpcClient

  constructor(client: XrpcClient) {
    this._client = client
  }

  async list(
    params: OmitKey<ComAtprotoRepoListRecords.QueryParams, 'collection'>,
  ): Promise<{
    cursor?: string
    records: { uri: string; value: NetRhizEntityProfile.Record }[]
  }> {
    const res = await this._client.call('com.atproto.repo.listRecords', {
      collection: 'net.rhiz.entity.profile',
      ...params,
    })
    return res.data
  }

  async get(
    params: OmitKey<ComAtprotoRepoGetRecord.QueryParams, 'collection'>,
  ): Promise<{ uri: string; cid: string; value: NetRhizEntityProfile.Record }> {
    const res = await this._client.call('com.atproto.repo.getRecord', {
      collection: 'net.rhiz.entity.profile',
      ...params,
    })
    return res.data
  }

  async create(
    params: OmitKey<
      ComAtprotoRepoCreateRecord.InputSchema,
      'collection' | 'record'
    >,
    record: Un$Typed<NetRhizEntityProfile.Record>,
    headers?: Record<string, string>,
  ): Promise<{ uri: string; cid: string }> {
    const collection = 'net.rhiz.entity.profile'
    const res = await this._client.call(
      'com.atproto.repo.createRecord',
      undefined,
      {
        collection,
        rkey: 'self',
        ...params,
        record: { ...record, $type: collection },
      },
      { encoding: 'application/json', headers },
    )
    return res.data
  }

  async put(
    params: OmitKey<
      ComAtprotoRepoPutRecord.InputSchema,
      'collection' | 'record'
    >,
    record: Un$Typed<NetRhizEntityProfile.Record>,
    headers?: Record<string, string>,
  ): Promise<{ uri: string; cid: string }> {
    const collection = 'net.rhiz.entity.profile'
    const res = await this._client.call(
      'com.atproto.repo.putRecord',
      undefined,
      { collection, ...params, record: { ...record, $type: collection } },
      { encoding: 'application/json', headers },
    )
    return res.data
  }

  async delete(
    params: OmitKey<ComAtprotoRepoDeleteRecord.InputSchema, 'collection'>,
    headers?: Record<string, string>,
  ): Promise<void> {
    await this._client.call(
      'com.atproto.repo.deleteRecord',
      undefined,
      { collection: 'net.rhiz.entity.profile', ...params },
      { headers },
    )
  }
}

export class NetRhizGraphNS {
  _client: XrpcClient

  constructor(client: XrpcClient) {
    this._client = client
  }

  findPath(
    params?: NetRhizGraphFindPath.QueryParams,
    opts?: NetRhizGraphFindPath.CallOptions,
  ): Promise<NetRhizGraphFindPath.Response> {
    return this._client.call('net.rhiz.graph.findPath', params, undefined, opts)
  }

  getNeighbors(
    params?: NetRhizGraphGetNeighbors.QueryParams,
    opts?: NetRhizGraphGetNeighbors.CallOptions,
  ): Promise<NetRhizGraphGetNeighbors.Response> {
    return this._client.call(
      'net.rhiz.graph.getNeighbors',
      params,
      undefined,
      opts,
    )
  }
}

export class NetRhizIntroNS {
  _client: XrpcClient
  request: NetRhizIntroRequestRecord

  constructor(client: XrpcClient) {
    this._client = client
    this.request = new NetRhizIntroRequestRecord(client)
  }
}

export class NetRhizIntroRequestRecord {
  _client: XrpcClient

  constructor(client: XrpcClient) {
    this._client = client
  }

  async list(
    params: OmitKey<ComAtprotoRepoListRecords.QueryParams, 'collection'>,
  ): Promise<{
    cursor?: string
    records: { uri: string; value: NetRhizIntroRequest.Record }[]
  }> {
    const res = await this._client.call('com.atproto.repo.listRecords', {
      collection: 'net.rhiz.intro.request',
      ...params,
    })
    return res.data
  }

  async get(
    params: OmitKey<ComAtprotoRepoGetRecord.QueryParams, 'collection'>,
  ): Promise<{ uri: string; cid: string; value: NetRhizIntroRequest.Record }> {
    const res = await this._client.call('com.atproto.repo.getRecord', {
      collection: 'net.rhiz.intro.request',
      ...params,
    })
    return res.data
  }

  async create(
    params: OmitKey<
      ComAtprotoRepoCreateRecord.InputSchema,
      'collection' | 'record'
    >,
    record: Un$Typed<NetRhizIntroRequest.Record>,
    headers?: Record<string, string>,
  ): Promise<{ uri: string; cid: string }> {
    const collection = 'net.rhiz.intro.request'
    const res = await this._client.call(
      'com.atproto.repo.createRecord',
      undefined,
      { collection, ...params, record: { ...record, $type: collection } },
      { encoding: 'application/json', headers },
    )
    return res.data
  }

  async put(
    params: OmitKey<
      ComAtprotoRepoPutRecord.InputSchema,
      'collection' | 'record'
    >,
    record: Un$Typed<NetRhizIntroRequest.Record>,
    headers?: Record<string, string>,
  ): Promise<{ uri: string; cid: string }> {
    const collection = 'net.rhiz.intro.request'
    const res = await this._client.call(
      'com.atproto.repo.putRecord',
      undefined,
      { collection, ...params, record: { ...record, $type: collection } },
      { encoding: 'application/json', headers },
    )
    return res.data
  }

  async delete(
    params: OmitKey<ComAtprotoRepoDeleteRecord.InputSchema, 'collection'>,
    headers?: Record<string, string>,
  ): Promise<void> {
    await this._client.call(
      'com.atproto.repo.deleteRecord',
      undefined,
      { collection: 'net.rhiz.intro.request', ...params },
      { headers },
    )
  }
}

export class NetRhizRelationshipNS {
  _client: XrpcClient
  record: NetRhizRelationshipRecordRecord

  constructor(client: XrpcClient) {
    this._client = client
    this.record = new NetRhizRelationshipRecordRecord(client)
  }
}

export class NetRhizRelationshipRecordRecord {
  _client: XrpcClient

  constructor(client: XrpcClient) {
    this._client = client
  }

  async list(
    params: OmitKey<ComAtprotoRepoListRecords.QueryParams, 'collection'>,
  ): Promise<{
    cursor?: string
    records: { uri: string; value: NetRhizRelationshipRecord.Record }[]
  }> {
    const res = await this._client.call('com.atproto.repo.listRecords', {
      collection: 'net.rhiz.relationship.record',
      ...params,
    })
    return res.data
  }

  async get(
    params: OmitKey<ComAtprotoRepoGetRecord.QueryParams, 'collection'>,
  ): Promise<{
    uri: string
    cid: string
    value: NetRhizRelationshipRecord.Record
  }> {
    const res = await this._client.call('com.atproto.repo.getRecord', {
      collection: 'net.rhiz.relationship.record',
      ...params,
    })
    return res.data
  }

  async create(
    params: OmitKey<
      ComAtprotoRepoCreateRecord.InputSchema,
      'collection' | 'record'
    >,
    record: Un$Typed<NetRhizRelationshipRecord.Record>,
    headers?: Record<string, string>,
  ): Promise<{ uri: string; cid: string }> {
    const collection = 'net.rhiz.relationship.record'
    const res = await this._client.call(
      'com.atproto.repo.createRecord',
      undefined,
      { collection, ...params, record: { ...record, $type: collection } },
      { encoding: 'application/json', headers },
    )
    return res.data
  }

  async put(
    params: OmitKey<
      ComAtprotoRepoPutRecord.InputSchema,
      'collection' | 'record'
    >,
    record: Un$Typed<NetRhizRelationshipRecord.Record>,
    headers?: Record<string, string>,
  ): Promise<{ uri: string; cid: string }> {
    const collection = 'net.rhiz.relationship.record'
    const res = await this._client.call(
      'com.atproto.repo.putRecord',
      undefined,
      { collection, ...params, record: { ...record, $type: collection } },
      { encoding: 'application/json', headers },
    )
    return res.data
  }

  async delete(
    params: OmitKey<ComAtprotoRepoDeleteRecord.InputSchema, 'collection'>,
    headers?: Record<string, string>,
  ): Promise<void> {
    await this._client.call(
      'com.atproto.repo.deleteRecord',
      undefined,
      { collection: 'net.rhiz.relationship.record', ...params },
      { headers },
    )
  }
}

export class NetRhizTrustNS {
  _client: XrpcClient
  metrics: NetRhizTrustMetricsRecord

  constructor(client: XrpcClient) {
    this._client = client
    this.metrics = new NetRhizTrustMetricsRecord(client)
  }
}

export class NetRhizTrustMetricsRecord {
  _client: XrpcClient

  constructor(client: XrpcClient) {
    this._client = client
  }

  async list(
    params: OmitKey<ComAtprotoRepoListRecords.QueryParams, 'collection'>,
  ): Promise<{
    cursor?: string
    records: { uri: string; value: NetRhizTrustMetrics.Record }[]
  }> {
    const res = await this._client.call('com.atproto.repo.listRecords', {
      collection: 'net.rhiz.trust.metrics',
      ...params,
    })
    return res.data
  }

  async get(
    params: OmitKey<ComAtprotoRepoGetRecord.QueryParams, 'collection'>,
  ): Promise<{ uri: string; cid: string; value: NetRhizTrustMetrics.Record }> {
    const res = await this._client.call('com.atproto.repo.getRecord', {
      collection: 'net.rhiz.trust.metrics',
      ...params,
    })
    return res.data
  }

  async create(
    params: OmitKey<
      ComAtprotoRepoCreateRecord.InputSchema,
      'collection' | 'record'
    >,
    record: Un$Typed<NetRhizTrustMetrics.Record>,
    headers?: Record<string, string>,
  ): Promise<{ uri: string; cid: string }> {
    const collection = 'net.rhiz.trust.metrics'
    const res = await this._client.call(
      'com.atproto.repo.createRecord',
      undefined,
      { collection, ...params, record: { ...record, $type: collection } },
      { encoding: 'application/json', headers },
    )
    return res.data
  }

  async put(
    params: OmitKey<
      ComAtprotoRepoPutRecord.InputSchema,
      'collection' | 'record'
    >,
    record: Un$Typed<NetRhizTrustMetrics.Record>,
    headers?: Record<string, string>,
  ): Promise<{ uri: string; cid: string }> {
    const collection = 'net.rhiz.trust.metrics'
    const res = await this._client.call(
      'com.atproto.repo.putRecord',
      undefined,
      { collection, ...params, record: { ...record, $type: collection } },
      { encoding: 'application/json', headers },
    )
    return res.data
  }

  async delete(
    params: OmitKey<ComAtprotoRepoDeleteRecord.InputSchema, 'collection'>,
    headers?: Record<string, string>,
  ): Promise<void> {
    await this._client.call(
      'com.atproto.repo.deleteRecord',
      undefined,
      { collection: 'net.rhiz.trust.metrics', ...params },
      { headers },
    )
  }
}
