"""add_site_settings_table

Revision ID: c3a1f9b2e541
Revises: bf2e0830be8b
Create Date: 2026-04-16 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3a1f9b2e541"
down_revision: Union[str, Sequence[str], None] = "bf2e0830be8b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "site_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", sa.String(length=500), nullable=False, server_default=""),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.execute(
        "INSERT INTO site_settings (key, value) VALUES ('sold_count', '620+'), ('subscribers_count', '13 600')"
    )


def downgrade() -> None:
    op.drop_table("site_settings")
