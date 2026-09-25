from uuid import UUID


from task_management_api.realtime.websocket.registry import EventRegistry
from task_management_api.realtime.websocket.events import WebSocketEvent
from task_management_api.realtime.websocket.context import WebSocketEventContext
from task_management_api.realtime.websocket.manager import connection_manager

from task_management_api.conversations.message_service import MessageService
from task_management_api.conversations.conversation_service import ConversationService


@EventRegistry.register(WebSocketEvent.MARK_MESSAGES_READ)
class MarkReadHandler:

    @staticmethod
    async def handle(
        context: WebSocketEventContext,
    ) -> None:
        message_ids = context.data.get("message_ids", [])

        message_ids = [
            UUID(message_id)
            for message_id in message_ids
        ]

        messages = MessageService.mark_messages_as_read(
            session=context.session,
            current_user=context.current_user,
            conversation_id=context.conversation_id,
            message_ids=message_ids,
        )

        if not messages:
            return

        read_at = messages[0].read_at
        read_at_str = read_at.isoformat() if read_at is not None else None

        context.session.commit()

        other_participant_id = (
            ConversationService.get_other_participant_id(
                session=context.session,
                current_user=context.current_user,
                conversation_id=context.conversation_id,
            )
        )

        await connection_manager.send_to_user(
            user_id=other_participant_id,
            event=WebSocketEvent.MESSAGES_READ,
            data={
                "conversation_id": str(context.conversation_id),
                "message_ids": [
                    str(message.id)
                    for message in messages
                ],
                "read_at": read_at_str,
                "read_by": {
                    "id": str(context.current_user.id),
                    "name": context.current_user.name,
                },
            },
        )