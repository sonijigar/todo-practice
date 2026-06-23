import { useEffect, useState } from 'react'
import { getTasks, addTask, toggleTask } from './api'

export default function App() {
  const [tasks, setTasks] = useState([])
  const [title, setTitle] = useState('')

  useEffect(() => {
    getTasks().then(setTasks)
  }, [])

  async function handleAdd(e) {
    e.preventDefault()
    if (!title.trim()) return
    await addTask(title)
    setTasks(await getTasks())
    setTitle('')
  }

  async function handleToggle(taskId) {
    const updated = await toggleTask(taskId)
    setTasks((prev) => prev.map((t) => (t.id === updated.id ? updated : t)))
  }

  return (
    <div style={{ maxWidth: 480, margin: '0 auto', padding: '40px 16px', fontFamily: 'sans-serif' }}>
      <h1>Tasks</h1>
      <form onSubmit={handleAdd}>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="New task..."
        />
        <button type="submit">Add</button>
      </form>
      <ul>
        {tasks.map((t) => (
          <li key={t.id} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span
              onClick={() => handleToggle(t.id)}
              style={{
                cursor: 'pointer',
                textDecoration: t.done ? 'line-through' : 'none',
              }}
            >
              {t.done ? '✓ ' : '○ '}{t.title}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
