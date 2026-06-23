# Aurelian Live-Coding Practice — Tasks App (FastAPI + React)

A small existing full-stack app, like what you'll get in the interview. One working
feature (list + add tasks). Your job: **read it, run it, then add features.**

## Run it (the "bootstrap")

**Backend** (terminal 1):
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload          # → http://localhost:8000  (docs at /docs)
```

**Frontend** (terminal 2):
```bash
cd frontend
npm install
npm run dev                        # → http://localhost:5173
```

Open http://localhost:5173 — you should see the task list and be able to add tasks.

## How to approach it (the interview method)
1. **Read first (~5 min).** Trace ONE feature end-to-end: how does a task get from
   `backend/main.py` → the API → `src/api.js` → `App.jsx` state → the rendered list?
2. **Find the seam.** Most features = backend field/endpoint → API call → React state → UI.
3. **Use your AI tool as the driver** — prompt with the context you just gathered, then
   read/verify/explain what it produces. Run it. Narrate.

## Practice features (easy → harder — do them in order)

1. **Toggle done** — click a task to mark it complete/incomplete.
   - Backend: `PATCH /tasks/{id}` (or `PUT`) to flip `done`. Frontend: click handler → update state.
2. **Delete a task** — a ✕ button on each row.
   - Backend: `DELETE /tasks/{id}`. Frontend: button → call API → remove from state.
3. **Filter** — All / Active / Completed buttons (frontend only — pure React state).
4. **Priority field** — add `priority` ("low/med/high") to the model + show a badge +
   a `<select>` in the add form. (Touches model, API, form, and render — the full stack.)
5. **Task count summary** — "2 of 3 done" line that updates live.

Each one mirrors a real "small feature" ask. Aim to do #1–#3 today; #4 is the best
full-stack rep.

## Tips
- Backend interactive docs at http://localhost:8000/docs — test endpoints there.
- `done` already exists in the backend model and is returned by the API — feature #1
  is mostly wiring it up on the frontend + an endpoint to change it.
- Keep a minimal version working first, then refine. Don't rabbit-hole.
