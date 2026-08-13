"""add tasks table

Revision ID: 845a7b3c2b82
Revises: 6f24dddc560c
Create Date: 2026-08-13 17:09:58.744727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '845a7b3c2b82'
down_revision: Union[str, Sequence[str], None] = '6f24dddc560c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    task_status = postgresql.ENUM(
        'PENDING',
        'IN_PROGRESS',
        'COMPLETED',
        name='taskstatus',
        create_type=False,
    )

    task_priority = postgresql.ENUM(
        'LOW',
        'MEDIUM',
        'HIGH',
        name='taskpriority',
        create_type=False,
    )

    task_status.create(
        op.get_bind(),
        checkfirst=True,
    )

    task_priority.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.create_table(
        'tasks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=2000), nullable=True),
        sa.Column('status', task_status, nullable=False),
        sa.Column('priority', task_priority, nullable=False),
        sa.Column('owner_id', sa.UUID(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ['owner_id'],
            ['users.id'],
            name=op.f('fk_tasks_owner_id_users'),
        ),
        sa.PrimaryKeyConstraint(
            'id',
            name=op.f('pk_tasks'),
        ),
    )

def downgrade() -> None:
    op.drop_table('tasks')

    task_priority = postgresql.ENUM(
        'LOW',
        'MEDIUM',
        'HIGH',
        name='taskpriority',
        create_type=False,
    )

    task_status = postgresql.ENUM(
        'PENDING',
        'IN_PROGRESS',
        'COMPLETED',
        name='taskstatus',
        create_type=False,
    )

    task_priority.drop(
        op.get_bind(),
        checkfirst=True,
    )

    task_status.drop(
        op.get_bind(),
        checkfirst=True,
    )