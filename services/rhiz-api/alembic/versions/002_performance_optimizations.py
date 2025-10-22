"""Performance optimizations and indexing

Revision ID: 002_performance_optimizations
Revises: 001_did_migration
Create Date: 2025-10-22 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_performance_optimizations'
down_revision = '001_did_migration'
branch_labels = None
depends_on = None


def upgrade():
    """Add performance optimizations"""
    
    # Create composite indexes for graph queries
    op.create_index(
        'idx_relationships_graph_query',
        'relationships',
        ['entity_a_id', 'entity_b_id', 'strength'],
        postgresql_where=sa.text('strength >= 30'),
        postgresql_concurrently=True
    )
    
    op.create_index(
        'idx_relationships_entity_strength',
        'relationships',
        ['entity_a_id', 'strength'],
        postgresql_concurrently=True
    )
    
    op.create_index(
        'idx_relationships_entity_b_strength',
        'relationships',
        ['entity_b_id', 'strength'],
        postgresql_concurrently=True
    )
    
    # Index for temporal queries (last_interaction)
    op.create_index(
        'idx_relationships_last_interaction',
        'relationships',
        ['last_interaction'],
        postgresql_concurrently=True
    )
    
    # Index for trust metrics queries
    op.create_index(
        'idx_trust_metrics_entity_score',
        'trust_metrics',
        ['entity_id', 'trust_score'],
        postgresql_concurrently=True
    )
    
    op.create_index(
        'idx_trust_metrics_calculated_at',
        'trust_metrics',
        ['last_calculated'],
        postgresql_concurrently=True
    )
    
    # Partial index for high-trust relationships
    op.create_index(
        'idx_relationships_high_trust',
        'relationships',
        ['entity_a_id', 'entity_b_id'],
        postgresql_where=sa.text('strength >= 70 AND consensus_score >= 0.8'),
        postgresql_concurrently=True
    )
    
    # Create relationship_contexts table for semantic search
    op.create_table(
        'relationship_contexts',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('relationship_id', sa.String(), sa.ForeignKey('relationships.id'), nullable=False),
        sa.Column('relationship_uri', sa.String(), nullable=True),
        sa.Column('domain', sa.String(50), nullable=False),
        sa.Column('expertise', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('collaboration_type', sa.String(50), nullable=False),
        sa.Column('semantic_tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('embedding', postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column('project_names', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('geographic_scope', sa.String(20), nullable=True),
        sa.Column('confidence_score', sa.Integer(), nullable=False, default=85),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    
    # Indexes for relationship_contexts
    op.create_index(
        'idx_contexts_relationship_id',
        'relationship_contexts',
        ['relationship_id'],
        unique=True
    )
    
    op.create_index(
        'idx_contexts_domain',
        'relationship_contexts',
        ['domain']
    )
    
    op.create_index(
        'idx_contexts_collaboration_type',
        'relationship_contexts',
        ['collaboration_type']
    )
    
    # GIN index for array columns (expertise, semantic_tags)
    op.create_index(
        'idx_contexts_expertise_gin',
        'relationship_contexts',
        ['expertise'],
        postgresql_using='gin'
    )
    
    op.create_index(
        'idx_contexts_semantic_tags_gin',
        'relationship_contexts',
        ['semantic_tags'],
        postgresql_using='gin'
    )
    
    # Partition trust_metrics by calculation date for better performance
    op.execute("""
        -- Create partitioned table for trust_metrics
        CREATE TABLE trust_metrics_partitioned (
            LIKE trust_metrics INCLUDING ALL
        ) PARTITION BY RANGE (last_calculated);
        
        -- Create partitions for current and future years
        CREATE TABLE trust_metrics_2024 PARTITION OF trust_metrics_partitioned
        FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
        
        CREATE TABLE trust_metrics_2025 PARTITION OF trust_metrics_partitioned
        FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
        
        CREATE TABLE trust_metrics_2026 PARTITION OF trust_metrics_partitioned
        FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
        
        -- Create default partition for future data
        CREATE TABLE trust_metrics_default PARTITION OF trust_metrics_partitioned
        DEFAULT;
    """)
    
    # Create materialized view for frequently accessed graph statistics
    op.execute("""
        CREATE MATERIALIZED VIEW graph_statistics AS
        SELECT 
            COUNT(*) as total_relationships,
            COUNT(DISTINCT entity_a_id) + COUNT(DISTINCT entity_b_id) as total_entities,
            AVG(strength) as avg_strength,
            AVG(consensus_score) as avg_consensus,
            COUNT(*) FILTER (WHERE strength >= 70) as high_trust_relationships,
            COUNT(*) FILTER (WHERE last_interaction >= NOW() - INTERVAL '30 days') as recent_relationships
        FROM relationships
        WHERE strength >= 30;
        
        -- Index on materialized view
        CREATE UNIQUE INDEX idx_graph_statistics_refresh
        ON graph_statistics ((1));
    """)
    
    # Create function to refresh materialized view
    op.execute("""
        CREATE OR REPLACE FUNCTION refresh_graph_statistics()
        RETURNS void AS $$
        BEGIN
            REFRESH MATERIALIZED VIEW CONCURRENTLY graph_statistics;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Add pgvector extension if available (for vector similarity search)
    try:
        op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Convert embedding column to vector type for better performance
        op.execute("""
            ALTER TABLE relationship_contexts 
            ALTER COLUMN embedding TYPE vector(384) 
            USING embedding::vector(384);
        """)
        
        # Create vector similarity index
        op.create_index(
            'idx_contexts_embedding_cosine',
            'relationship_contexts',
            ['embedding'],
            postgresql_using='ivfflat',
            postgresql_with={'lists': 100},
            postgresql_ops={'embedding': 'vector_cosine_ops'}
        )
        
    except Exception as e:
        # pgvector not available, keep as array
        print(f"pgvector not available: {e}")
        pass


def downgrade():
    """Remove performance optimizations"""
    
    # Drop indexes
    indexes_to_drop = [
        'idx_relationships_graph_query',
        'idx_relationships_entity_strength',
        'idx_relationships_entity_b_strength',
        'idx_relationships_last_interaction',
        'idx_trust_metrics_entity_score',
        'idx_trust_metrics_calculated_at',
        'idx_relationships_high_trust',
        'idx_contexts_relationship_id',
        'idx_contexts_domain',
        'idx_contexts_collaboration_type',
        'idx_contexts_expertise_gin',
        'idx_contexts_semantic_tags_gin',
    ]
    
    for index_name in indexes_to_drop:
        try:
            op.drop_index(index_name)
        except Exception:
            pass
    
    # Drop vector index if exists
    try:
        op.drop_index('idx_contexts_embedding_cosine')
    except Exception:
        pass
    
    # Drop materialized view and function
    op.execute("DROP FUNCTION IF EXISTS refresh_graph_statistics();")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS graph_statistics;")
    
    # Drop partitioned table
    op.execute("DROP TABLE IF EXISTS trust_metrics_partitioned CASCADE;")
    
    # Drop relationship_contexts table
    op.drop_table('relationship_contexts')