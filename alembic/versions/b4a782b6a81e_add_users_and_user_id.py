"""add users and user_id to sessions

Revision ID: b4a782b6a81e
Revises: 4d6dde3f7ba6
Create Date: 2026-06-23

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b4a782b6a81e'
down_revision: Union[str, Sequence[str], None] = '4d6dde3f7ba6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.add_column('sessions', sa.Column('user_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('sessions', 'user_id')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
