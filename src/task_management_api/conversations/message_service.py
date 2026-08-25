import math
from uuid import UUID
from datetime import (datetime, timezone, timedelta)
from sqlalchemy.orm import Session

from task_management_api.users.model import User
from task_management_api.tasks.repository import TaskRepository
from task_management_api.conversations.enums import ConversationStatus
from task_management_api.conversations.message_repository import MessageRepository
from task_management_api.conversations.conversation_repository import (
    ConversationRepository
)
from task_management_api.conversations.message_schema import (
    MessageBody,
    MessageResponse,
    MessageListResponse,
    SenderDetails
)
from task_management_api.core.exceptions import (
    ConversationNotFoundError,
    TaskNotFoundError,
    ForbiddenOperationError,
    MessageAlreadyDeletedError,
    MessageNotFoundError,
    MessageEditLimitExceededError
)

EDIT_TIME_LIMIT = timedelta(minutes=15)

class MessageService:
    
    @staticmethod
    def create_message(
        session: Session,
        current_user: User,
        conversation_id: UUID,
        message: MessageBody
    ) -> MessageResponse:
            
        conversation = ConversationRepository.get_active_by_id(
            session,
            conversation_id
        )
        
        if conversation is None:
            raise ConversationNotFoundError(
                "Conversation not found"
            )
            
        task = TaskRepository.get_active_by_id(
            session,
            conversation.task_id
        )

        if task is None:
            raise TaskNotFoundError(
                "Task not found"
            )
        
        is_owner = task.owner_id == current_user.id
        is_assignee = conversation.assignee_id == current_user.id
        
        if not is_owner and not is_assignee:
            raise ForbiddenOperationError(
                "You don't have permission to write the message"
            )
            
        return MessageRepository.create(
            session,
            conversation_id,
            current_user,
            message,
        )
        
        
    @staticmethod
    def update_message(
        session: Session,
        current_user: User,
        updated_message: MessageBody,
        conversation_id: UUID,
        message_id: UUID
    ) -> MessageResponse:

        conversation = ConversationRepository.get_active_by_id(
            session,
            conversation_id,
        )

        if conversation is None:
            raise ConversationNotFoundError(
                "Conversation not found"
            )

        message = MessageRepository.get_by_conversation_and_id(
            session,
            conversation_id,
            message_id,
        )

        if message is None:
            raise MessageNotFoundError(
                "Message not found"
            )

        if message.sender_id != current_user.id:
            raise ForbiddenOperationError(
                "You don't have permission to update this message"
            )
            
        if message.is_deleted:
            raise MessageAlreadyDeletedError(
                "Message is already deleted"
            )

        if datetime.now(timezone.utc) - message.created_at > EDIT_TIME_LIMIT:
            raise MessageEditLimitExceededError(
                "The message edit time limit has expired"
            )
            
        if message.content == updated_message.content:
            raise ValueError(
                "You can't update a message with the same content"
            )



        return MessageRepository.update(
            session,
            message,
            updated_message,
        )
        
    @staticmethod
    def delete_message(
        session: Session,
        current_user: User,
        conversation_id: UUID,
        message_id: UUID,
    ) -> None:

        conversation = ConversationRepository.get_active_by_id(
            session,
            conversation_id,
        )

        if conversation is None:
            raise ConversationNotFoundError(
                "Conversation not found"
            )

        message = MessageRepository.get_by_conversation_and_id(
            session,
            conversation_id,
            message_id,
        )

        if message is None:
            raise MessageNotFoundError(
                "Message not found"
            )

        if message.is_deleted:
            raise MessageAlreadyDeletedError(
                "Message is already deleted"
            )

        if message.sender_id != current_user.id:
            raise ForbiddenOperationError(
                "You don't have permission to delete this message"
            )

        MessageRepository.soft_delete(
            session,
            message,
        )
        
    @staticmethod
    def get_messages(
        session: Session,
        current_user: User,
        conversation_id: UUID,
        page: int = 1,
        limit: int = 10,
    ) -> MessageListResponse:

        conversation = ConversationRepository.get_by_id(
            session,
            conversation_id
        )

        if conversation is None:
            raise ConversationNotFoundError(
                "Conversation not found"
            )

        task = TaskRepository.get_active_by_id(
            session,
            conversation.task_id
        )

        if task is None:
            raise TaskNotFoundError(
                "Task not found"
            )

        is_owner = task.owner_id == current_user.id
        is_assignee = conversation.assignee_id == current_user.id

        if not is_owner and not is_assignee:
            raise ForbiddenOperationError(
                "You don't have permission to see messages"
            )

        # Assignee cannot access closed conversation
        if (
            is_assignee
            and conversation.status == ConversationStatus.CLOSED
        ):
            raise ConversationNotFoundError(
                "Conversation not found"
            )

        messages, total = MessageRepository.get_messages(
            session,
            conversation_id,
            page,
            limit
        )

        message_list = []

        for message in messages:

            content = message.content

            if message.is_deleted:
                content = "[This message was deleted]"

            message_list.append(
                MessageResponse(
                    id=message.id,
                    conversation_id=message.conversation_id,
                    sender=SenderDetails(
                        id=message.sender.id,
                        name=message.sender.name,
                        email=message.sender.email,
                    ),
                    content=content,
                    is_read=message.is_read,
                    read_at=message.read_at,
                    is_edited=message.is_edited,
                    edited_at=message.edited_at,
                    is_deleted=message.is_deleted,
                    deleted_at=message.deleted_at,
                    created_at=message.created_at,
                    updated_at=message.updated_at,
                )
            )

        total_pages = (
            math.ceil(total / limit)
            if total > 0
            else 0
        )

        return MessageListResponse(
            items=message_list,
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        )