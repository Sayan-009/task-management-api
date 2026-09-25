from task_management_api.realtime.websocket.registry import EventRegistry

from task_management_api.realtime.websocket.events import WebSocketEvent
from task_management_api.realtime.websocket.context import WebSocketEventContext




class EventDispatcher:
    
    @staticmethod
    async def dispatch(
        event: WebSocketEvent, 
        context: WebSocketEventContext,
    ) -> None:
        
        handler = EventRegistry.get_handler(event)
        
        if handler is None:
            raise ValueError(
                f"Unsupported event: {event}"
            )
            
            
        await handler.handle(
            context,
        )