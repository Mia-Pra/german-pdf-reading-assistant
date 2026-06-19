# Progress

## 2026-06-14

- Bootstrapped the document-first workflow for a German PDF reading assistant.
- Updated requirements after user clarification rounds.
- Changed target architecture from Streamlit MVP to React frontend plus FastAPI backend.
- Confirmed two pages: reader/assistant and vocabulary notebook.
- Confirmed no mind map, no OCR, backend `.env` API config, local JSON persistence, direct Word export.
- Completed Step 1: created React + Vite frontend skeleton, FastAPI backend skeleton, root README, and project ignore rules.
- Validated backend health endpoint with FastAPI TestClient returning 200 and `{"status": "ok"}`.
- Validated frontend with `npm run build`.
- Completed Step 2: added backend `.env.example`, settings loader, storage path module, storage directory placeholders, and startup storage initialization.
- Validated backend still starts without real AI credentials.
- Validated missing AI config reports: `AI configuration is missing. Set OPENAI_API_KEY, OPENAI_BASE_URL, and OPENAI_MODEL in backend/.env.`
- Validated startup creates `backend/storage/vocabulary.json` with an empty list.
- Completed Step 3: added PDF upload endpoint, PyMuPDF parsing, document JSON persistence, and PDF upload validation.
- Validated text-based German PDF upload returns 200, page count, parsed text, and writes `backend/storage/documents/current.json`.
- Validated non-PDF upload returns 400 with `Only PDF files are supported.`
- Validated empty text-layer PDF returns 422 with `No extractable text was found. OCR scanned PDFs are not supported.`
- Completed Step 4: added `GET /api/documents/current` and `GET /api/documents/current/pdf`.
- Validated current metadata returns filename, page count, parsed pages, and `pdf_url`.
- Validated current PDF endpoint returns `application/pdf` content.
- Validated missing current document returns 404 with `No current document is available. Upload a PDF first.`
- Completed Step 5: refined React routing shell, reader/assistant layout, assistant action panel, and vocabulary page shell.
- Validated frontend build with `npm run build`.
- Validated browser routing for `/` and `/vocabulary`.
- Validated desktop reader layout is side-by-side with about 69% PDF area and 30% assistant area at 1280px width.
- Validated mobile reader layout stacks at 390px width without overlap.
- Completed Step 6: connected the Reader page upload control to `POST /api/documents/upload` and rendered the backend PDF preview URL in an iframe.
- Validated frontend build with `npm run build`.
- Validated backend upload/current/PDF-preview API chain with a generated text-based PDF.
- Validated the Reader page contains one PDF file input, an Upload PDF button, initial placeholder state, and no initial error.
- Completed Step 7: added reusable OpenAI-compatible backend AI client, `.env` loading, AI-specific exception classes, and FastAPI error mapping helper.
- Validated missing AI config raises a clear `AIConfigurationError` naming missing `OPENAI_API_KEY` and `OPENAI_MODEL`.
- Validated mock OpenAI-compatible `/chat/completions` call sends the configured model and bearer token, and parses the returned assistant message.
- Validated backend health endpoint still returns 200.
- Completed Step 8: added `POST /api/ai/ask` for free-form document QA and connected the Reader assistant Send action to it.
- Validated missing current document returns 404 with `No current document is available. Upload a PDF first.`
- Validated empty question returns 400 with `Question cannot be empty.`
- Validated missing AI config returns a clear 503 error after a document is uploaded.
- Validated mock AI answer returns 200 with `answer` and `source_pages`.
- Validated frontend build with `npm run build`.
- Completed Step 9: added `POST /api/ai/summary` and connected the Summary fixed action button.
- Validated missing current document returns 404 for summary.
- Validated missing AI config returns a clear 503 error for summary after upload.
- Validated mock summary returns 200 with `summary` and `source_pages`.
- Validated frontend build with `npm run build`.
- Completed Step 10: added `POST /api/ai/translate/sentence` and connected the Sentence fixed action button.
- Validated empty sentence returns 400 with `Sentence cannot be empty.`
- Validated missing AI config returns a clear 503 error for sentence translation.
- Validated mock sentence translation returns 200 with `source_text` and `translation`.
- Validated frontend build with `npm run build`.
- Rechecked Step 10 after context reload: frontend build passed and `POST /api/ai/translate/sentence` still accepts valid input and rejects empty input.
- Completed Step 11: added `POST /api/ai/translate/word` and connected the Reader page Word action to it.
- Validated empty word returns 400 with `Word cannot be empty.`
- Validated invalid overlong word returns 400 with `Word is too long.`
- Validated missing AI config returns a clear 503 error for word translation.
- Validated mock word translation returns 200 with `source_word`, `lemma`, `part_of_speech`, `plural`, `translation`, and `example_sentence`.
- Validated frontend build with `npm run build`.
- Fixed original PDF preview regression: upload responses now include `pdf_url`, current PDFs are served inline for iframe display, and the Reader toolbar switches back to the original PDF view.
- Added frontend auto-load for the current backend document so an already uploaded PDF appears after page refresh.
- Validated frontend build, backend PDF preview headers, and browser switching from Parsed Text back to Original.

