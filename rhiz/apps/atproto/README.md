# AT Protocol Integration

AT Protocol services for Rhiz: Firehose ingestor, feed generator, and labeler.

## Services

### 1. Firehose Ingestor

Subscribes to the AT Protocol Firehose and ingests relationship signals.

```bash
pnpm ingest
```

**What it does:**
- Listens to the firehose for follows, likes, reposts
- Maps DIDs to Rhiz entities
- Creates/updates relationship records
- Publishes events to Redis for processing

### 2. Feed Generator

Custom feed algorithm that surfaces content based on trust relationships.

```bash
pnpm feed
```

**Endpoints:**
- `GET /.well-known/did.json` - DID document
- `POST /xrpc/app.bsky.feed.getFeedSkeleton` - Feed algorithm

### 3. Labeler

Applies trust-based labels to content and accounts.

```bash
pnpm labeler
```

**Labels:**
- `rhiz:high-trust` - Entity with high trust score
- `rhiz:verified-network` - Part of verified relationship network
- `rhiz:new-entity` - Recently joined, limited trust data

## Configuration

Set environment variables (see `.env.example`):

```env
ATPROTO_PDS_URL=https://bsky.social
ATPROTO_FIREHOSE_URL=wss://bsky.network
ATPROTO_DID=did:plc:your-did
ATPROTO_HANDLE=your.handle
ATPROTO_PASSWORD=your-password
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

## Architecture

```
┌─────────────┐
│  Firehose   │
│   (AT)      │
└─────┬───────┘
      │
      ▼
┌─────────────┐      ┌─────────────┐
│  Ingestor   │─────▶│    Redis    │
└─────┬───────┘      └─────────────┘
      │
      ▼
┌─────────────┐
│  Database   │
│  (Postgres) │
└─────────────┘
      ▲
      │
┌─────┴───────┐
│ Feed Gen &  │
│  Labeler    │
└─────────────┘
```

## Development

```bash
# Build
pnpm build

# Run in dev mode
pnpm dev

# Type check
pnpm typecheck

# Test
pnpm test
```

## Deployment

Each service can run independently:

```bash
# Docker
docker build -t rhiz-atproto .
docker run -e ATPROTO_SERVICE=firehose rhiz-atproto
docker run -e ATPROTO_SERVICE=feed rhiz-atproto
docker run -e ATPROTO_SERVICE=labeler rhiz-atproto
```

## License

MIT

