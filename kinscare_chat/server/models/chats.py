from pydantic import BaseModel


class ChatRequest(BaseModel):
    thread_id: str
    message: str

class InactiveChatRequest(BaseModel):
    thread_id: str
