from fastapi import FastAPI
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


class Task(BaseModel):
    id: int
    title: str
    done: bool = False


class NewTask(BaseModel):
    title: str


tasks: list[Task] = [
    Task(id=1, title="Read the codebase", done=True),
    Task(id=2, title="Run the app", done=False),
    Task(id=3, title="Add a feature", done=False),
]
next_id = 4


@app.get("/tasks")
def list_tasks():
    return tasks


@app.post("/tasks")
def create_task(payload: NewTask):
    global next_id
    task = Task(id=next_id, title=payload.title)
    tasks.append(task)
    next_id += 1
    return task
