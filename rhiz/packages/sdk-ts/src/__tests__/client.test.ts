import { describe, it, expect } from 'vitest';
import { RhizClient, RhizError } from '../client';

describe('RhizClient', () => {
  it('should initialize with config', () => {
    const client = new RhizClient({
      apiUrl: 'http://localhost:8000',
    });

    expect(client).toBeDefined();
    expect(client.graph).toBeDefined();
    expect(client.entities).toBeDefined();
    expect(client.analytics).toBeDefined();
  });

  it('should accept API key in config', () => {
    const client = new RhizClient({
      apiUrl: 'http://localhost:8000',
      apiKey: 'test-key',
    });

    expect(client).toBeDefined();
  });

  it('should create RhizError with correct properties', () => {
    const error = new RhizError('Test error', 404, { detail: 'Not found' });

    expect(error).toBeInstanceOf(Error);
    expect(error.name).toBe('RhizError');
    expect(error.message).toBe('Test error');
    expect(error.statusCode).toBe(404);
    expect(error.details).toEqual({ detail: 'Not found' });
  });
});

