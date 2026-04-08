from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models.task import Task
from ..models.project import Project

router = APIRouter()

@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    week_start = today_start - timedelta(days=today_start.weekday())

    # Total projects
    project_count = await db.scalar(
        select(func.count(Project.id)).where(Project.status == "active")
    ) or 0

    # Total tasks
    total_tasks = await db.scalar(select(func.count(Task.id))) or 0

    # Tasks due today
    due_today = await db.scalar(
        select(func.count(Task.id)).where(
            Task.due_date >= today_start,
            Task.due_date < today_end,
            Task.status != "done"
        )
    ) or 0

    # Overdue
    overdue = await db.scalar(
        select(func.count(Task.id)).where(
            Task.due_date < today_start,
            Task.status != "done"
        )
    ) or 0

    # Completed this week
    completed_week = await db.scalar(
        select(func.count(Task.id)).where(
            Task.status == "done",
            Task.updated_at >= week_start
        )
    ) or 0

    # Tasks by status
    status_result = await db.execute(
        select(Task.status, func.count(Task.id)).group_by(Task.status)
    )
    tasks_by_status = {row[0]: row[1] for row in status_result.all()}

    # Tasks by priority
    priority_result = await db.execute(
        select(Task.priority, func.count(Task.id)).group_by(Task.priority)
    )
    tasks_by_priority = {row[0]: row[1] for row in priority_result.all()}

    return {
        "total_projects": project_count,
        "total_tasks": total_tasks,
        "tasks_due_today": due_today,
        "overdue_tasks": overdue,
        "completed_this_week": completed_week,
        "tasks_by_status": tasks_by_status,
        "tasks_by_priority": tasks_by_priority,
    }
