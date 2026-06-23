const BASE = 'http://localhost:8000'

export async function getTasks() {
  const res = await fetch(`${BASE}/tasks`)
  return res.json()
}

export async function addTask(title, priority = 'medium', due_date_millis = null) {
  const res = await fetch(`${BASE}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, priority, due_date_millis }),
  })
  return res.json()
}

export async function toggleTask(taskId) {
  const res = await fetch(`${BASE}/tasks/${taskId}/toggle`, {
    method: 'POST',
  })
  if (!res.ok) throw new Error('Toggle failed')
  return res.json()
}

export async function changeTaskPriority(taskId, priority) {
  const res = await fetch(`${BASE}/tasks/${taskId}/priority`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ priority }),
  })
  if (!res.ok) throw new Error('Priority change failed')
  return res.json()
}
