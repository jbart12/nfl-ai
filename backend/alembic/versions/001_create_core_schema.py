"""create core schema

Revision ID: 001
Revises:
Create Date: 2025-10-26

Core schema for NFL AI prediction system:
- Players (unified across platforms)
- Games
- Player Props (from PrizePicks)
- Player Stats History (historical performance tracking)
- Predictions (our predictions with confidence)
- Player Injuries (from Sleeper)
- Weather Data
- News Items
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
import uuid


# revision identifiers, used by Alembic
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Players table - unified player database
    op.create_table(
        'players',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('espn_id', sa.Integer, unique=True, nullable=True, index=True),
        sa.Column('sleeper_id', sa.String(50), unique=True, nullable=True, index=True),
        sa.Column('nfl_id', sa.Integer, nullable=True, index=True),
        sa.Column('gsis_id', sa.String(50), nullable=True, index=True),
        sa.Column('prizepicks_player_id', sa.String(50), nullable=True, index=True),
        sa.Column('prizepicks_name', sa.String(255), nullable=True, index=True),

        # Player info
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('position', sa.String(10), nullable=False, index=True),
        sa.Column('team', sa.String(10), nullable=True, index=True),
        sa.Column('jersey_number', sa.Integer, nullable=True),
        sa.Column('status', sa.String(50), default='Active'),  # Active, Inactive, IR, etc.

        # Physical attributes
        sa.Column('height', sa.Integer, nullable=True),  # inches
        sa.Column('weight', sa.Integer, nullable=True),  # pounds
        sa.Column('age', sa.Integer, nullable=True),
        sa.Column('birth_date', sa.Date, nullable=True),
        sa.Column('college', sa.String(255), nullable=True),
        sa.Column('years_exp', sa.Integer, nullable=True),

        # Metadata
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.Column('last_verified_at', sa.DateTime(timezone=True), nullable=True),

        sa.Index('idx_player_name', 'name'),
        sa.Index('idx_player_team_position', 'team', 'position'),
    )

    # Teams table
    op.create_table(
        'teams',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('abbreviation', sa.String(10), unique=True, nullable=False, index=True),
        sa.Column('espn_id', sa.Integer, unique=True, nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('city', sa.String(255), nullable=False),
        sa.Column('conference', sa.String(10), nullable=True),  # AFC, NFC
        sa.Column('division', sa.String(50), nullable=True),  # North, South, East, West
        sa.Column('stadium_name', sa.String(255), nullable=True),
        sa.Column('is_dome', sa.Boolean, default=False),
        sa.Column('stadium_lat', sa.Float, nullable=True),
        sa.Column('stadium_lon', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),
    )

    # Games table
    op.create_table(
        'games',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('espn_game_id', sa.String(50), unique=True, nullable=True, index=True),
        sa.Column('season', sa.Integer, nullable=False, index=True),
        sa.Column('week', sa.Integer, nullable=False, index=True),
        sa.Column('season_type', sa.String(20), default='REG'),  # PRE, REG, POST

        # Teams
        sa.Column('home_team_id', UUID(as_uuid=True), sa.ForeignKey('teams.id'), nullable=False),
        sa.Column('away_team_id', UUID(as_uuid=True), sa.ForeignKey('teams.id'), nullable=False),
        sa.Column('home_team_abbr', sa.String(10), nullable=False),
        sa.Column('away_team_abbr', sa.String(10), nullable=False),

        # Game info
        sa.Column('game_time', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('status', sa.String(50), default='scheduled'),  # scheduled, in_progress, final
        sa.Column('home_score', sa.Integer, nullable=True),
        sa.Column('away_score', sa.Integer, nullable=True),

        # Weather (for outdoor games)
        sa.Column('temperature', sa.Integer, nullable=True),  # Fahrenheit
        sa.Column('wind_speed', sa.Integer, nullable=True),  # mph
        sa.Column('wind_direction', sa.String(10), nullable=True),
        sa.Column('precipitation', sa.Boolean, default=False),
        sa.Column('weather_description', sa.String(255), nullable=True),
        sa.Column('is_dome', sa.Boolean, default=False),

        # Metadata
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),

        sa.Index('idx_game_season_week', 'season', 'week'),
        sa.Index('idx_game_time', 'game_time'),
    )

    # Player Props (from PrizePicks)
    op.create_table(
        'props',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('prizepicks_projection_id', sa.String(50), unique=True, nullable=True, index=True),
        sa.Column('player_id', UUID(as_uuid=True), sa.ForeignKey('players.id'), nullable=False, index=True),
        sa.Column('game_id', UUID(as_uuid=True), sa.ForeignKey('games.id'), nullable=True, index=True),

        # Prop details
        sa.Column('stat_type', sa.String(100), nullable=False, index=True),  # "Passing Yards", "Receiving Yards", etc.
        sa.Column('line_score', sa.Float, nullable=False),  # The over/under line
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('description', sa.String(500), nullable=True),

        # Status
        sa.Column('is_active', sa.Boolean, default=True, index=True),
        sa.Column('is_promo', sa.Boolean, default=False),
        sa.Column('removed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('removal_reason', sa.String(255), nullable=True),  # "game_started", "player_out", etc.

        # Metadata
        sa.Column('first_seen_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),

        sa.Index('idx_prop_stat_type', 'stat_type'),
        sa.Index('idx_prop_active', 'is_active'),
        sa.Index('idx_prop_player_stat', 'player_id', 'stat_type'),
    )

    # Player Game Stats (historical performance - KEY for trend analysis)
    op.create_table(
        'player_game_stats',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('player_id', UUID(as_uuid=True), sa.ForeignKey('players.id'), nullable=False, index=True),
        sa.Column('game_id', UUID(as_uuid=True), sa.ForeignKey('games.id'), nullable=False, index=True),

        # Game context
        sa.Column('season', sa.Integer, nullable=False, index=True),
        sa.Column('week', sa.Integer, nullable=False, index=True),
        sa.Column('opponent_team_abbr', sa.String(10), nullable=False, index=True),
        sa.Column('is_home', sa.Boolean, nullable=False),

        # Comprehensive stats (store all available)
        sa.Column('stats_json', JSONB, nullable=False),  # Full stats object from ESPN

        # Common stats (for quick queries without JSON parsing)
        sa.Column('passing_yards', sa.Integer, nullable=True),
        sa.Column('passing_tds', sa.Integer, nullable=True),
        sa.Column('passing_completions', sa.Integer, nullable=True),
        sa.Column('passing_attempts', sa.Integer, nullable=True),
        sa.Column('interceptions', sa.Integer, nullable=True),

        sa.Column('rushing_yards', sa.Integer, nullable=True),
        sa.Column('rushing_attempts', sa.Integer, nullable=True),
        sa.Column('rushing_tds', sa.Integer, nullable=True),

        sa.Column('receiving_yards', sa.Integer, nullable=True),
        sa.Column('receptions', sa.Integer, nullable=True),
        sa.Column('targets', sa.Integer, nullable=True),
        sa.Column('receiving_tds', sa.Integer, nullable=True),

        sa.Column('fantasy_points', sa.Float, nullable=True),

        # Context
        sa.Column('weather_temp', sa.Integer, nullable=True),
        sa.Column('weather_wind', sa.Integer, nullable=True),
        sa.Column('was_injured', sa.Boolean, default=False),
        sa.Column('injury_status_before_game', sa.String(50), nullable=True),

        # Metadata
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),

        sa.Index('idx_pgs_player_season', 'player_id', 'season'),
        sa.Index('idx_pgs_season_week', 'season', 'week'),
        sa.UniqueConstraint('player_id', 'game_id', name='uq_player_game'),
    )

    # Predictions (our AI predictions)
    op.create_table(
        'predictions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('prop_id', UUID(as_uuid=True), sa.ForeignKey('props.id'), nullable=False, index=True),
        sa.Column('player_id', UUID(as_uuid=True), sa.ForeignKey('players.id'), nullable=False, index=True),
        sa.Column('game_id', UUID(as_uuid=True), sa.ForeignKey('games.id'), nullable=True, index=True),

        # Prediction
        sa.Column('prediction', sa.String(10), nullable=False),  # "OVER", "UNDER", "SKIP"
        sa.Column('confidence_score', sa.Float, nullable=False, index=True),  # 0-100
        sa.Column('predicted_value', sa.Float, nullable=True),  # Our predicted actual value
        sa.Column('line_score', sa.Float, nullable=False),  # Line at time of prediction
        sa.Column('stat_type', sa.String(100), nullable=False),

        # Reasoning
        sa.Column('reasoning_narrative', sa.Text, nullable=False),  # Full narrative
        sa.Column('reasoning_summary', sa.String(500), nullable=True),  # Short summary
        sa.Column('key_factors', JSONB, nullable=True),  # Array of key factors

        # RAG context
        sa.Column('similar_situations_count', sa.Integer, default=0),
        sa.Column('similar_situations_data', JSONB, nullable=True),

        # Results (filled in after game)
        sa.Column('actual_value', sa.Float, nullable=True),
        sa.Column('was_correct', sa.Boolean, nullable=True, index=True),
        sa.Column('result_margin', sa.Float, nullable=True),  # How much over/under the line

        # Metadata
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), index=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.Column('result_updated_at', sa.DateTime(timezone=True), nullable=True),

        sa.Index('idx_pred_confidence', 'confidence_score'),
        sa.Index('idx_pred_was_correct', 'was_correct'),
        sa.Index('idx_pred_created', 'created_at'),
    )

    # Player Injuries (from Sleeper)
    op.create_table(
        'player_injuries',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('player_id', UUID(as_uuid=True), sa.ForeignKey('players.id'), nullable=False, index=True),

        # Injury details
        sa.Column('status', sa.String(50), nullable=False, index=True),  # Questionable, Out, IR, etc.
        sa.Column('body_part', sa.String(100), nullable=True),
        sa.Column('injury_notes', sa.Text, nullable=True),
        sa.Column('practice_participation', sa.String(50), nullable=True),  # Full, Limited, DNP
        sa.Column('practice_description', sa.String(255), nullable=True),

        # Timeline
        sa.Column('first_reported', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, index=True),

        # Metadata
        sa.Column('source', sa.String(50), default='sleeper'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),

        sa.Index('idx_inj_player_status', 'player_id', 'status'),
        sa.Index('idx_inj_active', 'is_active'),
    )

    # News Items (from ESPN, Reddit, RotoWire)
    op.create_table(
        'news_items',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('player_id', UUID(as_uuid=True), sa.ForeignKey('players.id'), nullable=True, index=True),
        sa.Column('team_abbr', sa.String(10), nullable=True, index=True),

        # News details
        sa.Column('source', sa.String(50), nullable=False, index=True),  # espn, reddit, rotowire
        sa.Column('headline', sa.String(500), nullable=False),
        sa.Column('content', sa.Text, nullable=True),
        sa.Column('url', sa.String(1000), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True, index=True),

        # Classification
        sa.Column('is_injury_related', sa.Boolean, default=False, index=True),
        sa.Column('is_lineup_change', sa.Boolean, default=False),
        sa.Column('severity', sa.String(20), nullable=True),  # low, medium, high

        # Metadata
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),

        sa.Index('idx_news_source_published', 'source', 'published_at'),
    )

    # Next Gen Stats (advanced metrics)
    op.create_table(
        'player_nextgen_stats',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('player_id', UUID(as_uuid=True), sa.ForeignKey('players.id'), nullable=False, index=True),
        sa.Column('season', sa.Integer, nullable=False, index=True),
        sa.Column('week', sa.Integer, nullable=False, index=True),
        sa.Column('position', sa.String(10), nullable=False),

        # Store full NGS data as JSON
        sa.Column('stats_json', JSONB, nullable=False),

        # Common QB metrics (for quick queries)
        sa.Column('aggressiveness', sa.Float, nullable=True),
        sa.Column('avg_time_to_throw', sa.Float, nullable=True),
        sa.Column('completion_pct_above_expectation', sa.Float, nullable=True),
        sa.Column('avg_air_distance', sa.Float, nullable=True),
        sa.Column('max_completed_air_distance', sa.Float, nullable=True),

        # Metadata
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),

        sa.UniqueConstraint('player_id', 'season', 'week', name='uq_player_season_week_ngs'),
    )

    # Data Sync Log (track when we last synced each source)
    op.create_table(
        'data_sync_log',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('source', sa.String(50), nullable=False, index=True),  # prizepicks, sleeper, espn, etc.
        sa.Column('sync_type', sa.String(50), nullable=False),  # full, incremental, realtime
        sa.Column('status', sa.String(20), nullable=False),  # success, failed, partial
        sa.Column('records_processed', sa.Integer, default=0),
        sa.Column('records_created', sa.Integer, default=0),
        sa.Column('records_updated', sa.Integer, default=0),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Float, nullable=True),
        sa.Column('metadata', JSONB, nullable=True),

        sa.Index('idx_sync_source_started', 'source', 'started_at'),
    )


def downgrade():
    op.drop_table('data_sync_log')
    op.drop_table('player_nextgen_stats')
    op.drop_table('news_items')
    op.drop_table('player_injuries')
    op.drop_table('predictions')
    op.drop_table('player_game_stats')
    op.drop_table('props')
    op.drop_table('games')
    op.drop_table('teams')
    op.drop_table('players')
