# Implementation Plan

## Step 1: Create React And FastAPI Project Skeleton

Create `frontend/` with a Vite React app structure and `backend/` with a FastAPI app structure. Add root README setup notes.

Validation:

- Backend starts and exposes a health endpoint.
- Frontend starts and renders a basic two-page navigation shell.

## Step 2: Add Backend Configuration And Storage Directories

Add `.env.example`, backend settings loader, and local storage directories for uploads, parsed documents, translations, and vocabulary.

Validation:

- Backend can start without a real API key.
- Missing `.env` values produce clear runtime errors only when AI endpoints are called.
- Storage directories are created or documented.

## Step 3: Implement PDF Upload And Text Parsing API

Create `POST /api/documents/upload` to accept a PDF, save it locally, parse text with PyMuPDF, and store parsed pages in local JSON.

Validation:

- Uploading a text-based German PDF returns filename, page count, and parsed text metadata.
- Uploading a non-PDF returns a validation error.
- Uploading a scanned PDF with no text returns an OCR-not-supported message.

## Step 4: Implement Current Document API And PDF File Serving

Create `GET /api/documents/current` and a safe endpoint for serving the uploaded PDF preview file to the frontend.

Validation:

- Frontend or browser can fetch current document metadata.
- PDF preview URL can be opened after upload.

## Step 5: Build Frontend Page Layout And Routing

Create two routes: reader/assistant page and vocabulary page. Build the Page 1 70/30 layout and Page 2 vocabulary shell.

Validation:

- Page navigation works.
- Page 1 visually reserves about 70% width for the PDF and 30% for assistant controls on desktop.
- Mobile layout stacks sections without overlap.

## Step 6: Connect Frontend PDF Upload And Preview

Add upload UI on Page 1. Send PDFs to backend, then display the returned PDF preview URL in the left reading area.

Validation:

- User can upload a PDF from the browser.
- Original PDF preview appears after upload.
- Upload errors display clearly.

## Step 7: Implement AI Client On Backend

Add a reusable OpenAI-compatible client using `.env` values. Create shared request/response helpers and error handling.

Validation:

- A backend-only test prompt can call the configured model when `.env` is valid.
- Missing config returns a clear API error.

## Step 8: Implement Free-Form Document QA

Create `POST /api/ai/ask` using parsed document context and simple page selection or chunking.

Validation:

- User can ask a question about an uploaded PDF.
- Response appears in the assistant panel.
- Calling before upload returns a clear error.

## Step 9: Implement Document Summary Action

Create `POST /api/ai/summary` and connect it to a fixed frontend button.

Validation:

- Summary button returns a Chinese document summary.
- Long documents are chunked or summarized safely.

## Step 10: Implement Sentence Translation

Create `POST /api/ai/translate/sentence`. Connect it to manual input and selected text input from the reader area when available.

Validation:

- Manual sentence translation works.
- Selected text can be sent to the same endpoint.
- Empty input is rejected.

## Step 11: Implement Word Translation With Structured Output

Create `POST /api/ai/translate/word` returning lemma, part of speech, plural, Chinese translation, and example sentence.

Validation:

- Manual word input returns all required fields.
- Selected word input uses the same endpoint.
- Invalid or empty input is rejected.

## Step 12: Implement Vocabulary Persistence API

Create list, add, and delete endpoints backed by `storage/vocabulary.json`.

Validation:

- Adding a word persists it to local JSON.
- Refreshing the frontend still shows saved vocabulary.
- Duplicate entries are handled predictably.

## Step 13: Connect Add-To-Vocabulary From Word Results

Add frontend action to save the current word translation result to the backend vocabulary API.

Validation:

- Word result can be added with one click.
- Saved item appears on Page 2.

## Step 14: Implement Vocabulary Page Table

Build the Page 2 table with lemma, POS, plural, translation, and example sentence. Include delete controls.

Validation:

- Vocabulary loads from backend.
- Deleting one entry removes only that entry.

## Step 15: Implement Word Export

Create `GET /api/vocabulary/export` to generate a `.docx` file in memory and return it as a direct download. Add frontend export button.

Validation:

- Clicking export downloads a valid Word document.
- The Word file contains lemma, POS, plural, translation, and example sentence.

## Step 16: Implement Full-Document Translation Comparison Mode

Create `POST /api/ai/translate/full` and show original/translation comparison in the left reader area.

Validation:

- Full translation appears in the reader area, not only in the assistant panel.
- Translation is page-aligned or clearly section-aligned with the original.
- Repeated calls use cached translation when possible.

## Step 17: Polish Error States And README

Document setup, `.env`, backend startup, frontend startup, PDF limitations, and demo flow.

Validation:

- A fresh user can follow README steps to run both services.
- Known limitations include no OCR, no login, no database, and local-file persistence.

## Step 18: Add Production Deployment Support

Make frontend API routing, backend CORS, and backend storage configurable through
environment variables. Add Render and Vercel deployment descriptors and document
the production environment variables.

Validation:

- Frontend production build succeeds with a configured backend URL.
- Backend health endpoint succeeds with configured CORS and storage paths.
- Local defaults continue to support the existing development workflow.

## Step 19: Add Supabase Authentication And Durable Multi-User Storage

Add email/password authentication through Supabase. Require authenticated API
requests, store each user's PDF in Supabase Storage, and store current document
metadata, translation cache, and vocabulary in Supabase PostgreSQL tables with
row-level security.

Validation:

- Frontend production build succeeds with Supabase configuration.
- Missing backend Supabase configuration returns a clear service error.
- Unauthenticated stateful API requests return 401.
- Database migration defines per-user tables, constraints, and RLS policies.
- PDF, document metadata, translation cache, and vocabulary operations are scoped
  to the authenticated user.

## Step 20: Switch To Automatic Anonymous Authentication

Replace the email/password account screen with automatic Supabase anonymous
sign-in. Persist the anonymous session in the browser and continue using the
authenticated user id for database and Storage isolation.

Validation:

- A browser without a session automatically creates an anonymous Supabase user.
- A restored session opens the workspace without creating another user.
- The email/password form and sign-out action are removed.
- Frontend production build succeeds.
- Existing backend token verification and per-user RLS remain unchanged.

## Step 21: Make PDF Storage Object Names Unicode-Safe

Store uploaded PDFs under an ASCII-only UUID object name while preserving the
original client filename in document metadata for display.

Validation:

- A valid PDF with Chinese characters and spaces in its filename uploads through
  the backend flow without placing those characters in the Supabase Storage key.
- The generated object name matches `<32 lowercase hex characters>.pdf`.
- The upload response still returns the original filename for display.

## Step 22: Reduce PDF Upload Latency

Run local PDF text extraction and the private Supabase Storage upload
concurrently. Persist only the page text required by AI features, and return
compact document metadata to the frontend instead of returning the full parsed
document after upload.

Validation:

- PDF parsing and Storage upload overlap instead of running sequentially.
- Parsed page data no longer duplicates page text inside paragraph records.
- Upload and current-document responses omit internal parsed page content.
- Failed parsing removes any Storage object uploaded by the concurrent task.
- Backend syntax and frontend production build succeed.
