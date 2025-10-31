"""Add slate field to games and predictions tables

Revision ID: 003
Revises: 002
Create Date: 2025-10-30

Adds slate field to categorize games by time slot:
- THURSDAY: Thursday Night Football
- SUNDAY_EARLY: Sunday 1PM ET games
- SUNDAY_LATE: Sunday 4PM ET games
- SUNDAY_NIGHT: Sunday Night Football
- MONDAY: Monday Night Football
- SATURDAY: Saturday games (late season/playoffs)
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Add slate to games table
    op.add_column('games', sa.Column('slate', sa.String(), nullable=True))
    op.create_index('ix_games_slate', 'games', ['slate'])

    # Add slate to predictions table
    op.add_column('predictions', sa.Column('slate', sa.String(), nullable=True, index=True))


def downgrade():
    # Remove from predictions
    op.drop_column('predictions', 'slate')

    # Remove from games
    op.drop_index('ix_games_slate', table_name='games')
    op.drop_column('games', 'slate')
