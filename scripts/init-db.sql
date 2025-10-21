-- Initialize Rhiz database with pgvector extension
-- This script runs automatically on first container start

CREATE EXTENSION IF NOT EXISTS vector;

-- Create test database if not exists
SELECT 'CREATE DATABASE rhiz_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'rhiz_test')\gexec

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE rhiz TO rhiz;
GRANT ALL PRIVILEGES ON DATABASE rhiz_test TO rhiz;

