# Virtual Cadence

Virtual Cadence is a web application for remote EDA automation. The user-facing flow
talks **directly to Supabase** (Auth + PostgreSQL + Storage) — no backend server is
required for authentication, project/job management, or file upload from the browser.

## Architecture

```
React Frontend
     ↓ (Supabase JS, public anon key)
Supabase Auth  ·  PostgreSQL  ·  Storage (design-files)
     ↓
College Worker (future) → VMware/Linux → Cadence Genus → Reports → Supabase
```

The browser uses only **public** Supabase credentials (`VITE_SUPABASE_URL`,
`VITE_SUPABASE_ANON_KEY`). The service-role key is never exposed to the browser.

## Project structure

- `frontend/` — React + TypeScript + Vite. The entire user flow.
- `supabase/schema.sql` — tables, Row Level Security, and storage policies. Run this in
  the Supabase SQL Editor to enable the app.
- `backend/` — the original FastAPI backend. **Retained for reference / future worker
  functionality. It is NOT a dependency of the frontend.**

## Setup — Supabase

1. Create a Supabase project.
2. Open the **SQL Editor** and run the contents of `supabase/schema.sql`.
   This creates `profiles`, `projects`, `jobs`, `files`, `results` (with RLS), the
   `design-files` storage bucket, and its access policies.
3. Copy `frontend/.env.example` to `frontend/.env.local` and fill in:
   - `VITE_SUPABASE_URL` — your project URL
   - `VITE_SUPABASE_ANON_KEY` — the anon/publishable key (Settings → API)

## Local development (browser flow only — no FastAPI)

```bash
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite. Register/login uses Supabase Auth. Uploading a project
creates a project + job row, uploads files to `design-files/jobs/<user_id>/<job_id>/`,
records file metadata, and marks the job `QUEUED`.

## Manual test

1. Start only the frontend (`npm run dev`).
2. Open the site, register via Supabase Auth, and log in.
3. Upload `design.v`, `library.lib`, `constraints.sdc`.
4. Submit — the job status becomes `QUEUED`.
5. In the Supabase dashboard verify:
   - **Storage → `design-files` → `jobs/<user_id>/<job_id>/`** contains the three files.
   - **Table Editor** shows the project/job/file rows owned by your user.

## Backend tests (retained backend only)

```bash
.venv\Scripts\python.exe -m pytest backend/tests
```