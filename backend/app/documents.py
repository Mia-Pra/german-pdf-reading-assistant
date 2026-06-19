import json
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.pdf_parser import parse_pdf
from app.storage import DOCUMENTS_DIR, UPLOADS_DIR, ensure_storage_directories

router = APIRouter(prefix="/api/documents", tags=["documents"])

CURRENT_DOCUMENT_FILE = DOCUMENTS_DIR / "current.json"


def _safe_pdf_filename(filename: str) -> str:
    source_name = Path(filename or "uploaded.pdf").name
    if not source_name.lower().endswith(".pdf"):
        source_name = f"{source_name}.pdf"
    return f"{uuid4().hex}_{source_name}"


def load_current_document() -> dict[str, object]:
    if not CURRENT_DOCUMENT_FILE.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No current document is available. Upload a PDF first.",
        )

    try:
        return json.loads(CURRENT_DOCUMENT_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Current document metadata is corrupted.",
        ) from exc


def _current_pdf_path(document: dict[str, object]) -> Path:
    stored_filename = str(document.get("stored_filename", ""))
    if not stored_filename:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Current document PDF file is not available.",
        )

    candidate = (UPLOADS_DIR / stored_filename).resolve()
    uploads_root = UPLOADS_DIR.resolve()

    if uploads_root not in candidate.parents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stored PDF path is invalid.",
        )

    if not candidate.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Current document PDF file is missing.",
        )

    return candidate


@router.get("/current")
def get_current_document() -> dict[str, object]:
    document = load_current_document()
    return {
        **document,
        "pdf_url": "/api/documents/current/pdf",
    }


@router.get("/current/pdf")
def get_current_document_pdf() -> FileResponse:
    document = load_current_document()
    pdf_path = _current_pdf_path(document)
    filename = str(document.get("filename") or "document.pdf")
    return FileResponse(
        path=pdf_path,
        filename=filename,
        media_type="application/pdf",
        content_disposition_type="inline",
    )


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> dict[str, object]:
    ensure_storage_directories()

    filename = file.filename or "uploaded.pdf"
    if file.content_type != "application/pdf" and not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    pdf_filename = _safe_pdf_filename(filename)
    pdf_path = UPLOADS_DIR / pdf_filename
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded PDF is empty.",
        )

    pdf_path.write_bytes(contents)

    try:
        pages = parse_pdf(pdf_path)
    except Exception as exc:
        pdf_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file could not be parsed as a PDF.",
        ) from exc

    has_text = any(str(page["text"]).strip() for page in pages)
    if not has_text:
        pdf_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No extractable text was found. OCR scanned PDFs are not supported.",
        )

    document = {
        "document_id": uuid4().hex,
        "filename": filename,
        "stored_filename": pdf_filename,
        "page_count": len(pages),
        "pages": pages,
    }

    CURRENT_DOCUMENT_FILE.write_text(
        json.dumps(document, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return {
        **document,
        "pdf_url": "/api/documents/current/pdf",
    }
