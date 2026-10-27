from uuid import UUID
from fastapi import APIRouter, status, Depends, HTTPException, Query

from sqlalchemy.ext.asyncio import AsyncSession

from task_management_api.core.dependencies import get_current_user
from task_management_api.db.session import get_db

from task_management_api.users.model import User
from task_management_api.conversations.message_service import MessageService
from task_management_api.conversations.conversation_service import ConversationService
from task_management_api.conversations.message_schema import (
    MessageResponse,
    CreateMessageRequest,
    UpdateMessageRequest,
    MessageListResponse
)

from task_management_api.realtime.websocket.manager import (
    connection_manager
)
from task_management_api.realtime.websocket.events import (
    WebSocketEvent
)


message_router = APIRouter(
    prefix="/conversations",
    tags=["messages"]
)


@message_router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_message(
    conversation_id: UUID,
    message: CreateMessageRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> MessageResponse:
    try:
        created_message = await MessageService.create_message(
            session,
            current_user,
            conversation_id,
            message
        )

        await session.commit()
        
        
        other_participant_id = await ConversationService.get_other_participant_id(
            session=session,
            current_user=current_user,
            conversation_id=conversation_id,
        )

        await connection_manager.send_to_user(
            user_id=other_participant_id,
            event=WebSocketEvent.MESSAGE_CREATED,
            data={
                "id": str(created_message.id),
                "conversation_id": str(created_message.conversation_id),

                "sender": {
                    "id": str(created_message.sender.id),
                    "name": created_message.sender.name,
                    "email": created_message.sender.email,
                },

                "content": created_message.content,

                "reply_to": (
                    {
                        "id": str(created_message.reply_to.id),
                        "content": created_message.reply_to.content,
                        "sender": {
                            "id": str(created_message.reply_to.sender.id),
                            "name": created_message.reply_to.sender.name,
                            "email": created_message.reply_to.sender.email,
                        },
                        "is_deleted": created_message.reply_to.is_deleted,
                    }
                    if created_message.reply_to is not None
                    else None
                ),
                
                "attachments": [
                    {
                        "id": str(attachment.id),
                        "file_name": attachment.file_name,
                        "mime_type": attachment.mime_type,
                        "file_size": attachment.file_size,
                        "created_at": attachment.created_at.isoformat(),
                    }
                    for attachment in created_message.attachments
                ],

                "is_read": created_message.is_read,
                "is_edited": created_message.is_edited,
                "is_deleted": created_message.is_deleted,

                "created_at": created_message.created_at.isoformat(),
                "updated_at": created_message.updated_at.isoformat(),
            },
        )

        return created_message
    
    except Exception:
        await session.rollback()
        raise
        
        
        
@message_router.patch(
    "/{conversation_id}/messages/{message_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK
)
async def update_message(
    conversation_id: UUID,
    message_id: UUID,
    updated_message: UpdateMessageRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> MessageResponse:
    try:
        updated_message = await MessageService.update_message(
            session,
            current_user,
            updated_message,
            conversation_id,
            message_id
        )
        
        await session.commit()
        
        
        other_participant_id = await ConversationService.get_other_participant_id(
            session=session,
            current_user=current_user,
            conversation_id=conversation_id,
        ) 
        
        await connection_manager.send_to_user(
            user_id=other_participant_id,
            event=WebSocketEvent.MESSAGE_UPDATED,
            data={
                "id": str(updated_message.id),
                "conversation_id": str(updated_message.conversation_id),
                "sender": {
                    "id": str(updated_message.sender.id),
                    "name": updated_message.sender.name,
                    "email": updated_message.sender.email,
                },
                "content": updated_message.content,
                "is_read": updated_message.is_read,
                "is_edited": updated_message.is_edited,
                "is_deleted": updated_message.is_deleted,
                "created_at": updated_message.created_at.isoformat(),
                "updated_at": updated_message.updated_at.isoformat(),
            },
        )         
        
        return updated_message
    
    except Exception:
        await session.rollback()
        raise
    
    
@message_router.delete(
    "/{conversation_id}/messages/{message_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_message(
    conversation_id: UUID,
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> None:
    try:
        deleted_message = await MessageService.delete_message(
            session,
            current_user,
            conversation_id,
            message_id
        )
        await session.commit()
        
        other_participant_id = await ConversationService.get_other_participant_id(
            session=session,
            current_user=current_user,
            conversation_id=conversation_id,
        )

        await connection_manager.send_to_user(
            user_id=other_participant_id,
            event=WebSocketEvent.MESSAGE_DELETED,
            data={
                "id": str(deleted_message.id),
                "conversation_id": str(deleted_message.conversation_id),
                "is_deleted": deleted_message.is_deleted,
                "updated_at": deleted_message.updated_at.isoformat(),
            },
        )
    
    except Exception:
        await session.rollback()
        raise
        
        
@message_router.get(
    "/{conversation_id}/messages",
    response_model=MessageListResponse,
    status_code=status.HTTP_200_OK
)
async def get_messages(
    conversation_id: UUID,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> MessageListResponse:
    messages = await MessageService.get_messages(
        session,
        current_user,
        conversation_id,
        page,
        limit
    )
        
    return messages
    
    
    
    
@message_router.get(
    "/{conversation_id}/deleted/messages",
    response_model=MessageListResponse,
    status_code=status.HTTP_200_OK
)
async def get_deleted_task_messages(
    conversation_id: UUID,

    page: int = Query(
        default=1,
        ge=1
    ),

    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),

    current_user: User = Depends(get_current_user),

    session: AsyncSession = Depends(get_db),
) -> MessageListResponse:

    return await MessageService.get_deleted_task_messages(
        session=session,
        current_user=current_user,
        conversation_id=conversation_id,
        page=page,
        limit=limit
    )