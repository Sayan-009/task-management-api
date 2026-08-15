from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from task_management_api.tasks.enums import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
    )
    
class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    description: str | None = None
    priority: TaskPriority
    status: TaskStatus 
    created_at: datetime
    updated_at: datetime
    
    
class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    page: int
    limit: int
    total: int
    total_pages: int
    
    
class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length = 1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    priority: TaskPriority | None = None
    
class TaskStatusUpdate(BaseModel):
    status: TaskStatus

    
    