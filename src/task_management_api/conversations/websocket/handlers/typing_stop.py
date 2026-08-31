from uuid import UUID

from sqlalchemy.orm import (
    Session
)
from task_management_api.users.model import User
from task_management_api.conversations.websocket.registry import (
    EventRegistry
)
from task_management_api.conversations.websocket.events import (
    WebSocketEvent
)

from task_management_api.conversations.websocket.manager import (
    connection_manager
)



@EventRegistry.register(WebSocketEvent.TYPING_STOP)
class TypingStopHandler:
    
    @staticmethod
    async def handle(
        data: dict,
        conversation_id: UUID,
        current_user: User,
        session: Session,
    ) -> None:
        
        room_id = f"conversation:{conversation_id}"
        
        await connection_manager.broadcast(
            room_id=room_id,
            event=WebSocketEvent.USER_TYPING_STOPPED,
            data={
                "conversation_id": str(conversation_id),
                "user": {
                    "id": str(current_user.id),
                    "name": current_user.name
                },
            },
            exclude_user_ids=[current_user.id],
        )