"""make evidence_sections.keyword nullable

Revision ID: e1862ec94010
Revises: fc9b7a8ba8d1
Create Date: 2025-12-30 00:47:22.530862

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1862ec94010'
down_revision: Union[str, None] = 'fc9b7a8ba8d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        "evidence_sections",
        "keyword",
        existing_type=sa.String(),
        nullable=True,
    )

def downgrade():
    op.alter_column(
        "evidence_sections",
        "keyword",
        existing_type=sa.String(),
        nullable=False,
    )

