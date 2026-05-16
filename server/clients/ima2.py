"""Client gọi ima2-gen local server.

ima2-gen phải đang chạy (`npx ima2-gen serve` hoặc `ima2 serve`).
Login Codex OAuth trước nếu muốn dùng free path: `npx @openai/codex login`.
"""

from __future__ import annotations

import base64
import re
import time
from pathlib import Path

import httpx

from server.config import config


class Ima2Error(RuntimeError):
    """Raised khi ima2-gen API lỗi hoặc không phản hồi."""


_DATA_URL_RE = re.compile(r"^data:(?P<mime>[^;]+);base64,(?P<body>.+)$", re.DOTALL)


async def health() -> dict:
    """Ping ima2-gen. Raises Ima2Error nếu không reachable."""
    url = f"{config.ima2_server}/api/health"
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(url)
            r.raise_for_status()
            return r.json()
    except (httpx.HTTPError, ValueError) as e:
        raise Ima2Error(
            f"ima2-gen không reachable tại {config.ima2_server}. "
            f"Chạy `npx ima2-gen serve` trước. Lỗi: {e}"
        ) from e


async def generate_image(
    prompt: str,
    *,
    size: str = "1024x1024",
    quality: str = "medium",
    model: str = "gpt-5.4-mini",
    image_format: str = "png",
    output_dir: Path | None = None,
) -> dict:
    """Sinh 1 ảnh từ prompt. Trả dict {file_path, filename, mime}.

    Lưu ảnh ra `output_dir` (mặc định: ./output/) ngoài cache của ima2.
    """
    payload = {
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "format": image_format,
        "moderation": "auto",
        "provider": "oauth",
        "model": model,
    }
    url = f"{config.ima2_server}/api/generate"
    try:
        async with httpx.AsyncClient(timeout=300) as c:
            r = await c.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
    except httpx.HTTPError as e:
        raise Ima2Error(f"ima2-gen /api/generate fail: {e}") from e

    # ima2-gen có 2 format response tùy version:
    #   cũ:  {"images": [{"image": "data:...", "filename": ..., "revisedPrompt": ...}]}
    #   mới: {"image": "data:...", "filename": ..., "revisedPrompt": ...}
    # Chấp nhận cả 2.
    images = data.get("images") or []
    first = images[0] if images else data
    data_url = first.get("image", "")
    if not data_url:
        raise Ima2Error(f"ima2-gen không trả ảnh nào. Response: {data!r}")

    m = _DATA_URL_RE.match(data_url)
    if not m:
        raise Ima2Error(f"image field không phải data URL hợp lệ: {data_url[:60]}...")

    mime = m.group("mime")
    body_b64 = m.group("body")
    raw = base64.b64decode(body_b64)

    out_dir = output_dir or Path.cwd() / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = first.get("filename") or f"img-{int(time.time())}.{image_format}"
    file_path = out_dir / filename
    file_path.write_bytes(raw)

    return {
        "file_path": str(file_path.resolve()),
        "filename": filename,
        "mime": mime,
        "bytes": len(raw),
        "model": model,
        "revised_prompt": first.get("revisedPrompt"),
    }
