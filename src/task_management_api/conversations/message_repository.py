from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import (
   select,
   func
)
from sqlalchemy.orm import (
   Session,
   selectinload
)

from task_management_api.users.model import User
from task_management_api.conversations.message_model import PrivateMessage
from task_management_api.conversations.message_schema import (
   CreateMessageRequest,
   UpdateMessageRequest,
   MessageResponse,
)



class MessageRepository:
   
   @staticmethod
   def create(
      session: Session,
      conversation_id: UUID,
      sender: User,
      message: CreateMessageRequest,
   ) -> PrivateMessage:
      new_message = PrivateMessage(
         conversation_id=conversation_id,
         sender=sender,
         content=message.content,
         reply_to_message_id=message.reply_to_message_id,
      )
      
      session.add(new_message)
      session.flush()
      
      return new_message
   
   @staticmethod
   def get_by_id(
      session: Session,
      message_id: UUID,
   ) -> PrivateMessage | None:
      statement = select(PrivateMessage).where(PrivateMessage.id == message_id)
      return session.execute(statement).scalar_one_or_none()
   
   
   @staticmethod
   def get_by_conversation_and_id(
      session: Session,
      conversation_id: UUID,
      message_id: UUID,
   ) -> PrivateMessage | None:

      statement = (
         select(PrivateMessage)
         .where(
               PrivateMessage.id == message_id,
               PrivateMessage.conversation_id == conversation_id,
         )
      )

      return session.execute(statement).scalar_one_or_none()
   
   @staticmethod
   def get_messages(
      session: Session,
      conversation_id: UUID,
      page: int = 1,
      limit: int = 10,
   ) -> tuple[list[PrivateMessage], int]:

      total = session.execute(
         select(func.count())
         .select_from(PrivateMessage)
         .where(
               PrivateMessage.conversation_id == conversation_id
         )
      ).scalar_one()

      offset = (page - 1) * limit

      statement = (
         select(PrivateMessage)
         .where(
               PrivateMessage.conversation_id == conversation_id
         )
         .options(
               selectinload(PrivateMessage.sender),
               selectinload(PrivateMessage.reply_to)
               .selectinload(PrivateMessage.sender)
         )
         .order_by(
               PrivateMessage.created_at.asc()
         )
         .limit(limit)
         .offset(offset)
      )

      messages = session.execute(
         statement
      ).scalars().all()

      return messages, total
   
   
   @staticmethod
   def update(
      session: Session,
      message: PrivateMessage,
      updated_message: UpdateMessageRequest,
   ) -> PrivateMessage:
      message.content = updated_message.content
      message.is_edited = True
      message.edited_at = datetime.now(timezone.utc)
      
      session.flush()
      return message
   
   
   @staticmethod
   def soft_delete(
      session: Session,
      message: PrivateMessage
   ) -> None:
      
      message.is_deleted = True
      message.deleted_at = datetime.now(timezone.utc)
      
      session.flush()
      
      
   @staticmethod
   def mark_messages_as_read(
      session: Session,
      conversation_id: UUID,
      current_user_id: UUID,
      message_ids: list[UUID],
   ) -> list[PrivateMessage]:

      statement = (
         select(PrivateMessage)
         .where(
               PrivateMessage.conversation_id == conversation_id,
               PrivateMessage.id.in_(message_ids),
               PrivateMessage.sender_id != current_user_id,
               PrivateMessage.is_read.is_(False),
               PrivateMessage.is_deleted.is_(False),
         )
      )

      messages = (
         session.execute(statement)
         .scalars()
         .all()
      )

      read_at = datetime.now(timezone.utc)

      for message in messages:
         message.is_read = True
         message.read_at = read_at

      session.flush()

      return messages   