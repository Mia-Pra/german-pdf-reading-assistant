# German PDF Reading Assistant PRD

## Product Name

German PDF Reading Assistant Demo

## Target User

German learners and students who read German PDF documents and need AI-assisted comprehension, translation, and vocabulary collection.

## Product Goal

Build a two-page web demo with a React frontend and FastAPI backend. The app lets users upload a text-based German PDF, read the original PDF, ask AI questions about the document, translate sentences or words, run full-document translation, and export a vocabulary notebook as a Word file.

## Confirmed Requirements

- Tech stack: React frontend plus FastAPI backend.
- Page 1 layout: about 70% PDF reading area and about 30% AI assistant panel.
- Page 2: vocabulary notebook and Word export.
- PDF display: embed or preview the original PDF on the left while the backend parses text for AI use.
- AI assistant supports fixed actions and free-form questions.
- Fixed actions include document summary, sentence translation, full-document translation, and word translation.
- Mind map is excluded.
- Sentence and word translation support both manual input and selected text from the PDF reading area.
- Word translation returns lemma, part of speech, plural form, Chinese translation, and example sentence.
- Users can add unfamiliar words to the vocabulary notebook.
- Vocabulary fields: lemma, part of speech, plural form, translation, and example sentence.
- Vocabulary is persisted in backend local files, not only browser memory.
- API configuration is stored in backend `.env`; the frontend does not expose API keys.
- Users must be able to upload a PDF. No fixed sample PDF is required.
- OCR is not required; only text-based PDFs are supported.
- Word export should be downloaded directly from the frontend after clicking an export button.

## Primary User Flows

1. User opens the web app.
2. User uploads a text-based German PDF.
3. Backend parses text and stores document text for the current project/session.
4. Frontend shows the original PDF preview in the left 70% reading area.
5. User asks a free-form question or clicks a fixed AI action in the right 30% assistant panel.
6. User selects PDF text or manually enters a sentence or word for translation.
7. When translating a word, the system returns lemma, POS, plural, Chinese translation, and example sentence.
8. User adds a word result to the vocabulary notebook.
9. User opens Page 2 to review vocabulary.
10. User exports the vocabulary notebook as a `.docx` file.

## Key Constraints

- MVP only supports PDFs with extractable text. Scanned image PDFs are out of scope.
- No login system.
- No database in the MVP. Backend persists vocabulary and uploaded/parsed document state in local files.
- API keys must stay in backend `.env`.
- Full translation should be shown as an original/translation comparison mode, not only as chat text.
- Demo should be clear enough for interview presentation.

## Open Decisions

- The exact frontend build tool can be Vite unless another preference is added.
- The local file persistence format can be JSON unless another format is needed.
- Multi-user isolation is not required for MVP unless later requested.
