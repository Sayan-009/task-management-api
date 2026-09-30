from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from task_management_api.users.model import User


@dataclass
class WebSocketEventContext:
    data: dict[str, Any]
    current_user: User
    session: Session
    conversation_id: UUID | None = None
    