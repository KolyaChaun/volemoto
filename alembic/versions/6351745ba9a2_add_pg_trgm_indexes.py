"""add_pg_trgm_indexes

Revision ID: 6351745ba9a2
Revises: b417cee2f88f
Create Date: 2026-04-15 21:11:03.945950

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6351745ba9a2"
down_revision: Union[str, Sequence[str], None] = "b417cee2f88f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_bikes_search_trgm ON bikes "
        "USING GIN ((lower(coalesce(brand,'') || ' ' || coalesce(name,'') || ' ' "
        "|| coalesce(model,'') || ' ' || coalesce(article,'') || ' ' || coalesce(color,''))) "
        "gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_products_search_trgm ON products "
        "USING GIN ((lower(coalesce(name,'') || ' ' || coalesce(brand,'') || ' ' "
        "|| coalesce(model,'') || ' ' || coalesce(article,'') || ' ' "
        "|| coalesce(compatibility,'') || ' ' || coalesce(subcategory,''))) "
        "gin_trgm_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_bikes_search_trgm")
    op.execute("DROP INDEX IF EXISTS ix_products_search_trgm")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