## 2026-06-15

- Fixed the Full Translation `Not Found` issue by restarting the local backend so port 8000 loads the current route table.
- Improved the frontend Full Translation error message for default backend 404 responses, making stale backend processes easier to diagnose.
- Validated the running backend now exposes `POST /api/ai/translate/full`; a GET to the same path returns 405 with `Allow: POST` instead of 404.
- Validated frontend build with `npm.cmd run build` and backend syntax with `python -m compileall app`.
- Removed the Reader page Parsed Text mode from the toolbar and reader pane rendering.
- Removed now-unused parsed text view styles and updated the empty reader copy to reference only PDF preview and translation comparison.
- Updated architecture notes so the Reader toolbar responsibilities match the current UI.
- Completed Step 12: added backend vocabulary persistence API with `GET /api/vocabulary`, `POST /api/vocabulary`, and `DELETE /api/vocabulary/{id}`.
- Added local JSON-backed vocabulary loading and saving through `backend/storage/vocabulary.json`.
- Added duplicate handling by normalized lemma plus part of speech; duplicate adds return the existing item with `created: false`.
- Validated adding a word persists it to JSON, listing returns the saved item, duplicate adds do not create another entry, and deleting one id removes only that item.
- Validated backend health endpoint still returns 200 with `{"status": "ok"}`.
- Completed Step 13: connected the Reader page Add word action to `POST /api/vocabulary` for the current structured word translation result.
- Added frontend save feedback for saved, duplicate, saving, and error states.
- Added minimal Vocabulary page loading from `GET /api/vocabulary` so saved words appear on Page 2.
- Validated frontend build with `npm.cmd run build`.
- Validated vocabulary API add/list flow and confirmed a saved test word appeared on the Vocabulary page; removed the temporary test item afterward.
- Completed Step 14: implemented the Vocabulary page table with lemma, POS, plural, Chinese translation, example sentence, and per-row delete controls.
- Added frontend delete handling for `DELETE /api/vocabulary/{id}`, including per-row deleting state and delete error feedback.
- Tightened vocabulary table styling so long fields wrap predictably and the table remains usable on small screens.
- Validated frontend build with `npm.cmd run build`.
- Validated vocabulary API add/list/delete flow and confirmed deleting one id removes only that item.
- Validated in the browser that a temporary Step14 test word loaded on the Vocabulary page and was removed through the page delete button; confirmed the deletion persisted in backend storage.
- Completed Step 15: added `GET /api/vocabulary/export` to generate a `.docx` vocabulary notebook in memory and return it as a direct download.
- Added `python-docx` to backend requirements for deterministic Word document generation.
- Exported Word files include lemma, POS, plural, Chinese translation, and example sentence in a fixed-width table.
- Connected the frontend Export Word button to the backend export endpoint with download, exporting, and error states.
- Validated frontend build with `npm.cmd run build`.
- Validated the export endpoint returns the correct DOCX media type and `vocabulary-notebook.docx` download filename.
- Validated the generated DOCX can be opened with `python-docx` and contains the required headers and saved vocabulary content.
- Validated empty vocabulary export still returns a valid DOCX with an empty-state row.
- Validated the DOCX package structure and table OOXML contains table width, grid, and cell-width markers.
- Attempted render-based DOCX QA, but LibreOffice/`soffice` is not installed in the local environment, so visual PNG rendering could not be completed.
- Completed Step 16: added `POST /api/ai/translate/full` for page-aligned full-document translation.
- Added full-document translation cache storage at `backend/storage/translations/current_full_translation.json`, keyed by the current document id.
- Connected the Reader Full Translation action to the backend endpoint and made it switch the left reader pane into translation comparison mode.
- Added a reader-area comparison view with page sections and side-by-side original German text plus Chinese translation columns, with mobile fallback to stacked columns.
- Validated missing current document returns 404 for full-document translation.
- Validated first full translation call returns page-aligned `source_text` and `translation`, writes the cache file, and marks `cached: false`.
- Validated repeated full translation calls for the same document return `cached: true` and do not call the AI client again.
- Validated frontend build with `npm.cmd run build`.
- Validated backend syntax with `python -m compileall app`.
- Validated in the browser that the Reader page exposes translation controls and the Translation Compare mode renders in the left reader area.
- Noted that the currently running backend process on port 8000 had not been restarted and still returned 404 for the new endpoint; restart is required for browser-level Full Translation clicks against the live server.
- Completed Step 17: polished frontend document-action error states and updated README setup documentation.
- Disabled document-specific Reader actions when no PDF is loaded and added guidance that sentence and word translation still work with manual input.
- Replaced outdated assistant placeholder text with current completed workflow copy.
- Rewrote README with current backend setup, frontend setup, `.env` configuration, demo flow, API surface, local storage paths, and known limitations.
- Validated frontend build with `npm.cmd run build`.
- Validated backend syntax with `python -m compileall app`.
- Validated backend health endpoint still returns 200 with `{"status": "ok"}`.
- Validated README no longer contains stale Step 11/planned-feature status text.
- Validated in the browser that Reader page copy no longer contains the old "connected in later steps" text and still exposes Full Translation.
- Completed Step 18: added German synonyms to structured word translation and vocabulary records.
- Updated `POST /api/ai/translate/word` so responses include a `synonyms` array, requesting 3 to 5 German synonyms for suitable single-word inputs and allowing an empty array for unsuitable words, sentences, or longer phrases.
- Updated vocabulary create/list models to persist synonyms while normalizing older records without the field to an empty list.
- Updated the Reader word result, Add-to-vocabulary payload, Vocabulary table, and Word export to include synonyms, displaying `暂无近义词` when empty.
- Updated the design document, implementation plan, architecture notes, and README to include the new German synonyms field.
- Validated frontend build with `npm.cmd run build`.
- Validated backend syntax with `python -m compileall app`.
- Validated word translation, vocabulary save/list, and DOCX export with a mocked German synonym response; temporary test vocabulary was deleted afterward.
- Validated in the browser that the Vocabulary page renders the new Synonyms column and has no console errors.
- Completed Step 19: fixed German synonym quality and added backfill for existing saved vocabulary.
- Tightened word-translation synonym normalization so Chinese terms, duplicate values, and the source word or lemma are filtered out.
- Preserved the rule that sentence or longer phrase inputs return an empty synonym list instead of forced synonyms.
- Added `POST /api/vocabulary/synonyms/backfill` to fill missing German synonyms on existing single-word vocabulary items.
- Added the Vocabulary page `Update Synonyms` action so older saved rows can be refreshed without deleting and re-adding words.
- Repaired corrupted no-synonyms placeholder text in frontend and memory-bank documentation.
- Validated frontend build with `npm.cmd run build`.
- Validated backend syntax with `python -m compileall app`.
- Validated synonym filtering and backfill behavior with mocked AI responses against temporary vocabulary storage; the real `backend/storage/vocabulary.json` was not modified during validation.
- Validated in the browser that the Vocabulary page renders `Update Synonyms`, keeps the Synonyms table column, and reports no console errors.
- Reverted synonym functionality by user request.
- Removed `synonyms` from word translation responses, vocabulary create/list models, Add-to-vocabulary payloads, vocabulary table rendering, and Word export.
- Removed the vocabulary synonym backfill API and the Vocabulary page `Update Synonyms` action.
- Restored README, design document, implementation plan, and architecture notes to the original vocabulary fields: lemma, POS, plural, Chinese translation, and example sentence.
- Validated frontend build with `npm.cmd run build`.
- Validated backend syntax with `python -m compileall app`.
- Validated word translation, vocabulary add/list, and Word export no longer expose a `synonyms` field, even when upstream/mock input includes one.
- Validated in the browser that the Vocabulary page no longer shows `Update Synonyms` or a Synonyms table column, and the required-field count is back to 5.

