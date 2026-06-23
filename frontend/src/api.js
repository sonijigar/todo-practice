const BASE = 'http://localhost:8000'

export async function getTasks() {
  const res = await fetch(`${BASE}/tasks`)
  return res.json()
}

export async function addTask(title) {
  const res = await fetch(`${BASE}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
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
