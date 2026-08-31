from uuid import UUID

from sqlalchemy.orm import (
    Session
)

from task_management_api.users.model import User
from task_management_api.conversations.websocket.manager import (
    connection_manager
)
from task_management_api.conversations.websocket.registry import (
    EventRegistry
)
from task_management_api.conversations.websocket.events import (
    WebSocketEvent
)
from task_management_api.conversations.message_service import (
    MessageService
)


@EventRegistry.register(WebSocketEvent.MARK_MESSAGES_READ)
class MarkReadHandler:
    
    @staticmethod
    async def handle(
        data: dict,
        conversation_id: UUID,
        current_user: User,
        session: Session,
    ) -> None:
        message_ids = data.get("message_ids", [])
        
        message_ids = [
            UUID(message_id)
            for message_id in message_ids
        ]

        messages = MessageService.mark_messages_as_read(
            session=session,
            current_user=current_user,
            conversation_id=conversation_id,
            message_ids=message_ids,
        )

        session.commit()

        if messages:

            room_id = f"conversation:{conversation_id}"

            await connection_manager.broadcast(
                room_id=room_id,
                event=WebSocketEvent.MESSAGES_READ,
                data={
                    "conversation_id": str(conversation_id),
                    "message_ids": [
                        str(message.id)
                        for message in messages
                    ],
                    "read_at": (
                        messages[0].read_at.isoformat()
                    ),
                    "read_by": {
                        "id": str(current_user.id),
                        "name": current_user.name,
                    },
                },
            )       