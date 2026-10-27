from uuid import UUID
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from task_management_api.conversations.conversation_model import PrivateConversation
from task_management_api.conversations.message_model import PrivateMessage
from task_management_api.conversations.attachment_model import MessageAttachment

class AttachmentRepository:
    
    @staticmethod
    async def create(
        session: AsyncSession,
        attachment: MessageAttachment
    ) -> MessageAttachment:
        
        session.add(attachment)
        
        await session.flush()
        
        return attachment
    
    @staticmethod
    async def get_by_id(
        session: AsyncSession,
        attachment_id: UUID,
    ) -> MessageAttachment | None:
        
        statement = select(MessageAttachment).where(
            MessageAttachment.id == attachment_id
        )
        
        result = await session.execute(statement)
        
        return result.scalar_one_or_none()

    
    @staticmethod
    async def get_by_ids(
        session: AsyncSession,
        attachment_ids: list[UUID],
    ) -> list[MessageAttachment]:
        
        statement = select(MessageAttachment).where(
            MessageAttachment.id.in_(attachment_ids)
        )
        
        result = await session.execute(statement)
        
        return result.scalars().all()

    
    @staticmethod
    async def get_with_message(
        session: AsyncSession,
        attachment_id: UUID,
    ) -> MessageAttachment | None:
        
        statement = select(MessageAttachment).where(
            MessageAttachment.id == attachment_id
        ).options(
            joinedload(MessageAttachment.message)
            .joinedload(PrivateMessage.conversation)
            .joinedload(PrivateConversation.task)
        )
        
        result = await session.execute(statement)
        
        return result.scalar_one_or_none()
    
