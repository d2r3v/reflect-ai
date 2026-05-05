"""Add user_memories table

Revision ID: 2b8f7a3e9c15
Revises: 34da07402df8
Create Date: 2026-05-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '2b8f7a3e9c15'
down_revision: Union[str, Sequence[str], None] = '34da07402df8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_memories',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('keywords', sa.Text(), nullable=False),
        sa.Column('source_message_id', sa.UUID(), nullable=True),
        sa.Column('times_reinforced', sa.Integer(), nullable=False),
        sa.Column('last_reinforced_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.id'],
            name=op.f('fk_user_memories_user_id_users'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['source_message_id'], ['messages.id'],
            name=op.f('fk_user_memories_source_message_id_messages'),
            ondelete='SET NULL',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_user_memories')),
    )
    with op.batch_alter_table('user_memories', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_memories_user_id'), ['user_id'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('user_memories', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_memories_user_id'))
    op.drop_table('user_memories')
