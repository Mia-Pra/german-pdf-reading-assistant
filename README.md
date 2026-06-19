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
```

The backend can start without real AI credentials. Upload, preview, vocabulary list, delete, and Word export still work. AI endpoints return a clear setup error until the three `.env` values are configured.

## Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

If you add or change backend endpoints while the server is already running, restart the backend process so the new routes are loaded.

## Demo Flow

1. Start the backend and frontend.
2. Open the Reader page.
3. Upload a text-based German PDF.
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

## Local Storage

Runtime files are stored under `backend/storage/`:

- `uploads/`: uploaded PDFs.
- `documents/current.json`: parsed current document metadata and page text.
- `translations/current_full_translation.json`: cached full-document translation for the current document id.
- `vocabulary.json`: saved vocabulary items.

## Limitations

- No OCR. Scanned PDFs without extractable text return an OCR-not-supported error.
- No login or user accounts.
- No database; all persistence is local JSON/files.
- No cloud sync or multi-user permissions.
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
```

Set this frontend environment variable in Vercel:

```env
VITE_API_BASE_URL=https://your-backend.onrender.com
```

The Render Blueprint mounts a persistent disk at `/var/data` so uploaded PDFs,
translation cache, and vocabulary data survive service restarts. This demo has
no user accounts, so all visitors share the same stored document and vocabulary.
