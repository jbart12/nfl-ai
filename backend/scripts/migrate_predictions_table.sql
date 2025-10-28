-- Expand predictions table for opportunities feed
-- Run this inside the Docker postgres container

ALTER TABLE predictions ADD COLUMN IF NOT EXISTS player_name VARCHAR;
ALTER TABLE predictions ADD COLUMN IF NOT EXISTS player_position VARCHAR;
ALTER TABLE predictions ADD COLUMN IF NOT EXISTS team VARCHAR;
ALTER TABLE predictions ADD COLUMN IF NOT EXISTS opponent VARCHAR;
ALTER TABLE predictions ADD COLUMN IF NOT EXISTS week INTEGER;
ALTER TABLE predictions ADD COLUMN IF NOT EXISTS season INTEGER DEFAULT 2025;
ALTER TABLE predictions ADD COLUMN IF NOT EXISTS game_time TIMESTAMP;
ALTER TABLE predictions ADD COLUMN IF NOT EXISTS stat_type VARCHAR;
ALTER TABLE predictions ADD COLUMN IF NOT EXISTS line_score FLOAT;
ALTER TABLE predictions ADD COLUMN IF NOT EXISTS edge FLOAT;
ALTER TABLE predictions ADD COLUMN IF NOT EXISTS key_factors TEXT;
ALTER TABLE predictions ADD COLUMN IF NOT EXISTS risk_factors TEXT;
ALTER TABLE predictions ADD COLUMN IF NOT EXISTS comparable_game VARCHAR;
ALTER TABLE predictions ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE predictions ADD COLUMN IF NOT EXISTS is_archived BOOLEAN DEFAULT FALSE;
ALTER TABLE predictions ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();

-- Create indexes for common query patterns
CREATE INDEX IF NOT EXISTS ix_predictions_player_name ON predictions(player_name);
CREATE INDEX IF NOT EXISTS ix_predictions_player_position ON predictions(player_position);
CREATE INDEX IF NOT EXISTS ix_predictions_week ON predictions(week);
CREATE INDEX IF NOT EXISTS ix_predictions_game_time ON predictions(game_time);
CREATE INDEX IF NOT EXISTS ix_predictions_stat_type ON predictions(stat_type);
CREATE INDEX IF NOT EXISTS ix_predictions_confidence ON predictions(confidence);
CREATE INDEX IF NOT EXISTS ix_predictions_is_active ON predictions(is_active);
CREATE INDEX IF NOT EXISTS ix_predictions_created_at ON predictions(created_at);
CREATE INDEX IF NOT EXISTS ix_predictions_player_id ON predictions(player_id);
