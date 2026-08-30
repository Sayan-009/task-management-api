from fastapi import WebSocket
from typing import Any
from collections import defaultdict

class ConnectionManager:
    
    def __init__(self) -> None:
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)
    
    
    async def connect(
        self, 
        room_id: str,
        websocket: WebSocket,
    ) -> None:
        await websocket.accept()
        
        self.active_connections[room_id].append(websocket)
        
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
        
        if connections and websocket in connections:
            connections.remove(websocket)
            
        if connections and len(connections) == 0:
            del self.active_connections[room_id]
            
        print(f"Client disconnected from {room_id}")
        
        
    async def broadcast(
        self,
        room_id: str,
        event: str,
        data: dict[str, Any],
    ) -> None:
        connections = self.active_connections.get(room_id, [])
        
        payload = {
            "event": event,
            "data": data,
        }

        dead_connections = []
        # Use a list copy to prevent mutation issues during iteration
        for websocket in list(connections):
            try:
                await websocket.send_json(payload)
            except Exception as e:
                print(f"[WebSocket] Error broadcasting to connection in {room_id}: {e}")
                dead_connections.append(websocket)

        # Safely prune dead connections
        for websocket in dead_connections:
            self.disconnect(room_id, websocket)
                
            

connection_manager = ConnectionManager()