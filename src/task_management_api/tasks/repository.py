from uuid import UUID
from sqlalchemy import Select
from sqlalchemy.orm import Session

from task_management_api.tasks.model import Task
from task_management_api.tasks.schema import (
    TaskCreate
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
    def get_by_owner(
        session: Session,
        owner_id: UUID,
    ) -> list[Task]:
        statement = Select(Task).where(Task.owner_id == owner_id)
        
        tasks = session.execute(statement).scalars().all()
        
        return tasks
        
        