from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload


from task_management_api.conversations.conversation_model import PrivateConversation
from task_management_api.tasks.model import Task
from task_management_api.conversations.enums import ConversationStatus



class ConversationRepository:
    
    @staticmethod
    def get_by_id(
        session: Session,
        conversation_id: UUID,
    ) -> PrivateConversation | None:
        statement = select(PrivateConversation).where(
            PrivateConversation.id == conversation_id,
        )
        return session.execute(statement).scalar_one_or_none()
    
    @staticmethod
    def get_active_by_id(
        session: Session,
        conversation_id: UUID,
    ) -> PrivateConversation | None:
        statement = select(PrivateConversation).where(
            PrivateConversation.id == conversation_id,
            PrivateConversation.status == ConversationStatus.ACTIVE
        )
        return session.execute(statement).scalar_one_or_none()
    
    @staticmethod
    def get_by_task_and_assignee(
        session: Session,
        task_id: UUID,
        assignee_id: UUID
    ) -> PrivateConversation | None:
        statement = (
            select(PrivateConversation)
            .where(
                PrivateConversation.task_id == task_id,
                PrivateConversation.assignee_id == assignee_id
            )
        )
        
        return session.execute(statement).scalar_one_or_none()
    
    
    @staticmethod
    def get_conversations_by_task(
        session: Session,
        task_id: UUID,
        assignee_id: UUID | None = None,
        page: int = 1,
        limit: int = 10
    ) -> tuple[list[PrivateConversation], int]:

        conditions = [
            PrivateConversation.task_id == task_id
        ]

        if assignee_id is not None:
            conditions.append(
                PrivateConversation.assignee_id == assignee_id
            )

        total = session.execute(
            select(func.count())
            .select_from(PrivateConversation)
            .where(*conditions)
        ).scalar_one()

        offset = (page - 1) * limit

        statement = (
            select(PrivateConversation)
            .where(*conditions)
            .options(
                selectinload(PrivateConversation.assignee)
            )
            .order_by(
                PrivateConversation.created_at.asc()
            )
            .limit(limit)
            .offset(offset)
        )

        conversations = (
            session.execute(statement)
            .scalars()
            .all()
        )

        return conversations, total
        
    
    @staticmethod
    def create(
        session: Session,
        task_id: UUID,
        assignee_id: UUID,
    ) -> PrivateConversation:
        
        conversation = PrivateConversation(
            task_id=task_id,
            assignee_id=assignee_id,
            status = ConversationStatus.ACTIVE
        )
        
        session.add(conversation)
        session.flush()
        return conversation
    
    
    @staticmethod
    def reactive(
        session: Session,
        conversation: PrivateConversation
    ) -> PrivateConversation:
        conversation.status = ConversationStatus.ACTIVE
        session.flush()
        return conversation
    
    
    @staticmethod
    def close(
        session: Session,
        conversation: PrivateConversation
    ) -> PrivateConversation:
        conversation.status = ConversationStatus.CLOSED
        session.flush()
        return conversation