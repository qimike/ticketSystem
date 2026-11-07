# Ticket Triage

A small support-ticket system. Users submit tickets, an "AI" triage step suggests a category, a priority and a short summary, and a human has to approve the suggestion before it is saved.

- **Backend:** FastAPI ([main.py](main.py)), served by Uvicorn on `http://127.0.0.1:8000`
- **Frontend:** React + Vite ([frontend/](frontend/)), served on `http://localhost:5173`

> **Note:** The triage step is currently a keyword-based stub (`fake_Triage` in `main.py`), not a real AI model. Tickets are stored in memory, so they are lost when the backend restarts.

## Prerequisites

- Python 3.10 or later
- Node.js 22 (the frontend pins `22.23.4` through [Volta](https://volta.sh/); any recent Node 22 should work)
- npm

## 1. Set up the backend

From the project root:

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install fastapi uvicorn
```

Start the API:

```bash
uvicorn main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Interactive API docs are at `http://127.0.0.1:8000/docs`.

## 2. Set up the frontend

```bash
npm create vite@latest frontend
```

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

The frontend calls the API at `http://127.0.0.1:8000` (set in `frontend/src/App.jsx`), and the backend only accepts requests from `localhost:5173` and `127.0.0.1:5173` (CORS settings in `main.py`). If you change either port, update both places.

## Using the app

1. Enter a title and description and click **Submit ticket**. The ticket's status is `open`.
2. Click **Run AI triage**. The ticket gets a suggested category, priority and summary, and its status becomes `needs_review`.
3. Click **Approve**. The suggestions are saved as the final category and priority, and the status becomes `assigned`.

## API reference

| Method | Path                    | Description                                                                                       |
| ------ | ----------------------- | ------------------------------------------------------------------------------------------------- |
| `POST` | `/tickets`              | Create a ticket. Body: `{ "title": str, "description": str, "created_by": int }`                  |
| `GET`  | `/tickets`              | List tickets. Optional query: `?status=open\|needs_review\|assigned`                              |
| `POST` | `/tickets/{id}/triage`  | Run triage and store the suggestions; status becomes `needs_review`                               |
| `POST` | `/tickets/{id}/approve` | Accept the suggestions; status becomes `assigned`. Returns 400 if the ticket has not been triaged |

Example:

```bash
curl -X POST http://127.0.0.1:8000/tickets \
  -H "Content-Type: application/json" \
  -d '{"title": "Cannot login", "description": "SSO error on sign in", "created_by": 1}'
```

## Other frontend commands

Run these from `frontend/`:

| Command           | What it does                          |
| ----------------- | ------------------------------------- |
| `npm run build`   | Production build into `frontend/dist` |
| `npm run preview` | Serve the production build locally    |
| `npm run lint`    | Run ESLint                            |
