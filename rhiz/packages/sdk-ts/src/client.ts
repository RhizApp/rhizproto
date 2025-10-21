/**
 * Main Rhiz SDK client
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import { GraphAPI } from './api/graph';
import { EntitiesAPI } from './api/entities';
import { AnalyticsAPI } from './api/analytics';

export interface RhizClientConfig {
  apiUrl: string;
  apiKey?: string;
  timeout?: number;
  retries?: number;
}

export class RhizError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'RhizError';
  }
}

export class RhizClient {
  private client: AxiosInstance;
  public graph: GraphAPI;
  public entities: EntitiesAPI;
  public analytics: AnalyticsAPI;

  constructor(config: RhizClientConfig) {
    // Create axios instance
    this.client = axios.create({
      baseURL: `${config.apiUrl}/api/v1`,
      timeout: config.timeout || 30000,
      headers: {
        'Content-Type': 'application/json',
        ...(config.apiKey && { Authorization: `Bearer ${config.apiKey}` }),
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response) {
          throw new RhizError(
            error.response.data?.detail || error.message,
            error.response.status,
            error.response.data
          );
        }
        throw new RhizError(error.message);
      }
    );

    // Initialize API modules
    this.graph = new GraphAPI(this.client);
    this.entities = new EntitiesAPI(this.client);
    this.analytics = new AnalyticsAPI(this.client);
  }
}

