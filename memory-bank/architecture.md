# Architecture

## Current State

Step 1 is complete. The repository now has a minimal React + Vite frontend skeleton and a minimal FastAPI backend skeleton.

Step 2 is complete. Backend configuration and local storage scaffolding are now in place.

Step 3 is complete. The backend can upload, save, parse, validate, and persist text-based PDF documents.

Step 4 is complete. The backend can return current document metadata and safely serve the current uploaded PDF for preview.

Step 5 is complete. The frontend has the target two-route layout shell with a desktop 70/30 reader/assistant workspace and a vocabulary notebook shell.

Step 6 is complete. The Reader page can upload PDFs to the backend and render the current PDF preview in the left reading pane.

Step 7 is complete. The backend has a reusable OpenAI-compatible AI client and shared AI error mapping for future AI endpoints.

Step 8 is complete. The backend has free-form document QA, and the frontend assistant Send action is connected to it.

Step 9 is complete. The backend has document summary, and the frontend Summary action is connected to it.

Step 10 is complete. The backend has sentence translation, and the frontend Sentence action is connected to it.

Step 11 is complete. The backend has structured word translation, and the frontend Word action is connected to it.

Step 12 is complete. The backend can list, add, de-duplicate, persist, and delete vocabulary items in local JSON storage.

Step 13 is complete. The frontend can save the current word translation result to the backend vocabulary API, and the vocabulary page can load saved words from the backend.

Step 14 is complete. The vocabulary page renders the saved vocabulary table with required fields and can delete individual entries through the backend API.

Step 15 is complete. The backend can export saved vocabulary as an in-memory `.docx` download, and the frontend Export Word action downloads it.

Step 16 is complete. The backend can translate the full current document page by page with local cache reuse, and the frontend shows original/Chinese translation comparison in the reader area.

Step 17 is complete. The README documents setup, AI configuration, demo flow, API surface, local storage, and limitations; frontend document-action error states are polished.

Synonym functionality from Steps 18 and 19 has been removed by user request. The current implementation is restored to the original Step 17 vocabulary fields.

Production deployment support is complete. The frontend API base URL, backend
CORS origins, and backend storage directory are environment-configurable.
`render.yaml` defines the free FastAPI service and ephemeral runtime storage, while
`frontend/vercel.json` provides SPA route fallback for Vercel.

Step 19 is implemented. Supabase authentication gates the app.
PDFs are stored in a private Supabase Storage bucket, while parsed current
documents, translation caches, and vocabulary are stored per user in PostgreSQL.
The SQL migration enables row-level security.

Step 20 is implemented. The frontend automatically restores or creates a
Supabase anonymous session and no longer displays registration, sign-in, or
sign-out controls.

Step 21 is implemented. Supabase Storage PDF object names are generated as
ASCII-only UUID filenames, while the original user filename remains in document
metadata for display. This supports filenames containing Chinese characters,
spaces, or punctuation.

The active production demo uses two Render services:

- Static frontend: `https://german-pdf-reading-assistant-web.onrender.com`
- FastAPI backend: `https://german-pdf-reading-assistant.onrender.com`

Render has a `/*` to `/index.html` rewrite for React routes. The backend
`CORS_ORIGINS` setting allows the production frontend origin.

## Planned Top-Level Structure

- `frontend/`: React + Vite web app.
- `backend/`: FastAPI backend API.
- `README.md`: local development instructions.
- `.gitignore`: ignores generated frontend builds, dependencies, Python caches, virtual environments, and environment files.
- `render.yaml`: Render Blueprint for the free FastAPI backend with ephemeral storage.
- `frontend/vercel.json`: Vercel SPA rewrite configuration.
- `frontend/.env.example`: frontend backend-URL configuration template.
- `backend/storage/`: local runtime storage for uploaded PDFs, parsed document JSON, cached translations, and vocabulary JSON.
- `backend/.env.example`: template for AI provider configuration.
- `backend/app/config.py`: environment-backed settings object and AI configuration validation.
- `backend/app/storage.py`: storage paths and directory initialization.
- `backend/app/auth.py`: verifies Supabase access tokens and returns the authenticated user.
- `backend/app/supabase_store.py`: service-role access to Supabase REST and Storage APIs.
- `backend/supabase/migration.sql`: database tables, indexes, storage bucket, and RLS policies.
- `backend/app/pdf_parser.py`: PyMuPDF text extraction and paragraph splitting.
- `backend/app/documents.py`: document upload API and current parsed document persistence.
- `backend/app/ai_client.py`: OpenAI-compatible chat completions client and AI-specific exceptions.
- `backend/app/api_errors.py`: maps AI client exceptions to FastAPI HTTP errors.
- `backend/app/ai.py`: AI API routes for question answering, summary, sentence translation, structured word translation, and full-document page-aligned translation.
- `backend/app/vocabulary.py`: vocabulary API routes for listing, adding with duplicate handling, deleting local vocabulary items, and exporting vocabulary as a Word document.
- `memory-bank/design-document.md`: product and behavior specification.
- `memory-bank/tech-stack.md`: chosen technical stack and rationale.
- `memory-bank/implementation-plan.md`: ordered, verifiable implementation steps.
- `memory-bank/progress.md`: execution log after each validated step.
- `memory-bank/architecture.md`: current map of important files and responsibilities.

