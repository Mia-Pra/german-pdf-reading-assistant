import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, NavLink, Route, Routes } from "react-router-dom";
import {
  BookOpen,
  Download,
  FileText,
  Languages,
  LibraryBig,
  MessageSquareText,
  Plus,
  Search,
  Send,
  Trash2,
  Upload,
} from "lucide-react";
import "./styles.css";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");

function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <header className="topbar">
          <div>
            <p className="eyebrow">German PDF Assistant</p>
            <h1>Reading Workspace</h1>
          </div>
          <nav className="nav-tabs" aria-label="Primary navigation">
            <NavLink to="/" end>
              <BookOpen size={18} />
              Reader
            </NavLink>
            <NavLink to="/vocabulary">
              <LibraryBig size={18} />
              Vocabulary
            </NavLink>
          </nav>
        </header>

        <main>
          <Routes>
            <Route path="/" element={<ReaderPage />} />
            <Route path="/vocabulary" element={<VocabularyPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

function ReaderPage() {
  const fileInputRef = useRef(null);
  const [documentData, setDocumentData] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("idle");
  const [uploadError, setUploadError] = useState("");
  const [assistantInput, setAssistantInput] = useState("");
  const [assistantStatus, setAssistantStatus] = useState("idle");
  const [assistantResult, setAssistantResult] = useState(null);
  const [assistantError, setAssistantError] = useState("");
  const [assistantMode, setAssistantMode] = useState("qa");
  const [vocabularyStatus, setVocabularyStatus] = useState("idle");
  const [vocabularyMessage, setVocabularyMessage] = useState("");
  const [readerMode, setReaderMode] = useState("original");
  const [fullTranslation, setFullTranslation] = useState(null);
  const [fullTranslationStatus, setFullTranslationStatus] = useState("idle");
  const [fullTranslationError, setFullTranslationError] = useState("");
  const hasDocument = Boolean(documentData);
  const documentActionDisabled = assistantStatus === "asking" || !hasDocument;

  const pdfPreviewUrl = useMemo(() => {
    if (!documentData) {
      return "";
    }

    const pdfUrl = documentData.pdf_url || "/api/documents/current/pdf";
    return `${API_BASE_URL}${pdfUrl}?v=${encodeURIComponent(
      documentData.document_id,
    )}`;
  }, [documentData]);

  useEffect(() => {
    let isActive = true;

    async function loadCurrentDocument() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/documents/current`);
        if (response.status === 404) {
          return;
        }

        const payload = await response.json();
        if (!response.ok) {
          throw new Error(payload.detail || "Current PDF could not be loaded.");
        }

        if (isActive) {
          setDocumentData(payload);
          setUploadStatus("ready");
          setReaderMode("original");
          setFullTranslation(null);
          setFullTranslationStatus("idle");
          setFullTranslationError("");
        }
      } catch (error) {
        if (isActive) {
          setUploadError(error.message);
        }
      }
    }

    loadCurrentDocument();

    return () => {
      isActive = false;
    };
  }, []);

  async function handlePdfChange(event) {
    const file = event.target.files?.[0];
    event.target.value = "";

    if (!file) {
      return;
    }

    setUploadStatus("uploading");
    setUploadError("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_BASE_URL}/api/documents/upload`, {
        method: "POST",
        body: formData,
      });
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.detail || "PDF upload failed.");
      }

      setDocumentData(payload);
      setReaderMode("original");
      setUploadStatus("ready");
      setAssistantResult(null);
      setAssistantError("");
      setVocabularyMessage("");
      setVocabularyStatus("idle");
      setFullTranslation(null);
      setFullTranslationStatus("idle");
      setFullTranslationError("");
    } catch (error) {
      setDocumentData(null);
      setUploadStatus("error");
      setUploadError(error.message);
    }
  }

  async function handleAskDocument() {
    const question = assistantInput.trim();
    if (!documentData) {
      setAssistantError("Upload a text-based PDF before asking about the document.");
      return;
    }
    if (!question) {
      setAssistantError("Enter a question before sending.");
      return;
    }

    setAssistantStatus("asking");
    setAssistantError("");
    setAssistantResult(null);
    setVocabularyMessage("");
    setVocabularyStatus("idle");
    setAssistantMode("qa");

    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.detail || "AI question failed.");
      }

      setAssistantResult(payload);
      setAssistantStatus("ready");
    } catch (error) {
      setAssistantStatus("error");
      setAssistantError(error.message);
    }
  }

  async function handleSummary() {
    if (!documentData) {
      setAssistantError("Upload a text-based PDF before requesting a summary.");
      return;
    }

    setAssistantStatus("asking");
    setAssistantError("");
    setAssistantResult(null);
    setVocabularyMessage("");
    setVocabularyStatus("idle");
    setAssistantMode("summary");

    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/summary`, {
        method: "POST",
      });
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.detail || "Document summary failed.");
      }

      setAssistantResult({
        answer: payload.summary,
        source_pages: payload.source_pages,
      });
      setAssistantStatus("ready");
    } catch (error) {
      setAssistantStatus("error");
      setAssistantError(error.message);
    }
  }

  async function handleSentenceTranslation() {
    const selection = window.getSelection?.()?.toString().trim() || "";
    const sentence = selection || assistantInput.trim();
    if (!sentence) {
      setAssistantError("Enter or select a sentence before translating.");
      return;
    }

    setAssistantStatus("asking");
    setAssistantError("");
    setAssistantResult(null);
    setVocabularyMessage("");
    setVocabularyStatus("idle");
    setAssistantMode("sentence");

    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/translate/sentence`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ sentence }),
      });
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.detail || "Sentence translation failed.");
      }

      setAssistantResult(payload);
      setAssistantStatus("ready");
    } catch (error) {
      setAssistantStatus("error");
      setAssistantError(error.message);
    }
  }

  async function handleFullTranslation() {
    if (!documentData) {
      setAssistantError("Upload a text-based PDF before requesting full translation.");
      return;
    }

    setAssistantStatus("asking");
    setAssistantError("");
    setAssistantResult(null);
    setVocabularyMessage("");
    setVocabularyStatus("idle");
    setAssistantMode("full");
    setReaderMode("translation");
    setFullTranslationStatus("translating");
    setFullTranslationError("");

    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/translate/full`, {
        method: "POST",
      });
      const payload = await response.json();

      if (!response.ok) {
        const detail = payload.detail || "Full-document translation failed.";
        if (response.status === 404 && detail === "Not Found") {
          throw new Error(
            "Full Translation is not available on the running backend. Restart the backend service and try again.",
          );
        }
        throw new Error(detail);
      }

      setFullTranslation(payload);
      setFullTranslationStatus("ready");
      setAssistantResult({
        answer: payload.cached
          ? "Loaded cached full-document translation."
          : "Full-document translation is ready in the reader area.",
        source_pages: payload.pages.map((page) => page.page_number),
      });
      setAssistantStatus("ready");
    } catch (error) {
      setAssistantStatus("error");
      setFullTranslationStatus("error");
      setFullTranslationError(error.message);
      setAssistantError(error.message);
    }
  }

  async function handleWordTranslation() {
    const selection = window.getSelection?.()?.toString().trim() || "";
    const word = selection || assistantInput.trim();
    if (!word) {
      setAssistantError("Enter or select a word before translating.");
      return;
    }

    setAssistantStatus("asking");
    setAssistantError("");
    setAssistantResult(null);
    setVocabularyMessage("");
    setVocabularyStatus("idle");
    setAssistantMode("word");

    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/translate/word`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ word }),
      });
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.detail || "Word translation failed.");
      }

      setAssistantResult(payload);
      setAssistantStatus("ready");
    } catch (error) {
      setAssistantStatus("error");
      setAssistantError(error.message);
    }
  }

  async function handleAddWordToVocabulary() {
    if (!assistantResult || assistantMode !== "word") {
      setVocabularyMessage("Translate a word before adding it.");
      setVocabularyStatus("error");
      return;
    }

    setVocabularyStatus("saving");
    setVocabularyMessage("");

    try {
      const response = await fetch(`${API_BASE_URL}/api/vocabulary`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          word: assistantResult.source_word || assistantResult.lemma,
          lemma: assistantResult.lemma,
          part_of_speech: assistantResult.part_of_speech,
          plural: assistantResult.plural,
          translation: assistantResult.translation,
          example_sentence: assistantResult.example_sentence,
        }),
      });
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.detail || "Word could not be saved.");
      }

      setVocabularyStatus(payload.created ? "saved" : "duplicate");
      setVocabularyMessage(
        payload.created
          ? "Saved to vocabulary notebook."
          : "This word is already in the vocabulary notebook.",
      );
    } catch (error) {
      setVocabularyStatus("error");
      setVocabularyMessage(error.message);
    }
  }

  return (
    <section className="reader-layout" aria-label="PDF reader and AI assistant">
      <div className="pdf-pane">
        <div className="pane-header">
          <div>
            <span>PDF Original</span>
            <small>
              {documentData
                ? `${documentData.filename} - ${documentData.page_count} page${
                    documentData.page_count === 1 ? "" : "s"
                  }`
                : "70% reading area"}
            </small>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf,.pdf"
            className="visually-hidden"
            onChange={handlePdfChange}
          />
          <button
            type="button"
            className="icon-button"
            disabled={uploadStatus === "uploading"}
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload size={18} />
            {uploadStatus === "uploading" ? "Uploading..." : "Upload PDF"}
          </button>
        </div>
        <div className="reader-toolbar" aria-label="Reader mode">
          <button
            type="button"
            className={readerMode === "original" ? "active" : ""}
            onClick={() => setReaderMode("original")}
          >
            Original
          </button>
          <button
            type="button"
            className={readerMode === "translation" ? "active" : ""}
            onClick={() => setReaderMode("translation")}
          >
            Translation Compare
          </button>
        </div>
        <div className="pdf-stage">
          {readerMode === "original" && pdfPreviewUrl ? (
            <iframe
              title={`PDF preview: ${documentData.filename}`}
              className="pdf-frame"
              src={pdfPreviewUrl}
            />
          ) : readerMode === "translation" && documentData ? (
            <div className="translation-compare-view">
              {fullTranslationStatus === "translating" ? (
                <div className="document-sheet">
                  <div className="sheet-topline" />
                  <h2>Translation Compare</h2>
                  <p>Translating the full document page by page...</p>
                </div>
              ) : fullTranslationError ? (
                <div className="document-sheet">
                  <div className="sheet-topline" />
                  <h2>Translation Compare</h2>
                  <p className="assistant-error">{fullTranslationError}</p>
                </div>
              ) : fullTranslation?.pages?.length ? (
                fullTranslation.pages.map((page) => (
                  <article className="translation-page" key={page.page_number}>
                    <h2>Page {page.page_number}</h2>
                    <div className="translation-columns">
                      <section>
                        <h3>Original</h3>
                        <p>{page.source_text}</p>
                      </section>
                      <section>
                        <h3>Chinese Translation</h3>
                        <p>{page.translation}</p>
                      </section>
                    </div>
                  </article>
                ))
              ) : (
                <div className="document-sheet">
                  <div className="sheet-topline" />
                  <h2>Translation Compare</h2>
                  <p>
                    Click Full Translation to generate a page-aligned Chinese
                    translation for this document.
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="document-sheet">
              <div className="sheet-topline" />
              <h2>Deutsch PDF Vorschau</h2>
              <p>
                Upload a text-based German PDF to preview the original document
                here. Full-document translation comparison will use this space
                when generated.
              </p>
            </div>
          )}
        </div>
        {uploadError ? <div className="upload-error">{uploadError}</div> : null}
      </div>

      <aside className="assistant-pane" aria-label="AI assistant">
        <div className="pane-header">
          <div>
            <span>AI Assistant</span>
            <small>30% action panel</small>
          </div>
        </div>
        <div className="quick-actions">
          <button
            type="button"
            disabled={documentActionDisabled}
            onClick={handleSummary}
          >
            <FileText size={17} />
            Summary
          </button>
          <button
            type="button"
            disabled={documentActionDisabled}
            onClick={handleFullTranslation}
          >
            <Languages size={17} />
            Full Translation
          </button>
          <button
            type="button"
            disabled={assistantStatus === "asking"}
            onClick={handleSentenceTranslation}
          >
            <MessageSquareText size={17} />
            Sentence
          </button>
          <button
            type="button"
            disabled={assistantStatus === "asking"}
            onClick={handleWordTranslation}
          >
            <Search size={17} />
            Word
          </button>
        </div>
        {!documentData ? (
          <p className="action-hint">
            Upload a text-based PDF to enable document QA, summary, and full
            translation. Sentence and word translation still work with manual
            input.
          </p>
        ) : null}
        <label className="input-group">
          Ask or translate
          <textarea
            placeholder="Ask a question about the uploaded German PDF..."
            value={assistantInput}
            onChange={(event) => setAssistantInput(event.target.value)}
          />
        </label>
        <button
          className="primary-action"
          type="button"
          disabled={documentActionDisabled}
          onClick={handleAskDocument}
        >
          <Send size={18} />
          {assistantStatus === "asking" ? "Asking..." : "Send"}
        </button>
        <div className="assistant-result">
          <strong>Assistant output</strong>
          {assistantResult && assistantMode === "sentence" ? (
            <>
              <p className="source-text-label">German sentence</p>
              <p>{assistantResult.source_text}</p>
              <p className="source-text-label">Chinese translation</p>
              <p>{assistantResult.translation}</p>
            </>
          ) : assistantResult && assistantMode === "word" ? (
            <div className="word-result-grid">
              <span>Word</span>
              <strong>{assistantResult.source_word}</strong>
              <span>Lemma</span>
              <strong>{assistantResult.lemma || "-"}</strong>
              <span>POS</span>
              <strong>{assistantResult.part_of_speech || "-"}</strong>
              <span>Plural</span>
              <strong>{assistantResult.plural || "-"}</strong>
              <span>Translation</span>
              <strong>{assistantResult.translation || "-"}</strong>
              <span>Example</span>
              <strong>{assistantResult.example_sentence || "-"}</strong>
            </div>
          ) : assistantResult ? (
            <>
              <p>{assistantResult.answer}</p>
              <p className="source-pages">
                Source page{assistantResult.source_pages.length === 1 ? "" : "s"}:{" "}
                {assistantResult.source_pages.join(", ")}
              </p>
            </>
          ) : (
            <p>
              Ask about the uploaded document, translate selected or typed text,
              generate full-document comparison, or save structured word results.
            </p>
          )}
          {assistantError ? <p className="assistant-error">{assistantError}</p> : null}
          {vocabularyMessage ? (
            <p
              className={
                vocabularyStatus === "error"
                  ? "assistant-error"
                  : "vocabulary-message"
              }
            >
              {vocabularyMessage}
            </p>
          ) : null}
          <button
            type="button"
            className="secondary-action"
            disabled={
              assistantStatus === "asking" ||
              vocabularyStatus === "saving" ||
              assistantMode !== "word" ||
              !assistantResult
            }
            onClick={handleAddWordToVocabulary}
          >
            <Plus size={17} />
            {vocabularyStatus === "saving" ? "Saving..." : "Add word to notebook"}
          </button>
        </div>
      </aside>
    </section>
  );
}

function VocabularyPage() {
  const [items, setItems] = useState([]);
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState("");
  const [deleteError, setDeleteError] = useState("");
  const [exportStatus, setExportStatus] = useState("idle");
  const [exportError, setExportError] = useState("");

  useEffect(() => {
    let isActive = true;

    async function loadVocabulary() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/vocabulary`);
        const payload = await response.json();

        if (!response.ok) {
          throw new Error(payload.detail || "Vocabulary could not be loaded.");
        }

        if (isActive) {
          setItems(payload);
          setStatus("ready");
        }
      } catch (loadError) {
        if (isActive) {
          setError(loadError.message);
          setStatus("error");
        }
      }
    }

    loadVocabulary();

    return () => {
      isActive = false;
    };
  }, []);

  async function handleDeleteVocabularyItem(itemId) {
    setDeletingId(itemId);
    setDeleteError("");

    try {
      const response = await fetch(`${API_BASE_URL}/api/vocabulary/${itemId}`, {
        method: "DELETE",
      });
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.detail || "Vocabulary item could not be deleted.");
      }

      setItems((currentItems) =>
        currentItems.filter((item) => item.id !== payload.id),
      );
    } catch (deleteItemError) {
      setDeleteError(deleteItemError.message);
    } finally {
      setDeletingId("");
    }
  }

  async function handleExportVocabulary() {
    setExportStatus("exporting");
    setExportError("");

    try {
      const response = await fetch(`${API_BASE_URL}/api/vocabulary/export`);

      if (!response.ok) {
        let message = "Vocabulary export failed.";
        try {
          const payload = await response.json();
          message = payload.detail || message;
        } catch {
          // Keep the generic message when the response is not JSON.
        }
        throw new Error(message);
      }

      const blob = await response.blob();
      const contentDisposition = response.headers.get("Content-Disposition") || "";
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
      const filename = filenameMatch?.[1] || "vocabulary-notebook.docx";
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      setExportStatus("ready");
    } catch (exportVocabularyError) {
      setExportStatus("error");
      setExportError(exportVocabularyError.message);
    }
  }

  return (
    <section className="vocab-page">
      <div className="pane-header">
        <div>
          <span>Vocabulary Notebook</span>
          <small>Saved German word records</small>
        </div>
        <button
          type="button"
          className="icon-button"
          disabled={exportStatus === "exporting"}
          onClick={handleExportVocabulary}
        >
          <Download size={18} />
          {exportStatus === "exporting" ? "Exporting..." : "Export Word"}
        </button>
      </div>
      <div className="vocab-summary" aria-label="Vocabulary summary">
        <div>
          <strong>{items.length}</strong>
          <span>saved words</span>
        </div>
        <div>
          <strong>5</strong>
          <span>required fields</span>
        </div>
        <div>
          <strong>DOCX</strong>
          <span>export format</span>
        </div>
      </div>
      <div className="table-shell">
        {exportError ? <div className="table-error">{exportError}</div> : null}
        {deleteError ? <div className="table-error">{deleteError}</div> : null}
        <table>
          <thead>
            <tr>
              <th>Lemma</th>
              <th>POS</th>
              <th>Plural</th>
              <th>Translation</th>
              <th>Example</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {status === "loading" ? (
              <tr>
                <td colSpan="6">Loading saved words...</td>
              </tr>
            ) : status === "error" ? (
              <tr>
                <td colSpan="6">{error}</td>
              </tr>
            ) : items.length ? (
              items.map((item) => (
                <tr key={item.id}>
                  <td>{item.lemma || "-"}</td>
                  <td>{item.part_of_speech || "-"}</td>
                  <td>{item.plural || "-"}</td>
                  <td>{item.translation || "-"}</td>
                  <td>{item.example_sentence || "-"}</td>
                  <td>
                    <button
                      type="button"
                      className="danger-icon-button"
                      aria-label={`Delete ${item.lemma || "vocabulary item"}`}
                      title="Delete word"
                      disabled={deletingId === item.id}
                      onClick={() => handleDeleteVocabularyItem(item.id)}
                    >
                      <Trash2 size={17} />
                      {deletingId === item.id ? "Deleting..." : "Delete"}
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6">Saved words will appear here.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

createRoot(document.getElementById("root")).render(<App />);
