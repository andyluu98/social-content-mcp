"""Load env config. Priority: env var > .env file > built-in default."""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

# Priority: env var > ~/.social-content-mcp/.env > ./.env > built-in default
HOME_CONFIG_DIR = Path.home() / ".social-content-mcp"
HOME_ENV_FILE = HOME_CONFIG_DIR / ".env"

if HOME_ENV_FILE.exists():
    load_dotenv(HOME_ENV_FILE)
load_dotenv()  # also load ./.env if present (override-safe)


def _ima2_autodiscover() -> str | None:
    """Đọc URL ima2-gen từ ~/.ima2/server.json nếu có (ima2 ghi file này khi serve)."""
    advert = Path.home() / ".ima2" / "server.json"
    if not advert.exists():
        return None
    try:
        data = json.loads(advert.read_text(encoding="utf-8"))
        url = data.get("url")
        return url if isinstance(url, str) else None
    except (OSError, json.JSONDecodeError):
        return None


class Config:
    """Singleton config — read once tại startup."""

    aitoearn_api_key: str
    aitoearn_mcp_url: str
    ima2_server: str
    imgbb_api_key: str
    storage_provider: str

    def __init__(self) -> None:
        self.aitoearn_api_key = os.getenv("AITOEARN_API_KEY", "").strip()
        self.aitoearn_mcp_url = os.getenv(
            "AITOEARN_MCP_URL", "https://aitoearn.ai/api/unified/mcp"
        ).strip()

        ima2 = os.getenv("IMA2_SERVER", "").strip()
        if not ima2:
            ima2 = _ima2_autodiscover() or "http://localhost:3333"
        self.ima2_server = ima2.rstrip("/")

        self.imgbb_api_key = os.getenv("IMGBB_API_KEY", "").strip()
        self.storage_provider = os.getenv("STORAGE_PROVIDER", "catbox").strip().lower()

    def require_aitoearn(self) -> None:
        if not self.aitoearn_api_key:
            raise RuntimeError(
                "AITOEARN_API_KEY chưa set. Lấy tại https://aitoearn.ai → Settings → API Key."
            )

    def require_imgbb(self) -> None:
        if not self.imgbb_api_key:
            raise RuntimeError(
                "IMGBB_API_KEY chưa set. Free tại https://api.imgbb.com/ (cần cho upload ảnh local → URL public)."
            )


config = Config()
