"""add task deletion activity types

Revision ID: f5122bc2614c
Revises: a5c16f26ee2e
Create Date: 2026-08-20 00:19:23.082860

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5122bc2614c'
down_revision: Union[str, Sequence[str], None] = 'a5c16f26ee2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE taskactivitytype ADD VALUE IF NOT EXISTS 'DELETED'"
    )

    op.execute(
        "ALTER TYPE taskactivitytype ADD VALUE IF NOT EXISTS 'RESTORED'"
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
