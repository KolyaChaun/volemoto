"""add_exchange_rates_table

Revision ID: bf2e0830be8b
Revises: 6351745ba9a2
Create Date: 2026-04-15 21:34:42.039485

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bf2e0830be8b"
down_revision: Union[str, Sequence[str], None] = "6351745ba9a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "exchange_rates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("rate", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("currency"),
    )


def downgrade() -> None:
    op.drop_table("exchange_rates")
