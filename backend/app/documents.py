from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.auth import AuthenticatedUser, get_authenticated_user
from app.pdf_parser import parse_pdf
from app.supabase_store import (
    create_pdf_signed_url,
    get_current_document as get_stored_current_document,
    save_current_document,
    upload_pdf,
)

router = APIRouter(prefix="/api/documents", tags=["documents"])


def _safe_pdf_filename(_filename: str) -> str:
    return f"{uuid4().hex}.pdf"


def load_current_document(user_id: str) -> dict[str, object]:
    document = get_stored_current_document(user_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No current document is available. Upload a PDF first.",
        )
    return document


@router.get("/current")
def get_current_document(
    user: AuthenticatedUser = Depends(get_authenticated_user),
) -> dict[str, object]:
    document = load_current_document(user.id)
    return {
        **document,
        "pdf_url": create_pdf_signed_url(str(document["storage_path"])),
    }


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user: AuthenticatedUser = Depends(get_authenticated_user),
) -> dict[str, object]:
    if file.content_type != "application/pdf" and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    pdf_filename = _safe_pdf_filename(file.filename)
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded PDF is empty.",
        )

    with NamedTemporaryFile(suffix=".pdf", delete=False) as temporary_file:
        temporary_path = Path(temporary_file.name)
        temporary_file.write(contents)
    try:
        try:
            pages = parse_pdf(temporary_path)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file could not be parsed as a PDF.",
            ) from exc
    finally:
        temporary_path.unlink(missing_ok=True)

    has_text = any(str(page["text"]).strip() for page in pages)
    if not has_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No extractable text was found. OCR scanned PDFs are not supported.",
        )

    storage_path = upload_pdf(user.id, pdf_filename, contents)
    document: dict[str, object] = {
        "document_id": uuid4().hex,
        "filename": file.filename,
        "stored_filename": pdf_filename,
        "storage_path": storage_path,
        "page_count": len(pages),
        "pages": pages,
    }

    save_current_document(user.id, document)

    return {
        **document,
        "pdf_url": create_pdf_signed_url(storage_path),
    }
