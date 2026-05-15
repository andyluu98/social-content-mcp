"""Upload ảnh local lên catbox.moe — free, không cần API key.

Catbox giữ ảnh vĩnh viễn theo mặc định. Rate limit không công bố nhưng rộng.
Nếu cần ephemeral (xóa sau 1h/24h) đổi sang litterbox.catbox.moe.
"""

from __future__ import annotations

from pathlib import Path

import httpx


class CatboxError(RuntimeError):
    """Raised khi Catbox upload lỗi."""


_ENDPOINT = "https://catbox.moe/user/api.php"


async def upload(file_path: str | Path) -> str:
    """Upload file → URL public Catbox."""
    p = Path(file_path)
    if not p.exists():
        raise CatboxError(f"File không tồn tại: {p}")

    try:
        async with httpx.AsyncClient(timeout=120) as c:
            with p.open("rb") as f:
                r = await c.post(
                    _ENDPOINT,
                    data={"reqtype": "fileupload"},
                    files={"fileToUpload": (p.name, f, "application/octet-stream")},
                )
            r.raise_for_status()
            url = r.text.strip()
    except httpx.HTTPError as e:
        raise CatboxError(f"Catbox upload fail: {e}") from e

    if not url.startswith("http"):
        raise CatboxError(f"Catbox từ chối: {url[:200]}")
    return url
