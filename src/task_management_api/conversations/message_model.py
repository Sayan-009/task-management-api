from uuid import UUID
from uuid_utils import uuid7
from datetime import datetime, timezone

from sqlalchemy import (
    ForeignKey,
    DateTime,
    UUID as SQLUUID,
    String,
    Boolean,
    Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from task_management_api.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from task_management_api.users.model import User
    from task_management_api.conversations.conversation_model import PrivateConversation
    from task_management_api.conversations.attachment_model import MessageAttachment


class PrivateMessage(Base):
    __tablename__ = "messages"
    
    __table_args__ = (
        Index(
            "ix_messages_conversation_id_created_at",
            "conversation_id",
            "created_at"
        ),
    )

    id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=lambda: UUID(str(uuid7()))
    )

    conversation_id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )

    sender_id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    content: Mapped[str | None] = mapped_column(
        String(5000),
        nullable=True,
    )
    
    reply_to_message_id: Mapped[UUID | None] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey(
            "messages.id",
            ondelete="SET NULL"
        ),
        nullable=True,
    )    

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
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
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    sender: Mapped["User"] = relationship(
        back_populates="sent_private_messages"
    )

    conversation: Mapped["PrivateConversation"] = relationship(
        back_populates="messages"
    )
    
    reply_to: Mapped["PrivateMessage | None"] = relationship(
        "PrivateMessage",
        remote_side="PrivateMessage.id",
        foreign_keys=[reply_to_message_id],
        back_populates="replies",
    )

    replies: Mapped[list["PrivateMessage"]] = relationship(
        "PrivateMessage",
        foreign_keys=[reply_to_message_id],
        back_populates="reply_to",
    )
    
    attachments: Mapped[list["MessageAttachment"]] = relationship(
        "MessageAttachment",
        back_populates="message",
        cascade="all, delete-orphan",
    )