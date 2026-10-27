from uuid import UUID
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload, join, joinedload
from sqlalchemy.ext.asyncio import AsyncSession


from task_management_api.conversations.conversation_model import PrivateConversation
from task_management_api.tasks.model import Task
from task_management_api.conversations.enums import ConversationStatus



class ConversationRepository:
    
    @staticmethod
    async def get_by_id(
        session: AsyncSession,
        conversation_id: UUID,
    ) -> PrivateConversation | None:
        statement = select(PrivateConversation).where(
            PrivateConversation.id == conversation_id,
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_active_by_id(
        session: AsyncSession,
        conversation_id: UUID,
    ) -> PrivateConversation | None:
        statement = select(PrivateConversation).where(
            PrivateConversation.id == conversation_id,
            PrivateConversation.status == ConversationStatus.ACTIVE
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_task_and_assignee(
        session: AsyncSession,
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
        
        result = await session.execute(statement)
        return result.scalar_one_or_none()
    
    
    @staticmethod
    async def get_active_by_participant(
        session: AsyncSession,
        user_id: UUID,
    ) -> list[PrivateConversation]:
        statement = (
            select(PrivateConversation)
            .join(PrivateConversation.task)
            .where(
                PrivateConversation.status == ConversationStatus.ACTIVE,
                or_(
                    PrivateConversation.assignee_id == user_id,
                    Task.owner_id == user_id,
                ),
            )
            .options(
                joinedload(PrivateConversation.task)
                .joinedload(Task.owner)
            )
        )

        result = await session.execute(statement)
        return result.scalars().all()
    
    
    @staticmethod
    async def get_conversations_by_task(
        session: AsyncSession,
        task_id: UUID,
        assignee_id: UUID | None = None,
        page: int = 1,
        limit: int = 10
    ) -> tuple[list[PrivateConversation], int]:

        conditions = [
            PrivateConversation.task_id == task_id,
            PrivateConversation.status == ConversationStatus.ACTIVE
        ]

        if assignee_id is not None:
            conditions.append(
                PrivateConversation.assignee_id == assignee_id
            )

        total = (await session.execute(
            select(func.count())
            .select_from(PrivateConversation)
            .where(*conditions)
        )).scalar_one()

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
        
        result = await session.execute(statement)

        conversations = result.scalars().all()

        return conversations, total
        
    
    @staticmethod
    async def create(
        session: AsyncSession,
        task_id: UUID,
        assignee_id: UUID,
    ) -> PrivateConversation:
        
        conversation = PrivateConversation(
            task_id=task_id,
            assignee_id=assignee_id,
            status = ConversationStatus.ACTIVE
        )
        
        session.add(conversation)
        await session.flush()
        return conversation
    
    
    @staticmethod
    async def reactive(
        session: AsyncSession,
        conversation: PrivateConversation
    ) -> PrivateConversation:
        conversation.status = ConversationStatus.ACTIVE
        await session.flush()
        return conversation
    
    
    @staticmethod
    async def close(
        session: AsyncSession,
        conversation: PrivateConversation
    ) -> PrivateConversation:
        conversation.status = ConversationStatus.CLOSED
        await session.flush()
        return conversation