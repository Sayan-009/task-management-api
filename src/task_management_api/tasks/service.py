from uuid import UUID
from sqlalchemy.orm import Session


from task_management_api.users.model import User
from task_management_api.tasks.model import Task
from task_management_api.tasks.repository import TaskRepository
from task_management_api.tasks.schema import (
    TaskCreate
)



class TaskService:
    
    @staticmethod
    def create_task(
        session: Session,
        task: TaskCreate,
        owner_id: UUID,
    ) -> Task:
        return TaskRepository.create(
            session,
            owner_id,
            task
        )
        
    @staticmethod
    def get_user_tasks(
        session: Session,
        owner_id: UUID,
    ) -> list[Task]:
        return TaskRepository.get_by_owner(
            session,
            owner_id
        )