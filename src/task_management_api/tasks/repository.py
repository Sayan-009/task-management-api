from uuid import UUID
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session
from typing import Any


from task_management_api.tasks.enums import (TaskPriority, TaskStatus, TaskOrder, TaskSort)
from task_management_api.tasks.model import Task
from task_management_api.tasks.schema import (
    TaskCreate,
    TaskStatusUpdate
)

class TaskRepository:
    
    @staticmethod
    def create(
        session: Session,
        owner_id: UUID,
        task: TaskCreate
    ) -> Task:
        new_task = Task(
            title = task.title,
            description = task.description,
            priority = task.priority,
            owner_id = owner_id
        )
        
        session.add(new_task)
        
        session.flush()
        
        return new_task
    
    @staticmethod
    def update(
        session: Session,
        task: Task,
        updates: dict[str, Any],
    ) -> Task:
        for field, value in updates.items():
            setattr(task, field, value)
            
        session.add(task)
        session.flush()
        return task
    
    
    @staticmethod
    def get_by_owner(
        session: Session,
        owner_id: UUID,
        search: str | None = None,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        sort_by: TaskSort | None = None,
        order: TaskOrder = TaskOrder.ASC,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[Task], int]:
        
        statement = select(Task).where(Task.owner_id == owner_id)

        # Search
        if search is not None:
            search_pattern = f"%{search}%"

            statement = statement.where(
                or_(
                    Task.title.ilike(search_pattern),
                    Task.description.ilike(search_pattern),
                )
            )
        
        # Filtering
        if status is not None:
            statement = statement.where(Task.status == status)
            
        if priority is not None:
            statement = statement.where(Task.priority == priority)
            
        
        # Sorting
        if sort_by is not None:
            sort_column = {
                TaskSort.TITLE: Task.title,
                TaskSort.CREATED_AT: Task.created_at,
                TaskSort.UPDATED_AT: Task.updated_at,
                TaskSort.STATUS: Task.status,
                TaskSort.PRIORITY: Task.priority,
            }[sort_by]

            if order == TaskOrder.DESC:
                statement = statement.order_by(sort_column.desc())
            else:
                statement = statement.order_by(sort_column.asc())
        
        # Count BEFORE pagination
        total = session.execute(
            select(func.count()).select_from(
                statement.subquery()
            )
        ).scalar_one()
        
        # Pagination
        offset = (page - 1) * limit
        
        statement = statement.offset(offset).limit(limit)
        
        tasks = session.execute(statement).scalars().all()
        
        return tasks, total
    
    
    @staticmethod
    def get_by_id(
        session: Session,
        task_id: UUID,
    ) -> Task | None:
        statement = select(Task).where(
            Task.id == task_id
        )

        return session.execute(statement).scalar_one_or_none()
    
    
    @staticmethod
    def status_update(
        session: Session,
        task: Task,
        task_status: TaskStatusUpdate,
    ) -> Task:
        task.status = task_status.status
        session.flush()
        return task
    
    
    @staticmethod
    def delete(
        session: Session,
        task: Task,
    ) -> None:
        session.delete(task)
        session.flush()
            
        