/**
 * AT Protocol service configuration
 */

import dotenv from 'dotenv';

dotenv.config();

export const config = {
  // AT Protocol
  atproto: {
    pdsUrl: process.env.ATPROTO_PDS_URL || 'https://bsky.social',
    firehoseUrl: process.env.ATPROTO_FIREHOSE_URL || 'wss://bsky.network',
    did: process.env.ATPROTO_DID || '',
    handle: process.env.ATPROTO_HANDLE || '',
    password: process.env.ATPROTO_PASSWORD || '',
  },

  // Database
  database: {
    url: process.env.DATABASE_URL || 'postgresql://rhiz:rhiz@localhost:5432/rhiz',
  },

  // Redis
  redis: {
    url: process.env.REDIS_URL || 'redis://localhost:6379/0',
  },

  // Service
  service: {
    port: parseInt(process.env.PORT || '3100', 10),
    hostname: process.env.HOSTNAME || 'localhost',
  },

  // Feed Generator
  feed: {
    publisherDid: process.env.FEED_PUBLISHER_DID || '',
    serviceDid: process.env.FEED_SERVICE_DID || '',
    feedUri: process.env.FEED_URI || 'at://did:plc:example/app.bsky.feed.generator/rhiz',
  },

  // Labeler
  labeler: {
    did: process.env.LABELER_DID || '',
    signingKey: process.env.LABELER_SIGNING_KEY || '',
  },
};

