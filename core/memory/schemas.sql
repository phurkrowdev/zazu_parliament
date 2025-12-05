-- Zazu Memory Architecture Schema
-- Postgres with pgvector extension

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- EPISODIC MEMORY: Event log for all subsystem activities
-- ============================================================================

CREATE TABLE IF NOT EXISTS episodic_memory (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    subsystem_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    mode VARCHAR(20),
    context JSONB NOT NULL,
    related_event_id BIGINT REFERENCES episodic_memory(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_episodic_timestamp ON episodic_memory(timestamp DESC);
CREATE INDEX idx_episodic_subsystem ON episodic_memory(subsystem_id);
CREATE INDEX idx_episodic_event_type ON episodic_memory(event_type);
CREATE INDEX idx_episodic_context_gin ON episodic_memory USING GIN(context);

COMMENT ON TABLE episodic_memory IS 'Complete event log of all subsystem activities for temporal continuity';

-- ============================================================================
-- SEMANTIC MEMORY: Knowledge graph with vector embeddings
-- ============================================================================

CREATE TABLE IF NOT EXISTS semantic_memory (
    id BIGSERIAL PRIMARY KEY,
    node_id VARCHAR(255) UNIQUE NOT NULL,
    node_type VARCHAR(100) NOT NULL,
    properties JSONB NOT NULL DEFAULT '{}',
    embedding vector(384),  -- all-MiniLM-L6-v2 produces 384-dim vectors
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_semantic_node_type ON semantic_memory(node_type);
CREATE INDEX idx_semantic_embedding_hnsw ON semantic_memory USING hnsw(embedding vector_cosine_ops);
CREATE INDEX idx_semantic_properties_gin ON semantic_memory USING GIN(properties);

COMMENT ON TABLE semantic_memory IS 'Knowledge graph with vector similarity search for semantic reasoning';

-- ============================================================================
-- MISSION MEMORY: Hierarchical mission log for long-arc coherence
-- ============================================================================

CREATE TABLE IF NOT EXISTS mission_memory (
    id BIGSERIAL PRIMARY KEY,
    phase_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    mission_statement TEXT NOT NULL,
    coherence_score NUMERIC(3,2) CHECK (coherence_score >= 0 AND coherence_score <= 1),
    horizon VARCHAR(20) NOT NULL CHECK (horizon IN ('immediate', 'seasonal', 'epochal')),
    parent_mission_id BIGINT REFERENCES mission_memory(id),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_mission_phase ON mission_memory(phase_timestamp DESC);
CREATE INDEX idx_mission_parent ON mission_memory(parent_mission_id);
CREATE INDEX idx_mission_horizon ON mission_memory(horizon);

COMMENT ON TABLE mission_memory IS 'Hierarchical mission log tracking purpose evolution across time horizons';

-- Recursive query helper for mission ancestry
COMMENT ON COLUMN mission_memory.parent_mission_id IS 'Self-referencing FK for mission hierarchy traversal via CTE';

-- ============================================================================
-- CONSTITUTIONAL VIOLATION LOG: Audit trail for integrity monitoring
-- ============================================================================

CREATE TABLE IF NOT EXISTS constitutional_violations (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    subsystem_id VARCHAR(50) NOT NULL,
    violation_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('minor', 'major', 'critical')),
    description TEXT NOT NULL,
    context JSONB,
    resolution_status VARCHAR(50) DEFAULT 'pending' CHECK (resolution_status IN ('pending', 'auto_resolved', 'escalated', 'user_override')),
    resolution_timestamp TIMESTAMPTZ,
    related_event_id BIGINT REFERENCES episodic_memory(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_violations_timestamp ON constitutional_violations(timestamp DESC);
CREATE INDEX idx_violations_subsystem ON constitutional_violations(subsystem_id);
CREATE INDEX idx_violations_severity ON constitutional_violations(severity);
CREATE INDEX idx_violations_status ON constitutional_violations(resolution_status);

COMMENT ON TABLE constitutional_violations IS 'Audit trail for constitutional integrity violations';

-- ============================================================================
-- HALT EVENTS: Sentinel halt protocol tracking
-- ============================================================================

CREATE TABLE IF NOT EXISTS halt_events (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    halted_subsystem VARCHAR(50) NOT NULL,
    halt_reason VARCHAR(255) NOT NULL,
    repair_cycle_count INT DEFAULT 0,
    resolution VARCHAR(50) CHECK (resolution IN ('approved', 'rejected', 'escalated', 'timeout')),
    related_event_id BIGINT REFERENCES episodic_memory(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

CREATE INDEX idx_halt_timestamp ON halt_events(timestamp DESC);
CREATE INDEX idx_halt_subsystem ON halt_events(halted_subsystem);
CREATE INDEX idx_halt_resolution ON halt_events(resolution);

COMMENT ON TABLE halt_events IS 'Sentinel halt protocol tracking for anti-paralysis calibration';

-- ============================================================================
-- CALIBRATION HISTORY: Anti-paralysis and bias correction tracking
-- ============================================================================

CREATE TABLE IF NOT EXISTS calibration_history (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    subsystem_id VARCHAR(50) NOT NULL,
    calibration_type VARCHAR(100) NOT NULL,
    previous_threshold NUMERIC,
    new_threshold NUMERIC,
    trigger_reason TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_calibration_timestamp ON calibration_history(timestamp DESC);
CREATE INDEX idx_calibration_subsystem ON calibration_history(subsystem_id);
CREATE INDEX idx_calibration_type ON calibration_history(calibration_type);

COMMENT ON TABLE calibration_history IS 'Historical record of subsystem calibration adjustments';

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to retrieve mission ancestry
CREATE OR REPLACE FUNCTION get_mission_ancestry(target_mission_id BIGINT)
RETURNS TABLE (
    id BIGINT,
    mission_statement TEXT,
    coherence_score NUMERIC,
    horizon VARCHAR,
    depth INT
) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE ancestry AS (
        SELECT 
            m.id,
            m.mission_statement,
            m.coherence_score,
            m.horizon,
            m.parent_mission_id,
            0 AS depth
        FROM mission_memory m
        WHERE m.id = target_mission_id
        
        UNION ALL
        
        SELECT 
            m.id,
            m.mission_statement,
            m.coherence_score,
            m.horizon,
            m.parent_mission_id,
            a.depth + 1
        FROM mission_memory m
        INNER JOIN ancestry a ON m.id = a.parent_mission_id
    )
    SELECT id, mission_statement, coherence_score, horizon, depth
    FROM ancestry
    ORDER BY depth;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate halt rate for anti-paralysis
CREATE OR REPLACE FUNCTION calculate_halt_rate(lookback_window INT DEFAULT 100)
RETURNS NUMERIC AS $$
DECLARE
    total_events INT;
    halt_count INT;
BEGIN
    SELECT COUNT(*) INTO total_events
    FROM episodic_memory
    WHERE subsystem_id = 'sentinel'
    ORDER BY timestamp DESC
    LIMIT lookback_window;
    
    SELECT COUNT(*) INTO halt_count
    FROM halt_events
    ORDER BY timestamp DESC
    LIMIT lookback_window;
    
    IF total_events = 0 THEN
        RETURN 0;
    END IF;
    
    RETURN ROUND(halt_count::NUMERIC / total_events::NUMERIC, 2);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_halt_rate IS 'Calculates Sentinel halt rate for anti-paralysis threshold monitoring';

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert foundational mission (epochal horizon)
INSERT INTO mission_memory (mission_statement, coherence_score, horizon, metadata)
VALUES (
    'Amplify ordered intelligence in service of creative power, strategic clarity, and ethical alignment without overstepping agency or autonomy.',
    1.0,
    'epochal',
    '{"source": "constitution_kernel", "immutable": true}'
);
