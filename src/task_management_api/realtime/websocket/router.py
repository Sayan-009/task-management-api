from uuid import UUID
from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
)

from sqlalchemy.orm import Session

from task_management_api.realtime.websocket.dispatcher import EventDispatcher

from task_management_api.realtime.websocket.manager import connection_manager

from task_management_api.realtime.websocket.events import WebSocketEvent
from task_management_api.realtime.websocket.context import WebSocketEventContext
from task_management_api.users.presence_service import PresenceService
from task_management_api.core.websocket_dependencies import get_websocket_user
from task_management_api.db.session import get_db
from task_management_api.users.model import User
import task_management_api.conversations.realtime.handlers  


websocket_router = APIRouter(
    prefix="/ws",
    tags=["websocket"],
)

@websocket_router.websocket("/")
async def websocket_endpoint(
    websocket: WebSocket,
    current_user: User = Depends(get_websocket_user),
    session: Session = Depends(get_db)
) -> None:
    
    is_first_connection = await connection_manager.connect(
        current_user.id,
        websocket,
    )
    
    if is_first_connection:
        await PresenceService.handle_user_online(
            session,
            current_user,
        )

    await PresenceService.send_presence_snapshot(
        session,
        current_user,
    )
    
    try:
        while True:
            payload = await websocket.receive_json()

            event_name = payload.get("event")
            
            conversation_id = payload.get("conversation_id")

            if conversation_id is not None:
                conversation_id = UUID(conversation_id)
                
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

            try:
                await EventDispatcher.dispatch(
                    event=event,
                    context=WebSocketEventContext(
                        data=data,
                        current_user=current_user,
                        session=session,
                        conversation_id=conversation_id,
                    ),
                )
            except Exception as e:
                import logging
                logger = logging.getLogger("uvicorn.error")
                logger.exception(f"[WebSocket Error] Exception while processing event '{event_name}': {e}")
                await websocket.send_json({
                    "event": "error",
                    "data": {
                        "message": "Failed to process WebSocket event",
                        "event": event_name,
                    },
                })
                continue
                    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {current_user.id}")
        
    finally:
        is_last_connection = connection_manager.disconnect(
            current_user.id,
            websocket,
        )

        if is_last_connection:
            await PresenceService.handle_user_offline(
                session,
                current_user,
            )