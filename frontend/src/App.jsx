import { useEffect, useState } from 'react'
import { getTasks, addTask, toggleTask, changeTaskPriority } from './api'

const PRIORITIES = [
  { value: 'high', label: 'High', color: '#d32f2f' },
  { value: 'medium', label: 'Medium', color: '#ed6c02' },
  { value: 'low', label: 'Low', color: '#2e7d32' },
]

const PRIORITY_COLORS = Object.fromEntries(PRIORITIES.map((p) => [p.value, p.color]))

const THEMES = {
  light: {
    bg: '#ffffff',
    text: '#1a1a1a',
    textMuted: '#999',
    inputBg: '#fff',
    inputBorder: '#ccc',
    cardBorder: '#eee',
    errorBg: '#fdecea',
    errorText: '#d32f2f',
    dropdownBg: '#fff',
    dropdownBorder: '#ddd',
    dropdownShadow: '0 4px 12px rgba(0,0,0,0.12)',
    doneBadgeBg: '#e0e0e0',
    toggleIcon: '☀️',
    toggleBg: '#f0f0f0',
  },
  dark: {
    bg: '#1a1a2e',
    text: '#e0e0e0',
    textMuted: '#666',
    inputBg: '#16213e',
    inputBorder: '#2a2a4a',
    cardBorder: '#2a2a4a',
    errorBg: '#3d1c1c',
    errorText: '#ff6b6b',
    dropdownBg: '#16213e',
    dropdownBorder: '#2a2a4a',
    dropdownShadow: '0 4px 12px rgba(0,0,0,0.4)',
    doneBadgeBg: '#2a2a4a',
    toggleIcon: '🌙',
    toggleBg: '#2a2a4a',
  },
}

