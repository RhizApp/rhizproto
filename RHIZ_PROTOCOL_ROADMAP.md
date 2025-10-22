# Rhiz Protocol Roadmap

**The Relationship Protocol - AT Protocol First**

---

## Vision

Build the best relationship protocol on AT Protocol, focused on making relationships machine-readable, verifiable, and valuable. Multi-chain expansion only when it makes strategic sense.

## Strategy

**Relationships First:**
- Perfect relationship data structures
- Rock-solid trust algorithms
- Network attestation that works
- Best-in-class developer experience

**AT Protocol Deep:**
- Native implementation, not bolted-on
- Leverage AT Protocol's strengths
- Federation-ready from day one
- User-owned data always

**Multi-Chain Later:**
- When we have product-market fit
- When users demand it
- When we have resources
- Not before we nail relationships

---

## Year 1 (2025-2026): Foundation + Relationships

### Q4 2025: Core Protocol (Current)

**Status:** Foundation Complete ✅

**Achieved:**
- 11 Lexicon schemas validated
- DID-native architecture
- Content-addressed records
- Firehose indexer operational
- Database migration complete
- SDK with AT Protocol support

**Next:**
- Protocol specification documentation
- Polish existing implementation
- Production readiness

---

### Q1 2026: Attestation System (Phase 2A)

**Goal:** Network-verified relationships with conviction scores

**Deliverables:**

1. **Conviction Algorithm**
   - Reputation-weighted attestations
   - Temporal decay (180-day half-life)
   - Confidence scaling
   - Trend detection (increasing/stable/decreasing)
   - **Target:** <100ms calculation for 100 attestations

2. **Database Schema**
   - `attestations` table
   - `conviction_scores` cache table
   - Conviction columns on relationships
   - Optimized indexes

3. **API Endpoints**
   - `GET /xrpc/net.rhiz.conviction.getScore`
   - `GET /xrpc/net.rhiz.conviction.listAttestations`
   - Real-time conviction updates
   - **Target:** <200ms p95 latency

4. **SDK Methods**
   - `attestRelationship()`
   - `getConviction()`
   - `listAttestations()`
   - TypeScript + Python

5. **UI Components**
   - ConvictionBadge (show trust level)
   - AttestationButton (submit attestations)
   - Attestation list view
   - Mobile responsive

**Success Metrics:**
- 30% of relationships have ≥1 attestation (Month 3)
- 80%+ conviction accuracy vs manual validation
- 90%+ fraud detection (fake relationships <40 conviction)
- <100ms conviction calculation, <200ms API latency

**Timeline:** 8 weeks

**Resources:** Already planned in `RHIZ_ATTESTATION_IMPLEMENTATION_PLAN.md`

---

### Q2 2026: Relationship Quality

**Goal:** Make relationships the most useful data structure for trust

**Deliverables:**

1. **Rich Relationship Context**
   - Structured context fields (not just free text)
   - Relationship tags/labels
   - Shared experiences/events
   - Mutual connections
   - Evidence attachments

2. **Relationship Analytics**
   - Strength distribution charts
   - Trust momentum visualization
   - Attestation timeline
   - Relationship health score
   - Decay warnings

3. **Advanced Trust Metrics**
   - Trust velocity (rate of change)
   - Reciprocity index
   - Network centrality
   - Cluster analysis
   - Path diversity

4. **Relationship Recommendations**
   - Suggest attestations (who can verify this?)
   - Suggest connections (who should you connect to?)
   - Suggest strengthenings (relationships that need updates)
   - Anomaly detection (unusual patterns)

**Success Metrics:**
- 60% of relationships have structured context
- 40% of users update relationships monthly
- Trust metrics 85%+ accurate
- 500+ active monthly users

**Timeline:** 12 weeks

---

### Q3 2026: Developer Experience

**Goal:** Make Rhiz the easiest trust protocol to integrate

**Deliverables:**

1. **SDK Improvements**
   - Simplified API surface
   - Better error messages
   - Retry logic and resilience
   - Webhook support for events
   - TypeScript strict mode
   - React hooks (`useRelationship`, `useTrustScore`)

2. **Documentation**
   - Interactive API docs
   - Code examples for common patterns
   - Video tutorials
   - Migration guides
   - Troubleshooting guide
   - FAQ

3. **Developer Tools**
   - Rhiz CLI for testing
   - Local dev environment (Docker)
   - Relationship graph visualizer
   - Attestation simulator
   - Trust score playground

