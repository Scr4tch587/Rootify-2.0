"""create evidence_sections

Revision ID: d30a55d50f34
Revises: 77148f27b5a2
Create Date: 2025-12-21 23:20:47.964928

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd30a55d50f34'
down_revision: Union[str, None] = '77148f27b5a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'evidence_sections',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('artist_id', sa.Integer(), sa.ForeignKey('artists.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source', sa.Text(), nullable=False),
        sa.Column('keyword', sa.Text(), nullable=False),
        sa.Column('section_path', sa.Text(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column("is_fallback", sa.Boolean(), nullable=False, server_default=sa.text("False")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint('artist_id', 'source', 'section_path', name='uq_evidence_sections_artist_source_section_path'),
    )
    op.create_index(
        'ix_evidence_sections_artist_id',
        'evidence_sections',
        ['artist_id'],
    )


def downgrade() -> None:
    op.drop_index('ix_evidence_sections_artist_id', table_name='evidence_sections')
    op.drop_table('evidence_sections')
