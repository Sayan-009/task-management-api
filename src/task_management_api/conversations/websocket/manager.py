from uuid import UUID
from fastapi import WebSocket
from typing import Any
from collections import defaultdict
from task_management_api.conversations.websocket.connection import Connection

class ConnectionManager:
    
    def __init__(self) -> None:
        self.active_connections: dict[str, list[Connection]] = defaultdict(list)
    
    
    async def connect(
        self, 
        room_id: str,
        user_id: UUID,
        websocket: WebSocket,
    ) -> None:
        await websocket.accept()
        
        self.active_connections[room_id].append(Connection(user_id=user_id, websocket=websocket))
        
        print(
            f"Client connected to {room_id}. "
            f"Total connections: {len(self.active_connections[room_id])}"
        )
        
        
    def disconnect(
        self,
        room_id: str,
        websocket: WebSocket,
    ) -> None:
        
        connections = self.active_connections.get(room_id)
        
        if connections is None:
            return
        
        connection = next(
            (
                connection
                for connection in connections
                if connection.websocket == websocket
            ),
            None,
        )
        
        if connection is not None:
            connections.remove(connection)
            
        if len(connections) == 0:
            del self.active_connections[room_id]
            
        print(f"Client disconnected from {room_id}")
        
        
    async def broadcast(
        self,
        room_id: str,
        event: str,
        data: dict[str, Any],
        exclude_user_ids: list[UUID] | None = None,
    ) -> None:
        connections = self.active_connections.get(room_id, [])
        
        payload = {
            "event": event,
            "data": data,
        }

        dead_connections = []
        # Use a list copy to prevent mutation issues during iteration
        for connection in list(connections):
            if exclude_user_ids is not None and connection.user_id in exclude_user_ids:
                continue
            try:
                await connection.websocket.send_json(payload)
            except Exception as e:
                print(f"[WebSocket] Error broadcasting to connection in {room_id}: {e}")
                dead_connections.append(connection)

        # Safely prune dead connections
        for connection in dead_connections:
            self.disconnect(room_id, connection.websocket)
                
            

connection_manager = ConnectionManager()