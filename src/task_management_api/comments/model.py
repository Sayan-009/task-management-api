from uuid import UUID
from uuid_utils import uuid7
from datetime import datetime, timezone

from sqlalchemy import UUID as SQLUUID, String, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from task_management_api.db.base import Base
from task_management_api.users.model import User
from task_management_api.tasks.model import Task


class TaskComment(Base):
    __tablename__ = "comments"
    
    __table_args__ = (
        Index(
            "ix_comments_task_id_created_at",
            "task_id",
            "created_at"
        ),
    )
    
    id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=lambda: UUID(str(uuid7())),
    )
    
    content: Mapped[str] = mapped_column(
        String(5000),
        nullable=False
    )
    
    task_id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    author_id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    
    is_edited: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    edited_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
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
    
    author: Mapped[User] = relationship(
        back_populates="comments"
    )
    
    task: Mapped[Task] = relationship(
        back_populates="comments"
    )
    
    