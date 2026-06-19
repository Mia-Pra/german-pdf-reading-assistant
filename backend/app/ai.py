import json
import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.ai_client import AIClientError, AIResponseError, create_ai_client
from app.api_errors import ai_error_to_http_exception
from app.auth import AuthenticatedUser, get_authenticated_user
from app.documents import load_current_document
from app.supabase_store import get_full_translation, save_full_translation

router = APIRouter(prefix="/api/ai", tags=["ai"])


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    source_pages: list[int]


class SummaryResponse(BaseModel):
    summary: str
    source_pages: list[int]


class SentenceTranslationRequest(BaseModel):
    sentence: str


class SentenceTranslationResponse(BaseModel):
    source_text: str
    translation: str


class WordTranslationRequest(BaseModel):
    word: str


class WordTranslationResponse(BaseModel):
    source_word: str
    lemma: str
    part_of_speech: str
    plural: str
    translation: str
    example_sentence: str


class FullTranslationPage(BaseModel):
    page_number: int
    source_text: str
    translation: str


class FullTranslationResponse(BaseModel):
    document_id: str
    filename: str
    pages: list[FullTranslationPage]
    cached: bool


def _keywords(text: str) -> set[str]:
    return {
        word.lower()
        for word in re.findall(r"[\w\u00c0-\u024f]+", text, flags=re.UNICODE)
        if len(word) > 2
    }


def _select_relevant_pages(
    pages: list[dict[str, Any]],
    question: str,
    *,
    limit: int = 3,
) -> list[dict[str, Any]]:
    question_terms = _keywords(question)
    scored_pages = []

    for page in pages:
        text = str(page.get("text", ""))
        page_terms = _keywords(text)
        score = len(question_terms & page_terms)
        if score == 0 and text.strip():
            score = 1
        scored_pages.append((score, page))

    ranked = [
        page
        for score, page in sorted(
            scored_pages,
            key=lambda item: (item[0], -int(item[1].get("page_number", 0))),
            reverse=True,
        )
        if score > 0
    ]
    return ranked[:limit]


def _build_context(pages: list[dict[str, Any]], max_chars: int = 8000) -> str:
    chunks = []
    remaining = max_chars

    for page in pages:
        page_number = page.get("page_number")
        text = str(page.get("text", "")).strip()
        if not text:
            continue

        chunk = f"[Page {page_number}]\n{text}"
        if len(chunk) > remaining:
            chunk = chunk[:remaining]
        chunks.append(chunk)
        remaining -= len(chunk)
        if remaining <= 0:
            break

    return "\n\n".join(chunks)


def _get_document_pages(user_id: str) -> list[dict[str, Any]]:
    document = load_current_document(user_id)
    pages = document.get("pages")
    if not isinstance(pages, list) or not pages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No parsed document text is available. Upload a PDF first.",
        )
    return pages


def _parse_json_object(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise AIResponseError("AI provider did not return JSON.")
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise AIResponseError("AI provider returned invalid JSON.") from exc

    if not isinstance(parsed, dict):
        raise AIResponseError("AI provider JSON response must be an object.")
    return parsed


def _string_field(data: dict[str, Any], field: str) -> str:
    value = data.get(field, "")
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    return value.strip()



def _translate_page_text(page_number: int, source_text: str) -> str:
    text = source_text.strip()
    if not text:
        return ""

    messages = [
        {
            "role": "system",
            "content": (
                "You translate German PDF text for Chinese-speaking learners. "
                "Return only the Chinese translation. Preserve paragraph breaks where useful. "
                "Do not add commentary, markdown, or page labels."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Translate this German text from page {page_number} into Chinese:\n\n"
                f"{text}"
            ),
        },
    ]
    return create_ai_client().chat(messages, temperature=0.1, max_tokens=2500)


@router.post("/ask", response_model=AskResponse)
def ask_document(
    request: AskRequest,
    user: AuthenticatedUser = Depends(get_authenticated_user),
) -> AskResponse:
    question = request.question.strip()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty.",
        )

    pages = _get_document_pages(user.id)
    relevant_pages = _select_relevant_pages(pages, question)
    if not relevant_pages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No readable document text is available for answering.",
        )

    context = _build_context(relevant_pages)
    source_pages = [int(page["page_number"]) for page in relevant_pages]
    messages = [
        {
            "role": "system",
            "content": (
                "You answer questions about a German PDF for a Chinese-speaking "
                "learner. Answer in Chinese. Use only the provided document "
                "context. If the context is insufficient, say so clearly."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Document context:\n{context}\n\n"
                f"Question:\n{question}\n\n"
                f"Return a concise answer and mention the relevant page numbers: {source_pages}."
            ),
        },
    ]

    try:
        answer = create_ai_client().chat(messages, temperature=0.2)
    except AIClientError as exc:
        raise ai_error_to_http_exception(exc) from exc

    return AskResponse(answer=answer, source_pages=source_pages)


