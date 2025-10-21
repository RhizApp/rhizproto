/**
 * Feed Generator Server
 * Provides custom feed algorithm based on trust relationships
 */

import express from 'express';
import { config } from '../config';

const app = express();
app.use(express.json());

// Well-known DID document
app.get('/.well-known/did.json', (req, res) => {
  res.json({
    '@context': ['https://www.w3.org/ns/did/v1'],
    id: config.feed.serviceDid,
    service: [
      {
        id: '#bsky_fg',
        type: 'BskyFeedGenerator',
        serviceEndpoint: `https://${config.service.hostname}`,
      },
    ],
  });
});

// Feed skeleton endpoint
app.post('/xrpc/app.bsky.feed.getFeedSkeleton', async (req, res) => {
  const { feed, limit = 50, cursor } = req.body;

  console.log(`📰 Feed request: ${feed}, limit: ${limit}, cursor: ${cursor}`);

  // TODO: Implement actual feed algorithm
  // 1. Get requesting user's trust network
  // 2. Fetch posts from high-trust entities
  // 3. Rank by trust score and recency
  // 4. Return post URIs in ranked order

  // Stub response
  res.json({
    cursor: cursor || undefined,
    feed: [
      // Example post URIs would go here
      // { post: 'at://did:plc:example/app.bsky.feed.post/abc123' }
    ],
  });
});

// Describe feed generator
app.get('/xrpc/app.bsky.feed.describeFeedGenerator', (req, res) => {
  res.json({
    did: config.feed.serviceDid,
    feeds: [
      {
        uri: config.feed.feedUri,
        displayName: 'Rhiz Trust Feed',
        description:
          'Content from your high-trust network, surfaced by relationship intelligence',
        avatar: '',
      },
    ],
  });
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'feed-generator' });
});

// Start server
if (require.main === module) {
  const port = config.service.port;
  app.listen(port, () => {
    console.log(`🎯 Feed Generator listening on port ${port}`);
    console.log(`Feed URI: ${config.feed.feedUri}`);
  });
}

export { app };

