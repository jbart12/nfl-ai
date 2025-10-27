"""Initial schema for AI prediction system

Revision ID: 001
Revises:
Create Date: 2025-10-26

Creates minimal tables needed for AI prediction system:
- Players
- Teams
- Games
- PlayerGameStats
- PrizePicksProjections
- TeamDefensiveStats
- PlayerInjuries
- Predictions
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Players table
    op.create_table(
        'players',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('player_position', sa.String(), nullable=True),
        sa.Column('team_id', sa.String(), nullable=True),
        sa.Column('jersey_number', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=True, server_default='ACTIVE'),
        sa.Column('espn_id', sa.String(), nullable=True),
        sa.Column('sleeper_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_players_name', 'name'),
        sa.Index('ix_players_espn_id', 'espn_id', unique=True),
        sa.Index('ix_players_sleeper_id', 'sleeper_id', unique=True),
    )

    # Teams table
    op.create_table(
        'teams',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('conference', sa.String(), nullable=True),
        sa.Column('division', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Games table
    op.create_table(
        'games',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('season', sa.Integer(), nullable=False),
        sa.Column('week', sa.Integer(), nullable=False),
        sa.Column('game_date', sa.Date(), nullable=True),
        sa.Column('game_time', sa.DateTime(), nullable=True),
        sa.Column('home_team_id', sa.String(), nullable=True),
        sa.Column('away_team_id', sa.String(), nullable=True),
        sa.Column('opponent_team_id', sa.String(), nullable=True),
        sa.Column('home_score', sa.Integer(), nullable=True),
        sa.Column('away_score', sa.Integer(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('weather_description', sa.String(), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('wind_speed', sa.Float(), nullable=True),
        sa.Column('is_dome', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('vegas_line', sa.Float(), nullable=True),
        sa.Column('over_under', sa.Float(), nullable=True),
        sa.Column('espn_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['home_team_id'], ['teams.id']),
        sa.ForeignKeyConstraint(['away_team_id'], ['teams.id']),
        sa.Index('ix_games_season', 'season'),
        sa.Index('ix_games_week', 'week'),
        sa.Index('ix_games_game_date', 'game_date'),
        sa.Index('ix_games_espn_id', 'espn_id', unique=True),
    )

    # PlayerGameStats table
    op.create_table(
        'player_game_stats',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('player_id', sa.String(), nullable=False),
        sa.Column('game_id', sa.String(), nullable=False),
        sa.Column('season', sa.Integer(), nullable=False),
        sa.Column('week', sa.Integer(), nullable=False),
        sa.Column('snap_count', sa.Integer(), nullable=True),
        sa.Column('snap_percentage', sa.Float(), nullable=True),
        sa.Column('passing_completions', sa.Integer(), nullable=True),
        sa.Column('passing_attempts', sa.Integer(), nullable=True),
        sa.Column('passing_yards', sa.Integer(), nullable=True),
        sa.Column('passing_touchdowns', sa.Integer(), nullable=True),
        sa.Column('passing_long', sa.Integer(), nullable=True),
        sa.Column('interceptions', sa.Integer(), nullable=True),
        sa.Column('rushing_attempts', sa.Integer(), nullable=True),
        sa.Column('rushing_yards', sa.Integer(), nullable=True),
        sa.Column('rushing_touchdowns', sa.Integer(), nullable=True),
        sa.Column('rushing_long', sa.Integer(), nullable=True),
        sa.Column('receiving_targets', sa.Integer(), nullable=True),
        sa.Column('receiving_receptions', sa.Integer(), nullable=True),
        sa.Column('receiving_yards', sa.Integer(), nullable=True),
        sa.Column('receiving_touchdowns', sa.Integer(), nullable=True),
        sa.Column('receiving_long', sa.Integer(), nullable=True),
        sa.Column('fantasy_points', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['player_id'], ['players.id']),
        sa.ForeignKeyConstraint(['game_id'], ['games.id']),
        sa.Index('ix_player_game_stats_player_id', 'player_id'),
        sa.Index('ix_player_game_stats_game_id', 'game_id'),
        sa.Index('ix_player_game_stats_season', 'season'),
    )

    # PrizePicksProjections table
    op.create_table(
        'prizepicks_projections',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('player_name', sa.String(), nullable=False),
        sa.Column('stat_type', sa.String(), nullable=False),
        sa.Column('line_score', sa.Float(), nullable=False),
        sa.Column('league', sa.String(), nullable=True, server_default='NFL'),
        sa.Column('game_time', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_prizepicks_projections_player_name', 'player_name'),
        sa.Index('ix_prizepicks_projections_is_active', 'is_active'),
        sa.Index('ix_prizepicks_projections_external_id', 'external_id', unique=True),
    )

    # TeamDefensiveStats table
    op.create_table(
        'team_defensive_stats',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('team_id', sa.String(), nullable=False),
        sa.Column('season', sa.Integer(), nullable=False),
        sa.Column('week', sa.Integer(), nullable=False),
        sa.Column('defensive_position', sa.String(), nullable=False),
        sa.Column('rank_vs_position', sa.Integer(), nullable=True),
        sa.Column('avg_points_allowed', sa.Float(), nullable=True),
        sa.Column('games_played', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id']),
    )

    # PlayerInjuries table
    op.create_table(
        'player_injuries',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('player_id', sa.String(), nullable=False),
        sa.Column('injury_status', sa.String(), nullable=True),
        sa.Column('injury_type', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('injured_date', sa.Date(), nullable=True),
        sa.Column('expected_return', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['player_id'], ['players.id']),
        sa.Index('ix_player_injuries_player_id', 'player_id'),
    )

    # Predictions table
    op.create_table(
        'predictions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('prop_id', sa.String(), nullable=True),
        sa.Column('player_id', sa.String(), nullable=True),
        sa.Column('prediction', sa.String(), nullable=False),
        sa.Column('confidence', sa.Integer(), nullable=False),
        sa.Column('projected_value', sa.Float(), nullable=False),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('model_version', sa.String(), nullable=True),
        sa.Column('similar_situations_count', sa.Integer(), nullable=True),
        sa.Column('actual_value', sa.Float(), nullable=True),
        sa.Column('was_correct', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['prop_id'], ['prizepicks_projections.id']),
        sa.ForeignKeyConstraint(['player_id'], ['players.id']),
    )


def downgrade():
    op.drop_table('predictions')
    op.drop_table('player_injuries')
    op.drop_table('team_defensive_stats')
    op.drop_table('prizepicks_projections')
    op.drop_table('player_game_stats')
    op.drop_table('games')
    op.drop_table('teams')
    op.drop_table('players')
