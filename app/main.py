from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import projects, tasks, stats, ai

app = FastAPI(title="TaskPilot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router, prefix="/api", tags=["projects"])
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(stats.router, prefix="/api", tags=["stats"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])

@app.get("/api/health")
async def health():
    return {"healthy": True}
