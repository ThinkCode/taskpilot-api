from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..database import get_db
from ..models.project import Project
from ..models.task import Task
from ..schemas.project_schema import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter()

@router.get("/projects")
async def list_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Project)
        .where(Project.status == "active")
        .order_by(Project.created_at.desc())
    )
    projects = result.scalars().all()

    responses = []
    for p in projects:
        task_count = len(p.tasks)
        completed = sum(1 for t in p.tasks if t.status == "done")
        responses.append(ProjectResponse(
            id=p.id, name=p.name, description=p.description,
            color=p.color, status=p.status,
            task_count=task_count, completed_count=completed,
            created_at=p.created_at, updated_at=p.updated_at,
        ))
    return responses

@router.get("/projects/{project_id}")
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")

    task_count = len(project.tasks)
    completed = sum(1 for t in project.tasks if t.status == "done")
    return ProjectResponse(
        id=project.id, name=project.name, description=project.description,
        color=project.color, status=project.status,
        task_count=task_count, completed_count=completed,
        created_at=project.created_at, updated_at=project.updated_at,
    )

@router.post("/projects", status_code=201)
async def create_project(data: ProjectCreate, db: AsyncSession = Depends(get_db)):
    project = Project(name=data.name, description=data.description, color=data.color)
    db.add(project)
    await db.flush()
    await db.refresh(project)
    return ProjectResponse(
        id=project.id, name=project.name, description=project.description,
        color=project.color, status=project.status,
        task_count=0, completed_count=0,
        created_at=project.created_at, updated_at=project.updated_at,
    )

@router.put("/projects/{project_id}")
async def update_project(project_id: str, data: ProjectUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    await db.flush()
    await db.refresh(project)
    task_count = len(project.tasks)
    completed = sum(1 for t in project.tasks if t.status == "done")
    return ProjectResponse(
        id=project.id, name=project.name, description=project.description,
        color=project.color, status=project.status,
        task_count=task_count, completed_count=completed,
        created_at=project.created_at, updated_at=project.updated_at,
    )

@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")
    await db.delete(project)
