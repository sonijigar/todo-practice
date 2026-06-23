import pytest
from fastapi.testclient import TestClient

from main import Task, app
import main


@pytest.fixture(autouse=True)
def reset_tasks():
    """Reset the in-memory task list before each test."""
    main.tasks.clear()
    main.tasks.extend([
        Task(id=1, title="Read the codebase", done=True),
        Task(id=2, title="Run the app", done=False),
        Task(id=3, title="Add a feature", done=False),
    ])
    main.next_id = 4
    yield


client = TestClient(app)


# ── GET /tasks ──────────────────────────────────────────────


class TestListTasks:
    def test_returns_all_tasks(self):
        res = client.get("/tasks")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 3

    def test_task_structure(self):
        res = client.get("/tasks")
        task = res.json()[0]
        assert "id" in task
        assert "title" in task
        assert "done" in task


# ── POST /tasks ─────────────────────────────────────────────


class TestCreateTask:
    def test_creates_task_successfully(self):
        res = client.post("/tasks", json={"title": "Write tests"})
        assert res.status_code == 200
        data = res.json()
        assert data["title"] == "Write tests"
        assert data["done"] is False
        assert data["id"] == 4

    def test_new_task_appears_in_list(self):
        client.post("/tasks", json={"title": "Deploy app"})
        res = client.get("/tasks")
        titles = [t["title"] for t in res.json()]
        assert "Deploy app" in titles