export default function App() {
  const [tasks, setTasks] = useState([])
  const [title, setTitle] = useState('')
  const [priority, setPriority] = useState('medium')
  const [dueDate, setDueDate] = useState('')
  const [dueTimezone, setDueTimezone] = useState('local')
  const [showDatePicker, setShowDatePicker] = useState(false)
  const [error, setError] = useState(null)
  const [editingPriorityId, setEditingPriorityId] = useState(null)
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode')
    return saved ? JSON.parse(saved) : false
  })

  const theme = darkMode ? THEMES.dark : THEMES.light

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode))
  }, [darkMode])

  useEffect(() => {
    getTasks().then(setTasks)
  }, [])

  async function handleAdd(e) {
    e.preventDefault()
    if (!title.trim()) return

    let due_date_millis = null
    if (dueDate) {
      const [year, month, day] = dueDate.split('-').map(Number)
      if (dueTimezone === 'gmt') {
        due_date_millis = Date.UTC(year, month - 1, day, 23, 59, 59, 999)
      } else {
        due_date_millis = new Date(year, month - 1, day, 23, 59, 59, 999).getTime()
      }

      // Past date validation
      const endOfTodayLocal = new Date()
      endOfTodayLocal.setHours(0, 0, 0, 0)
      if (due_date_millis < endOfTodayLocal.getTime()) {
        setError("Due date cannot be in the past.")
        return
      }
    }

    try {
      setError(null)
      await addTask(title, priority, due_date_millis)
      setTasks(await getTasks())
      setTitle('')
      setPriority('medium')
      setDueDate('')
      setDueTimezone('local')
      setShowDatePicker(false)
    } catch {
      setError("Couldn't add task. Please try again.")
    }
  }

  async function handleToggle(taskId) {
    try {
      setError(null)
      const updated = await toggleTask(taskId)
      setTasks((prev) => prev.map((t) => (t.id === updated.id ? updated : t)))
    } catch {
      setError("Couldn't update the task. Please try again later.")
      setTimeout(() => setError(null), 3000)
    }
  }

  async function handlePriorityChange(taskId, newPriority) {
    try {
      setError(null)
      const updated = await changeTaskPriority(taskId, newPriority)
      setTasks((prev) => prev.map((t) => (t.id === updated.id ? updated : t)))
      setEditingPriorityId(null)
    } catch {
      setError("Couldn't update the task. Please try again later.")
      setTimeout(() => setError(null), 3000)
    }
  }

  const showPriority = title.trim().length > 0

  return (
    <div
      style={{
        minHeight: '100vh',
        background: theme.bg,
        color: theme.text,
        transition: 'background 0.3s ease, color 0.3s ease',
      }}
    >
      <div style={{ maxWidth: 480, margin: '0 auto', padding: '40px 16px', fontFamily: 'sans-serif' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: 0 }}>Tasks</h1>
          <button
            onClick={() => setDarkMode(!darkMode)}
            style={{
              background: theme.toggleBg,
              border: 'none',
              borderRadius: 20,
              padding: '6px 14px',
              cursor: 'pointer',
              fontSize: 16,
              transition: 'all 0.3s ease',
            }}
            title={darkMode ? 'Switch to light mode' : 'Switch to night mode'}
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>

        <form onSubmit={handleAdd} style={{ marginTop: 20 }}>
          <div style={{ display: 'flex', gap: 8 }}>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="New task..."
              style={{
                flex: 1,
                padding: 6,
                background: theme.inputBg,
                color: theme.text,
                border: `1px solid ${theme.inputBorder}`,
                borderRadius: 4,
                outline: 'none',
                transition: 'all 0.3s ease',
              }}
            />
            <button
              type="submit"
              style={{
                padding: '6px 16px',
                background: darkMode ? '#0f3460' : '#1976d2',
                color: '#fff',
                border: 'none',
                borderRadius: 4,
                cursor: 'pointer',
                transition: 'background 0.3s ease',
              }}
            >
              Add
            </button>
          </div>

          {showPriority && (
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: 10,
                marginTop: 12,
                animation: 'fadeIn 0.2s ease-in',
              }}
            >
              {/* Priority Select Buttons */}
              <div>
                <label style={{ fontSize: 11, fontWeight: 600, color: theme.textMuted, display: 'block', marginBottom: 4 }}>Priority</label>
                <div style={{ display: 'flex', gap: 6 }}>
                  {PRIORITIES.map((p) => {
                    const isSelected = priority === p.value
                    return (
                      <button
                        key={p.value}
                        type="button"
                        onClick={() => setPriority(p.value)}
                        style={{
                          flex: 1,
                          padding: '5px 0',
                          border: `2px solid ${p.color}`,
                          borderRadius: 6,
                          background: isSelected ? p.color : 'transparent',
                          color: isSelected ? '#fff' : p.color,
                          fontWeight: isSelected ? 700 : 500,
                          cursor: 'pointer',
                          fontSize: 12,
                          transition: 'all 0.15s ease',
                        }}
                      >
                        {p.label}
                      </button>
                    )
                  })}
                </div>
              </div>

              {/* Optional Due Date Trigger Button */}
              <div>
                <button
                  type="button"
                  onClick={() => setShowDatePicker(!showDatePicker)}
                  style={{
                    background: dueDate ? (darkMode ? '#0f3460' : '#1976d2') : 'transparent',
                    color: dueDate ? '#fff' : (darkMode ? '#e0e0e0' : '#1976d2'),
                    border: `1px solid ${darkMode ? '#2a2a4a' : '#1976d2'}`,
                    borderRadius: 6,
                    padding: '6px 12px',
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 6,
                    transition: 'all 0.2s ease',
                  }}
                >
                  📅 {dueDate ? `Due: ${dueDate} (${dueTimezone === 'gmt' ? 'GMT' : 'Local'})` : 'Set Due Date'}
                </button>
              </div>

              {/* Time and Date Picker Drawer */}
              {showDatePicker && (
                <div
                  style={{
                    background: theme.dropdownBg,
                    border: `1px solid ${theme.dropdownBorder}`,
                    borderRadius: 8,
                    padding: 12,
                    boxShadow: theme.dropdownShadow,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 10,
                  }}
                >
                  <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
                    <div style={{ flex: 1, minWidth: 150 }}>
                      <label style={{ fontSize: 11, fontWeight: 600, color: theme.textMuted, display: 'block', marginBottom: 4 }}>Date</label>
                      <input
                        type="date"
                        value={dueDate}
                        min={(() => {
                          const today = new Date()
                          const yyyy = today.getFullYear()
                          const mm = String(today.getMonth() + 1).padStart(2, '0')
                          const dd = String(today.getDate()).padStart(2, '0')
                          return `${yyyy}-${mm}-${dd}`
                        })()}
                        onChange={(e) => setDueDate(e.target.value)}
                        style={{
                          width: '100%',
                          boxSizing: 'border-box',
                          padding: 6,
                          background: theme.inputBg,
                          color: theme.text,
                          border: `1px solid ${theme.inputBorder}`,
                          borderRadius: 4,
                          outline: 'none',
                        }}
                      />
                    </div>

                    <div>
                      <label style={{ fontSize: 11, fontWeight: 600, color: theme.textMuted, display: 'block', marginBottom: 4 }}>Timezone</label>
                      <div style={{ display: 'flex', gap: 4 }}>
                        <button
                          type="button"
                          onClick={() => setDueTimezone('local')}
                          style={{
                            padding: '5px 10px',
                            border: `1px solid ${dueTimezone === 'local' ? (darkMode ? '#0f3460' : '#1976d2') : theme.inputBorder}`,
                            borderRadius: 4,
                            background: dueTimezone === 'local' ? (darkMode ? '#0f3460' : '#1976d2') : 'transparent',
                            color: dueTimezone === 'local' ? '#fff' : theme.text,
                            fontSize: 11,
                            fontWeight: 600,
                            cursor: 'pointer',
                          }}
                        >
                          Local
                        </button>
                        <button
                          type="button"
                          onClick={() => setDueTimezone('gmt')}
                          style={{
                            padding: '5px 10px',
                            border: `1px solid ${dueTimezone === 'gmt' ? (darkMode ? '#0f3460' : '#1976d2') : theme.inputBorder}`,
                            borderRadius: 4,
                            background: dueTimezone === 'gmt' ? (darkMode ? '#0f3460' : '#1976d2') : 'transparent',
                            color: dueTimezone === 'gmt' ? '#fff' : theme.text,
                            fontSize: 11,
                            fontWeight: 600,
                            cursor: 'pointer',
                          }}
                        >
                          GMT
                        </button>
                      </div>
                    </div>
                  </div>

                  {dueDate && (
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 4 }}>
                      <span style={{ fontSize: 11, color: theme.textMuted }}>
                        Timestamp: 11:59:59 PM in {dueTimezone === 'gmt' ? 'GMT' : 'Local'}
                      </span>
                      <button
                        type="button"
                        onClick={() => {
                          setDueDate('')
                          setShowDatePicker(false)
                        }}
                        style={{
                          background: 'transparent',
                          color: '#d32f2f',
                          border: 'none',
                          cursor: 'pointer',
                          fontSize: 11,
                          fontWeight: 600,
                        }}
                      >
                        Remove Date
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </form>

        {error && (
          <p style={{
            color: theme.errorText,
            background: theme.errorBg,
            padding: '8px 12px',
            borderRadius: 4,
            marginTop: 12,
            transition: 'all 0.3s ease',
          }}>
            {error}
          </p>
        )}

        <ul style={{ marginTop: 16, padding: 0, listStyle: 'none' }}>
          {tasks.map((t) => (
            <li
              key={t.id}
              style={{
                padding: '6px 0',
                borderBottom: `1px solid ${theme.cardBorder}`,
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                transition: 'border-color 0.3s ease',
              }}
            >
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
                <span
                  onClick={() => handleToggle(t.id)}
                  style={{
                    cursor: 'pointer',
                    textDecoration: t.done ? 'line-through' : 'none',
                    color: t.done ? theme.textMuted : 'inherit',
                  }}
                >
                  {t.done ? '✓ ' : '○ '}{t.title}
                </span>
                {t.due_date_millis && (
                  <span style={{ fontSize: 11, color: theme.textMuted, display: 'flex', alignItems: 'center', gap: 4 }}>
                    📅 Due: {new Date(t.due_date_millis).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                  </span>
                )}
              </div>

              <div style={{ position: 'relative' }}>
                <span
                  onClick={(e) => {
                    e.stopPropagation()
                    if (!t.done) setEditingPriorityId(editingPriorityId === t.id ? null : t.id)
                  }}
                  style={{
                    fontSize: 11,
                    fontWeight: 600,
                    padding: '2px 8px',
                    borderRadius: 10,
                    background: t.done ? theme.doneBadgeBg : `${PRIORITY_COLORS[t.priority]}18`,
                    color: t.done ? theme.textMuted : PRIORITY_COLORS[t.priority],
                    textTransform: 'capitalize',
                    cursor: t.done ? 'default' : 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  {t.priority}
                </span>

                {editingPriorityId === t.id && (
                  <div
                    style={{
                      position: 'absolute',
                      right: 0,
                      top: '100%',
                      marginTop: 4,
                      display: 'flex',
                      gap: 4,
                      background: theme.dropdownBg,
                      border: `1px solid ${theme.dropdownBorder}`,
                      borderRadius: 8,
                      padding: 4,
                      boxShadow: theme.dropdownShadow,
                      zIndex: 10,
                      animation: 'fadeIn 0.15s ease-in',
                    }}
                  >
                    {PRIORITIES.map((p) => {
                      const isCurrent = t.priority === p.value
                      return (
                        <button
                          key={p.value}
                          onClick={(e) => {
                            e.stopPropagation()
                            if (!isCurrent) handlePriorityChange(t.id, p.value)
                            else setEditingPriorityId(null)
                          }}
                          style={{
                            border: `2px solid ${p.color}`,
                            borderRadius: 6,
                            background: isCurrent ? p.color : 'transparent',
                            color: isCurrent ? '#fff' : p.color,
                            fontWeight: isCurrent ? 700 : 500,
                            cursor: 'pointer',
                            fontSize: 11,
                            padding: '3px 10px',
                            transition: 'all 0.15s ease',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {p.label}
                        </button>
                      )
                    })}
                  </div>
                )}
              </div>
            </li>
          ))}
        </ul>

        <style>{`
          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-4px); }
            to   { opacity: 1; transform: translateY(0); }
          }
        `}</style>
      </div>
    </div>
  )
}
