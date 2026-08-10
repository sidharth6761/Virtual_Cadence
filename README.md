# Virtual Cadence

Virtual Cadence is a modern web application for remote EDA automation. The first phase provides a polished frontend for Cadence Genus project submission and a local FastAPI backend that stores uploads on disk.

## Structure

- frontend: React, TypeScript, Vite, Tailwind CSS, React Router, React Hook Form, Axios
- backend: FastAPI, file upload endpoint, local storage, CORS

## Local Development

### Backend

1. Create and activate a Python environment.
2. Install dependencies from `backend/requirements.txt`.
3. Start the API server:

```bash
uvicorn main:app --reload --app-dir backend
```

### Frontend

1. Install dependencies in `frontend`.
2. Start the dev server:

```bash
npm run dev
```

By default the frontend targets `http://localhost:8000`.