## 2026-06-19

- Completed Step 18: added production deployment support for Render and Vercel.
- Replaced the frontend's fixed localhost API URL with `VITE_API_BASE_URL` while preserving the local default.
- Added configurable backend `CORS_ORIGINS` and `STORAGE_DIR` settings while preserving local defaults.
- Added a Render Blueprint with FastAPI build/start commands, health check, environment variables, and a persistent disk mounted at `/var/data`.
- Added Vercel SPA rewrite configuration so direct navigation to React routes works.
- Documented production environment variables and the demo's shared-data limitation.
- Validated the frontend production build with a configured remote API URL.
- Validated the backend health endpoint returns 200 with configured production CORS and a temporary storage directory.
- Adjusted the Render Blueprint to use the free instance type without a persistent
  disk after Render identified disks as a paid resource requiring payment details.
- Production runtime data now uses `/tmp` and may be lost when the free service
  restarts or sleeps; this tradeoff is documented in the README and architecture.
- Published the repository at `https://github.com/Mia-Pra/german-pdf-reading-assistant`.
- Deployed the FastAPI backend on Render's free tier at
  `https://german-pdf-reading-assistant.onrender.com`.
- Stored the AI provider configuration in Render environment variables and
  verified `/health` returns 200.
- Vercel rejected account login pending additional account verification, so the
  frontend was deployed as a free Render Static Site instead.
- Deployed the React frontend at
  `https://german-pdf-reading-assistant-web.onrender.com`.
- Added the production frontend to backend CORS and configured a Render SPA
  rewrite from `/*` to `/index.html`.
- Implemented Step 19: Supabase authentication and durable multi-user storage.
- Added frontend email/password registration, sign-in, persisted sessions, and sign-out.
- Added authenticated API requests using the Supabase access token.
- Added backend Supabase token verification and clear 401/503 error handling.
- Migrated PDF persistence to a private Supabase Storage bucket with signed preview URLs.
- Migrated current document metadata, full-translation cache, and vocabulary to
  per-user PostgreSQL records accessed through the backend service role.
- Added `backend/supabase/migration.sql` with tables, duplicate constraints,
  private storage bucket creation, and row-level security policies.
- Added Render and frontend environment variable templates for Supabase.
- Validated backend syntax with `python -m compileall app`.
- Validated the frontend production build with `npm.cmd run build`.
- Validated missing configuration returns 503, missing or invalid auth returns
  401, and two simulated authenticated users cannot list or delete each other's
  vocabulary.
- Validated the public homepage, direct `/vocabulary` route, vocabulary API,
  CORS response, and a live sentence translation of `Guten Tag` to `您好`.
