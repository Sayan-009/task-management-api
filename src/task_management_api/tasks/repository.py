from uuid import UUID
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session, joinedload
from typing import Any


from task_management_api.tasks.enums import (TaskPriority, TaskStatus, TaskOrder, TaskSort, AssignedTaskSort)
from task_management_api.users.model import User
from task_management_api.tasks.model import Task
from task_management_api.tasks.schema import (
    TaskCreate,
    TaskStatusUpdate,
)
from task_management_api.tasks.assignee_model import TaskAssignee

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
        
        # Count before pagination
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
        
        
    @staticmethod
    def create_many(
        session: Session,
        task_id: UUID,
        assignee_ids: list[UUID]
    ) -> list[TaskAssignee]:
        assignments = [
            TaskAssignee(
                task_id = task_id,
                user_id = user_id,
            )
            for user_id in assignee_ids
        ]
        
        session.add_all(assignments)
        
        session.flush()
        
        return assignments
    
    @staticmethod
    def get_by_task_user(
        session: Session,
        task_id: UUID,
        user_id: UUID,
    ) -> TaskAssignee | None:
        
        statement = select(TaskAssignee).where(
            TaskAssignee.user_id == user_id,
            TaskAssignee.task_id == task_id,
        )
        
        return session.execute(statement).scalar_one_or_none()
    
    
    @staticmethod
    def delete_assignee(
        session: Session,
        task_assignee: TaskAssignee
    ) -> None:
        session.delete(task_assignee)
        session.flush()
        
        
    @staticmethod
    def get_task_with_assignees(
        session: Session,
        task_id: UUID
    ) -> Task | None:
        statement = select(Task).where(
            Task.id == task_id
        ).options(
            joinedload(Task.owner),
            joinedload(Task.assignees).joinedload(TaskAssignee.user),
        )
        
        return session.execute(statement).unique().scalar_one_or_none()
    
    
    
    @staticmethod
    def update_assignee_status(
        session: Session,
        task_assignee: TaskAssignee,
        update_status: TaskStatusUpdate,
    ) -> TaskAssignee:
        
        task_assignee.status = update_status.status
        session.flush()
        return task_assignee
    
    
    @staticmethod
    def get_tasks_by_assignee(
        session: Session,
        user_id: UUID,
        search: str | None = None,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        sort_by: AssignedTaskSort | None = None,
        order: TaskOrder = TaskOrder.ASC,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[TaskAssignee], int]:

        statement = (
            select(TaskAssignee)
            .join(TaskAssignee.task)
            .where(TaskAssignee.user_id == user_id)
            .options(
                joinedload(TaskAssignee.task)
                .joinedload(Task.owner),
            )
        )
        
        
        # Search
        if search:
            search_pattern = f"%{search}%"

            statement = statement.where(
                or_(
                    Task.title.ilike(search_pattern),
                    Task.description.ilike(search_pattern),
                )
            )

        # Filtering
        if status is not None:
            statement = statement.where(
                TaskAssignee.status == status
            )

        if priority is not None:
            statement = statement.where(
                Task.priority == priority
            )

        # Sorting
        if sort_by is not None:
            sort_column = {
                AssignedTaskSort.TITLE: Task.title,
                AssignedTaskSort.STATUS: TaskAssignee.status,
                AssignedTaskSort.PRIORITY: Task.priority,
            }[sort_by]

            if order == TaskOrder.DESC:
                statement = statement.order_by(
                    sort_column.desc(),
                    Task.id.desc(),
                )
            else:
                statement = statement.order_by(
                    sort_column.asc(),
                    Task.id.asc(),
                )

        # Count before pagination
        total = session.execute(
            select(func.count()).select_from(
                statement.subquery()
            )
        ).scalar_one()

        # Pagination
        offset = (page - 1) * limit

        statement = statement.offset(offset).limit(limit)

        task_assignees = (
            session.execute(statement)
            .scalars()
            .all()
        )

        return task_assignees, total