"""expand predictions table for opportunities feed

Revision ID: 002
Revises: 001
Create Date: 2025-10-27

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to predictions table
    op.add_column('predictions', sa.Column('player_name', sa.String(), nullable=True))
    op.add_column('predictions', sa.Column('player_position', sa.String(), nullable=True))
    op.add_column('predictions', sa.Column('team', sa.String(), nullable=True))
    op.add_column('predictions', sa.Column('opponent', sa.String(), nullable=True))
    op.add_column('predictions', sa.Column('week', sa.Integer(), nullable=True))
    op.add_column('predictions', sa.Column('season', sa.Integer(), nullable=True))
    op.add_column('predictions', sa.Column('game_time', sa.DateTime(), nullable=True))
    op.add_column('predictions', sa.Column('stat_type', sa.String(), nullable=True))
    op.add_column('predictions', sa.Column('line_score', sa.Float(), nullable=True))
    op.add_column('predictions', sa.Column('edge', sa.Float(), nullable=True))
    op.add_column('predictions', sa.Column('key_factors', sa.Text(), nullable=True))
    op.add_column('predictions', sa.Column('risk_factors', sa.Text(), nullable=True))
    op.add_column('predictions', sa.Column('comparable_game', sa.String(), nullable=True))
    op.add_column('predictions', sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'))
    op.add_column('predictions', sa.Column('is_archived', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('predictions', sa.Column('updated_at', sa.DateTime(), nullable=True))

    # Create indexes for common query patterns
    op.create_index('ix_predictions_player_name', 'predictions', ['player_name'])
    op.create_index('ix_predictions_player_position', 'predictions', ['player_position'])
    op.create_index('ix_predictions_week', 'predictions', ['week'])
    op.create_index('ix_predictions_game_time', 'predictions', ['game_time'])
    op.create_index('ix_predictions_stat_type', 'predictions', ['stat_type'])
    op.create_index('ix_predictions_confidence', 'predictions', ['confidence'])
    op.create_index('ix_predictions_is_active', 'predictions', ['is_active'])
    op.create_index('ix_predictions_created_at', 'predictions', ['created_at'])
    op.create_index('ix_predictions_player_id', 'predictions', ['player_id'])


def downgrade():
    # Remove indexes
    op.drop_index('ix_predictions_player_id', 'predictions')
    op.drop_index('ix_predictions_created_at', 'predictions')
    op.drop_index('ix_predictions_is_active', 'predictions')
    op.drop_index('ix_predictions_confidence', 'predictions')
    op.drop_index('ix_predictions_stat_type', 'predictions')
    op.drop_index('ix_predictions_game_time', 'predictions')
    op.drop_index('ix_predictions_week', 'predictions')
    op.drop_index('ix_predictions_player_position', 'predictions')
    op.drop_index('ix_predictions_player_name', 'predictions')

    # Remove columns
    op.drop_column('predictions', 'updated_at')
    op.drop_column('predictions', 'is_archived')
    op.drop_column('predictions', 'is_active')
    op.drop_column('predictions', 'comparable_game')
    op.drop_column('predictions', 'risk_factors')
    op.drop_column('predictions', 'key_factors')
    op.drop_column('predictions', 'edge')
    op.drop_column('predictions', 'line_score')
    op.drop_column('predictions', 'stat_type')
    op.drop_column('predictions', 'game_time')
    op.drop_column('predictions', 'season')
    op.drop_column('predictions', 'week')
    op.drop_column('predictions', 'opponent')
    op.drop_column('predictions', 'team')
    op.drop_column('predictions', 'player_position')
    op.drop_column('predictions', 'player_name')
