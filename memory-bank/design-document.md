# German PDF Reading Assistant Design Document

## Scope

This project is a React + FastAPI demo for AI-assisted German PDF reading. It has two pages:

- Page 1: PDF reading and AI assistant.
- Page 2: vocabulary notebook and Word export.

The app focuses on a complete demo loop: upload PDF, preview original PDF, parse text on the backend, ask AI questions, translate text, enrich word information, save vocabulary, and export vocabulary as Word.

## Non-Goals

- No OCR for scanned PDFs.
- No mind map feature.
- No social-login providers; email/password authentication is used.
- No requirement to perfectly reproduce PDF layout in parsed text; the original PDF preview handles visual reading.

## Page Structure

### Page 1: Reader And AI Assistant

The page uses a two-column layout:

- Left area: about 70% width, original PDF preview and optional translated comparison mode.
- Right area: about 30% width, AI assistant panel.

The assistant panel includes:

- Fixed action buttons for document summary, full-document translation, sentence translation, and word translation.
- Free-form question input.
- Manual text input for sentence or word translation.
- Display area for AI results.
- Add-to-vocabulary action when the current result is a word translation.

### Page 2: Vocabulary Notebook

The vocabulary page shows saved words in a table and allows direct Word export.

Required vocabulary fields:

- lemma
- part of speech
- plural form
- Chinese translation
- example sentence

The app may also store the surface word and source page internally if useful, but the user-confirmed required fields are the fields above.

## Core User Journeys

### Upload And Read PDF

User uploads a PDF from Page 1. The frontend sends the file to FastAPI. The backend saves the PDF locally, extracts text with PyMuPDF, and returns document metadata and page text. The frontend embeds the original PDF for reading.

Acceptance:

- A text-based German PDF can be uploaded.
- The original PDF can be previewed.
- Backend parsed text is available for AI features.
- If the PDF has no extractable text, the app clearly says OCR is not supported.
- The PDF belongs only to the authenticated user and remains available after backend restarts.

### Ask About The Document

User asks a free-form question in the AI assistant panel. The backend uses parsed document text as context and calls an OpenAI-compatible LLM configured through `.env`.

Acceptance:

- User can ask a question after upload.
- Response is shown in the assistant panel.
- The app handles missing PDF or missing API config with clear errors.

### Generate Document Summary

User clicks document summary. The backend summarizes the parsed PDF text.

Acceptance:

- Summary is returned in Chinese.
- Long documents are handled by chunking or page-level summarization if needed.

### Translate Sentence

User either selects text from the reading area or manually enters a sentence in the assistant panel. The backend translates it into Chinese.

Acceptance:

- Manual input works.
- Selected text input works if available from the PDF preview or parsed text layer.
- Result is displayed in the assistant panel.

### Translate Word

User either selects a word or manually enters a German word. The backend returns a structured result:

- lemma
- part of speech
- plural form
- Chinese translation
- example sentence

Acceptance:

- Word translation returns all required fields.
- Missing plural form is represented as empty, not fabricated.
- Result can be added to vocabulary.

### Full-Document Translation

User clicks full-document translation. The app enters comparison mode in the left reader area, showing original content and Chinese translation side by side or page-aligned.

Acceptance:

- Full translation is not only shown as a chat message.
- Original/translation comparison is visible in the reader area.
- Translation is cached to avoid unnecessary repeated API calls.

### Vocabulary Notebook And Export

User saves word translation results into the vocabulary notebook. Backend persists vocabulary to local JSON. Page 2 reads vocabulary from the backend and exports it as a `.docx` download.

Acceptance:

- Saved vocabulary survives page refresh and app navigation.
- Saved vocabulary is isolated by authenticated Supabase user id.
- Duplicate words are not added repeatedly.
- Export button downloads a valid Word file.
- Word file contains lemma, POS, plural, translation, and example sentence.

## Backend API Surface

Planned endpoints:

- `POST /api/documents/upload`: upload PDF, save file, parse text.
- `GET /api/documents/current`: return current document metadata and parsed pages.
- `POST /api/ai/ask`: answer a free-form question using document context.
- `POST /api/ai/summary`: summarize current document.
- `POST /api/ai/translate/sentence`: translate a German sentence to Chinese.
- `POST /api/ai/translate/word`: return structured German word information.
- `POST /api/ai/translate/full`: translate full document and return page-aligned result.
- `GET /api/vocabulary`: list saved vocabulary.
- `POST /api/vocabulary`: add vocabulary item.
- `DELETE /api/vocabulary/{id}`: delete vocabulary item.
- `GET /api/vocabulary/export`: return a generated `.docx` file download.

## Data Model

### Parsed Document

```json
{
  "document_id": "string",
  "filename": "string",
  "pages": [
    {
      "page_number": 1,
      "text": "string",
      "paragraphs": [
        {
          "paragraph_id": 1,
          "text": "string"
        }
      ]
    }
  ]
}
```

### Vocabulary Item

```json
{
  "id": "string",
  "word": "string",
  "lemma": "string",
  "part_of_speech": "string",
  "plural": "string",
  "translation": "string",
  "example_sentence": "string",
  "source_page": 1
}
```

Only lemma, part of speech, plural, translation, and example sentence are required for display. `word` and `source_page` are useful metadata.

## Persistence

Supabase persistence:

- Private `pdfs` Storage bucket: uploaded PDFs under `{user_id}/`.
- `current_documents`: current parsed document and PDF object path per user.
- `full_translations`: cached translation per user and current document id.
- `vocabulary`: saved vocabulary rows per user.

Supabase Auth provides email/password accounts. PostgreSQL row-level security and
backend user-id filtering prevent one account from accessing another account's data.

## AI Configuration

Backend `.env` stores:

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`

The frontend never displays or submits API keys.

## Edge Cases

- No PDF uploaded: AI actions return a clear error.
- PDF has no extractable text: return OCR-not-supported message.
- API config missing: backend returns setup error.
- LLM failure: frontend shows error and keeps current document/vocabulary state.
- Missing or expired login: backend returns 401 and the user signs in again.
- User enters empty word or sentence: validation error.
- Duplicate vocabulary: backend returns existing item or duplicate warning.
- Long PDF: backend chunks text before summary or full translation.

## Acceptance Criteria

- React app has exactly two main pages: reader/assistant and vocabulary.
- Page 1 uses about 70/30 layout.
- User can upload and preview a PDF.
- Backend parses PDF text and makes it available to AI endpoints.
- Free-form document question works.
- Document summary works.
- Sentence translation works through manual input and selected text input.
- Word translation returns lemma, POS, plural, Chinese translation, and example sentence.
- User can add word translation output to vocabulary.
- Vocabulary persists in Supabase PostgreSQL and is isolated per account.
- Page 2 lists vocabulary and downloads a valid Word file.
- Full-document translation is shown in original/translation comparison mode.
