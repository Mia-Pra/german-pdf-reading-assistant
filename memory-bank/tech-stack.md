# Tech Stack

## Frontend

React with Vite

Reason: Vite provides a fast, simple React setup for a demo. React is suitable for a two-page app, PDF preview, assistant panel state, and vocabulary table.

## Frontend Routing

React Router

Reason: The app has two clear pages: reader/assistant and vocabulary notebook.

## PDF Preview

Browser PDF embed or React PDF viewer

Reason: The requirement is to show the original PDF visually while the backend parses text. The MVP can start with browser-native PDF embedding using an uploaded file URL. If selection support is insufficient, parsed text can be shown as an additional selectable text layer.

## Backend

FastAPI

Reason: FastAPI is lightweight, easy to demo, and provides clean API endpoints for upload, parsing, AI calls, vocabulary persistence, and Word export.

## Backend Runtime

Python 3.10 or newer

Reason: Good compatibility with FastAPI, PyMuPDF, python-docx, OpenAI SDK, and German NLP libraries if needed.

## PDF Parsing

PyMuPDF

Reason: Reliable extraction of text from text-based PDFs with page numbers.

## AI API

OpenAI-compatible chat completions through backend `.env`

Reason: Keeps API keys out of the frontend and allows OpenAI, DeepSeek, Qwen-compatible endpoints, or other OpenAI-style providers.

## Word Information

LLM structured output first, optional spaCy enhancement later

Reason: The user requires lemma, POS, plural, translation, and example sentence. For a demo, LLM structured JSON is the fastest complete path. spaCy can later improve deterministic lemma/POS extraction, but it does not reliably provide Chinese translation or plural for every word by itself.

## Vocabulary Persistence

Local JSON files under `storage/`

Reason: User wants backend local persistence but no database complexity. JSON is transparent and easy to inspect during a demo.

## Word Export

python-docx

Reason: Generates `.docx` vocabulary notebook files directly from backend data.

## Environment Configuration

Backend `.env`

Required keys:

```env
OPENAI_API_KEY=
OPENAI_BASE_URL=
OPENAI_MODEL=
```

## Testing

- Backend: pytest for parsing, vocabulary storage, and export logic.
- Frontend: manual smoke test for page navigation, upload, assistant actions, and export.
- API: FastAPI generated docs at `/docs` for endpoint checks.

## Local Development

Planned commands:

```powershell
cd backend
uvicorn app.main:app --reload
```

```powershell
cd frontend
npm install
npm run dev
```
