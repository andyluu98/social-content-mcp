"""HTTP clients gọi service upstream + dispatcher chọn CDN."""

from __future__ import annotations

from pathlib import Path

from server.config import config


async def upload_to_cdn(file_path: str | Path) -> str:
    """Upload file local → URL public, theo provider trong config (STORAGE_PROVIDER)."""
    provider = config.storage_provider
    if provider == "catbox":
        from server.clients.catbox import upload
        return await upload(file_path)
    if provider == "imgbb":
        from server.clients.imgbb import upload
        return await upload(file_path)
    raise RuntimeError(
        f"STORAGE_PROVIDER='{provider}' chưa hỗ trợ. "
        f"Hỗ trợ: catbox (mặc định, không cần key), imgbb (cần IMGBB_API_KEY)."
    )
