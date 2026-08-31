from dataclasses import dataclass
from uuid import UUID


from fastapi import WebSocket

@dataclass
class Connection:
    user_id: UUID
    websocket: WebSocket