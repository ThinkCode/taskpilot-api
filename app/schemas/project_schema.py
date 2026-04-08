import uuid
from datetime import datetime
from pydantic import BaseModel

class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    color: str = "#3b82f6"

class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    color: str | None = None
    status: str | None = None

class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    color: str
    status: str
    task_count: int = 0
    completed_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
