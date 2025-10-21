/**
 * Labeler Server
 * Applies trust-based labels to content and accounts
 */

import express from 'express';
import { config } from '../config';

const app = express();
app.use(express.json());

// Well-known DID document
app.get('/.well-known/did.json', (req, res) => {
  res.json({
    '@context': ['https://www.w3.org/ns/did/v1'],
    id: config.labeler.did,
    service: [
      {
        id: '#atproto_labeler',
        type: 'AtprotoLabeler',
        serviceEndpoint: `https://${config.service.hostname}`,
      },
    ],
  });
});

// Query labels endpoint
app.get('/xrpc/com.atproto.label.queryLabels', async (req, res) => {
  const { uris, sources, limit = 50, cursor } = req.query;

  console.log(`🏷️  Label query: ${uris}, sources: ${sources}`);

  // TODO: Implement actual labeling logic
  // 1. Look up entities in Rhiz database
  // 2. Get trust metrics
  // 3. Apply appropriate labels based on trust scores
  // 4. Return label records

  // Stub response
  res.json({
    cursor: cursor || undefined,
    labels: [
      // Example labels would go here:
      // {
      //   src: config.labeler.did,
      //   uri: 'at://did:plc:example',
      //   val: 'rhiz:high-trust',
      //   cts: new Date().toISOString(),
      // }
    ],
  });
});

// Subscribe to label stream
app.get('/xrpc/com.atproto.label.subscribeLabels', async (req, res) => {
  console.log('📡 Label subscription requested');

  // TODO: Implement WebSocket stream for label updates
  res.status(501).json({ error: 'Subscription not yet implemented' });
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'labeler' });
});

// Start server
if (require.main === module) {
  const port = config.service.port + 1; // Use different port
  app.listen(port, () => {
    console.log(`🏷️  Labeler listening on port ${port}`);
    console.log(`Labeler DID: ${config.labeler.did}`);
  });
}

export { app };

