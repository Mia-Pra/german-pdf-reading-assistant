from pathlib import Path

from app.config import get_settings


STORAGE_DIR = get_settings().storage_dir
UPLOADS_DIR = STORAGE_DIR / "uploads"
DOCUMENTS_DIR = STORAGE_DIR / "documents"
TRANSLATIONS_DIR = STORAGE_DIR / "translations"
FULL_TRANSLATION_FILE = TRANSLATIONS_DIR / "current_full_translation.json"
VOCABULARY_FILE = STORAGE_DIR / "vocabulary.json"

STORAGE_PATHS: tuple[Path, ...] = (
    STORAGE_DIR,
    UPLOADS_DIR,
    DOCUMENTS_DIR,
    TRANSLATIONS_DIR,
)


def ensure_storage_directories() -> None:
    for path in STORAGE_PATHS:
        path.mkdir(parents=True, exist_ok=True)

    if not VOCABULARY_FILE.exists():
        VOCABULARY_FILE.write_text("[]\n", encoding="utf-8")
