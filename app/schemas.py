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

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: str = "medium"
    due_date: datetime | None = None

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    completed: bool | None = None
    due_date: datetime | None = None

class UserCreate(BaseModel):
    email:str
    password:str

class UserResponse(BaseModel):
    id:int
    email:str
    created_at:datetime

    model_config={
        "from_attributes": True
    }

class UserLogin(BaseModel):
    email:str
    password:str

class TokenResponse(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str