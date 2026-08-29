from uuid import UUID
from uuid_utils import uuid7
from datetime import datetime, timezone

from sqlalchemy import (
    ForeignKey,
    DateTime,
    UUID as SQLUUID,
    Enum,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from task_management_api.db.base import Base
from task_management_api.conversations.enums import ConversationStatus

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from task_management_api.users.model import User
    from task_management_api.tasks.model import Task
    from task_management_api.conversations.message_model import PrivateMessage



class PrivateConversation(Base):
    __tablename__ = "conversations"

    __table_args__ = (
        UniqueConstraint(
            "task_id",
            "assignee_id",
            name="uq_conversations_task_assignee"
        ),
    )

    id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=lambda: UUID(str(uuid7()))
    )

    task_id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    )

    assignee_id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    status: Mapped[ConversationStatus] = mapped_column(
        Enum(ConversationStatus),
        default=ConversationStatus.ACTIVE,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    messages: Mapped[list["PrivateMessage"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan"
    )

    assignee: Mapped["User"] = relationship(
        back_populates="assigned_private_conversations"
    )

    task: Mapped["Task"] = relationship(
        back_populates="private_conversations"
    )