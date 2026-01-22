# University Policy QA Frontend (Next.js)

This frontend provides a polished UI for the RAG‑based University Policy & Student Handbook QA system. It connects to the FastAPI backend and renders answers with citations using Markdown.

## Features

- Modern, assistant‑style UI with quick actions
- Template prompts that auto‑submit
- Markdown rendering for formatted answers
- Built‑in `/api/ask` proxy to avoid CORS issues

## Prerequisites

- Node.js 18+
- Backend running on `http://localhost:8001` (see root README)

## Quick Start

1) Install dependencies:

```bash
npm install
```

2) Start the dev server:

```bash
npm run dev
```

3) Open:

```
http://localhost:3000
```

## Backend Connection

The frontend sends questions to `POST /api/ask`, which proxies to the backend API.

- Default backend URL: `http://localhost:8001`
- Override with `NEXT_PUBLIC_API_BASE`

Example (PowerShell):

```powershell
$env:NEXT_PUBLIC_API_BASE = "http://localhost:8001"
npm run dev
```

## File Overview

- `app/page.tsx` – main UI and submission logic
- `app/api/ask/route.ts` – API proxy to backend
- `app/page.module.css` – UI styles

## Troubleshooting

- **Failed to fetch**: backend not running or wrong `NEXT_PUBLIC_API_BASE`.
- **Module not found**: run `npm install` after pulling updates.

## Build for Production

```bash
npm run build
npm run start
```
