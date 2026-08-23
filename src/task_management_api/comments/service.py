import math
from uuid import UUID
from fastapi import Query
from sqlalchemy.orm import Session

from task_management_api.users.model import User
from task_management_api.tasks.repository import TaskRepository
from task_management_api.comments.repository import CommentRepository
from task_management_api.core.exceptions import (
    TaskNotFoundError,
    ForbiddenOperationError,
    CommentNotFoundError, 
    UpdateSameContentError
)
from task_management_api.comments.schema import (
    CreateComment,
    CommentResponse,
    UpdateComment,
    AuthorDetails,
    CommentListResponse
)



class CommentService:
    
    @staticmethod
    def create_comment(
        session: Session,
        task_id: UUID,
        current_user: User,
        comment_data: CreateComment,
    ) -> CommentResponse:

        task = TaskRepository.get_active_by_id(
            session,
            task_id
        )

        if task is None:
            raise TaskNotFoundError(
                "Task not found"
            )

        is_owner = current_user.id == task.owner_id

        is_task_assignee = TaskRepository.get_by_task_user(
            session,
            task_id,
            user_id=current_user.id
        ) is not None

        if not is_owner and not is_task_assignee:
            raise ForbiddenOperationError(
                "You don't have permission to write the comment for this task"
            )

        return CommentRepository.create(
            session,
            task_id,
            current_user,
            comment_data,
        )
    
    
    @staticmethod
    def update_comment(
        session: Session,
        comment_id: UUID,
        current_user: User,
        update_data: UpdateComment,
    ) -> CommentResponse:
        comment = CommentRepository.get_active_comment(
            session,
            comment_id
        )
        
        if not comment:
            raise CommentNotFoundError(
                "Comment not found"
            )
            
        if comment.author_id != current_user.id:
            raise ForbiddenOperationError(
                "You don't have permission to update this comment"
            )   
            
        if comment.content == update_data.content:
            raise UpdateSameContentError(
                "You can't update your comment by same comment"
            )
            
        updated_comment = CommentRepository.update(
            session,
            comment,
            update_data,
        )
        
        return CommentResponse(
            id = updated_comment.id,
            content = updated_comment.content,
            task_id = updated_comment.task_id,
            author = AuthorDetails(
                id=current_user.id,
                name=current_user.name,
                email=current_user.email,
            ),
            is_edited=updated_comment.is_edited,
            edited_at=updated_comment.edited_at,
            is_deleted=updated_comment.is_deleted,
            deleted_at=updated_comment.deleted_at,
            created_at=updated_comment.created_at,
            updated_at=updated_comment.updated_at,
        )
        
        
    @staticmethod
    def delete_comment(
        session: Session,
        comment_id: UUID,
        current_user: User
    ) -> None:
        comment = CommentRepository.get_active_comment(
            session,
            comment_id
        )
        
        if not comment:
            raise CommentNotFoundError(
                "Comment not found"
            )
            
        if comment.author_id != current_user.id:
            raise ForbiddenOperationError(
                "You don't have permission to delete this comment"
            )        
            
            
        CommentRepository.soft_delete(
            session,
            comment
        )
        
        
        
    @staticmethod
    def get_comments(
        session: Session,
        current_user: User,
        task_id: UUID,
        page: int,
        limit: int
    ) -> CommentListResponse:

        
        task = TaskRepository.get_active_by_id(
            session,
            task_id
        )

        if task is None:
            raise TaskNotFoundError(
                "Task not found"
            )

    
        is_owner = current_user.id == task.owner_id

        is_task_assignee = (
            TaskRepository.get_by_task_user(
                session,
                task_id,
                user_id=current_user.id
            )
            is not None
        )

        if not is_owner and not is_task_assignee:
            raise ForbiddenOperationError(
                "You are not allowed to see comments of this task"
            )

    
        comments, total = CommentRepository.comments_by_task_id(
            session=session,
            task_id=task_id,
            page=page,
            limit=limit,
        )

  
        comment_list = []

        for comment in comments:

            content = comment.content

            if comment.is_deleted:
                content = "[This comment was deleted]"

            comment_list.append(
                CommentResponse(
                    id=comment.id,
                    content=content,
                    task_id=comment.task_id,

                    author=AuthorDetails(
                        id=comment.author.id,
                        name=comment.author.name,
                        email=comment.author.email,
                    ),

                    is_edited=comment.is_edited,
                    edited_at=comment.edited_at,

                    is_deleted=comment.is_deleted,
                    deleted_at=comment.deleted_at,

                    created_at=comment.created_at,
                    updated_at=comment.updated_at,
                )
            )

        total_pages = (
            math.ceil(total / limit)
            if total > 0
            else 0
        )

        return CommentListResponse(
            items=comment_list,
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages
        )

        
            
            


            
        
         
        
        
        
        
        
            
        