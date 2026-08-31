from uuid import UUID

from sqlalchemy.orm import Session

from task_management_api.conversations.websocket import handlers

from task_management_api.conversations.websocket.registry import (
    EventRegistry
)

from task_management_api.conversations.websocket.events import (
    WebSocketEvent
)

from task_management_api.users.model import User



class EventDispatcher:
    
    @staticmethod
    async def dispatch(
        event: WebSocketEvent, 
        data: dict,
        conversation_id: UUID,
        current_user: User,
        session: Session,
    ) -> None:
        
        handler = EventRegistry.get_handler(event)
        
        if handler is None:
            raise ValueError(
                f"Unsupported event: {event}"
            )
            
            
        await handler.handle(
            data,
            conversation_id,
            current_user,
            session,
        )