"""Add DID as primary key for entities

Revision ID: 001_did_migration
Revises:
Create Date: 2025-10-21

This migration transforms the entities table to use DIDs as primary keys
following AT Protocol best practices.

Migration steps:
1. Add did column (nullable initially)
2. Add profile_uri and profile_cid columns for AT Protocol records
3. Backfill DIDs for existing entities
4. Make did primary key and drop old id column
5. Update foreign key references
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_did_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema to DID-native"""

    # Step 1: Add new DID-related columns to entities table
    # Make them nullable initially to allow data migration
    op.add_column(
        'entities',
        sa.Column('did_new', sa.String(length=255), nullable=True)
    )
    op.add_column(
        'entities',
        sa.Column('profile_uri', sa.String(length=500), nullable=True)
    )
    op.add_column(
        'entities',
        sa.Column('profile_cid', sa.String(length=255), nullable=True)
    )

    # Step 2: For existing entities, generate placeholder DIDs
    # In production, this should be replaced with actual DID creation
    # or manual mapping of existing entities to their DIDs
    op.execute("""
        UPDATE entities
        SET did_new = 'did:plc:' || LOWER(
            SUBSTRING(MD5(id::text) FROM 1 FOR 32)
        )
        WHERE did IS NULL OR did = ''
    """)

    # Copy existing did values to did_new if they exist
    op.execute("""
        UPDATE entities
        SET did_new = did
        WHERE did IS NOT NULL AND did != ''
    """)

    # Step 3: Add indexes and constraints to did_new
    op.create_index('ix_entities_did_new', 'entities', ['did_new'])
    op.create_unique_constraint('uq_entities_did_new', 'entities', ['did_new'])

    # Step 4: Make did_new not nullable now that data is migrated
    op.alter_column('entities', 'did_new', nullable=False)

    # Step 5: Drop old did column and rename did_new to did
    op.drop_index('ix_entities_did', table_name='entities')
    op.drop_column('entities', 'did')
    op.alter_column('entities', 'did_new', new_column_name='did')

    # Step 6: Update trust_metrics table to reference DIDs
    # Add new entity_did column
    op.add_column(
        'trust_metrics',
        sa.Column('entity_did_new', sa.String(length=255), nullable=True)
    )

    # Migrate trust_metrics foreign key references
    op.execute("""
        UPDATE trust_metrics tm
        SET entity_did_new = e.did
        FROM entities e
        WHERE tm.entity_id = e.id
    """)

    # Make entity_did_new not nullable and create foreign key
    op.alter_column('trust_metrics', 'entity_did_new', nullable=False)
    op.create_foreign_key(
        'fk_trust_metrics_entity_did',
        'trust_metrics',
        'entities',
        ['entity_did_new'],
        ['did'],
        ondelete='CASCADE'
    )

    # Create index on new foreign key
    op.create_index(
        'ix_trust_metrics_entity_did_new',
        'trust_metrics',
        ['entity_did_new']
    )

    # Drop old foreign key and column
    op.drop_constraint(
        'trust_metrics_entity_id_fkey',
        'trust_metrics',
        type_='foreignkey'
    )
    op.drop_column('trust_metrics', 'entity_id')

    # Rename entity_did_new to entity_did
    op.alter_column('trust_metrics', 'entity_did_new', new_column_name='entity_did')

    # Step 7: Update relationships table to use DIDs
    # Add new DID columns and AT Protocol columns
    op.add_column(
        'relationships',
        sa.Column('participant_did_1_new', sa.String(length=255), nullable=True)
    )
    op.add_column(
        'relationships',
        sa.Column('participant_did_2_new', sa.String(length=255), nullable=True)
    )
    op.add_column(
        'relationships',
        sa.Column('at_uri', sa.String(length=500), nullable=True)
    )
    op.add_column(
        'relationships',
        sa.Column('cid', sa.String(length=255), nullable=True)
    )

    # Migrate relationship participant references
    op.execute("""
        UPDATE relationships r
        SET participant_did_1_new = e.did
        FROM entities e
        WHERE r.participant_1_id = e.id
    """)

    op.execute("""
        UPDATE relationships r
        SET participant_did_2_new = e.did
        FROM entities e
        WHERE r.participant_2_id = e.id
    """)

    # Make new columns not nullable
    op.alter_column('relationships', 'participant_did_1_new', nullable=False)
    op.alter_column('relationships', 'participant_did_2_new', nullable=False)

    # Create indexes and foreign keys
    op.create_index(
        'ix_relationships_participant_did_1_new',
        'relationships',
        ['participant_did_1_new']
    )
    op.create_index(
        'ix_relationships_participant_did_2_new',
        'relationships',
        ['participant_did_2_new']
    )

    op.create_foreign_key(
        'fk_relationships_participant_did_1',
        'relationships',
        'entities',
        ['participant_did_1_new'],
        ['did'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_relationships_participant_did_2',
        'relationships',
        'entities',
        ['participant_did_2_new'],
        ['did'],
        ondelete='CASCADE'
    )

    # Drop old columns and rename new ones
    op.drop_constraint(
        'relationships_participant_1_id_fkey',
        'relationships',
        type_='foreignkey'
    )
    op.drop_constraint(
        'relationships_participant_2_id_fkey',
        'relationships',
        type_='foreignkey'
    )
    op.drop_column('relationships', 'participant_1_id')
    op.drop_column('relationships', 'participant_2_id')

    op.alter_column(
        'relationships',
        'participant_did_1_new',
        new_column_name='participant_did_1'
    )
    op.alter_column(
        'relationships',
        'participant_did_2_new',
        new_column_name='participant_did_2'
    )

    # Step 8: Finally, make DID the primary key of entities table
    # This requires dropping the old primary key and creating a new one
    op.drop_constraint('entities_pkey', 'entities', type_='primary')
    op.drop_column('entities', 'id')
    op.create_primary_key('entities_pkey', 'entities', ['did'])


def downgrade() -> None:
    """Downgrade back to integer ID primary keys"""

    # Note: This is a lossy downgrade. AT Protocol URIs and CIDs will be lost.
    # This should only be used in development.

    # Add back id columns
    op.add_column(
        'entities',
        sa.Column('id', sa.String(length=255), nullable=True)
    )

    # Generate IDs from DIDs
    op.execute("""
        UPDATE entities
        SET id = 'entity_' || SUBSTRING(did FROM 9 FOR 10)
    """)

    op.alter_column('entities', 'id', nullable=False)

    # Recreate old structure (simplified)
    op.drop_constraint('entities_pkey', 'entities', type_='primary')
    op.create_primary_key('entities_pkey', 'entities', ['id'])

    # Drop AT Protocol columns
    op.drop_column('entities', 'profile_uri')
    op.drop_column('entities', 'profile_cid')

    # Note: Full downgrade would require reversing all relationship
    # and trust_metrics changes. This is left as an exercise.

