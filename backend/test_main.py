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


# ── POST /tasks/{task_id}/toggle ────────────────────────────


class TestToggleTask:
    def test_toggle_undone_to_done(self):
        res = client.post("/tasks/2/toggle")
        assert res.status_code == 200
        assert res.json()["done"] is True

    def test_toggle_done_to_undone(self):
        res = client.post("/tasks/1/toggle")
        assert res.status_code == 200
        assert res.json()["done"] is False

    def test_double_toggle_returns_to_original(self):
        client.post("/tasks/2/toggle")  # False → True
        res = client.post("/tasks/2/toggle")  # True → False
        assert res.json()["done"] is False

    def test_toggle_updates_task_list(self):
        client.post("/tasks/2/toggle")
        res = client.get("/tasks")
        task2 = next(t for t in res.json() if t["id"] == 2)
        assert task2["done"] is True

    def test_toggle_nonexistent_task_returns_404(self):
        res = client.post("/tasks/999/toggle")
        assert res.status_code == 404
        assert res.json()["detail"] == "Task not found"
