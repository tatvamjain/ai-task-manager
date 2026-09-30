from datetime import datetime

from pydantic import BaseModel


class TaskResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    priority: str
    completed: bool
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime