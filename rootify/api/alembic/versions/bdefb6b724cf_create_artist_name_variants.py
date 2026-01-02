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
    op.create_table('artist_name_variants',
    sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
    sa.Column('canonical_name', sa.String(length=255), nullable=False),
    sa.Column('variant_name', sa.String(length=255), nullable=False),
    sa.Column('variant_norm', sa.String(length=255), nullable=False),
    sa.Column('first_token', sa.String(length=255), nullable=False),
    sa.Column("token_count", sa.Integer(), nullable=False),
    sa.Column("char_len", sa.Integer(), nullable=False),
    sa.Column("source", sa.String(length=255), nullable=False),
    sa.Column("match_form", sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    sa.UniqueConstraint(
        "variant_norm",
        "canonical_name",
        name="uq_artist_name_variants_variant_norm_canonical_name",
    ),)
    op.create_index(
        'ix_artist_name_variants_first_token',
        'artist_name_variants',
        ['first_token'],
    )
    op.create_index('ix_artist_name_variants_variant_norm', 'artist_name_variants', ['variant_norm'])
def downgrade() -> None:
    op.drop_index('ix_artist_name_variants_variant_norm', table_name='artist_name_variants')
    op.drop_index('ix_artist_name_variants_first_token', table_name='artist_name_variants')
    op.drop_table('artist_name_variants')