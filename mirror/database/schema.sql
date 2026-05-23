-- MIRROR Database Schema
-- SQLite 3 — auto-created on first run

-- Leads database
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fb_id TEXT UNIQUE NOT NULL,
    name TEXT,
    profile_url TEXT,
    group_name TEXT,
    post_content TEXT,
    post_url TEXT,
    detected_keywords TEXT,
    budget_range TEXT,
    urgency TEXT,
    pain_points TEXT,
    personality_type TEXT,
    preferred_tone TEXT,
    active_hours TEXT,
    engagement_style TEXT,
    risk_factors TEXT,
    sentiment TEXT,
    hotness_score INTEGER DEFAULT 0,
    status TEXT DEFAULT 'new',
    archaeology_report TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversations database
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    direction TEXT CHECK(direction IN ('outgoing', 'incoming')),
    channel TEXT CHECK(channel IN ('comment', 'dm', 'group_post')),
    template_used TEXT,
    response_id TEXT,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);

CREATE TABLE IF NOT EXISTS nurture_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER NOT NULL,
    step INTEGER NOT NULL,
    action_type TEXT,
    scheduled_for TIMESTAMP,
    executed_at TIMESTAMP,
    status TEXT DEFAULT 'pending',
    notes TEXT,
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);

-- Competitor intel database
CREATE TABLE IF NOT EXISTS competitors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    fb_profile_url TEXT,
    detected_in_group TEXT,
    pitch_pattern TEXT,
    mentioned_price REAL,
    weakness TEXT,
    activity_frequency TEXT,
    last_active TIMESTAMP,
    first_detected TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS competitor_mentions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    competitor_id INTEGER NOT NULL,
    group_name TEXT,
    post_content TEXT,
    sentiment TEXT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (competitor_id) REFERENCES competitors(id)
);

-- Logs database
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module TEXT NOT NULL,
    action TEXT NOT NULL,
    status TEXT CHECK(status IN ('success', 'failure', 'warning', 'info')),
    detail TEXT,
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS api_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL,
    endpoint TEXT,
    tokens_used INTEGER,
    latency_ms INTEGER,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module TEXT NOT NULL,
    error_type TEXT,
    error_message TEXT,
    traceback TEXT,
    recovered BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_hotness ON leads(hotness_score);
CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at);
CREATE INDEX IF NOT EXISTS idx_conversations_lead ON conversations(lead_id);
CREATE INDEX IF NOT EXISTS idx_nurture_lead ON nurture_actions(lead_id);
CREATE INDEX IF NOT EXISTS idx_nurture_status ON nurture_actions(status);
CREATE INDEX IF NOT EXISTS idx_logs_module ON activity_logs(module);
CREATE INDEX IF NOT EXISTS idx_logs_created ON activity_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_api_provider ON api_usage(provider);
CREATE INDEX IF NOT EXISTS idx_errors_module ON errors(module);
