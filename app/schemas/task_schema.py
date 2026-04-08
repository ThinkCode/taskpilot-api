import uuid
from datetime import datetime
from pydantic import BaseModel
from .project_schema import ProjectResponse

class SubtaskCreate(BaseModel):
    title: str

class SubtaskResponse(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    title: str
    done: bool
    position: int

    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    title: str
    description: str = ""
    status: str = "todo"
    priority: str = "medium"
    due_date: datetime | None = None

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    due_date: datetime | None = None
    position: int | None = None

class TaskPositionUpdate(BaseModel):
    status: str
    position: int

class TaskResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    description: str
    status: str
    priority: str
    due_date: datetime | None
    position: int
    subtasks: list[SubtaskResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
