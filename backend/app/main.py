from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ai import router as ai_router
from app.config import get_settings
from app.documents import router as documents_router
from app.storage import ensure_storage_directories
from app.vocabulary import router as vocabulary_router

settings = get_settings()

app = FastAPI(
    title="German PDF Reading Assistant API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router)
app.include_router(ai_router)
app.include_router(vocabulary_router)


@app.on_event("startup")
def startup() -> None:
    ensure_storage_directories()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
