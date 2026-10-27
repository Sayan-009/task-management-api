from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import (
   select,
   func
)
from sqlalchemy.orm import (
   selectinload
)
from sqlalchemy.ext.asyncio import AsyncSession

from task_management_api.users.model import User
from task_management_api.conversations.message_model import PrivateMessage
from task_management_api.conversations.message_schema import (
   CreateMessageRequest,
   UpdateMessageRequest,
)



class MessageRepository:
   
   @staticmethod
   async def create(
      session: AsyncSession,
      conversation_id: UUID,
      sender: User,
      message: CreateMessageRequest,
   ) -> PrivateMessage:
      new_message = PrivateMessage(
         conversation_id=conversation_id,
         sender=sender,
         content=message.content,
         reply_to_message_id=message.reply_to_message_id,
          attachments=[],
      )
      
      session.add(new_message)
      await session.flush()
      
      return new_message
   
   @staticmethod
   async def get_by_id(
      session: AsyncSession,
      message_id: UUID,
   ) -> PrivateMessage | None:
      statement = select(PrivateMessage).where(PrivateMessage.id == message_id)
      result = await session.execute(statement)
      return result.scalar_one_or_none()
   
   
   @staticmethod
   async def get_by_conversation_and_id(
      session: AsyncSession,
      conversation_id: UUID,
      message_id: UUID,
   ) -> PrivateMessage | None:

      statement = (
         select(PrivateMessage)
         .options(
            selectinload(PrivateMessage.attachments),
            selectinload(PrivateMessage.sender),
            selectinload(PrivateMessage.reply_to)
                .selectinload(PrivateMessage.sender),
         )
         .where(
               PrivateMessage.id == message_id,
               PrivateMessage.conversation_id == conversation_id,
         )
      )

      result = await session.execute(statement)
      return result.scalar_one_or_none()
   
   @staticmethod
   async def get_messages(
      session: AsyncSession,
      conversation_id: UUID,
      page: int = 1,
      limit: int = 10,
   ) -> tuple[list[PrivateMessage], int]:

      total = (await session.execute(
         select(func.count())
         .select_from(PrivateMessage)
         .where(
               PrivateMessage.conversation_id == conversation_id
         )
      )).scalar_one()

      offset = (page - 1) * limit

      statement = (
         select(PrivateMessage)
         .where(
               PrivateMessage.conversation_id == conversation_id
         )
         .options(
               selectinload(PrivateMessage.sender),
               selectinload(PrivateMessage.attachments),
               selectinload(PrivateMessage.reply_to)
               .selectinload(PrivateMessage.sender),
         )
         .order_by(
               PrivateMessage.created_at.asc()
         )
         .limit(limit)
         .offset(offset)
      )
      
      result = await session.execute(statement)

      messages = result.scalars().all()

      return messages, total
   
   
   @staticmethod
   async def update(
      session: AsyncSession,
      message: PrivateMessage,
      updated_message: UpdateMessageRequest,
   ) -> PrivateMessage:
      message.content = updated_message.content
      message.is_edited = True
      message.edited_at = datetime.now(timezone.utc)
      
      await session.flush()
      return message
   
   
   @staticmethod
   async def soft_delete(
      session: AsyncSession,
      message: PrivateMessage
   ) -> None:
      
      message.is_deleted = True
      message.deleted_at = datetime.now(timezone.utc)
      
      await session.flush()
      
      
   @staticmethod
   async def mark_messages_as_read(
      session: AsyncSession,
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
      
      result = await session.execute(statement)

      messages = result.scalars().all()

      read_at = datetime.now(timezone.utc)

      for message in messages:
         message.is_read = True
         message.read_at = read_at

      await session.flush()

      return messages   