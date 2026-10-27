from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from task_management_api.users.model import User


@dataclass
class WebSocketEventContext:
    data: dict[str, Any]
    current_user: User
    session: AsyncSession
    conversation_id: UUID | None = None
    