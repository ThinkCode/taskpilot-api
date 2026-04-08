from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models.task import Task
from ..models.subtask import Subtask
from ..schemas.task_schema import TaskCreate, TaskUpdate, TaskPositionUpdate, TaskResponse, SubtaskCreate, SubtaskResponse

router = APIRouter()

@router.get("/projects/{project_id}/tasks")
async def list_tasks(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Task)
        .where(Task.project_id == project_id)
        .order_by(Task.position)
    )
    tasks = result.scalars().all()
    return [TaskResponse.model_validate(t) for t in tasks]

@router.get("/tasks/{task_id}")
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(404, "Task not found")
    return TaskResponse.model_validate(task)

@router.post("/projects/{project_id}/tasks", status_code=201)
async def create_task(project_id: str, data: TaskCreate, db: AsyncSession = Depends(get_db)):
    # Get max position
    result = await db.execute(
        select(func.coalesce(func.max(Task.position), 0))
        .where(Task.project_id == project_id, Task.status == data.status)
    )
    max_pos = result.scalar()

    task = Task(
        project_id=project_id,
        title=data.title,
        description=data.description,
        status=data.status,
        priority=data.priority,
        due_date=data.due_date,
        position=max_pos + 1,
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return TaskResponse.model_validate(task)

@router.put("/tasks/{task_id}")
async def update_task(task_id: str, data: TaskUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(404, "Task not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    await db.flush()
    await db.refresh(task)
    return TaskResponse.model_validate(task)

@router.put("/tasks/{task_id}/position")
async def update_task_position(task_id: str, data: TaskPositionUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(404, "Task not found")

    task.status = data.status
    task.position = data.position
    await db.flush()
    await db.refresh(task)
    return TaskResponse.model_validate(task)

@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(404, "Task not found")
    await db.delete(task)

# Subtasks
@router.post("/tasks/{task_id}/subtasks", status_code=201)
async def create_subtask(task_id: str, data: SubtaskCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(func.coalesce(func.max(Subtask.position), 0))
        .where(Subtask.task_id == task_id)
    )
    max_pos = result.scalar()

    subtask = Subtask(task_id=task_id, title=data.title, position=max_pos + 1)
    db.add(subtask)
    await db.flush()
    await db.refresh(subtask)
    return SubtaskResponse.model_validate(subtask)

@router.put("/subtasks/{subtask_id}")
async def update_subtask(subtask_id: str, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subtask).where(Subtask.id == subtask_id))
    subtask = result.scalar_one_or_none()
    if not subtask:
        raise HTTPException(404, "Subtask not found")
    for k, v in data.items():
        if hasattr(subtask, k):
            setattr(subtask, k, v)
    await db.flush()
    await db.refresh(subtask)
    return SubtaskResponse.model_validate(subtask)

@router.delete("/subtasks/{subtask_id}", status_code=204)
async def delete_subtask(subtask_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subtask).where(Subtask.id == subtask_id))
    subtask = result.scalar_one_or_none()
    if not subtask:
        raise HTTPException(404, "Subtask not found")
    await db.delete(subtask)
