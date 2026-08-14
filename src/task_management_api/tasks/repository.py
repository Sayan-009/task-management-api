from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Any

from task_management_api.tasks.model import Task
from task_management_api.tasks.schema import (
    TaskCreate,
    TaskUpdate,
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
    ) -> list[Task]:
        statement = select(Task).where(Task.owner_id == owner_id)
        
        tasks = session.execute(statement).scalars().all()
        
        return tasks
    
    
    @staticmethod
    def get_by_id(
        session: Session,
        task_id: UUID,
    ) -> Task | None:
        statement = select(Task).where(
            Task.id == task_id
        )

        return session.execute(statement).scalar_one_or_none()
            
        