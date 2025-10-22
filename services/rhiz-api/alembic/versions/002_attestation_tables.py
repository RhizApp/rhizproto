"""Add attestation and conviction tables

Revision ID: 002_attestation_tables
Revises: 001_did_migration
Create Date: 2025-10-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_attestation_tables'
down_revision = '001_did_migration'
branch_labels = None
depends_on = None


def upgrade():
    # Attestations table
    op.create_table(
        'attestations',
        sa.Column('uri', sa.Text(), primary_key=True),
        sa.Column('attester_did', sa.Text(), nullable=False),
        sa.Column('target_uri', sa.Text(), nullable=False),
        sa.Column('attestation_type', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Integer(), nullable=False),
        sa.Column('evidence', sa.Text(), nullable=True),
        sa.Column('suggested_strength', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('indexed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('cid', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['attester_did'], ['entities.did'], ondelete='CASCADE'),
    )
    
    # Indexes for fast queries
    op.create_index('idx_attestations_target', 'attestations', ['target_uri'])
    op.create_index('idx_attestations_attester', 'attestations', ['attester_did'])
    op.create_index('idx_attestations_type', 'attestations', ['attestation_type'])
    op.create_index('idx_attestations_created', 'attestations', ['created_at'])
    
    # Conviction scores cache table
    op.create_table(
        'conviction_scores',
        sa.Column('target_uri', sa.Text(), primary_key=True),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('attestation_count', sa.Integer(), nullable=False),
        sa.Column('verify_count', sa.Integer(), nullable=False),
        sa.Column('dispute_count', sa.Integer(), nullable=False),
        sa.Column('strengthen_count', sa.Integer(), nullable=False),
        sa.Column('weaken_count', sa.Integer(), nullable=False),
        sa.Column('last_updated', sa.DateTime(timezone=True), nullable=False),
        sa.Column('trend', sa.Text(), nullable=True),
        sa.Column('top_attester_reputation', sa.Integer(), nullable=True),
    )
    
    op.create_index('idx_conviction_score', 'conviction_scores', ['score'])
    op.create_index('idx_conviction_updated', 'conviction_scores', ['last_updated'])
    
    # Add conviction columns to relationships table
    op.add_column('relationships', sa.Column('conviction_score', sa.Integer(), nullable=True))
    op.add_column('relationships', sa.Column('attestation_count', sa.Integer(), server_default='0'))
    
    op.create_index('idx_relationships_conviction', 'relationships', ['conviction_score'])


def downgrade():
    op.drop_index('idx_relationships_conviction')
    op.drop_column('relationships', 'attestation_count')
    op.drop_column('relationships', 'conviction_score')
    
    op.drop_index('idx_conviction_updated')
    op.drop_index('idx_conviction_score')
    op.drop_table('conviction_scores')
    
    op.drop_index('idx_attestations_created')
    op.drop_index('idx_attestations_type')
    op.drop_index('idx_attestations_attester')
    op.drop_index('idx_attestations_target')
    op.drop_table('attestations')

