from datetime import datetime, timezone
from uuid import UUID
from uuid_utils import uuid7
from sqlalchemy import (
    String,
    Integer,
    UUID as SQLUUID,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from typing import TYPE_CHECKING

from task_management_api.db.base import Base

if TYPE_CHECKING:
    from task_management_api.users.model import User
    from task_management_api.conversations.message_model import PrivateMessage


class MessageAttachment(Base):
    
    __tablename__ = "message_attachments"
    
    __table_args__ = (
        Index("ix_message_attachments_message_id", "message_id",),
    )
    
    id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=lambda: UUID(str(uuid7())),
    )
    
    message_id: Mapped[UUID | None] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=True,
    )
    
    uploaded_by: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    
    file_name: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )
    
    stored_name: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )
    
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    message: Mapped["PrivateMessage"] = relationship(
        "PrivateMessage",
        back_populates="attachments"
    )
    
    uploaded_by_user: Mapped["User"] = relationship(
        "User",
        back_populates="attachments"
    )