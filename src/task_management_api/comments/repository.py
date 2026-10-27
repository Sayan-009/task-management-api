from uuid import UUID
from fastapi import Query
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from task_management_api.users.model import User
from task_management_api.comments.model import TaskComment
from task_management_api.comments.schema import (
    CreateComment,
    UpdateComment
)



class CommentRepository:
    
    @staticmethod
    async def create(
        session: AsyncSession,
        task_id: UUID,
        author: User,
        comment_data: CreateComment,
    ) -> TaskComment:

        comment = TaskComment(
            content=comment_data.content,
            task_id=task_id,
            author=author
        )

        session.add(comment)
        await session.flush()

        return comment
    
    
    @staticmethod
    async def get_active_comment(
        session: AsyncSession,
        comment_id: UUID
    ) -> TaskComment | None:
        statement = select(TaskComment).where(
            TaskComment.id == comment_id,
            TaskComment.is_deleted.is_(False)
        )
        
        result = await session.execute(statement)
        
        return result.scalar_one_or_none()
    
    
    @staticmethod
    async def update(
        session: AsyncSession,
        comment: TaskComment,
        update_data: UpdateComment,
    ) -> TaskComment:
        comment.content = update_data.content
        comment.is_edited = True
        comment.edited_at = datetime.now(timezone.utc)
        
        await session.flush()
        
        return comment
    
    
    @staticmethod
    async def soft_delete(
        session: AsyncSession,
        comment: TaskComment,
    ) -> TaskComment:
        comment.is_deleted = True
        comment.deleted_at = datetime.now(timezone.utc)
        
        await session.flush()
        return comment


    @staticmethod
    async def comments_by_task_id(
        session: AsyncSession,
        task_id: UUID,
        page: int,
        limit: int,
    ) -> tuple[list[TaskComment], int]:
        

        total = (await session.execute(
            select(func.count())
            .select_from(TaskComment)
            .where(
                TaskComment.task_id == task_id
            )
        )).scalar_one()

   
        offset = (page - 1) * limit

  
        statement = (
            select(TaskComment)
            .where(
                TaskComment.task_id == task_id
            )
            .options(
                selectinload(TaskComment.author)
            )
            .order_by(
                TaskComment.created_at.asc()
            )
            .limit(limit)
            .offset(offset)
        )
        
        result = await session.execute(statement)

        comments = result.scalars().all()

        return comments, total