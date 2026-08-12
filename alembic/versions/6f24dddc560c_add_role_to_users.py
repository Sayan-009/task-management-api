"""add role to users

Revision ID: 6f24dddc560c
Revises: f233a8c1276d
Create Date: 2026-08-12 11:18:13.709670

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f24dddc560c'
down_revision: Union[str, Sequence[str], None] = 'f233a8c1276d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_role = sa.Enum(
        'USER',
        'ADMIN',
        name='userrole',
    )

    user_role.create(op.get_bind(), checkfirst=True)

    op.add_column(
        'users',
        sa.Column(
            'role',
            user_role,
            nullable=False,
            server_default='USER',
        ),
    )

    op.alter_column(
        'users',
        'role',
        server_default=None,
    )


def downgrade() -> None:
    user_role = sa.Enum(
        'USER',
        'ADMIN',
        name='userrole',
    )

    op.drop_column('users', 'role')

    user_role.drop(op.get_bind(), checkfirst=True)
