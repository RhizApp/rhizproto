/**
 * Entities API operations
 * Updated for DID-native operations
 */

import type { AxiosInstance } from 'axios';
import type { Entity } from '@atproto/rhiz-protocol';
import type { RhizRepoWriter, RecordRef } from '@atproto/rhiz-protocol';

/**
 * Create entity profile request (DID-native)
 */
export interface CreateEntityRequest {
  did: string; // Required: DID as primary identifier
  handle?: string; // Optional: human-readable handle
  name: string; // Display name
  type: string; // person, organization, agent
  bio?: string;
  avatar_url?: string;
}

/**
 * Update entity profile request
 */
export interface UpdateEntityRequest {
  name?: string;
  bio?: string;
  avatar_url?: string;
  handle?: string;
}

export class EntitiesAPI {
  constructor(
    private client: AxiosInstance,
    private repoWriter?: RhizRepoWriter,
  ) {}

  /**
   * Create entity profile (DID-based)
   * If repo writer is available, creates profile record in AT Protocol repo
   */
  async create(data: CreateEntityRequest): Promise<Entity> {
    // If we have repo writer, create profile record directly
    if (this.repoWriter) {
      const recordRef = await this.repoWriter.createProfile(data.did, {
        displayName: data.name,
        entityType: data.type,
        bio: data.bio,
        avatarUrl: data.avatar_url,
        verified: false,
        createdAt: new Date().toISOString(),
      });

      // Also register with API for indexing
      const response = await this.client.post('/entities/', {
        ...data,
        profile_uri: recordRef.uri,
        profile_cid: recordRef.cid,
      });

      return response.data;
    }

    // Fallback to API-only
    const response = await this.client.post('/entities/', data);
    return response.data;
  }

  /**
   * Get entity by DID
   */
  async get(did: string): Promise<Entity> {
    const response = await this.client.get(`/entities/${did}`);
    return response.data;
  }

  /**
   * Get entity by handle (resolves to DID first)
   */
  async getByHandle(handle: string): Promise<Entity> {
    const response = await this.client.get(`/entities/by-handle/${handle}`);
    return response.data;
  }

  /**
   * Update entity profile
   */
  async update(did: string, data: UpdateEntityRequest): Promise<Entity> {
    const response = await this.client.patch(`/entities/${did}`, data);
    return response.data;
  }

  /**
   * Delete entity profile
   */
  async delete(did: string): Promise<void> {
    await this.client.delete(`/entities/${did}`);
  }

  /**
   * Get entity profile directly from AT Protocol repo
   */
  async getProfileFromRepo(did: string): Promise<{
    record: any;
    cid: string;
  }> {
    if (!this.repoWriter) {
      throw new Error('Repo writer not configured');
    }
    return await this.repoWriter.getProfile(did);
  }
}

