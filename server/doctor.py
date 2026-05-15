"""`social-content-mcp doctor` — chẩn đoán cài đặt.

In status từng phần: Python, Node, ima2-gen, env keys, ima2 service, AiToEarn ping.
"""

from __future__ import annotations

import asyncio
import shutil
import sys

from server.config import HOME_ENV_FILE, config


def _check(label: str, ok: bool, detail: str = "") -> None:
    mark = "✓" if ok else "✗"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))


async def _async_checks() -> None:
    print("\n--- Upstream services ---")

    from server.clients.ima2 import Ima2Error, health
    try:
        h = await health()
        _check("ima2-gen reachable", True, f"{config.ima2_server} ({h.get('version', '?')})")
    except Ima2Error as e:
        _check("ima2-gen reachable", False, str(e)[:120])

    from server.clients.aitoearn import credits_balance
    if not config.aitoearn_api_key:
        _check("AiToEarn API reachable", False, "AITOEARN_API_KEY chưa set — chạy `init` trước")
    else:
        try:
            balance = await credits_balance()
            _check("AiToEarn API reachable", True, balance.replace("\n", " ")[:80])
        except Exception as e:  # noqa: BLE001  — doctor cần khoan dung
            _check("AiToEarn API reachable", False, str(e)[:120])


def run() -> None:
    print("social-content-mcp doctor\n")

    print("--- Runtime ---")
    _check(
        "Python 3.11+",
        sys.version_info >= (3, 11),
        f"{sys.version_info.major}.{sys.version_info.minor}",
    )
    _check("Node.js installed", shutil.which("node") is not None)
    _check("ima2 CLI installed", shutil.which("ima2") is not None)

    print("\n--- Config ---")
    _check("Env file present", HOME_ENV_FILE.exists(), str(HOME_ENV_FILE))
    _check("AITOEARN_API_KEY set", bool(config.aitoearn_api_key))
    _check(
        f"STORAGE_PROVIDER = {config.storage_provider}",
        config.storage_provider in ("catbox", "imgbb"),
    )
    if config.storage_provider == "imgbb":
        _check("IMGBB_API_KEY set", bool(config.imgbb_api_key))

    asyncio.run(_async_checks())
    print()
