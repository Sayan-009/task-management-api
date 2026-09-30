import math
from uuid import UUID

from sqlalchemy.orm import Session

from task_management_api.conversations.conversation_model import PrivateConversation
from task_management_api.conversations.conversation_repository import ConversationRepository
from task_management_api.tasks.repository import TaskRepository
from task_management_api.conversations.enums import ConversationStatus
from task_management_api.users.model import User
from task_management_api.tasks.assignee_model import TaskAssignee
from task_management_api.conversations.conversation_schema import (
    ConversationListResponse
)
from task_management_api.core.exceptions import (
    TaskNotFoundError,
    ForbiddenOperationError,
    ConversationNotFoundError
)


class ConversationService:
    
    
    @staticmethod
    def create_or_reactive(
        session: Session,
        task_id: UUID,
        assignee_id: UUID
    ) -> PrivateConversation:

        conversation = ConversationRepository.get_by_task_and_assignee(
            session,
            task_id,
            assignee_id
        )
        
        if conversation is None:
            return ConversationRepository.create(
                session,
                task_id,
                assignee_id
            ) 
            
        if conversation.status == ConversationStatus.CLOSED:
            return ConversationRepository.reactive(
                session,
                conversation
            )
            
            
        return conversation
    
    
    
    @staticmethod
    def close_conversation(
        session: Session,
        task_id: UUID,
        assignee_id: UUID,
    ) -> PrivateConversation | None:
        conversation = ConversationRepository.get_by_task_and_assignee(
            session,
            task_id,
            assignee_id
        )
        
        if conversation is None:
            return None
            
        if conversation.status == ConversationStatus.ACTIVE:
            return ConversationRepository.close(
                session,
                conversation
            )
            
        return conversation
    
    
    @staticmethod
    def get_related_user_ids(
        session: Session,
        user_id: UUID
    ) -> set[UUID]:
        related_user_ids: set[UUID] = set()
        
        related_conversations = ConversationRepository.get_active_by_participant(
            session,
            user_id,
        )
        
        for conversation in related_conversations:
            owner_id = conversation.task.owner_id
            assignee_id = conversation.assignee_id
            if owner_id == user_id:
                related_user_ids.add(assignee_id)
            else:
                related_user_ids.add(owner_id)
                
        return related_user_ids
    
    
    @staticmethod
    def get_conversation(
        session: Session,
        current_user: User,
        task_id: UUID,
        page: int = 1,
        limit: int = 10
    ) -> ConversationListResponse:
        
        task = TaskRepository.get_active_by_id(
            session,
            task_id
        )
        
        if task is None:
            raise TaskNotFoundError(
                "Task not found"
            )
            
        is_owner = (task.owner_id == current_user.id)  
        is_assignee = TaskRepository.get_by_task_user(
            session,
            task_id,
            current_user.id,
        ) is not None
        
        if not is_owner and not is_assignee:
            raise ForbiddenOperationError(
                "You don't have permission to see the conversations"
            )
            
        conversations, total = ConversationRepository.get_conversations_by_task(
            session=session,
            task_id=task_id,
            assignee_id=current_user.id if is_assignee else None,
            page=page,
            limit=limit
        )
        
        
        total_pages = (
            math.ceil(total / limit)
            if total > 0
            else 0
        )       
        
        
        return ConversationListResponse(
            items=conversations,
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages
        )
        
        
        
    @staticmethod
    def get_deleted_task_conversations(
        session: Session,
        current_user: User,
        task_id: UUID,
        page: int = 1,
        limit: int = 10
    ) -> ConversationListResponse:

        task = TaskRepository.get_by_id(
            session,
            task_id
        )

        if task is None:
            raise TaskNotFoundError(
                "Task not found"
            )

        if not task.is_deleted:
            raise TaskNotFoundError(
                "Task is not deleted"
            )

        # Only the task owner can access it
        if task.owner_id != current_user.id:
            raise ForbiddenOperationError(
                "You don't have permission to see these conversations"
            )

        conversations, total = (
            ConversationRepository.get_conversations_by_task(
                session=session,
                task_id=task_id,
                page=page,
                limit=limit
            )
        )

        total_pages = (
            math.ceil(total / limit)
            if total > 0
            else 0
        )

        return ConversationListResponse(
            items=conversations,
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages
        )
        
        
    @staticmethod
    def validate_conversation_access(
        session: Session,
        current_user: User,
        conversation_id: UUID,
    ) -> PrivateConversation:

        conversation = ConversationRepository.get_active_by_id(
            session,
            conversation_id,
        )

        if conversation is None:
            raise ConversationNotFoundError(
                "Active conversation not found"
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

        return conversation
    
    @staticmethod
    def get_other_participant_id(
        session: Session,
        current_user: User,
        conversation_id: UUID,
    ) -> UUID:
        conversation = ConversationRepository.get_active_by_id(
            session,
            conversation_id,
        )

        if conversation is None:
            raise ConversationNotFoundError(
                "Active conversation not found"
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
            
        if is_owner:
            return conversation.assignee_id
        
        return task.owner_id