4. **Integration Guides**
   - Integrate Rhiz into existing apps
   - Best practices for relationship modeling
   - Privacy configuration guide
   - Performance optimization tips
   - Case studies

**Success Metrics:**
- Developer onboarding <30 minutes
- 50+ developers building on Rhiz
- 10+ production applications
- 90%+ SDK satisfaction score

**Timeline:** 10 weeks

---

## Year 2 (2026-2027): Scale + Ecosystem

### Q4 2026: Performance & Scale

**Goal:** Support 100K+ relationships without breaking

**Deliverables:**

1. **Database Optimization**
   - Query optimization (EXPLAIN ANALYZE)
   - Advanced indexing strategies
   - Materialized views for complex queries
   - Partitioning for large tables
   - Connection pooling tuning

2. **Caching Layer**
   - Redis for hot data
   - Conviction score caching
   - Trust metrics caching
   - Graph query results caching
   - Cache invalidation strategy

3. **API Performance**
   - GraphQL API (optional, alongside REST)
   - Batch operations
   - Pagination improvements
   - Response streaming for large datasets
   - Rate limiting per user

4. **Infrastructure**
   - Horizontal scaling (multiple API instances)
   - Load balancer configuration
   - Read replicas for queries
   - CDN for static assets
   - Monitoring and alerting (DataDog/Grafana)

**Success Metrics:**
- 100K+ relationships indexed
- <200ms p95 API latency maintained
- 99.9% uptime
- Support 1000 req/s

**Timeline:** 8 weeks

---

### Q1 2027: Advanced Features

**Goal:** Unique capabilities no other protocol has

**Deliverables:**

1. **Temporal Trust Dynamics**
   - Relationship decay modeling
   - Trust momentum detection
   - Prediction: future trust trajectory
   - Seasonal patterns (interaction frequency)
   - Historical trust queries

2. **Smart Pathfinding**
   - Trust-weighted shortest path
   - Multiple path discovery (top 5 paths)
   - Path quality scoring
   - Intermediary suggestions
   - Path visualization

3. **Relationship Clustering**
   - Community detection algorithms
   - Identify tight-knit groups
   - Weak ties vs strong ties analysis
   - Bridge identification (connectors)
   - Clique analysis

4. **Context Matching**
   - Find relationships by context
   - Domain expertise matching
   - Shared experience discovery
   - Common connections
   - Interest alignment

**Success Metrics:**
- Pathfinding <500ms for 6 hops
- 80%+ of paths lead to successful intros
- Users find 5+ useful connections via clustering
- Context matching 70%+ relevant

**Timeline:** 12 weeks

---

### Q2 2027: Ecosystem Growth

**Goal:** 10+ applications building on Rhiz

**Deliverables:**

1. **Application Templates**
   - Professional networking app
   - Community mapping tool
   - Introduction platform
   - Reputation system
   - Trust-based marketplace

2. **Integration Partnerships**
   - Integrate with 3+ existing AT Protocol apps
   - Bluesky integration (show Rhiz relationships)
   - Partner with identity providers
   - Academic partnerships (research)
   - Enterprise POCs

3. **Developer Program**
   - Developer grants ($5K-$25K)
   - Technical support channel
   - Office hours (weekly)
   - Hackathon prizes
   - Case study spotlight

4. **Marketing & Community**
   - Protocol website launch
   - Developer blog
   - Twitter/Bluesky presence
   - Discord community
   - Monthly developer calls

**Success Metrics:**
- 20+ applications using Rhiz
- 100+ active developers
- 5+ integrations with existing apps
- 1000+ community members

**Timeline:** 12 weeks

---

### Q3 2027: Standards & Recognition

**Goal:** Rhiz recognized as AT Protocol standard for relationships

**Deliverables:**

1. **Standards Documentation**
   - Submit specification to AT Protocol community
   - Propose as AT Protocol extension
   - Present at AT Protocol events
   - Academic paper on trust algorithms
   - W3C Community Group exploration

2. **Reference Implementation**
   - Code quality audit
   - Security audit
   - Performance benchmarks published
   - Implementation guide for others
   - Compliance test suite

3. **Industry Validation**
   - 3+ enterprise pilots
   - Case studies published
   - ROI analysis for businesses
   - Privacy compliance audit (GDPR)
   - Accessibility audit (WCAG)

