from uuid import UUID
from datetime import datetime, timezone

from uuid_utils import uuid7
from sqlalchemy import UUID as SQLUUID, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


from task_management_api.db.base import Base
from task_management_api.tasks.enums import (
    TaskPriority, 
    TaskStatus
)
from task_management_api.users.model import User
from task_management_api.tasks.assignee_model import TaskAssignee
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from task_management_api.tasks.activity_model import TaskActivity
    from task_management_api.comments.model import TaskComment


class Task(Base):
    __tablename__ = "tasks"
    
    id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=lambda:UUID(str(uuid7())),
    )
    
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    
    description: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )
    
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus),
        nullable=False,
        default=TaskStatus.PENDING
    )
    
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority),
        nullable=False,
        default=TaskPriority.MEDIUM
    )
    
    owner_id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    
    owner: Mapped[User] = relationship(
        back_populates="tasks"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
        
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )    
    
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    assignees: Mapped[list["TaskAssignee"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )
    
    activities: Mapped[list["TaskActivity"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )
    
    comments: Mapped[list["TaskComment"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan"
    )