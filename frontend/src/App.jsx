import { useEffect, useState } from 'react'
import { getTasks, addTask } from './api'

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
          <li key={t.id}>
            {t.done ? '✓ ' : '○ '}{t.title}
          </li>
        ))}
      </ul>
    </div>
  )
}
