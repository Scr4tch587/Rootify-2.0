"""create artist_name_variants

Revision ID: bdefb6b724cf
Revises: e1862ec94010
Create Date: 2025-12-30 04:50:55.930101

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bdefb6b724cf'
down_revision: Union[str, None] = 'e1862ec94010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('artists_variants',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('canonical_name', sa.String(length=255), nullable=False),
    sa.Column('variant_name', sa.String(length=255), nullable=False),
    sa.Column('variant_norm', sa.String(length=255), nullable=False),
    sa.Column('first_token', sa.String(length=255), nullable=False),
    sa.Column("id", sa.Integer(), primary_key=True),
def downgrade() -> None:
    pass
