"""FastMCP server — tools cho Claude Code / Codex / Gemini.

Run: `python -m server` hoặc `social-content-mcp` (sau khi pip install).
"""

from __future__ import annotations

from typing import Literal

from mcp.server.fastmcp import FastMCP

from server.clients import aitoearn, upload_to_cdn
from server.clients import ima2 as ima2_client
from server.config import config

mcp = FastMCP("social-content-mcp")


# ============================================
# Image generation (free Codex OAuth qua ima2-gen)
# ============================================

@mcp.tool()
async def generate_image(
    prompt: str,
    size: Literal["1024x1024", "1024x1792", "1792x1024"] = "1024x1024",
    quality: Literal["low", "medium", "high"] = "medium",
    model: Literal["gpt-5.4", "gpt-5.4-mini", "gpt-5.5"] = "gpt-5.4-mini",
) -> dict:
    """Sinh ảnh AI miễn phí qua ima2-gen + Codex OAuth.

    Yêu cầu: ima2-gen serve đang chạy + Codex CLI đã login (`npx @openai/codex login`).
    Trả về đường dẫn file local. Dùng `upload_image` để có URL public cho publish.
    """
    return await ima2_client.generate_image(
        prompt, size=size, quality=quality, model=model
    )


@mcp.tool()
async def upload_image(file_path: str) -> dict:
    """Upload ảnh local → URL public, dùng provider trong STORAGE_PROVIDER env.

    Mặc định: catbox (free, không cần key). Đổi sang `imgbb` nếu set IMGBB_API_KEY.
    """
    url = await upload_to_cdn(file_path)
    return {"url": url, "provider": config.storage_provider}


# ============================================
# Account discovery
# ============================================

@mcp.tool()
async def list_accounts() -> str:
    """List mọi social account đã connect vào AiToEarn (FB Page, IG, TikTok, ...).

    Dùng trước khi publish để biết accountId cần truyền.
    """
    return await aitoearn.list_accounts()


@mcp.tool()
async def check_balance() -> str:
    """Xem credit còn lại trong AiToEarn."""
    return await aitoearn.credits_balance()


# ============================================
# Publishing
# ============================================

PLATFORMS = Literal[
    "facebook", "instagram", "tiktok", "threads", "twitter", "pinterest"
]

_PUBLISH_DISPATCH = {
    "facebook": aitoearn.publish_to_facebook,
    "instagram": aitoearn.publish_to_instagram,
    "tiktok": aitoearn.publish_to_tiktok,
    "threads": aitoearn.publish_to_threads,
    "twitter": aitoearn.publish_to_twitter,
    "pinterest": aitoearn.publish_to_pinterest,
}


async def _do_publish(
    platform: str,
    account_id: str,
    title: str,
    description: str,
    image_urls: list[str],
    hashtags: list[str] | None,
) -> str:
    fn = _PUBLISH_DISPATCH[platform]
    return await fn(account_id, title, description, image_urls, hashtags)


@mcp.tool()
async def publish_post(
    platform: PLATFORMS,
    account_id: str,
    title: str,
    description: str,
    image_urls: list[str],
    hashtags: list[str] | None = None,
) -> str:
    """Đăng 1 bài lên 1 platform cụ thể.

    image_urls phải là URL public (dùng `upload_image` nếu mới generate từ ima2).
    Trả về flowId để check status sau.

    LƯU Ý TikTok: AiToEarn hard-code privacy PUBLIC nhưng TikTok chặn → fail.
    Workaround: đăng qua web aitoearn.ai dashboard, chọn privacy SELF_ONLY.
    """
    return await _do_publish(platform, account_id, title, description, image_urls, hashtags)


@mcp.tool()
async def compose_and_publish(
    platform: PLATFORMS,
    account_id: str,
    title: str,
    description: str,
    image_prompt: str,
    hashtags: list[str] | None = None,
    image_size: Literal["1024x1024", "1024x1792", "1792x1024"] = "1024x1024",
) -> dict:
    """One-shot: generate ảnh → upload CDN → publish. Trả flowId + URL ảnh."""
    img = await ima2_client.generate_image(image_prompt, size=image_size)
    url = await upload_to_cdn(img["file_path"])
    flow_result = await _do_publish(
        platform, account_id, title, description, [url], hashtags
    )
    return {
        "image_path": img["file_path"],
        "image_url": url,
        "publish_result": flow_result,
    }


@mcp.tool()
async def check_status(flow_id: str) -> str:
    """Check trạng thái 1 task publish trước đó.

    status=1 thành công, status=-1 thất bại (xem errorMsg).
    """
    return await aitoearn.task_status(flow_id)


@mcp.tool()
async def ima2_health() -> dict:
    """Kiểm tra ima2-gen server có chạy không (debug helper)."""
    return await ima2_client.health()


# ============================================
# Entry point
# ============================================

def serve() -> None:
    """Stdio MCP — tương thích Claude Code, Codex, Gemini CLI."""
    mcp.run()


# Backward compat alias
main = serve


if __name__ == "__main__":
    serve()
