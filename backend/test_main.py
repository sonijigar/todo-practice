import pytest
from fastapi.testclient import TestClient

from main import Priority, Task, app
import main


@pytest.fixture(autouse=True)
def reset_tasks():
    """Reset the in-memory task list before each test."""
    main.tasks.clear()
    main.tasks.extend([
        Task(id=1, title="Read the codebase", done=True, priority=Priority.HIGH),
        Task(id=2, title="Run the app", done=False, priority=Priority.MEDIUM),
        Task(id=3, title="Add a feature", done=False, priority=Priority.HIGH),
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
        assert "priority" in task

    def test_undone_tasks_come_first(self):
        res = client.get("/tasks")
        data = res.json()
        done_flags = [t["done"] for t in data]
        # All undone tasks should appear before any done tasks
        assert done_flags == sorted(done_flags, key=lambda d: d)

    def test_undone_tasks_sorted_by_priority_high_first(self):
        res = client.get("/tasks")
        data = res.json()
        undone = [t for t in data if not t["done"]]
        priorities = [t["priority"] for t in undone]
        # HIGH (id=3) should come before MEDIUM (id=2)
        assert priorities == ["high", "medium"]

    def test_sort_order_with_all_priorities(self):
        """Add a LOW priority task and verify full sort order."""
        main.tasks.append(Task(id=4, title="Low prio", done=False, priority=Priority.LOW))
        res = client.get("/tasks")
        data = res.json()
        undone = [t for t in data if not t["done"]]
        priorities = [t["priority"] for t in undone]
        assert priorities == ["high", "medium", "low"]


# ── POST /tasks ─────────────────────────────────────────────


class TestCreateTask:
    def test_creates_task_successfully(self):
        res = client.post("/tasks", json={"title": "Write tests"})
        assert res.status_code == 200
        data = res.json()
        assert data["title"] == "Write tests"
        assert data["done"] is False
        assert data["id"] == 4

    def test_default_priority_is_medium(self):
        res = client.post("/tasks", json={"title": "No priority"})
        assert res.json()["priority"] == "medium"

    def test_explicit_priority_high(self):
        res = client.post("/tasks", json={"title": "Urgent", "priority": "high"})
        assert res.json()["priority"] == "high"

    def test_explicit_priority_low(self):
        res = client.post("/tasks", json={"title": "Someday", "priority": "low"})
        assert res.json()["priority"] == "low"

    def test_invalid_priority_returns_422(self):
        res = client.post("/tasks", json={"title": "Bad", "priority": "critical"})
        assert res.status_code == 422

    def test_new_task_appears_in_list(self):
        client.post("/tasks", json={"title": "Deploy app"})
        res = client.get("/tasks")
        titles = [t["title"] for t in res.json()]
        assert "Deploy app" in titles

    def test_ids_auto_increment(self):
        r1 = client.post("/tasks", json={"title": "First"})
        r2 = client.post("/tasks", json={"title": "Second"})
        assert r2.json()["id"] == r1.json()["id"] + 1

    def test_missing_title_returns_422(self):
        res = client.post("/tasks", json={})
        assert res.status_code == 422

    def test_empty_body_returns_422(self):
        res = client.post("/tasks", content="", headers={"Content-Type": "application/json"})
        assert res.status_code == 422


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

    def test_toggle_preserves_priority(self):
        res = client.post("/tasks/3/toggle")
        assert res.json()["priority"] == "high"

    def test_toggle_updates_task_list(self):
        client.post("/tasks/2/toggle")
        res = client.get("/tasks")
        task2 = next(t for t in res.json() if t["id"] == 2)
        assert task2["done"] is True

    def test_toggle_nonexistent_task_returns_404(self):
        res = client.post("/tasks/999/toggle")
        assert res.status_code == 404
        assert res.json()["detail"] == "Task not found"

    def test_toggle_invalid_id_returns_422(self):
        res = client.post("/tasks/abc/toggle")
        assert res.status_code == 422


# ── POST /tasks/{task_id}/priority ──────────────────────────


class TestChangeTaskPriority:
    def test_change_priority_to_low(self):
        res = client.post("/tasks/2/priority", json={"priority": "low"})
        assert res.status_code == 200
        assert res.json()["priority"] == "low"

    def test_change_priority_to_high(self):
        res = client.post("/tasks/2/priority", json={"priority": "high"})
        assert res.status_code == 200
        assert res.json()["priority"] == "high"

    def test_change_priority_same_value(self):
        res = client.post("/tasks/2/priority", json={"priority": "medium"})
        assert res.status_code == 200
        assert res.json()["priority"] == "medium"

    def test_change_priority_updates_list(self):
        client.post("/tasks/2/priority", json={"priority": "high"})
        res = client.get("/tasks")
        task2 = next(t for t in res.json() if t["id"] == 2)
        assert task2["priority"] == "high"

    def test_change_priority_affects_sort_order(self):
        # Task 2 is medium, promote to high — should sort before task 3 (or equal)
        client.post("/tasks/2/priority", json={"priority": "high"})
        res = client.get("/tasks")
        undone = [t for t in res.json() if not t["done"]]
        assert all(t["priority"] == "high" for t in undone)

    def test_change_priority_on_done_task_returns_400(self):
        res = client.post("/tasks/1/priority", json={"priority": "low"})
        assert res.status_code == 400
        assert res.json()["detail"] == "Can't modify a completed task"

    def test_invalid_priority_value_returns_422(self):
        res = client.post("/tasks/2/priority", json={"priority": "critical"})
        assert res.status_code == 422

    def test_missing_priority_returns_422(self):
        res = client.post("/tasks/2/priority", json={})
        assert res.status_code == 422

    def test_nonexistent_task_returns_404(self):
        res = client.post("/tasks/999/priority", json={"priority": "high"})
        assert res.status_code == 404
        assert res.json()["detail"] == "Task not found"

    def test_invalid_task_id_returns_422(self):
        res = client.post("/tasks/abc/priority", json={"priority": "high"})
        assert res.status_code == 422