4. **Thought Leadership**
   - Conference talks (5+)
   - Podcast interviews
   - Blog post series
   - Research collaborations
   - Open-source advocacy

**Success Metrics:**
- Mentioned in AT Protocol documentation
- 2+ academic citations
- 5+ conference presentations
- 3+ enterprise customers

**Timeline:** 12 weeks

---

## Year 3 (2027-2028): Maturity + Sustainability

### Q4 2027: Advanced Trust

**Goal:** Best-in-class trust algorithms

**Deliverables:**

1. **Machine Learning Models**
   - Trust score prediction
   - Fraud detection models
   - Anomaly detection
   - Relationship strength estimation
   - Sybil attack detection

2. **Privacy Features**
   - Selective disclosure
   - Private attestations (only parties see)
   - Encrypted relationship context
   - Zero-knowledge proofs (research)
   - Anonymous attestation protocol

3. **Reputation Systems**
   - Attester reputation scoring
   - Domain-specific reputation
   - Reputation markets (future token?)
   - Reputation portability
   - Reputation recovery mechanisms

4. **Advanced Analytics**
   - Trust network visualization
   - Influence scoring
   - Bottleneck identification
   - Network health metrics
   - Predictive analytics

**Success Metrics:**
- ML models 90%+ accurate
- Privacy features used in 20% of relationships
- Reputation scores 85%+ accurate
- Zero false positive Sybil detection

**Timeline:** 12 weeks

---

### Q1 2028: Protocol Sustainability

**Goal:** Long-term protocol sustainability model

**Deliverables:**

1. **Economic Model (If Needed)**
   - Fee structure analysis
   - Premium features identification
   - Enterprise pricing
   - API rate limit tiers
   - Sustainability model (non-token first)

2. **Governance**
   - Rhiz Improvement Proposals (RIPs)
   - Community voting mechanism
   - Protocol foundation (if needed)
   - Multi-stakeholder governance
   - Transparent decision-making

3. **Long-term Stewardship**
   - Core team funding
   - Bug bounty program
   - Security incident response
   - Deprecation policy
   - Backwards compatibility guarantees

4. **Ecosystem Fund**
   - Developer grants program
   - Research funding
   - Community events
   - Educational initiatives
   - Open-source contributions

**Success Metrics:**
- Sustainable revenue (if needed)
- 10+ core contributors
- $100K+ in grants distributed
- 5-year protocol roadmap

**Timeline:** 12 weeks

---

### Q2 2028: Multi-Chain Exploration (Optional)

**Goal:** Evaluate multi-chain if strategically valuable

**Decision Criteria:**
- AT Protocol has limitations we can't work around
- Users demanding other chains (proven demand)
- Funding available for expansion
- Team capacity increased (3+ people)
- Product-market fit proven (10K+ users)

**If All Criteria Met:**

1. **Chain Selection**
   - Evaluate NEAR vs EVM
   - Cost/benefit analysis
   - Developer ecosystem assessment
   - User demand analysis
   - Technical feasibility study

2. **Design Specification**
   - Chain-agnostic data models
   - Cross-chain identifier mapping
   - Bridge architecture
   - Storage optimization
   - Gas cost analysis

3. **Prototype**
   - Smart contract development
   - Indexer adaptation
   - SDK updates
   - Testing on testnet
   - Community feedback

4. **Launch Decision**
   - Go/no-go based on prototype
   - Resource allocation
   - Timeline planning
   - Risk assessment
   - Strategic value validation

**If Criteria Not Met:**
- Continue focusing on AT Protocol
- Deepen relationship features
- Expand ecosystem
- Improve developer experience

---

### Q3 2028: Ecosystem Maturity

**Goal:** Thriving ecosystem of Rhiz applications

**Deliverables:**

1. **Usage Dashboard**
   - Real-time protocol statistics
   - Application showcase
   - Developer metrics
   - Network health indicators
   - Growth trends

2. **Success Stories**
   - 20+ case studies
   - Video testimonials
   - Impact measurements
   - ROI calculations
   - Best practices documentation

3. **Educational Content**
   - Online course (Rhiz Protocol 101)
   - Workshop materials
   - University curriculum
   - Certification program
   - Conference track

4. **Long-Term Vision**
   - 5-year roadmap
   - Research agenda
   - Standards evolution
   - Ecosystem growth plan
   - Impact goals