## Planned Frontend Responsibilities

Implemented now:

- Two-page navigation shell.
- Reader page placeholder with PDF area, reader mode toolbar, and AI assistant area.
- PDF file input wired to `POST /api/documents/upload`.
- Upload state handling for idle, uploading, ready, and error states.
- PDF iframe preview using the backend `pdf_url` returned after upload.
- Automatic anonymous sign-in and persisted browser session.
- Bearer access token attached to every application API request.
- Reader page automatically loads the current backend document on page open when one exists.
- Reader toolbar can switch between original PDF preview and full-document translation comparison.
- Assistant panel shell with fixed action buttons for summary, full translation, sentence translation, and word translation.
- Assistant text input wired to `POST /api/ai/ask`.
- Summary fixed action wired to `POST /api/ai/summary`.
- Sentence fixed action wired to `POST /api/ai/translate/sentence`.
- Word fixed action wired to `POST /api/ai/translate/word`.
- Full Translation fixed action wired to `POST /api/ai/translate/full`.
- Assistant answer display with source page numbers and error state.
- Clear disabled states and guidance for document-specific actions when no PDF is loaded.
- Structured word result display for source word, lemma, part of speech, plural, translation, and example sentence.
- Add-to-vocabulary action for structured word translation results, with saved, duplicate, saving, and error feedback.
- Full-document translation comparison view in the reader pane with page-aligned original text and Chinese translation columns.
- Full Translation errors now distinguish a stale backend route (`404 Not Found` from FastAPI's default handler) from document or AI-provider errors, so users know to restart the backend when the running service is out of date.
- Vocabulary page shell with summary metrics, required-field table, backend-loaded saved rows, per-row delete controls, and Word export download action.
- Responsive behavior: desktop side-by-side reader/assistant layout; mobile stacked layout below the phone breakpoint.

Planned next:

- No planned implementation steps remain.

## Planned Backend Responsibilities

Implemented now:

- FastAPI application entry point.
- CORS configuration for local Vite frontend.
- `/health` endpoint.
- Environment-backed settings loader for `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_MODEL`.
- Environment-backed production settings for `CORS_ORIGINS` and `STORAGE_DIR`.
- Explicit AI config validation helper for future AI endpoints.
- Supabase configuration for project URL, anon key, service-role key, and private PDF bucket.
- `POST /api/documents/upload` for authenticated PDF parsing, private Storage upload, and per-user document persistence.
- `GET /api/documents/current` for current parsed metadata and `pdf_url`.
- Signed private Storage URLs for iframe PDF preview.
- Validation for non-PDF uploads, empty uploads, invalid PDFs, and no-text PDFs.
- Safe current-PDF lookup that prevents arbitrary path serving and reports missing metadata/files clearly.
- OpenAI-compatible `/chat/completions` client using backend `.env` values.
- AI error classes for missing configuration, provider failures, and unexpected provider responses.
- Shared helper for converting AI client errors to HTTP errors.
- `POST /api/ai/ask` for question validation, current document loading, simple relevant-page selection, AI prompting, and source page return.
- `POST /api/ai/summary` for current document loading, context chunking, summary prompting, and source page return.
- `POST /api/ai/translate/sentence` for manual or selected German sentence translation to Chinese.
- `POST /api/ai/translate/word` for manual or selected German word analysis with lemma, part of speech, plural, translation, and example sentence.
- `POST /api/ai/translate/full` for page-aligned full-document Chinese translation, cached per authenticated user.
- `GET /api/vocabulary` for listing only the authenticated user's saved vocabulary.
- `POST /api/vocabulary` for validating and adding vocabulary items, returning an existing item when the same lemma and part of speech already exist.
- `DELETE /api/vocabulary/{id}` for deleting one saved vocabulary item by id.
- `GET /api/vocabulary/export` for generating the authenticated user's `.docx` vocabulary notebook.

Planned next:

- No planned implementation steps remain.

## Planned API Groups

- `/api/documents/*`: upload, current document, PDF preview.
- `/api/ai/*`: ask, summary, sentence translation, word translation, full translation.
- `/api/vocabulary/*`: list, add, delete, export Word.

## Update Rule

Update this file after each validated implementation step that adds, removes, or changes important files or responsibilities.
