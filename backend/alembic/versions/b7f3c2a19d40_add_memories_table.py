"""add memories table

Revision ID: b7f3c2a19d40
Revises: 34da07402df8
Create Date: 2026-07-25 01:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7f3c2a19d40'
down_revision: Union[str, Sequence[str], None] = '34da07402df8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'memories',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('source_message_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_memories_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_memories')),
    )
    with op.batch_alter_table('memories', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_memories_user_id'), ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('memories', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_memories_user_id'))
    op.drop_table('memories')
