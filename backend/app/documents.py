import asyncio
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.auth import AuthenticatedUser, get_authenticated_user
from app.pdf_parser import parse_pdf
from app.supabase_store import (
    create_pdf_signed_url,
    delete_pdf,
    get_current_document as get_stored_current_document,
    save_current_document,
    upload_pdf,
)

router = APIRouter(prefix="/api/documents", tags=["documents"])


def _storage_pdf_filename() -> str:
    return f"{uuid4().hex}.pdf"


def _document_response(document: dict[str, object]) -> dict[str, object]:
    return {
        "document_id": document["document_id"],
        "filename": document["filename"],
        "stored_filename": document["stored_filename"],
        "storage_path": document["storage_path"],
        "page_count": document["page_count"],
        "pdf_url": create_pdf_signed_url(str(document["storage_path"])),
    }


async def _delete_pdf_quietly(storage_path: str) -> None:
    try:
        await asyncio.to_thread(delete_pdf, storage_path)
    except Exception:
        pass


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
    return _document_response(document)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user: AuthenticatedUser = Depends(get_authenticated_user),
) -> dict[str, object]:
    original_filename = Path(file.filename or "uploaded.pdf").name
    if (
        file.content_type != "application/pdf"
        and not original_filename.lower().endswith(".pdf")
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    pdf_filename = _storage_pdf_filename()
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded PDF is empty.",
        )

    with NamedTemporaryFile(suffix=".pdf", delete=False) as temporary_file:
        temporary_path = Path(temporary_file.name)
        temporary_file.write(contents)
    storage_path = f"{user.id}/{pdf_filename}"
    parse_task = asyncio.to_thread(parse_pdf, temporary_path)
    upload_task = asyncio.to_thread(upload_pdf, user.id, pdf_filename, contents)

    try:
        parse_result, upload_result = await asyncio.gather(
            parse_task,
            upload_task,
            return_exceptions=True,
        )
    finally:
        temporary_path.unlink(missing_ok=True)

    if isinstance(parse_result, Exception):
        if not isinstance(upload_result, Exception):
            await _delete_pdf_quietly(storage_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file could not be parsed as a PDF.",
        ) from parse_result
    if isinstance(upload_result, Exception):
        raise upload_result

    pages = parse_result

    has_text = any(str(page["text"]).strip() for page in pages)
    if not has_text:
        await _delete_pdf_quietly(storage_path)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No extractable text was found. OCR scanned PDFs are not supported.",
        )

    storage_path = upload_result
    document: dict[str, object] = {
        "document_id": uuid4().hex,
        "filename": original_filename,
        "stored_filename": pdf_filename,
        "storage_path": storage_path,
        "page_count": len(pages),
        "pages": pages,
    }

    save_current_document(user.id, document)

    return _document_response(document)
