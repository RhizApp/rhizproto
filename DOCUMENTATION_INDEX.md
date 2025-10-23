# Rhiz Protocol - Documentation Index

**Last Updated:** October 23, 2025

This index provides a complete map of all Rhiz Protocol documentation organized by purpose and audience.

---

## 🚀 New to Rhiz? Start Here

| Document | Purpose | Time | Audience |
|----------|---------|------|----------|
| **[README.md](README.md)** | Project overview and quick start | 5 min | Everyone |
| **[START_HERE.md](START_HERE.md)** | Navigation guide and pathways | 10 min | New developers |
| **[STATUS.md](STATUS.md)** | Current implementation status | 10 min | Contributors |

**Recommended Path:**
1. Read README.md for overview
2. Follow START_HERE.md based on your role
3. Check STATUS.md for current progress

---

## 📖 Protocol Specification (Canonical)

These documents define the protocol itself. They are the **source of truth** for what Rhiz Protocol is and how it works.

| Document | Description | Audience | Stability |
|----------|-------------|----------|-----------|
| **[PROTOCOL_SPECIFICATION.md](PROTOCOL_SPECIFICATION.md)** | Formal protocol specification<br>- Core primitives (Entity, Relationship, Attestation, Trust)<br>- Data structures (chain-agnostic)<br>- Protocol operations<br>- Security requirements | Protocol designers<br>Implementers<br>Standards bodies | **Canonical**<br>Version 1.0 |
| **[RHIZ_PROTOCOL_ROADMAP.md](RHIZ_PROTOCOL_ROADMAP.md)** | 3-year development roadmap<br>- Year 1: Foundation + Relationships<br>- Year 2: Scale + Features<br>- Year 3: Maturity + Sustainability<br>- Quarterly milestones | Contributors<br>Stakeholders<br>Product teams | **Active**<br>Updated quarterly |

**Key Principle:** Protocol specification is implementation-agnostic. The AT Protocol implementation is the reference but not the only way to implement Rhiz.

---

## 🛠️ Implementation Guides

These documents explain **how to implement** Rhiz Protocol, with the AT Protocol implementation as the reference.

### Core Implementation

| Document | Description | Audience | Stability |
|----------|-------------|----------|-----------|
| **[AT_PROTOCOL_IMPLEMENTATION_GUIDE.md](AT_PROTOCOL_IMPLEMENTATION_GUIDE.md)** | Complete implementation guide<br>- Architecture patterns<br>- Lexicon design decisions<br>- Repository operations<br>- Trust calculation algorithms<br>- Performance optimizations<br>- Lessons learned | Implementers<br>Protocol developers<br>System architects | **Stable**<br>Reference guide |
| **[AT_PROTOCOL_NATIVE_MIGRATION.md](AT_PROTOCOL_NATIVE_MIGRATION.md)** | Architecture decisions<br>- DID-native transformation<br>- Content-addressing patterns<br>- AppView pattern implementation<br>- Migration strategies | Technical architects<br>Advanced developers | **Historical**<br>Architecture reference |
| **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** | Get running in 30 minutes<br>- Installation steps<br>- Configuration<br>- First relationship example<br>- Common troubleshooting | New developers<br>Quick evaluation | **Active**<br>Maintained |

### Phase-Specific Implementation

| Document | Description | Status |
|----------|-------------|--------|
| **[RHIZ_ATTESTATION_IMPLEMENTATION_PLAN.md](RHIZ_ATTESTATION_IMPLEMENTATION_PLAN.md)** | Phase 2A: Attestation System<br>- 8-week tactical plan<br>- Conviction algorithm design<br>- API endpoint specifications<br>- UI component requirements | 📋 **Planning**<br>Q1 2026 |

---

## 🏗️ Project Documentation

These documents describe the **current implementation** and project organization.

| Document | Description | Audience | Update Frequency |
|----------|-------------|----------|------------------|
| **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** | System architecture<br>- What makes Rhiz different<br>- Core capabilities<br>- Tech stack<br>- Use cases<br>- Flagship applications | Developers building on Rhiz<br>Product teams<br>Potential contributors | **Quarterly** |
| **[STATUS.md](STATUS.md)** | Current implementation status<br>- Phase completion tracking<br>- Active work<br>- Metrics and KPIs<br>- Known issues<br>- Next steps | Contributors<br>Project managers<br>Stakeholders | **Weekly** during active dev<br>**Monthly** otherwise |

