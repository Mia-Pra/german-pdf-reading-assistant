# German PDF Reading Assistant Demo

React + FastAPI demo for AI-assisted German PDF reading.

The app has two pages:

- Reader: upload and preview a German PDF, ask questions, summarize, translate sentences or words, and show full-document Chinese translation beside the original text.
- Vocabulary: review saved word records, delete entries, and export the notebook as a Word `.docx` file.

## Requirements

- Python 3.11 or newer
- Node.js 20 or newer
- A text-based PDF with selectable/extractable text
- An OpenAI-compatible chat completions provider for AI actions

## Backend Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload
```

The backend starts at `http://127.0.0.1:8000`.

Configure `backend/.env` before using AI actions:

```env
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen-plus
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_STORAGE_BUCKET=pdfs
```

The backend starts without Supabase values, but authenticated application APIs
return a clear configuration error until they are set. Never put the service-role
key in the frontend.

## Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

If you add or change backend endpoints while the server is already running, restart the backend process so the new routes are loaded.

## Demo Flow

1. Open the app. It automatically creates or restores an anonymous session.
2. Upload a text-based German PDF.
4. Use the assistant actions:
   - `Summary`: Chinese summary of the current PDF.
   - `Full Translation`: page-aligned original/Chinese comparison in the left reader pane.
   - `Sentence`: translate selected or manually typed German text.
   - `Word`: return lemma, part of speech, plural, Chinese translation, and example sentence.
5. Save a word result to the vocabulary notebook.
6. Open the Vocabulary page.
7. Delete unwanted entries or export the notebook as `vocabulary-notebook.docx`.

## API Summary

- `GET /health`: backend health check.
- `POST /api/documents/upload`: upload, save, and parse a PDF.
- `GET /api/documents/current`: return current document metadata and parsed text.
- `GET /api/documents/current/pdf`: serve the current PDF inline for preview.
- `POST /api/ai/ask`: answer a question using the current document.
- `POST /api/ai/summary`: summarize the current document in Chinese.
- `POST /api/ai/translate/sentence`: translate German text into Chinese.
- `POST /api/ai/translate/word`: return structured German vocabulary data.
- `POST /api/ai/translate/full`: return page-aligned full-document Chinese translation and reuse the local cache.
- `GET /api/vocabulary`: list saved vocabulary.
- `POST /api/vocabulary`: save a vocabulary item with duplicate handling.
- `DELETE /api/vocabulary/{id}`: delete one vocabulary item.
- `GET /api/vocabulary/export`: download the vocabulary notebook as Word.

## Supabase Setup

1. Create a free Supabase project.
2. Open SQL Editor and run [`backend/supabase/migration.sql`](backend/supabase/migration.sql).
3. In Project Settings > API, copy the project URL, anon key, and service-role key.
4. Configure the backend and frontend variables shown above.

Supabase stores:

- Private PDFs in the `pdfs` Storage bucket.
- One current parsed document per account.
- One full-translation cache per account.
- Vocabulary rows owned by each account.

Enable **Anonymous Sign-Ins** in Supabase Authentication settings. The migration
enables row-level security. The FastAPI backend derives every query from the
verified anonymous user id, so browsers cannot read or modify another browser
session's data.

## Limitations

- No OCR. Scanned PDFs without extractable text return an OCR-not-supported error.
- Supabase free-tier quotas apply.
- Anonymous data is tied to browser storage. Clearing site data or changing
  browsers creates a new user and makes the previous data inaccessible.
- Parsed text does not preserve exact PDF layout. The original PDF iframe is used for visual reading.

## Production Deployment

The repository includes deployment configuration for:

- Render: deploy the FastAPI backend from the root `render.yaml` Blueprint.
- Vercel: deploy the `frontend/` directory as a Vite application.

Set these backend environment variables in Render:

```env
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen-plus
CORS_ORIGINS=https://your-frontend.vercel.app
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_STORAGE_BUCKET=pdfs
```

Set this frontend environment variable in Vercel:

```env
VITE_API_BASE_URL=https://your-backend.onrender.com
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

The Render backend can remain on the free instance type because durable data is
stored in Supabase rather than Render's `/tmp` filesystem.

Current deployment:

- Web app: https://german-pdf-reading-assistant-web.onrender.com
- Backend API: https://german-pdf-reading-assistant.onrender.com
- Health check: https://german-pdf-reading-assistant.onrender.com/health
