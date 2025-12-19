-- Neon Serverless Postgres Schema for RAG Chatbot
-- Created: 2025-12-17
-- Purpose: Store query logs and ingestion metadata

-- Drop existing tables if they exist (for development)
DROP TABLE IF EXISTS query_logs CASCADE;
DROP TABLE IF EXISTS ingestion_logs CASCADE;

-- Create query_logs table
CREATE TABLE query_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    query_text TEXT NOT NULL,
    query_mode VARCHAR(20) NOT NULL CHECK (query_mode IN ('full_book', 'selected_text')),
    selected_text TEXT,
    answer_text TEXT NOT NULL,
    source_chunks JSONB NOT NULL DEFAULT '[]'::jsonb,
    response_time_ms INTEGER NOT NULL CHECK (response_time_ms >= 0),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for query_logs
CREATE INDEX idx_query_logs_session ON query_logs(session_id);
CREATE INDEX idx_query_logs_created ON query_logs(created_at DESC);
CREATE INDEX idx_query_logs_mode ON query_logs(query_mode);

-- Create ingestion_logs table
CREATE TABLE ingestion_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    status VARCHAR(20) NOT NULL CHECK (status IN ('running', 'completed', 'failed')),
    total_chunks INTEGER CHECK (total_chunks >= 0),
    total_files INTEGER CHECK (total_files >= 0),
    error_message TEXT,
    metadata JSONB,
    CONSTRAINT check_completed_after_started CHECK (completed_at IS NULL OR completed_at >= started_at)
);

-- Create indexes for ingestion_logs
CREATE INDEX idx_ingestion_logs_status ON ingestion_logs(status);
CREATE INDEX idx_ingestion_logs_started ON ingestion_logs(started_at DESC);

-- Grant permissions (adjust username as needed)
-- GRANT ALL PRIVILEGES ON TABLE query_logs TO your_user;
-- GRANT ALL PRIVILEGES ON TABLE ingestion_logs TO your_user;

-- Add comments for documentation
COMMENT ON TABLE query_logs IS 'Stores all chatbot queries and responses for monitoring and analysis';
COMMENT ON TABLE ingestion_logs IS 'Tracks document ingestion pipeline executions';

COMMENT ON COLUMN query_logs.source_chunks IS 'JSONB array of source citations: [{chapter, section, file, url, similarity_score}]';
COMMENT ON COLUMN query_logs.query_mode IS 'Query mode: full_book (vector search) or selected_text (direct context)';
COMMENT ON COLUMN ingestion_logs.metadata IS 'JSONB object with ingestion parameters: {chunk_size, overlap, model, etc}';
