/**
 * Analytics API operations
 */

import type { AxiosInstance } from 'axios';
import type { TrustMetrics } from '@rhiz/protocol';

export interface TrustHealthResponse {
  entity_id: string;
  trust_level: string;
  trust_score: number;
  network_size: number;
  verified_ratio: number;
  recent_activity: number;
  recommendations: string[];
}

export interface NetworkStatsResponse {
  total_entities: number;
  total_relationships: number;
  avg_trust_score: number;
  verified_entities: number;
}

export class AnalyticsAPI {
  constructor(private client: AxiosInstance) {}

  async getTrustHealth(entityId: string): Promise<TrustHealthResponse> {
    const response = await this.client.get(`/analytics/trust-health/${entityId}`);
    return response.data;
  }

  async getTrustMetrics(entityId: string): Promise<TrustMetrics> {
    const response = await this.client.get(`/analytics/trust-metrics/${entityId}`);
    return response.data;
  }

  async getNetworkStats(): Promise<NetworkStatsResponse> {
    const response = await this.client.get('/analytics/network-stats');
    return response.data;
  }
}

