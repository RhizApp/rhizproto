# 🌐 Rhiz Protocol

**Building the Relationship Layer of the Internet**

[![CI](https://github.com/rhiz/rhiz/workflows/CI/badge.svg)](https://github.com/rhiz/rhiz/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Rhiz Protocol establishes open infrastructure for relationship intelligence: a universal schema that represents, verifies, and measures trust between people, organizations, and agents.

**FundRhiz** is the first implementation, automating warm introductions between founders and investors through trust-weighted graph analytics and AI agents.

## 🚀 Quick Start (10 Minutes)

```bash
# Prerequisites: Node 20+, Python 3.11+, Docker, pnpm
git clone https://github.com/rhiz/rhiz.git
cd rhiz
make install
make dev
```

Visit:
- **FundRhiz App**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Documentation**: http://localhost:3001

## 📦 Monorepo Structure

```
rhiz/
├── apps/
│   ├── api/              # FastAPI backend
│   ├── web/              # Next.js FundRhiz app
│   ├── atproto/          # AT Protocol services
│   └── docs/             # Docusaurus documentation
├── packages/
│   ├── protocol/         # Core protocol schemas
│   ├── sdk-ts/           # TypeScript SDK
│   ├── sdk-py/           # Python SDK
│   └── shared/           # Shared utilities
└── scripts/              # Dev and deployment scripts
```

## 🏗️ Architecture

**Four-Layer Model**:
1. **Data Layer**: PostgreSQL + pgvector for graph storage
2. **Intelligence Layer**: Trust scoring, path-finding algorithms
3. **Agent Layer**: Multi-agent coordination and negotiation
4. **Application Layer**: FundRhiz, WeRhiz (future)

**Built on AT Protocol** for identity, federation, and data distribution.

## 🛠️ Tech Stack

- **Backend**: FastAPI, SQLAlchemy 2, Pydantic v2
- **Frontend**: Next.js 15, React 19, Tailwind CSS
- **Database**: PostgreSQL 16 + pgvector 0.7
- **Cache**: Redis 7
- **AT Protocol**: Firehose, Feed Generator, Labeler
- **Monorepo**: pnpm workspaces + Turborepo

## 📚 Documentation

- [Protocol Specification](./docs/protocol/README.md)
- [API Reference](./docs/api/README.md)
- [SDK Guides](./docs/sdk/README.md)
- [Deployment Guide](./docs/deployment/README.md)

## 🧪 Testing

```bash
# Run all tests
make test

# Backend tests
cd apps/api && poetry run pytest

# Frontend tests
cd apps/web && pnpm test

# SDK tests
cd packages/sdk-ts && pnpm test
cd packages/sdk-py && poetry run pytest
```

## 🔒 Security & Privacy

- **Privacy by default**: Consent on each relationship edge
- **No secrets in repo**: Use `.env` files (see `.env.example`)
- **Audit logs**: All sensitive operations logged
- **Encryption**: End-to-end for private relationships

## 🤝 Contributing

We follow atomic commits with conventional commit messages:

```bash
git commit -m "feat(api): add trust scoring endpoint"
git commit -m "fix(web): resolve graph rendering issue"
```

See [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

## 📄 License

Dual-licensed under MIT and Apache 2.0. See [LICENSE-MIT](./LICENSE-MIT) and [LICENSE-APACHE](./LICENSE-APACHE).

## 🌟 Vision

Rhiz Protocol is building the open standard for relationship data—making relationships programmable, verifiable, and interoperable across all applications.

**Current Focus**: FundRhiz MVP (2025)
**Next**: WeRhiz professional OS
**Foundation**: Universal relationship infrastructure

---

**[Website](https://rhiz.network)** • **[Docs](https://docs.rhiz.network)** • **[Discord](https://discord.gg/rhiz)** • **[Twitter](https://twitter.com/rhizprotocol)**

