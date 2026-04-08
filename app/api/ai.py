import json
import httpx
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ..config import settings
from ..schemas.ai_schema import ChatMessage

router = APIRouter()

SYSTEM_PROMPT = """You are TaskPilot, an AI assistant for project management. You help users manage their projects and tasks efficiently. You are concise, helpful, and proactive about deadlines and priorities.

When asked about what to work on, consider:
- Tasks that are overdue (highest priority)
- Tasks due today
- High/urgent priority tasks
- Tasks that have been in progress too long

Keep responses brief and actionable."""

@router.post("/chat")
async def chat(message: ChatMessage):
    async def generate():
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(
                    f"{settings.OLLAMA_BASE_URL}/api/chat",
                    json={
                        "model": settings.OLLAMA_MODEL,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": message.message},
                        ],
                        "stream": True,
                    },
                )

                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                chunk = data["message"]["content"]
                                yield f"data: {json.dumps({'content': chunk})}\n\n"
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            yield f"data: {json.dumps({'content': 'AI service unavailable. Make sure Ollama is running.'})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
