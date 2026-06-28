# Smart Monkey Frontend

Vite + React + TypeScript boilerplate for a coding platform frontend.

## Run

```bash
npm install
npm run dev
```

## Environment Setup

Create a local `.env` file for development.

Safe client-side variables:

```env
VITE_APP_NAME=Smart Monkey
VITE_API_BASE_URL=http://localhost:3000
VITE_FOUNDRY_PROJECT_LABEL=Azure Foundry Connected
VITE_FOUNDRY_REGION=Private
```

Secret handling rules:

- Only `VITE_` variables are exposed to the browser.
- Do not put `AZURE_FOUNDRY_API_KEY` or any secret into `VITE_` variables.
- Keep Azure Foundry credentials in a backend service, server runtime, or managed secret store.
- The frontend should call your backend API, and the backend should call Azure Foundry.

## Suggested Backend Secret Variables

These should stay server-side only:

```env
AZURE_FOUNDRY_ENDPOINT=
AZURE_FOUNDRY_API_KEY=
AZURE_FOUNDRY_DEPLOYMENT=
AZURE_FOUNDRY_API_VERSION=2025-01-01-preview
```