@router.post("/summary", response_model=SummaryResponse)
def summarize_document(
    user: AuthenticatedUser = Depends(get_authenticated_user),
) -> SummaryResponse:
    pages = _get_document_pages(user.id)
    readable_pages = [page for page in pages if str(page.get("text", "")).strip()]
    if not readable_pages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No readable document text is available for summarizing.",
        )

    context = _build_context(readable_pages, max_chars=12000)
    source_pages = [int(page["page_number"]) for page in readable_pages]
    messages = [
        {
            "role": "system",
            "content": (
                "You summarize German PDF documents for Chinese-speaking learners. "
                "Answer in Chinese. Focus on the document's main topic, key points, "
                "and learning value. Use only the provided context."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Document context:\n{context}\n\n"
                "Summarize this German PDF in Chinese. Return 3 to 6 concise bullet "
                "points and mention the reference page numbers at the end."
            ),
        },
    ]

    try:
        summary = create_ai_client().chat(messages, temperature=0.2)
    except AIClientError as exc:
        raise ai_error_to_http_exception(exc) from exc

    return SummaryResponse(summary=summary, source_pages=source_pages)


@router.post("/translate/full", response_model=FullTranslationResponse)
def translate_full_document(
    user: AuthenticatedUser = Depends(get_authenticated_user),
) -> FullTranslationResponse:
    document = load_current_document(user.id)
    document_id = str(document.get("document_id", "")).strip()
    filename = str(document.get("filename", "")).strip() or "document.pdf"
    pages = document.get("pages")

    if not document_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Current document metadata is missing a document id.",
        )
    if not isinstance(pages, list) or not pages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No parsed document text is available. Upload a PDF first.",
        )

    cached = get_full_translation(user.id, document_id)
    if cached is not None:
        return FullTranslationResponse.model_validate({**cached, "cached": True})

    readable_pages = [page for page in pages if str(page.get("text", "")).strip()]
    if not readable_pages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No readable document text is available for translation.",
        )

    translated_pages: list[FullTranslationPage] = []
    try:
        for page in readable_pages:
            page_number = int(page.get("page_number", len(translated_pages) + 1))
            source_text = str(page.get("text", "")).strip()
            translated_pages.append(
                FullTranslationPage(
                    page_number=page_number,
                    source_text=source_text,
                    translation=_translate_page_text(page_number, source_text),
                )
            )
    except AIClientError as exc:
        raise ai_error_to_http_exception(exc) from exc

    response = FullTranslationResponse(
        document_id=document_id,
        filename=filename,
        pages=translated_pages,
        cached=False,
    )
    save_full_translation(user.id, document_id, response.model_dump())
    return response


@router.post("/translate/sentence", response_model=SentenceTranslationResponse)
def translate_sentence(
    request: SentenceTranslationRequest,
    user: AuthenticatedUser = Depends(get_authenticated_user),
) -> SentenceTranslationResponse:
    sentence = request.sentence.strip()
    if not sentence:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sentence cannot be empty.",
        )

    messages = [
        {
            "role": "system",
            "content": (
                "You translate German sentences for Chinese-speaking learners. "
                "Return only the Chinese translation, concise and natural."
            ),
        },
        {
            "role": "user",
            "content": f"Translate this German sentence into Chinese:\n{sentence}",
        },
    ]

    try:
        translation = create_ai_client().chat(messages, temperature=0.1)
    except AIClientError as exc:
        raise ai_error_to_http_exception(exc) from exc

    return SentenceTranslationResponse(source_text=sentence, translation=translation)


@router.post("/translate/word", response_model=WordTranslationResponse)
def translate_word(
    request: WordTranslationRequest,
    user: AuthenticatedUser = Depends(get_authenticated_user),
) -> WordTranslationResponse:
    word = request.word.strip()
    if not word:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Word cannot be empty.",
        )
    if len(word) > 80:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Word is too long.",
        )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a German vocabulary assistant for Chinese-speaking learners. "
                "Return only valid JSON with these exact string fields: lemma, "
                "part_of_speech, plural, translation, example_sentence. "
                "If a plural form does not apply, return an empty string for plural. Do not use markdown."
            ),
        },
        {
            "role": "user",
            "content": (
                "Analyze this German word and translate it into Chinese. "
                f"Word:\n{word}"
            ),
        },
    ]

    try:
        content = create_ai_client().chat(messages, temperature=0.1)
        data = _parse_json_object(content)
    except AIClientError as exc:
        raise ai_error_to_http_exception(exc) from exc

    return WordTranslationResponse(
        source_word=word,
        lemma=_string_field(data, "lemma"),
        part_of_speech=_string_field(data, "part_of_speech"),
        plural=_string_field(data, "plural"),
        translation=_string_field(data, "translation"),
        example_sentence=_string_field(data, "example_sentence"),
    )
