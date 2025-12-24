"""create_evidence_claims

Revision ID: e7a973ada57b
Revises: d30a55d50f34
Create Date: 2025-12-24 00:12:59.091217

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7a973ada57b'
down_revision: Union[str, None] = 'd30a55d50f34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "evidence_claims",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("artist_id", sa.Integer(), sa.ForeignKey("artists.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("influence_artist", sa.String(), nullable=False),
        sa.Column("pattern_type", sa.String(), nullable=False),
        sa.Column("section_path", sa.String(), nullable=False),
        sa.Column("snippet", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("extraction_version", sa.String(), nullable=True),
    )

    op.create_index(
        "uq_evidence_claims_dedupe",
        "evidence_claims",
        ["artist_id", "source", "influence_artist", "section_path", "snippet"],
        unique=True,
    )

def downgrade() -> None:
    op.drop_index("uq_evidence_claims_dedupe", table_name="evidence_claims")
    op.drop_table("evidence_claims")
