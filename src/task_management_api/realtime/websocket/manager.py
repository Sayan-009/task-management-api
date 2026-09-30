from collections import defaultdict
from typing import Any
from uuid import UUID


from fastapi import WebSocket


from task_management_api.realtime.websocket.connection import Connection

class ConnectionManager:
    
    def __init__(self) -> None:
        self.active_connections: dict[UUID, list[Connection]] = defaultdict(list)
    
    
    async def connect(
        self, 
        user_id: UUID,
        websocket: WebSocket,
    ) -> bool:
        await websocket.accept()
        self.active_connections[user_id].append(Connection(websocket=websocket))
        print("new client is connected")
        total_user_connections = len(self.active_connections[user_id])
        is_first_connection = total_user_connections == 1
        return is_first_connection
        
        
    def disconnect(
        self,
        user_id: UUID,
        websocket: WebSocket,
    ) -> bool:
        
        connections = self.active_connections.get(user_id)
        
        if connections is None:
            return False
        
        connection = next(
            (
                connection
                for connection in connections
                if connection.websocket == websocket
            ),
            None,
        )
        
        if connection is None:
            return False
        
        connections.remove(connection)
        print("one client is disconnected")
            
        if len(connections) == 0:
            del self.active_connections[user_id]
            return True
            
        return False
    
    
    async def send_to_user(
        self,
        user_id: UUID,
        event: str,
        data: dict[str, Any],
    ) -> None:
        connections = self.active_connections.get(user_id, [])
        
        payload = {
            "event": event,
            "data": data,
        }
        
        dead_connections = []
        
        for connection in list(connections):
            try:
                await connection.websocket.send_json(payload)
            except Exception as e:
                print(f"[WebSocket] Error sending to user client in {user_id}: {e}")
                dead_connections.append(connection)
                
        for connection in dead_connections:
            self.disconnect(user_id, connection.websocket)
            
    
    async def send_to_users(
        self,
        user_ids: list[UUID],
        event: str,
        data: dict[str, Any],
    ) -> None:
        for user_id in user_ids:
            await self.send_to_user(
                user_id,
                event,
                data,
            )
                

connection_manager = ConnectionManager()