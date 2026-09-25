import math
from uuid import UUID
from datetime import (datetime, timezone, timedelta)
from sqlalchemy.orm import Session

from task_management_api.users.model import User
from task_management_api.tasks.repository import TaskRepository
from task_management_api.conversations.enums import ConversationStatus
from task_management_api.conversations.message_repository import MessageRepository
from task_management_api.conversations.attachment_repository import AttachmentRepository
from task_management_api.conversations.conversation_repository import (
    ConversationRepository
)
from task_management_api.conversations.message_schema import (
    CreateMessageRequest,
    UpdateMessageRequest,
    MessageResponse,
    MessageListResponse,
    ReplyMessageResponse,
    SenderDetails,
)
from task_management_api.core.exceptions import (
    ConversationNotFoundError,
    TaskNotFoundError,
    ForbiddenOperationError,
    MessageAlreadyDeletedError,
    MessageNotFoundError,
    MessageEditLimitExceededError,
    AttachmentNotFoundError,
    AttachmentAlreadyAttachedError,
)

from task_management_api.conversations.attachment_schema import (
    AttachmentResponse
)

EDIT_TIME_LIMIT = timedelta(minutes=15)

class MessageService:
    
    @staticmethod
    def _build_message_response(
        message
    ) -> MessageResponse:

        content = message.content

        if message.is_deleted:
            content = "[This message was deleted]"

        reply_to = None

        if message.reply_to is not None:

            reply_content = message.reply_to.content

            if message.reply_to.is_deleted:
                reply_content = "[This message was deleted]"

            reply_to = ReplyMessageResponse(
                id=message.reply_to.id,
                content=reply_content,
                sender=SenderDetails(
                    id=message.reply_to.sender.id,
                    name=message.reply_to.sender.name,
                    email=message.reply_to.sender.email,
                ),
                is_deleted=message.reply_to.is_deleted,
            )

        return MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,

            sender=SenderDetails(
                id=message.sender.id,
                name=message.sender.name,
                email=message.sender.email,
            ),

            content=content,
            reply_to=reply_to,
            
            attachments=[
                AttachmentResponse(
                    id=attachment.id,
                    file_name=attachment.file_name,
                    mime_type=attachment.mime_type,
                    file_size=attachment.file_size,
                    created_at=attachment.created_at,
                )
                for attachment in message.attachments
            ],

            is_read=message.is_read,
            read_at=message.read_at,

            is_edited=message.is_edited,
            edited_at=message.edited_at,

            is_deleted=message.is_deleted,
            deleted_at=message.deleted_at,

            created_at=message.created_at,
            updated_at=message.updated_at,
        )
    
    @staticmethod
    def create_message(
        session: Session,
        current_user: User,
        conversation_id: UUID,
        message: CreateMessageRequest,
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
            
            
        if message.reply_to_message_id is not None:
            replied_message = (
                MessageRepository.get_by_conversation_and_id(
                    session=session,
                    conversation_id=conversation_id,
                    message_id=message.reply_to_message_id,
                )
            )

            if replied_message is None:
                raise MessageNotFoundError(
                    "The message you are trying to reply to was not found"
                )
                
        attachments = []
                
        if message.attachment_ids:
            attachments = AttachmentRepository.get_by_ids(
                session,
                message.attachment_ids,
            )

            if len(attachments) != len(message.attachment_ids):
                raise AttachmentNotFoundError(
                    "One or more attachments were not found"
                )
                
            for attachment in attachments:
                if attachment.uploaded_by != current_user.id:
                    raise ForbiddenOperationError(
                        "You don't have permission to use one or more attachments"
                    )
                    
            for attachment in attachments:
                if attachment.message_id is not None:
                    raise AttachmentAlreadyAttachedError(
                        "One or more attachments are already attached to a message"
                    )
            
        created_message = MessageRepository.create(
            session,
            conversation_id,
            current_user,
            message,
        )
        
        created_message.attachments.extend(attachments)
        
        # for attachment in attachments:
        #     attachment.message_id = created_message.id

        return MessageService._build_message_response(
            created_message
        )
        
        
    @staticmethod
    def update_message(
        session: Session,
        current_user: User,
        updated_message: UpdateMessageRequest,
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
        
        return message
        
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

        message_list = [
            MessageService._build_message_response(message)
            for message in messages
        ]

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
        
        
    @staticmethod
    def get_deleted_task_messages(
        session: Session,
        current_user: User,
        conversation_id: UUID,
        page: int = 1,
        limit: int = 10,
    ) -> MessageListResponse:

        # Get conversation
        conversation = ConversationRepository.get_by_id(
            session,
            conversation_id
        )

        if conversation is None:
            raise ConversationNotFoundError(
                "Conversation not found"
            )

        # Get task, including soft-deleted tasks
        task = TaskRepository.get_by_id(
            session,
            conversation.task_id
        )

        if task is None:
            raise TaskNotFoundError(
                "Task not found"
            )

        # This endpoint is only for deleted tasks
        if not task.is_deleted:
            raise TaskNotFoundError(
                "Task is not deleted"
            )

        # Only task owner can see messages
        if task.owner_id != current_user.id:
            raise ForbiddenOperationError(
                "You don't have permission to see these messages"
            )

        # Fetch messages using existing repository
        messages, total = MessageRepository.get_messages(
            session=session,
            conversation_id=conversation_id,
            page=page,
            limit=limit
        )

        messages_list = [
            MessageService._build_message_response(message)
            for message in messages
        ]

        total_pages = (
            math.ceil(total / limit)
            if total > 0
            else 0
        )

        return MessageListResponse(
            items=messages_list,
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages
        )
        
    @staticmethod
    def mark_messages_as_read(
        session: Session,
        current_user: User,
        conversation_id: UUID,
        message_ids: list[UUID],
    ):
        
        conversation = ConversationRepository.get_active_by_id(
            session,
            conversation_id,
        )

        if conversation is None:
            raise ConversationNotFoundError(
                "Conversation not found"
            )

        task = TaskRepository.get_active_by_id(
            session,
            conversation.task_id,
        )

        if task is None:
            raise TaskNotFoundError(
                "Task not found"
            )

        is_owner = task.owner_id == current_user.id
        is_assignee = conversation.assignee_id == current_user.id

        if not is_owner and not is_assignee:
            raise ForbiddenOperationError(
                "You don't have permission to access this conversation"
            )

        messages = MessageRepository.mark_messages_as_read(
            session=session,
            conversation_id=conversation_id,
            current_user_id=current_user.id,
            message_ids=message_ids,
        )

        return messages