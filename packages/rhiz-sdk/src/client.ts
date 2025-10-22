/**
 * Main Rhiz SDK client
 * Now with AT Protocol native support (DIDs, AT URIs, content-addressing)
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import { GraphAPI } from './api/graph';
import { EntitiesAPI } from './api/entities';
import { AnalyticsAPI } from './api/analytics';
import { ConvictionAPI } from './api/conviction';
import { AtpAgent } from '@atproto/api';
import { RhizRepoWriter } from '@atproto/rhiz-protocol';

export interface RhizClientConfig {
  apiUrl: string;
  apiKey?: string;
  timeout?: number;
  retries?: number;
  // AT Protocol config (optional, for direct repo operations)
  atproto?: {
    service: string; // PDS URL
    identifier?: string; // DID or handle
    password?: string;
  };
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
  private atpAgent?: AtpAgent;
  private repoWriter?: RhizRepoWriter;

  public graph: GraphAPI;
  public entities: EntitiesAPI;
  public analytics: AnalyticsAPI;
  public conviction: ConvictionAPI;

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

    // Initialize AT Protocol agent if config provided
    if (config.atproto) {
      this.atpAgent = new AtpAgent({ service: config.atproto.service });
      this.repoWriter = new RhizRepoWriter(this.atpAgent);
    }

    // Initialize API modules
    this.graph = new GraphAPI(this.client);
    this.entities = new EntitiesAPI(this.client, this.repoWriter);
    this.analytics = new AnalyticsAPI(this.client);
    this.conviction = new ConvictionAPI(this.client, this.repoWriter);
  }

  /**
   * Login to AT Protocol (required for repo operations)
   */
  async login(identifier: string, password: string): Promise<void> {
    if (!this.atpAgent) {
      throw new RhizError('AT Protocol not configured');
    }

    await this.atpAgent.login({ identifier, password });
  }

  /**
   * Get the repo writer for direct AT Protocol operations
   */
  get repo(): RhizRepoWriter {
    if (!this.repoWriter) {
      throw new RhizError('AT Protocol not configured');
    }
    return this.repoWriter;
  }
}

