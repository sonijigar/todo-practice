from enum import Enum

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# React dev server runs on :5173 — allow it to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


PRIORITY_ORDER = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}


class Task(BaseModel):
    id: int
    title: str
    done: bool = False
    priority: Priority = Priority.MEDIUM


class NewTask(BaseModel):
    title: str
    priority: Priority = Priority.MEDIUM


class ChangePriority(BaseModel):
    priority: Priority


tasks: list[Task] = [
    Task(id=1, title="Read the codebase", done=True, priority=Priority.HIGH),
    Task(id=2, title="Run the app", done=False, priority=Priority.MEDIUM),
    Task(id=3, title="Add a feature", done=False, priority=Priority.HIGH),
]
next_id = 4


@app.get("/tasks")
def list_tasks():
    return sorted(tasks, key=lambda t: (t.done, PRIORITY_ORDER[t.priority]))


@app.post("/tasks")
def create_task(payload: NewTask):
    global next_id
    task = Task(id=next_id, title=payload.title, priority=payload.priority)
    tasks.append(task)
    next_id += 1
    return task


@app.post("/tasks/{task_id}/toggle")
def toggle_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            task.done = not task.done
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.post("/tasks/{task_id}/priority")
def change_task_priority(task_id: int, payload: ChangePriority):
    for task in tasks:
        if task.id == task_id:
            if task.done:
                raise HTTPException(status_code=400, detail="Can't modify a completed task")
            task.priority = payload.priority
            return task
    raise HTTPException(status_code=404, detail="Task not found")