---

## 🔧 Technical Resources

### Schemas and Specifications

| Resource | Description | Location |
|----------|-------------|----------|
| **Lexicon Schemas** | 11 JSON schemas defining net.rhiz.* collections<br>- Entity profiles<br>- Relationship records<br>- Trust metrics<br>- Attestations<br>- Graph queries | [`lexicons/net/rhiz/`](lexicons/net/rhiz/) |
| **Interop Test Files** | Validation test data<br>- Valid record examples<br>- Test fixtures<br>- Syntax validation | [`interop-test-files/rhiz/`](interop-test-files/rhiz/) |

### Package Documentation

| Package | Documentation | Location |
|---------|---------------|----------|
| **rhiz-protocol** | Core protocol (TypeScript)<br>Lexicons, types, identity, signing | [`packages/rhiz-protocol/README.md`](packages/rhiz-protocol/README.md) |
| **rhiz-sdk** | TypeScript SDK | [`packages/rhiz-sdk/README.md`](packages/rhiz-sdk/README.md) |
| **rhiz-sdk-py** | Python SDK | [`packages/rhiz-sdk-py/README.md`](packages/rhiz-sdk-py/README.md) |
| **rhiz-api** | FastAPI backend | [`services/rhiz-api/README.md`](services/rhiz-api/README.md) |
| **rhiz-atproto** | Firehose indexer | [`services/rhiz-atproto/README.md`](services/rhiz-atproto/README.md) |
| **fundrhiz** | Flagship application | [`services/fundrhiz/README.md`](services/fundrhiz/README.md) |

---

## 👥 Community Documentation

| Document | Description | Audience |
|----------|-------------|----------|
| **[CONTRIBUTORS.md](CONTRIBUTORS.md)** | Contributing guidelines<br>- Development setup<br>- Contribution workflow<br>- Code standards<br>- Commit conventions | Contributors<br>Open source developers |
| **[SECURITY.md](SECURITY.md)** | Security policies<br>- Responsible disclosure<br>- Supported versions<br>- Security contacts | Security researchers<br>Auditors |

---

## 📦 Archive

Historical documents that have been completed or superseded. Kept for reference.

| Category | Location | Contents |
|----------|----------|----------|
| **Historical Implementation Reports** | [`docs/archive/`](docs/archive/) | - Phase 1 completion reports<br>- Refactor status documents<br>- Planning summaries<br>- Outdated guides |

**Note:** Archived documents are not actively maintained. For current information, always refer to canonical documents.

See [`docs/archive/README.md`](docs/archive/README.md) for complete archive index.

---

## 📚 Document Categories Explained

### Canonical Documents
**Purpose:** Define what Rhiz Protocol **is**  
**Stability:** High - changes require community review  
**Examples:** PROTOCOL_SPECIFICATION.md, RHIZ_PROTOCOL_ROADMAP.md

### Implementation Guides
**Purpose:** Explain **how to build** Rhiz Protocol  
**Stability:** Medium - updated as patterns evolve  
**Examples:** AT_PROTOCOL_IMPLEMENTATION_GUIDE.md

### Project Documentation
**Purpose:** Describe the **current state** of the project  
**Stability:** Low - updated frequently  
**Examples:** STATUS.md, PROJECT_OVERVIEW.md

### Technical Resources
**Purpose:** Provide **schemas, tests, and references**  
**Stability:** High for schemas, Medium for tests  
**Examples:** Lexicon schemas, Interop tests

---

## 🎯 Documentation by Role

### I'm a Protocol Designer
**Focus on:** Protocol specification and theory
1. [PROTOCOL_SPECIFICATION.md](PROTOCOL_SPECIFICATION.md) - The formal spec
2. [Lexicon Schemas](lexicons/net/rhiz/) - Data structure definitions
3. [RHIZ_PROTOCOL_ROADMAP.md](RHIZ_PROTOCOL_ROADMAP.md) - Evolution plans

### I'm Implementing Rhiz on Another Platform
**Focus on:** Implementation patterns
1. [PROTOCOL_SPECIFICATION.md](PROTOCOL_SPECIFICATION.md) - What to implement
2. [AT_PROTOCOL_IMPLEMENTATION_GUIDE.md](AT_PROTOCOL_IMPLEMENTATION_GUIDE.md) - Reference patterns
3. [Interop Tests](interop-test-files/rhiz/) - Validation examples

