from uuid import UUID
from datetime import datetime, timezone

from uuid_utils import uuid7
from sqlalchemy import (
    UUID as SQLUUID,
    DateTime,
    Enum,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from task_management_api.db.base import Base
from task_management_api.tasks.enums import TaskStatus
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from task_management_api.tasks.model import Task
    from task_management_api.users.model import User


class TaskAssignee(Base):
    __tablename__ = "task_assignees"

    __table_args__ = (
        UniqueConstraint(
            "task_id",
            "user_id",
            name="uq_task_assignee",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=lambda: UUID(str(uuid7())),
    )

    task_id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    )

    user_id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus),
        nullable=False,
        default=TaskStatus.PENDING,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    task: Mapped["Task"] = relationship(
        back_populates="assignees",
    )

    user: Mapped["User"] = relationship(
        back_populates="assigned_tasks",
    )