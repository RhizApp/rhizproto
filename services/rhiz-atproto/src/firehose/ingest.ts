/**
 * Firehose Ingestor
 * Subscribes to AT Protocol firehose and ingests relationship signals
 */

import { Firehose } from '@atproto/sync';
import WebSocket from 'ws';
import { config } from '../config';

interface FirehoseEvent {
  did: string;
  kind: 'commit' | 'handle' | 'account';
  commit?: {
    record: unknown;
    collection: string;
    rkey: string;
    operation: 'create' | 'update' | 'delete';
  };
}

class FirehoseIngestor {
  private firehose: Firehose<unknown> | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;

  async start(): void {
    console.log('🔥 Starting Firehose Ingestor...');
    console.log(`Connecting to: ${config.atproto.firehoseUrl}`);

    await this.connect();
  }

  private async connect(): Promise<void> {
    try {
      this.firehose = new Firehose({
        url: config.atproto.firehoseUrl,
        handleEvent: this.handleEvent.bind(this),
      });

      await this.firehose.start();
      this.reconnectAttempts = 0;
      console.log('✅ Connected to Firehose');
    } catch (error) {
      console.error('❌ Failed to connect to Firehose:', error);
      this.handleReconnect();
    }
  }

  private async handleEvent(event: FirehoseEvent): Promise<void> {
    try {
      // Skip non-commit events for now
      if (event.kind !== 'commit' || !event.commit) {
        return;
      }

      const { collection, operation, record } = event.commit;

      // Process relationship-relevant collections
      if (collection === 'app.bsky.graph.follow') {
        await this.handleFollow(event.did, record, operation);
      } else if (collection === 'app.bsky.feed.like') {
        await this.handleLike(event.did, record, operation);
      } else if (collection === 'app.bsky.feed.repost') {
        await this.handleRepost(event.did, record, operation);
      }
    } catch (error) {
      console.error('Error handling event:', error);
    }
  }

  private async handleFollow(
    did: string,
    record: unknown,
    operation: string
  ): Promise<void> {
    console.log(`📊 Follow event: ${did} - ${operation}`);
    // TODO: Map DID to entity, create/update relationship
    // This would call the Rhiz API to update the relationship graph
  }

  private async handleLike(did: string, record: unknown, operation: string): Promise<void> {
    // Likes can be signals of relationship strength
    console.log(`👍 Like event: ${did} - ${operation}`);
  }

  private async handleRepost(
    did: string,
    record: unknown,
    operation: string
  ): Promise<void> {
    // Reposts can indicate trust/endorsement
    console.log(`🔄 Repost event: ${did} - ${operation}`);
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached. Exiting.');
      process.exit(1);
    }

    this.reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})...`);
    setTimeout(() => this.connect(), delay);
  }

  async stop(): void {
    console.log('Stopping Firehose Ingestor...');
    // Cleanup
  }
}

// Main execution
if (require.main === module) {
  const ingestor = new FirehoseIngestor();

  ingestor.start().catch((error) => {
    console.error('Fatal error:', error);
    process.exit(1);
  });

  // Graceful shutdown
  process.on('SIGINT', async () => {
    console.log('Received SIGINT, shutting down...');
    await ingestor.stop();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    console.log('Received SIGTERM, shutting down...');
    await ingestor.stop();
    process.exit(0);
  });
}

export { FirehoseIngestor };

