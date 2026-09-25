from datetime import datetime, timezone
from sqlalchemy.orm import Session

from task_management_api.users.model import User

from task_management_api.conversations.conversation_service import ConversationService

from task_management_api.realtime.websocket.manager import connection_manager

from task_management_api.realtime.websocket.events import WebSocketEvent

class PresenceService:
    
    @staticmethod
    async def handle_user_online(
        session: Session,
        user: User,
    ) -> None:
        
        related_user_ids = ConversationService.get_related_user_ids(
            session=session,
            user_id=user.id,
        )
        
        if not related_user_ids:
            return
        
        await connection_manager.send_to_users(
            user_ids=list(related_user_ids),
            event=WebSocketEvent.USER_ONLINE,
            data={
                "user": {
                    "id": str(user.id),
                    "name": user.name,
                },
            },
        )

    @staticmethod
    async def send_presence_snapshot(
        session: Session,
        user: User,
    ) -> None:

        related_user_ids = ConversationService.get_related_user_ids(
            session=session,
            user_id=user.id,
        )

        if not related_user_ids:
            return

        online_user_ids = [
            str(uid)
            for uid in related_user_ids
            if uid in connection_manager.active_connections
        ]

        await connection_manager.send_to_user(
            user_id=user.id,
            event=WebSocketEvent.PRESENCE_SNAPSHOT,
            data={
                "online_user_ids": online_user_ids,
            },
        )

    
    @staticmethod
    async def handle_user_offline(
        session: Session,
        user: User,
    ) -> None:
        
        user.last_seen_at = datetime.now(timezone.utc)
        session.commit()
        
        related_user_ids = ConversationService.get_related_user_ids(
            session=session,
            user_id=user.id,
        )
        
        if not related_user_ids:
            return
        
        await connection_manager.send_to_users(
            user_ids=list(related_user_ids),
            event=WebSocketEvent.USER_OFFLINE,
            data={
                "user": {
                    "id": str(user.id),
                    "name": user.name,
                },
                "last_seen_at": user.last_seen_at.isoformat(),
            }
        )