/**
 * Entities API operations
 */

import type { AxiosInstance } from 'axios';
import type { Entity } from '@rhiz/protocol';

export interface CreateEntityRequest {
  id: string;
  type: string;
  name: string;
  bio?: string;
  avatar_url?: string;
  did?: string;
  handle?: string;
}

export interface UpdateEntityRequest {
  name?: string;
  bio?: string;
  avatar_url?: string;
  handle?: string;
}

export class EntitiesAPI {
  constructor(private client: AxiosInstance) {}

  async create(data: CreateEntityRequest): Promise<Entity> {
    const response = await this.client.post('/entities/', data);
    return response.data;
  }

  async get(entityId: string): Promise<Entity> {
    const response = await this.client.get(`/entities/${entityId}`);
    return response.data;
  }

  async update(entityId: string, data: UpdateEntityRequest): Promise<Entity> {
    const response = await this.client.patch(`/entities/${entityId}`, data);
    return response.data;
  }

  async delete(entityId: string): Promise<void> {
    await this.client.delete(`/entities/${entityId}`);
  }
}

