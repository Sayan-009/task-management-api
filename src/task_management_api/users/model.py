from datetime import datetime, timezone
from uuid import UUID

from uuid_utils import uuid7
from sqlalchemy import UUID as SQLUUID, String, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from task_management_api.db.base import Base
from task_management_api.users.enums import UserRole
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from task_management_api.tasks.model import Task



class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=lambda: UUID(str(uuid7())),
    )
    
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True
    )
    
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.USER
    )
    
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
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
    
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="owner"
    )