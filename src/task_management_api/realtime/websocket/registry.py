from typing import Callable

from task_management_api.realtime.websocket.events import (
    WebSocketEvent
)

class EventRegistry:
    
    _handlers: dict[WebSocketEvent, type] = {}
    
    @classmethod
    def register(
        cls,
        event_name: WebSocketEvent,
    ) -> Callable:
        
        def decorator(handler: type) -> type:
            
            cls._handlers[event_name] = handler
            
            return handler
        
        return decorator
    
    
    @classmethod
    def get_handler(
        cls,
        event_name: WebSocketEvent,
    ) -> type | None:
        
        return cls._handlers.get(event_name)