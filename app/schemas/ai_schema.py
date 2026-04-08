from pydantic import BaseModel

class ChatMessage(BaseModel):
    message: str
    context_type: str | None = None
    context_id: str | None = None
