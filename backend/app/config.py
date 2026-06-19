from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
STORAGE_DIR = BASE_DIR / "storage"


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_base_url: str
    openai_model: str
    storage_dir: Path
    cors_origins: tuple[str, ...]

    @property
    def has_ai_config(self) -> bool:
        return bool(self.openai_api_key and self.openai_base_url and self.openai_model)

    def require_ai_config(self) -> None:
        if not self.has_ai_config:
            missing = []
            if not self.openai_api_key:
                missing.append("OPENAI_API_KEY")
            if not self.openai_base_url:
                missing.append("OPENAI_BASE_URL")
            if not self.openai_model:
                missing.append("OPENAI_MODEL")
            raise RuntimeError(
                "AI configuration is missing. Set OPENAI_API_KEY, "
                "OPENAI_BASE_URL, and OPENAI_MODEL in backend/.env. "
                f"Missing: {', '.join(missing)}."
            )

def get_settings() -> Settings:
    load_dotenv(ENV_FILE)
    storage_dir = Path(os.getenv("STORAGE_DIR", str(STORAGE_DIR))).expanduser()
    if not storage_dir.is_absolute():
        storage_dir = BASE_DIR / storage_dir
    cors_origins = tuple(
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    )
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip(),
        openai_model=os.getenv("OPENAI_MODEL", "").strip(),
        storage_dir=storage_dir,
        cors_origins=cors_origins,
    )
