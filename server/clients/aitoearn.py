"""Client gọi AiToEarn MCP cloud qua JSON-RPC.

AiToEarn dùng header `x-api-key` (KHÔNG phải Authorization: Bearer).
Endpoint trả streaming/event-stream — accept cả 2 kiểu trong header Accept.
"""

from __future__ import annotations

import itertools
from typing import Any

import httpx

from server.config import config


class AitoearnError(RuntimeError):
    """Raised khi AiToEarn MCP trả lỗi."""


_id_seq = itertools.count(1)


def _headers() -> dict[str, str]:
    config.require_aitoearn()
    return {
        "x-api-key": config.aitoearn_api_key,
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }


async def _rpc(method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    body = {
        "jsonrpc": "2.0",
        "id": next(_id_seq),
        "method": method,
        "params": params or {},
    }
    try:
        async with httpx.AsyncClient(timeout=60) as c:
            r = await c.post(config.aitoearn_mcp_url, headers=_headers(), json=body)
            r.raise_for_status()
            data = r.json()
    except httpx.HTTPError as e:
        raise AitoearnError(f"AiToEarn RPC {method} fail: {e}") from e

    if "error" in data:
        raise AitoearnError(f"AiToEarn RPC error: {data['error']}")
    return data.get("result", {})


async def call_tool(name: str, arguments: dict[str, Any]) -> str:
    """Gọi 1 tool MCP, trả về text trong content[0]."""
    result = await _rpc("tools/call", {"name": name, "arguments": arguments})
    contents = result.get("content") or []
    texts = [c.get("text", "") for c in contents if c.get("type", "text") == "text"]
    return "\n".join(texts)


async def list_accounts() -> str:
    """List mọi account đã connect (TikTok, FB Page, IG, ...)."""
    return await call_tool("getAllAccounts", {})


async def publish_to_facebook(
    account_id: str,
    title: str,
    desc: str,
    img_urls: list[str],
    topics: list[str] | None = None,
) -> str:
    """Đăng FB. FB bắt buộc có ít nhất 1 ảnh URL."""
    if not img_urls:
        raise AitoearnError("Facebook bắt buộc imgUrlList có ít nhất 1 URL.")
    return await call_tool(
        "publishPostToFacebook",
        {
            "accountId": account_id,
            "title": title,
            "desc": desc,
            "imgUrlList": img_urls,
            "topics": topics or [],
        },
    )


async def publish_to_instagram(
    account_id: str,
    title: str,
    desc: str,
    img_urls: list[str],
    topics: list[str] | None = None,
) -> str:
    """Đăng IG. Hỗ trợ image (Post) và video (Reel)."""
    return await call_tool(
        "publishPostToInstagram",
        {
            "accountId": account_id,
            "title": title,
            "desc": desc,
            "imgUrlList": img_urls,
            "topics": topics or [],
        },
    )


async def publish_to_tiktok(
    account_id: str,
    title: str,
    desc: str,
    img_urls: list[str],
    topics: list[str] | None = None,
) -> str:
    """Đăng TikTok photo. CẢNH BÁO: MCP không cho chỉnh privacy → server hardcode
    PUBLIC_TO_EVERYONE nhưng TikTok từ chối vì app chưa qua App Review →
    100% fail cho đến khi AiToEarn vá. Dùng web dashboard chỉnh SELF_ONLY."""
    return await call_tool(
        "publishPostToTiktok",
        {
            "accountId": account_id,
            "title": title,
            "desc": desc,
            "imgUrlList": img_urls,
            "topics": (topics or [])[:5],
        },
    )


async def publish_to_threads(
    account_id: str,
    title: str,
    desc: str,
    img_urls: list[str],
    topics: list[str] | None = None,
) -> str:
    return await call_tool(
        "publishPostToThreads",
        {
            "accountId": account_id,
            "title": title,
            "desc": desc,
            "imgUrlList": img_urls,
            "topics": topics or [],
        },
    )


async def publish_to_twitter(
    account_id: str,
    title: str,
    desc: str,
    img_urls: list[str],
    topics: list[str] | None = None,
) -> str:
    return await call_tool(
        "publishPostToTwitter",
        {
            "accountId": account_id,
            "title": title[:280],
            "desc": desc[:280],
            "imgUrlList": img_urls[:4],
            "topics": topics or [],
        },
    )


async def publish_to_pinterest(
    account_id: str,
    title: str,
    desc: str,
    img_urls: list[str],
    topics: list[str] | None = None,
) -> str:
    return await call_tool(
        "publishPostToPinterest",
        {
            "accountId": account_id,
            "title": title,
            "desc": desc,
            "imgUrlList": img_urls,
            "topics": topics or [],
        },
    )


async def task_status(flow_id: str) -> str:
    """Check publish task status. status=1 success, status=-1 fail."""
    return await call_tool("getPublishingTaskStatus", {"flowId": flow_id})


async def credits_balance() -> str:
    return await call_tool("getMyCreditsBalance", {})
