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

from task_management_api.conversations.websocket.dispatcher import (
    EventDispatcher
)

from task_management_api.conversations.websocket.manager import (
    connection_manager
)


from task_management_api.core.exceptions import (
    TaskNotFoundError,
    ConversationNotFoundError,
    ForbiddenOperationError,
)

from task_management_api.conversations.conversation_service import ConversationService
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
        current_user.id,
        websocket,
    )
    
    try:
        while True:
            payload = await websocket.receive_json()

            event_name = payload.get("event")
            data = payload.get("data", {})

            try:
                event = WebSocketEvent(event_name)

            except ValueError:
                await websocket.send_json({
                    "event": "error",
                    "data": {
                        "message": f"Unsupported event: {event_name}",
                    },
                })
                continue

            await EventDispatcher.dispatch(
                event=event,
                data=data,
                conversation_id=conversation_id,
                current_user=current_user,
                session=session,
            )      
                    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {room_id}")
        
        connection_manager.disconnect(
            room_id,
            websocket,
        )