**Success Metrics:**
- 50+ applications using Rhiz
- 50K+ entities, 500K+ relationships
- 100K+ attestations
- 1000+ developers trained

**Timeline:** 12 weeks

---

## Implementation Priorities

### Small Team (1-3 People) Focus

**Year 1 - Build:**
- Q1: Attestation system (relationships with conviction)
- Q2: Relationship quality features
- Q3: Developer experience excellence
- Core: Make AT Protocol implementation rock-solid

**Year 2 - Scale:**
- Q4: Performance & infrastructure
- Q1: Advanced trust features
- Q2: Ecosystem partnerships
- Q3: Standards recognition
- Core: Support growing user base

**Year 3 - Sustain:**
- Q4: ML and privacy features
- Q1: Sustainability model
- Q2: Multi-chain evaluation (maybe)
- Q3: Ecosystem maturity
- Core: Long-term protocol health

---

## Success Metrics

### Year 1 Targets
- 10,000+ entities
- 50,000+ relationships
- 10,000+ attestations
- 10+ applications using Rhiz
- 50+ active developers

### Year 2 Targets
- 50,000+ entities
- 500,000+ relationships
- 100,000+ attestations
- 30+ applications
- 200+ active developers

### Year 3 Targets
- 100,000+ entities
- 2,000,000+ relationships
- 500,000+ attestations
- 100+ applications
- 500+ active developers

---

## Key Principles

### 1. Relationships First
Every decision evaluated against: "Does this make relationships more useful?"

### 2. AT Protocol Deep
Build with AT Protocol's strengths, not against them. User ownership, federation, portability.

### 3. Quality Over Features
Better to have 10 features that work perfectly than 50 that work poorly.

### 4. Developer Love
Developers are our users. Make their lives easy, they'll build amazing things.

### 5. Multi-Chain Only When Ready
Don't dilute focus. When we nail relationships on AT Protocol, then consider expansion.

---

## Risk Mitigation

### Technical Risks
- **Performance:** Benchmark early, optimize continuously
- **Security:** Audit before production, bug bounties
- **Scalability:** Design for 10x growth from day one

### Adoption Risks
- **Network effects:** Focus on one killer app (FundRhiz)
- **Developer friction:** Obsess over DX
- **Competition:** Interoperability as moat

### Team Risks
- **Burnout:** Scope appropriately for 1-3 people
- **Focus:** Say no to distractions
- **Funding:** Seek grants, bootstrap, sustainable from day one

---

## Multi-Chain Decision Framework

**When to consider multi-chain:**

✅ **YES if:**
- 10,000+ monthly active users on AT Protocol
- Proven demand (users asking for specific chains)
- Technical limitations we can't solve on AT Protocol
- Funding secured ($500K+ for expansion)
- Team grown to 5+ people
- Product-market fit clearly validated

❌ **NO if:**
- Still building core relationship features
- Small team (1-3 people)
- AT Protocol serving users well
- No clear user demand
- Would dilute focus
- Financial sustainability uncertain

**Current Status:** Focus on AT Protocol. Revisit Q2 2028.

---

## Long-Term Vision

**3 Years:** Rhiz is the standard for relationships on AT Protocol

**Impact:**
- Every AT Protocol app uses Rhiz for relationships
- Warm introductions are automated and trust-based
- Professional networking is verifiable, not vanity metrics
- Users own their relationship data
- Trust is portable across services

**Success Looks Like:**
- "Rhiz" is synonymous with "relationships on AT Protocol"
- Developers say "we use Rhiz for trust"
- Users say "my Rhiz connections helped me"
- Academia studies Rhiz trust algorithms
- Industry adopts Rhiz as standard

---

## Next 90 Days (Q4 2025)

### Week 1-8: Attestation System
Execute `RHIZ_ATTESTATION_IMPLEMENTATION_PLAN.md`:
- Week 1-2: Foundation (types, DB, algorithm)
- Week 3-4: Integration (API, indexer)
- Week 5-6: SDK & UI
- Week 7-8: Testing & launch

### Week 9-12: Relationship Quality
- Structured context fields
- Relationship analytics
- Trust velocity calculations
- User feedback integration

**Goal:** Ship attestation system, start seeing real conviction scores on relationships.

---

**Roadmap Version:** 1.0  
**Date:** October 22, 2025  
**Status:** Active Development  
**Focus:** Relationships First, AT Protocol Deep

**We're building the relationship layer AT Protocol needs.**

