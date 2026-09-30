from task_management_api.realtime.websocket.registry import EventRegistry
from task_management_api.realtime.websocket.events import WebSocketEvent
from task_management_api.realtime.websocket.context import WebSocketEventContext
from task_management_api.realtime.websocket.manager import connection_manager


from task_management_api.conversations.conversation_service import ConversationService




@EventRegistry.register(WebSocketEvent.TYPING_STOP)
class TypingStopHandler:
    
    @staticmethod
    async def handle(
        context: WebSocketEventContext,
    ) -> None:
        
        other_participant_id = ConversationService.get_other_participant_id(
            session=context.session,
            current_user=context.current_user,
            conversation_id=context.conversation_id,
        )
        
        await connection_manager.send_to_user(
            user_id=other_participant_id,
            event=WebSocketEvent.USER_TYPING_STOPPED,
            data={
                "conversation_id": str(context.conversation_id),
                "user": {
                    "id": str(context.current_user.id),
                    "name": context.current_user.name
                },
            },
        )