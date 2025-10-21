/**
 * API client for Rhiz backend
 */

import axios, { AxiosInstance } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class RhizAPI {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_URL}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for auth
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
  }

  // Graph endpoints
  async findPath(query: {
    from: string;
    to: string;
    max_hops?: number;
    min_strength?: number;
  }) {
    const response = await this.client.post('/graph/find-path', query);
    return response.data;
  }

  async getNeighbors(entityId: string, minStrength = 0.0) {
    const response = await this.client.get(`/graph/neighbors/${entityId}`, {
      params: { min_strength: minStrength },
    });
    return response.data;
  }

  // Entity endpoints
  async getEntity(entityId: string) {
    const response = await this.client.get(`/entities/${entityId}`);
    return response.data;
  }

  async createEntity(data: {
    id: string;
    type: string;
    name: string;
    bio?: string;
  }) {
    const response = await this.client.post('/entities/', data);
    return response.data;
  }

  async updateEntity(entityId: string, data: Partial<{ name: string; bio: string }>) {
    const response = await this.client.patch(`/entities/${entityId}`, data);
    return response.data;
  }

  // Analytics endpoints
  async getTrustHealth(entityId: string) {
    const response = await this.client.get(`/analytics/trust-health/${entityId}`);
    return response.data;
  }

  async getTrustMetrics(entityId: string) {
    const response = await this.client.get(`/analytics/trust-metrics/${entityId}`);
    return response.data;
  }

  async getNetworkStats() {
    const response = await this.client.get('/analytics/network-stats');
    return response.data;
  }
}

export const api = new RhizAPI();

