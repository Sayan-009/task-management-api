from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, func, or_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any


from task_management_api.tasks.enums import (
    TaskPriority, 
    TaskStatus, 
    TaskOrder, 
    TaskSort, 
    AssignedTaskSort,
    TaskActivityType
)
from task_management_api.tasks.model import Task
from task_management_api.tasks.assignee_model import TaskAssignee
from task_management_api.tasks.activity_model import TaskActivity
from task_management_api.tasks.schema import (
    TaskCreate,
    TaskStatusUpdate,
)

class TaskRepository:
    
    @staticmethod
    async def create(
        session: AsyncSession,
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
        
        await session.flush()
        
        return new_task
    
    @staticmethod
    async def update(
        session: AsyncSession,
        task: Task,
        updates: dict[str, Any],
    ) -> Task:
        for field, value in updates.items():
            setattr(task, field, value)
            
        session.add(task)
        await session.flush()
        return task
    
    
    @staticmethod
    async def get_by_owner(
        session: AsyncSession,
        owner_id: UUID,
        search: str | None = None,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        sort_by: TaskSort | None = None,
        order: TaskOrder = TaskOrder.ASC,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[Task], int]:
        
        statement = select(Task).where(
            Task.owner_id == owner_id,
            Task.is_deleted.is_(False)
        )

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
        total = await session.execute(
            select(func.count()).select_from(
                statement.subquery()
            )
        )
        total = total.scalar_one()
        
        # Pagination
        offset = (page - 1) * limit
        
        statement = statement.offset(offset).limit(limit)
        
        result = await session.execute(statement)
        
        tasks = result.scalars().all()
        
        return tasks, total
    
    
    @staticmethod
    async def get_by_id(
        session: AsyncSession,
        task_id: UUID,
    ) -> Task | None:
        statement = select(Task).where(
            Task.id == task_id
        )

        result = await session.execute(statement)
        return result.scalar_one_or_none()

    
    @staticmethod
    async def get_active_by_id(
        session: AsyncSession,
        task_id: UUID,
    ) -> Task | None:
        statement = select(Task).where(
            Task.id == task_id,
            Task.is_deleted.is_(False),
        )

        result = await session.execute(statement)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def status_update(
        session: AsyncSession,
        task: Task,
        task_status: TaskStatusUpdate,
    ) -> Task:
        task.status = task_status.status
        await session.flush()
        return task
    
    
    @staticmethod
    async def soft_delete_task(
        session: AsyncSession,
        task: Task,
    ) -> Task:
        task.is_deleted = True
        task.deleted_at = datetime.now(timezone.utc)

        await session.flush()

        return task
    
    
    @staticmethod
    async def hard_delete_task(
        session: AsyncSession,
        task: Task,
    ) -> None:
        await session.delete(task)
        await session.flush()
        
    
    @staticmethod
    async def restore_task(
        session: AsyncSession,
        task: Task,
    ) -> Task:
        task.is_deleted = False
        task.deleted_at = None

        await session.flush()

        return task
        
        
    @staticmethod
    async def create_many(
        session: AsyncSession,
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
        await session.flush()
        
        return assignments
    
    @staticmethod
    async def get_by_task_user(
        session: AsyncSession,
        task_id: UUID,
        user_id: UUID,
    ) -> TaskAssignee | None:
        
        statement = select(TaskAssignee).where(
            TaskAssignee.user_id == user_id,
            TaskAssignee.task_id == task_id,
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()
    
    
    @staticmethod
    async def delete_assignee(
        session: AsyncSession,
        task_assignee: TaskAssignee
    ) -> None:
        await session.delete(task_assignee)
        await session.flush()
        
        
    @staticmethod
    async def get_task_with_assignees(
        session: AsyncSession,
        task_id: UUID
    ) -> Task | None:
        statement = select(Task).where(
            Task.id == task_id
        ).options(
            joinedload(Task.owner),
            joinedload(Task.assignees).joinedload(TaskAssignee.user),
        )
        
        result = await session.execute(statement)
        return result.unique().scalar_one_or_none()
    
    
    
    @staticmethod
    async def update_assignee_status(
        session: AsyncSession,
        task_assignee: TaskAssignee,
        update_status: TaskStatusUpdate,
    ) -> TaskAssignee:
        
        task_assignee.status = update_status.status
        await session.flush()
        return task_assignee
    
    
    @staticmethod
    async def get_tasks_by_assignee(
        session: AsyncSession,
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
            .where(
                TaskAssignee.user_id == user_id,
                Task.is_deleted.is_(False),
            )
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
        total = (await session.execute(
            select(func.count()).select_from(
                statement.subquery()
            )
        )).scalar_one()

        # Pagination
        offset = (page - 1) * limit

        statement = statement.offset(offset).limit(limit)
        
        result = await session.execute(statement)

        task_assignees = result.scalars().all()

        return task_assignees, total
    
    
    @staticmethod
    async def get_deleted_tasks(
        session: AsyncSession,
        owner_id: UUID,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[Task], int]:

        statement = (
            select(Task)
            .where(Task.is_deleted.is_(True))
            .options(
                joinedload(Task.owner),
            )
            .order_by(
                Task.deleted_at.desc(),
                Task.id.desc(),
            )
        )

        if owner_id is not None:
            statement = statement.where(
                Task.owner_id == owner_id
            )

        total = (await session.execute(
            select(func.count()).select_from(
                statement.subquery()
            )
        )).scalar_one()

        offset = (page - 1) * limit

        statement = statement.offset(offset).limit(limit)
        
        
        result = await session.execute(statement)

        tasks = result.scalars().all()

        return tasks, total
    
    
    @staticmethod
    async def create_activity(
        session: AsyncSession,
        task_id: UUID,
        user_id: UUID,
        action: TaskActivityType,
        field: str | None = None,
        old_value: str | None = None,
        new_value: str | None = None,
    ) -> TaskActivity:
        activity = TaskActivity(
            task_id=task_id,
            user_id=user_id,
            action=action,
            field=field,
            old_value=old_value,
            new_value=new_value,
        )
        
        session.add(activity)
        await session.flush()
        return activity
    
    
    @staticmethod
    async def get_task_activities(
        session: AsyncSession,
        task_id: UUID,
        page: int = 1,
        limit: int = 10
    ) -> tuple[list[TaskActivity], int]:
        statement = (
            select(TaskActivity)
            .where(TaskActivity.task_id == task_id)
            .options(
                joinedload(TaskActivity.user)
            )
            .order_by(
                TaskActivity.created_at.desc(),
                TaskActivity.id.desc(),
            ) 
        )
        
        total = (await session.execute(
            select(func.count()).select_from(
                statement.subquery()
            )
        )).scalar_one()

        offset = (page - 1) * limit

        statement = statement.offset(offset).limit(limit) 
        
        result = await session.execute(statement)    
        
        task_activities = result.scalars().all()
        
        return task_activities, total
        
        