### I'm Building an Application Using Rhiz
**Focus on:** SDK usage and APIs
1. [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) - Get running fast
2. [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Architecture understanding
3. [packages/rhiz-sdk/](packages/rhiz-sdk/) - SDK documentation

### I'm Contributing to the Project
**Focus on:** Current work and standards
1. [STATUS.md](STATUS.md) - What's happening now
2. [CONTRIBUTORS.md](CONTRIBUTORS.md) - How to contribute
3. [RHIZ_ATTESTATION_IMPLEMENTATION_PLAN.md](RHIZ_ATTESTATION_IMPLEMENTATION_PLAN.md) - Next phase work

### I'm Evaluating Rhiz Protocol
**Focus on:** Overview and capabilities
1. [README.md](README.md) - Quick overview
2. [PROTOCOL_SPECIFICATION.md](PROTOCOL_SPECIFICATION.md) - What it does
3. [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Why it matters

---

## 🔄 Documentation Maintenance

### Update Frequency

| Document | Frequency | Trigger |
|----------|-----------|---------|
| STATUS.md | Weekly during dev | Feature completion, milestones |
| PROTOCOL_SPECIFICATION.md | As needed (rare) | Protocol changes (RIP process) |
| RHIZ_PROTOCOL_ROADMAP.md | Quarterly | Quarter boundaries, major pivots |
| AT_PROTOCOL_IMPLEMENTATION_GUIDE.md | Monthly | Pattern changes, lessons learned |
| PROJECT_OVERVIEW.md | Quarterly | Architecture changes, new features |
| README.md | As needed | Major project changes |

### Consistency Checks

When updating documentation:
1. ✅ Update STATUS.md to reflect current state
2. ✅ Update README.md if project direction changes
3. ✅ Update START_HERE.md if document structure changes
4. ✅ Update DOCUMENTATION_INDEX.md (this file) if docs are added/removed
5. ✅ Archive completed status/tracking documents
6. ✅ Update relevant package READMEs

---

## 📝 Contributing to Documentation

### Reporting Issues
- Outdated information: Open issue with "docs" label
- Broken links: Open issue with "docs" and "bug" labels
- Missing documentation: Open issue with "docs" and "enhancement" labels

### Proposing Changes
1. Small fixes (typos, links): Direct PR
2. Content updates: Issue first, then PR
3. New documents: Discuss in issue before creating

### Documentation Standards
- Use Markdown
- Include table of contents for long documents
- Add "Last Updated" dates
- Link to related documents
- Keep examples up-to-date with current API

---

## 🗺️ Documentation Organization

```
rhizproto/
├── README.md                                    # Project overview
├── START_HERE.md                                # Navigation guide
├── STATUS.md                                    # Current status
├── DOCUMENTATION_INDEX.md                       # This file
│
├── [Canonical Protocol Documents]
├── PROTOCOL_SPECIFICATION.md                    # Formal spec
├── RHIZ_PROTOCOL_ROADMAP.md                     # Roadmap
│
├── [Implementation Guides]
├── AT_PROTOCOL_IMPLEMENTATION_GUIDE.md          # How to implement
├── AT_PROTOCOL_NATIVE_MIGRATION.md              # Architecture decisions
├── QUICK_START_GUIDE.md                         # Quick start
├── RHIZ_ATTESTATION_IMPLEMENTATION_PLAN.md      # Phase 2A plan
│
├── [Project Documentation]
├── PROJECT_OVERVIEW.md                          # System architecture
├── SECURITY.md                                  # Security policies
├── CONTRIBUTORS.md                              # Contributing guide
│
├── [Technical Resources]
├── lexicons/net/rhiz/                           # Lexicon schemas
├── interop-test-files/rhiz/                     # Test fixtures
├── packages/*/README.md                         # Package docs
├── services/*/README.md                         # Service docs
│
└── [Archive]
    └── docs/archive/                            # Historical documents
```

---

## 📞 Questions About Documentation?

**GitHub Discussions:** For questions about using the docs  
**GitHub Issues:** For reporting doc bugs or suggesting improvements  
**Email:** docs@rhiz.network (for sensitive documentation issues)

---

**Last Updated:** October 23, 2025  
**Maintained by:** Rhiz Protocol Team  
**License:** MIT / Apache 2.0 (like all project documentation)

**Rhiz Protocol - Making relationships machine-readable.**

