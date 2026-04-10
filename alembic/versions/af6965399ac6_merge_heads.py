"""merge heads

Revision ID: af6965399ac6
Revises: 5d72d481e873, 3a9f7c2d1e08
Create Date: 2026-04-09 16:03:30.714011

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af6965399ac6'
down_revision: Union[str, Sequence[str], None] = ('5d72d481e873', '3a9f7c2d1e08')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
