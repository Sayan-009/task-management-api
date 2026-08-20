from uuid import UUID
from datetime import datetime, timezone
from uuid_utils import uuid7

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    UUID as SQLUUID,
    DateTime,
    Enum, 
    ForeignKey,
    String
)


from task_management_api.db.base import Base
from task_management_api.tasks.enums import TaskActivityType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from task_management_api.users.model import User
    from task_management_api.tasks.model import Task




class TaskActivity(Base):
    __tablename__ = "activities"
    
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
        nullable=False
    )
    
    action: Mapped[TaskActivityType] = mapped_column(
        Enum(TaskActivityType),
        nullable=False
    )
    
    field: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    
    old_value: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    
    new_value: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    
    task: Mapped["Task"] = relationship(
        back_populates="activities",
    )
    
    user: Mapped["User"] = relationship(
        back_populates="activities"
    )