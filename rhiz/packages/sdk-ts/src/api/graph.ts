/**
 * Graph API operations
 */

import type { AxiosInstance } from 'axios';
import type { GraphPathResponse, GraphQueryRequest } from '@rhiz/protocol';

export class GraphAPI {
  constructor(private client: AxiosInstance) {}

  async findPath(query: GraphQueryRequest): Promise<GraphPathResponse> {
    const response = await this.client.post('/graph/find-path', query);
    return response.data;
  }

  async getNeighbors(
    entityId: string,
    options?: { min_strength?: number }
  ): Promise<{ entity_id: string; neighbors: unknown[]; count: number }> {
    const response = await this.client.get(`/graph/neighbors/${entityId}`, {
      params: options,
    });
    return response.data;
  }
}

