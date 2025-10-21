"""
Seed database with demo data for local development
"""

import asyncio
from datetime import datetime

from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal, init_db
from app.models.entity import Entity, EntityType
from app.models.relationship import (
    ConsentLevel,
    Relationship,
    RelationshipType,
    Visibility,
)
from app.models.trust_metrics import TrustMetrics


async def seed_demo_data() -> None:
    """Seed database with demo entities and relationships"""
    print("🌱 Seeding demo data...")

    # Initialize database
    await init_db()

    async with AsyncSessionLocal() as session:
        # Check if data already exists
        result = await session.execute(select(Entity).limit(1))
        if result.scalar_one_or_none():
            print("⚠️  Data already exists. Skipping seed.")
            return

        # Create demo entities
        entities = [
            Entity(
                id="alice_founder",
                type=EntityType.PERSON,
                name="Alice Chen",
                bio="Founder & CEO of StartupX. Building AI-powered logistics.",
                verified=True,
                did="did:plc:alice123",
                handle="alice.startup.com",
            ),
            Entity(
                id="bob_investor",
                type=EntityType.PERSON,
                name="Bob Wilson",
                bio="Partner at VentureY. Focused on B2B SaaS.",
                verified=True,
                did="did:plc:bob456",
                handle="bob.venture.com",
            ),
            Entity(
                id="carol_connector",
                type=EntityType.PERSON,
                name="Carol Martinez",
                bio="Head of Partnerships at TechCorp. Connector extraordinaire.",
                verified=True,
            ),
            Entity(
                id="dave_investor",
                type=EntityType.PERSON,
                name="Dave Kumar",
                bio="Angel investor. 50+ investments in early-stage startups.",
                verified=True,
            ),
            Entity(
                id="eve_founder",
                type=EntityType.PERSON,
                name="Eve Thompson",
                bio="Co-founder of ProductZ. Previously exited to BigCo.",
                verified=True,
            ),
        ]

        for entity in entities:
            session.add(entity)

        await session.flush()
        print(f"✅ Created {len(entities)} demo entities")

        # Create relationships
        relationships = [
            # Alice knows Carol (former colleagues)
            Relationship(
                id="rel_alice_carol",
                entity_a_id="alice_founder",
                entity_b_id="carol_connector",
                type=RelationshipType.PROFESSIONAL,
                strength=0.85,
                context="Former colleagues at TechCorp. Worked together for 3 years.",
                consensus_score=0.9,
                verifier_count=3,
                confidence=0.92,
                last_verified=datetime.utcnow(),
                visibility=Visibility.NETWORK,
                consent=ConsentLevel.FULL,
                start_date=datetime(2020, 1, 1),
                last_interaction=datetime.utcnow(),
                history=[],
                contributors=["alice_founder", "carol_connector"],
                version="0.1.0",
            ),
            # Carol knows Bob (investment network)
            Relationship(
                id="rel_carol_bob",
                entity_a_id="carol_connector",
                entity_b_id="bob_investor",
                type=RelationshipType.PROFESSIONAL,
                strength=0.75,
                context="Connected through investment network. Regular coffee meetings.",
                consensus_score=0.85,
                verifier_count=2,
                confidence=0.88,
                last_verified=datetime.utcnow(),
                visibility=Visibility.NETWORK,
                consent=ConsentLevel.FULL,
                start_date=datetime(2021, 6, 1),
                last_interaction=datetime.utcnow(),
                history=[],
                contributors=["carol_connector", "bob_investor"],
                version="0.1.0",
            ),
            # Eve knows Dave (co-investors)
            Relationship(
                id="rel_eve_dave",
                entity_a_id="eve_founder",
                entity_b_id="dave_investor",
                type=RelationshipType.PROFESSIONAL,
                strength=0.90,
                context="Dave was Eve's first investor. Still advises actively.",
                consensus_score=0.95,
                verifier_count=5,
                confidence=0.97,
                last_verified=datetime.utcnow(),
                visibility=Visibility.NETWORK,
                consent=ConsentLevel.FULL,
                start_date=datetime(2018, 3, 1),
                last_interaction=datetime.utcnow(),
                history=[],
                contributors=["eve_founder", "dave_investor"],
                version="0.1.0",
            ),
            # Carol knows Eve (founder community)
            Relationship(
                id="rel_carol_eve",
                entity_a_id="carol_connector",
                entity_b_id="eve_founder",
                type=RelationshipType.PROFESSIONAL,
                strength=0.70,
                context="Met through founder community events. Occasional advisor.",
                consensus_score=0.80,
                verifier_count=2,
                confidence=0.83,
                last_verified=datetime.utcnow(),
                visibility=Visibility.NETWORK,
                consent=ConsentLevel.LIMITED,
                start_date=datetime(2022, 1, 1),
                last_interaction=datetime.utcnow(),
                history=[],
                contributors=["carol_connector", "eve_founder"],
                version="0.1.0",
            ),
        ]

        for relationship in relationships:
            session.add(relationship)

        await session.flush()
        print(f"✅ Created {len(relationships)} demo relationships")

        # Create trust metrics
        trust_metrics = [
            TrustMetrics(
                entity_id="alice_founder",
                trust_score=0.82,
                reputation=0.85,
                reciprocity=0.80,
                consistency=0.78,
                relationship_count=1,
                verified_relationship_count=1,
                last_calculated=datetime.utcnow(),
            ),
            TrustMetrics(
                entity_id="bob_investor",
                trust_score=0.88,
                reputation=0.90,
                reciprocity=0.85,
                consistency=0.90,
                relationship_count=1,
                verified_relationship_count=1,
                last_calculated=datetime.utcnow(),
            ),
            TrustMetrics(
                entity_id="carol_connector",
                trust_score=0.91,
                reputation=0.92,
                reciprocity=0.90,
                consistency=0.91,
                relationship_count=3,
                verified_relationship_count=3,
                last_calculated=datetime.utcnow(),
            ),
        ]

        for metrics in trust_metrics:
            session.add(metrics)

        await session.commit()
        print(f"✅ Created {len(trust_metrics)} trust metric records")

        print("\n🎉 Demo data seeded successfully!")
        print("\n📊 Summary:")
        print(f"  - Entities: {len(entities)}")
        print(f"  - Relationships: {len(relationships)}")
        print(f"  - Trust Metrics: {len(trust_metrics)}")
        print("\n💡 Example: Alice can reach Bob through Carol")


if __name__ == "__main__":
    asyncio.run(seed_demo_data())

