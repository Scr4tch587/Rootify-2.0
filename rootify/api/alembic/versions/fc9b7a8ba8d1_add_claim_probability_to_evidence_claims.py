"""add claim_probability to evidence_claims

Revision ID: fc9b7a8ba8d1
Revises: e7a973ada57b
Create Date: 2025-12-29 05:04:24.441718

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc9b7a8ba8d1'
down_revision: Union[str, None] = 'e7a973ada57b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1) Add the column with a server default so existing rows get a value
    op.add_column(
        "evidence_claims",
        sa.Column(
            "claim_probability",
            sa.Float(),
            nullable=False,
            server_default=sa.text("1.0"),
        ),
    )

    # 2) Optional but recommended: remove the default so future inserts rely on app/ORM defaults
    op.alter_column(
        "evidence_claims",
        "claim_probability",
        server_default=None,
    )

def downgrade() -> None:
    op.drop_column("evidence_claims", "claim_probability")