from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from task_management_api.conversations.conversation_model import PrivateConversation
from task_management_api.conversations.message_model import PrivateMessage
from task_management_api.conversations.attachment_model import MessageAttachment

class AttachmentRepository:
    
    @staticmethod
    def create(
        session: Session,
        attachment: MessageAttachment
    ) -> MessageAttachment:
        
        session.add(attachment)
        
        session.flush()
        
        return attachment
    
    @staticmethod
    def get_by_id(
        session: Session,
        attachment_id: UUID,
    ) -> MessageAttachment | None:
        
        statement = select(MessageAttachment).where(
            MessageAttachment.id == attachment_id
        )
        
        return session.execute(statement).scalar_one_or_none()

    
    @staticmethod
    def get_by_ids(
        session: Session,
        attachment_ids: list[UUID],
    ) -> list[MessageAttachment]:
        
        statement = select(MessageAttachment).where(
            MessageAttachment.id.in_(attachment_ids)
        )
        
        return session.execute(statement).scalars().all()
    
    
    @staticmethod
    def get_with_message(
        session: Session,
        attachment_id: UUID,
    ) -> MessageAttachment | None:
        
        statement = select(MessageAttachment).where(
            MessageAttachment.id == attachment_id
        ).options(
            joinedload(MessageAttachment.message)
            .joinedload(PrivateMessage.conversation)
            .joinedload(PrivateConversation.task)
        )
        
        return session.execute(statement).scalar_one_or_none()
    
