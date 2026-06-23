# React + Flask Cheatsheet — Live-Coding Feature Work

Focused on the ~90% you need to add a small feature to an existing full-stack app.
Mental model: **backend field/endpoint → API call → React state → UI.**

---

# REACT

## 1. Component + JSX
```jsx
function Hello({ name }) {            // props come in as one object
  return <h1>Hello, {name}</h1>       // {} = JS expression inside JSX
}
// use it: <Hello name="Jigar" />
```

## 2. State — `useState`
```jsx
import { useState } from 'react'

function Counter() {
  const [count, setCount] = useState(0)   // [value, setter]
  return <button onClick={() => setCount(count + 1)}>{count}</button>
}
```
- State is **immutable** — never mutate; always pass a NEW value to the setter.

## 3. Events
```jsx
<button onClick={handleClick}>Go</button>
<input onChange={(e) => setText(e.target.value)} />
<form onSubmit={(e) => { e.preventDefault(); /* ... */ }}>
```

## 4. Controlled form input (value + onChange)
```jsx
const [title, setTitle] = useState('')
<input value={title} onChange={(e) => setTitle(e.target.value)} />
```

## 5. Render a list (`.map` + `key`)
```jsx
<ul>
  {tasks.map((t) => (
    <li key={t.id}>{t.title}</li>      // key MUST be stable + unique
  ))}
</ul>
```

## 6. Conditional rendering
```jsx
{loading && <p>Loading…</p>}
{error ? <p>Error</p> : <List items={items} />}
{task.done ? '✓' : ''}
```

## 7. Fetch data on mount — `useEffect`
```jsx
import { useEffect, useState } from 'react'

const [tasks, setTasks] = useState([])
useEffect(() => {
  fetch('http://localhost:8000/tasks')
    .then((res) => res.json())
    .then(setTasks)
}, [])                                  // [] = run once on mount
```
- Empty deps `[]` = once. `[x]` = re-run when x changes. Omit = every render (rarely want).

## 8. Immutable array updates — THE feature operations
```jsx
// ADD
setTasks([...tasks, newTask])

// REMOVE (delete feature)
setTasks(tasks.filter((t) => t.id !== id))

// UPDATE one item (toggle / edit feature)
setTasks(tasks.map((t) => (t.id === id ? { ...t, done: !t.done } : t)))
```
These three cover most "small feature" asks. Memorize them.

## 9. POST / PATCH / DELETE with fetch
```jsx
// POST
await fetch(`${BASE}/tasks`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ title }),
})

// PATCH (toggle)
await fetch(`${BASE}/tasks/${id}`, { method: 'PATCH' })

// DELETE
await fetch(`${BASE}/tasks/${id}`, { method: 'DELETE' })
```
Pattern: call API → then update local state to match.

## 10. Passing handlers down (lift state up)
```jsx
// Parent owns state + handler; child calls it.
<TaskItem task={t} onToggle={() => toggle(t.id)} onDelete={() => remove(t.id)} />

function TaskItem({ task, onToggle, onDelete }) {
  return (
    <li>
      <span onClick={onToggle}>{task.title}</span>
      <button onClick={onDelete}>✕</button>
    </li>
  )
}
```

---

# FLASK

## 1. Minimal app
```python
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.get("/health")
def health():
    return {"ok": True}        # dict auto-serializes to JSON

# run:  flask --app main run --debug    (or app.run(debug=True))
```

## 2. Routes + methods
```python
@app.get("/tasks")            # GET
def list_tasks(): ...

@app.post("/tasks")           # POST
def create_task(): ...

# older style:
@app.route("/tasks", methods=["GET", "POST"])
```

## 3. Read JSON body
```python
@app.post("/tasks")
def create_task():
    data = request.get_json()       # -> dict
    title = data["title"]
    ...
    return jsonify(task), 201       # body, status code
```

## 4. Path params
```python
@app.patch("/tasks/<int:task_id>")     # <int:..> casts to int
def toggle(task_id):
    ...
```

## 5. Query params
```python
# GET /tasks?done=true
done = request.args.get("done")        # string or None
```

## 6. Return JSON + status
```python
return jsonify(tasks)                  # 200 default
return jsonify(task), 201              # created
return {"error": "not found"}, 404
```

## 7. In-memory CRUD (typical interview store)
```python
tasks = [{"id": 1, "title": "Read", "done": False}]
next_id = 2

@app.get("/tasks")
def list_tasks():
    return jsonify(tasks)

@app.post("/tasks")
def create_task():
    global next_id
    data = request.get_json()
    task = {"id": next_id, "title": data["title"], "done": False}
    tasks.append(task); next_id += 1
    return jsonify(task), 201

@app.patch("/tasks/<int:task_id>")
def toggle(task_id):
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = not t["done"]
            return jsonify(t)
    return {"error": "not found"}, 404

@app.delete("/tasks/<int:task_id>")
def delete(task_id):
    global tasks
    tasks = [t for t in tasks if t["id"] != task_id]
    return "", 204
```

## 8. CORS (React on :5173 calling Flask on :8000/:5000)
```python
from flask_cors import CORS      # pip install flask-cors
CORS(app)                        # allow all origins (fine for dev/interview)
```
If a fetch fails with a CORS error in the browser console — this is the fix.

---

# FLASK ↔ FastAPI (your practice app is FastAPI)

| Concept | Flask | FastAPI |
|---|---|---|
| Route GET | `@app.get("/x")` | `@app.get("/x")` (same) |
| JSON body | `request.get_json()` | function param w/ Pydantic model |
| Return JSON | `jsonify(obj)` / dict | `return obj` (auto) |
| Path param | `<int:id>` | `def f(id: int)` |
| Query param | `request.args.get("q")` | `def f(q: str = None)` |
| Status code | `return body, 201` | `@app.post(..., status_code=201)` |
| Run | `flask --app main run` | `uvicorn main:app --reload` |
| CORS | `flask_cors.CORS(app)` | `CORSMiddleware` |
| Docs UI | (none built-in) | `/docs` (free!) |

FastAPI body example:
```python
from pydantic import BaseModel
class NewTask(BaseModel):
    title: str

@app.post("/tasks")
def create(payload: NewTask):     # FastAPI parses + validates JSON for you
    return {"id": 1, "title": payload.title}
```

---

# THE RECIPE (use this live)
1. **Read** — trace one existing feature: backend route → API helper → React fetch → state → render.
2. **Find the seam** — where does the data flow? Extend it one notch.
3. **Backend first** — add/modify the endpoint; test it at `/docs` or with the browser.
4. **Frontend** — call it, update state immutably, render.
5. **Run + verify** — actually click the feature. Check one edge case.
6. **Narrate** the whole time; let AI draft, but read & explain every line.
