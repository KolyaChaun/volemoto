"""add products table

Revision ID: 3a9f7c2d1e08
Revises: e362ea13cdbe
Create Date: 2026-04-09 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "3a9f7c2d1e08"
down_revision: Union[str, Sequence[str], None] = "e362ea13cdbe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("article", sa.String(10), nullable=True, default=""),
        sa.Column("name", sa.String(200), nullable=True),
        sa.Column("brand", sa.String(100), nullable=True, default=""),
        sa.Column("price", sa.Integer(), nullable=True, default=0),
        sa.Column("condition", sa.String(100), nullable=True, default=""),
        sa.Column("available", sa.Boolean(), nullable=True, default=True),
        sa.Column("status", sa.String(30), nullable=True, default="available"),
        sa.Column("description", sa.Text(), nullable=True, default=""),
        sa.Column("photo", sa.String(300), nullable=True, default=""),
        sa.Column("category", sa.String(30), nullable=True),
        sa.Column("size", sa.String(100), nullable=True, default=""),
        sa.Column("compatibility", sa.String(500), nullable=True, default=""),
        sa.Column("youtube_url", sa.String(500), nullable=True, default=""),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_products_id"), "products", ["id"], unique=False)

    op.create_table(
        "product_photos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("path", sa.String(300), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_product_photos_id"), "product_photos", ["id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_product_photos_id"), table_name="product_photos")
    op.drop_table("product_photos")
    op.drop_index(op.f("ix_products_id"), table_name="products")
    op.drop_table("products")
