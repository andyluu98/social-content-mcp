"""Upload ảnh local lên ImgBB → URL public.

ImgBB free, không expire mặc định, ~50 upload/giờ.
Lấy key tại https://api.imgbb.com/.
"""

from __future__ import annotations

import base64
from pathlib import Path

import httpx

from server.config import config


class ImgbbError(RuntimeError):
    """Raised khi ImgBB upload lỗi."""


_ENDPOINT = "https://api.imgbb.com/1/upload"


async def upload(file_path: str | Path) -> str:
    """Upload file → trả URL public của ảnh."""
    config.require_imgbb()
    p = Path(file_path)
    if not p.exists():
        raise ImgbbError(f"File không tồn tại: {p}")

    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    try:
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(
                _ENDPOINT,
                params={"key": config.imgbb_api_key},
                data={"image": b64, "name": p.stem},
            )
            r.raise_for_status()
            payload = r.json()
    except httpx.HTTPError as e:
        raise ImgbbError(f"ImgBB upload fail: {e}") from e

    if not payload.get("success"):
        raise ImgbbError(f"ImgBB từ chối: {payload}")

    return payload["data"]["url"]
