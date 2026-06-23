from enum import Enum

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from telemetry import setup_telemetry, api_metrics

app = FastAPI()
setup_telemetry(app)

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
    start = api_metrics.start_timer()
    status = 200
    try:
        return sorted(tasks, key=lambda t: (t.done, PRIORITY_ORDER[t.priority]))
    finally:
        api_metrics.publish(method="GET", endpoint="/tasks", status=status, start=start)


@app.post("/tasks")
def create_task(payload: NewTask):
    start = api_metrics.start_timer()
    status = 200
    try:
        global next_id
        task = Task(id=next_id, title=payload.title, priority=payload.priority)
        tasks.append(task)
        next_id += 1
        return task
    finally:
        api_metrics.publish(method="POST", endpoint="/tasks", status=status, start=start)


@app.post("/tasks/{task_id}/toggle")
def toggle_task(task_id: int):
    start = api_metrics.start_timer()
    status = 404
    try:
        for task in tasks:
            if task.id == task_id:
                task.done = not task.done
                status = 200
                return task
        raise HTTPException(status_code=404, detail="Task not found")
    finally:
        api_metrics.publish(method="POST", endpoint="/tasks/{task_id}/toggle", status=status, start=start)


@app.post("/tasks/{task_id}/priority")
def change_task_priority(task_id: int, payload: ChangePriority):
    start = api_metrics.start_timer()
    status = 404
    try:
        for task in tasks:
            if task.id == task_id:
                if task.done:
                    status = 400
                    raise HTTPException(status_code=400, detail="Can't modify a completed task")
                task.priority = payload.priority
                status = 200
                return task
        raise HTTPException(status_code=404, detail="Task not found")
    finally:
        api_metrics.publish(method="POST", endpoint="/tasks/{task_id}/priority", status=status, start=start)
