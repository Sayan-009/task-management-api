from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    status,
)

from sqlalchemy.orm import Session

from task_management_api.conversations.websocket.manager import (
    connection_manager
)


from task_management_api.core.exceptions import (
    TaskNotFoundError,
    ConversationNotFoundError,
    ForbiddenOperationError,
)

from task_management_api.conversations.conversation_service import ConversationService
from task_management_api.conversations.message_service import MessageService
from task_management_api.conversations.websocket.events import WebSocketEvent

from task_management_api.core.websocket_dependencies import get_websocket_user
from task_management_api.db.session import get_db
from task_management_api.users.model import User


websocket_router = APIRouter(
    prefix="/ws",
    tags=["websocket"],
)



@websocket_router.websocket(
    "/conversations/{conversation_id}"
)
async def conversation_websocket(
    websocket: WebSocket,
    conversation_id: UUID,
    current_user: User = Depends(get_websocket_user),
    session: Session = Depends(get_db)
) -> None:
    
    try:
        ConversationService.validate_conversation_access(
            session=session,
            current_user=current_user,
            conversation_id=conversation_id,
        )

    except (
        TaskNotFoundError,
        ConversationNotFoundError,
        ForbiddenOperationError,
    ):
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="You don't have permission to access this conversation",
        )
    
    room_id = f"conversation:{conversation_id}"
    
    await connection_manager.connect(
        room_id,
        websocket
    )
    
    try:
        while True:
            payload = await websocket.receive_json()

            event = payload.get("event")
            data = payload.get("data", {})

            if event == WebSocketEvent.MARK_MESSAGES_READ:

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
    except WebSocketDisconnect:
        
        print(f"WebSocket disconnected: {room_id}")
        
        connection_manager.disconnect(
            room_id,
            websocket,
        )