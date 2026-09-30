from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from .database import get_db
from .models import Task

app = FastAPI()


@app.get("/")
def home():
    return {"message": "AI Task Manager API"}


@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()