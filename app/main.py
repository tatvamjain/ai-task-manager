from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from .schemas import TaskResponse, TaskCreate, TaskUpdate, UserCreate, UserResponse
from .schemas import UserLogin, TokenResponse
from .database import get_db
from .models import Task, User, RefreshToken
from .auth import hash_password
from .auth import verify_password, create_access_token, hash_refresh_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .auth import verify_access_token, create_refresh_token
from datetime import datetime, timedelta, timezone

app = FastAPI()

security=HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})
    current_user = db.query(User).filter(User.id==user_id).first()
    if current_user is None:
        raise HTTPException(status_code=401, detail = "User not found", headers= {"WWW-Authenticate": "Bearer"})
    return current_user

@app.get("/")
def home():
    return {"message": "AI Task Manager API"}

@app.get("/auth/me")
def get_my_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at
    }



@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()

@app.post("/tasks", response_model=TaskResponse, status_code = 201)
def create_task(task: TaskCreate, db: Session=Depends(get_db)):
    new_task=Task(
        user_id=1,
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id:int, db: Session=Depends(get_db)):
    task=db.query(Task).filter(Task.id==task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id:int , updates:TaskUpdate, db:Session=Depends(get_db)):
    task=db.query(Task).filter(Task.id==task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found",)
    update_data=updates.model_dump(exclude_unset=True)
    for field,value in update_data.items():
        setattr(task,field,value)

    db.commit()
    db.refresh(task)
    return task

@app.delete("/tasks/{task_id}",status_code=204)
def Task_delete(task_id:int, db:Session=Depends(get_db)):
    task=db.query(Task).filter(Task.id==task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail = "Task not found")
    db.delete(task)
    db.commit()


@app.post("/auth/register", response_model=UserResponse, status_code=201)
def register_user(user:UserCreate, db:Session=Depends(get_db)):
    existing_user=db.query(User).filter(User.email==user.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail = "Email already registered")
    new_user=User(
        email=user.email,
        password_hash=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/auth/login", response_model=TokenResponse)
def login_user(user: UserLogin, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing_user or not verify_password(
        user.password, existing_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Generate access token
    access_token = create_access_token(existing_user.id)

    # Generate refresh token
    refresh_token = create_refresh_token()

    # Hash refresh token before storing it
    token_hash = hash_refresh_token(refresh_token)

    # Calculate refresh token expiry
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    # Store refresh token in database
    new_refresh_token = RefreshToken(
        user_id=existing_user.id,
        token_hash=token_hash,
        expires_at=expires_at
    )

    db.add(new_refresh_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
    