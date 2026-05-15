"""Interactive setup wizard — `social-content-mcp init`.

Mục tiêu: user chỉ trả lời vài câu, wizard lo:
- check Python/Node
- cài ima2-gen global (Y/n)
- chạy `npx @openai/codex login` (Y/n)
- hỏi AiToEarn API key + chọn CDN provider
- ghi ~/.social-content-mcp/.env
- ghi MCP config vào Claude / Codex / Gemini đã detect
- test ping toàn bộ
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
CFG_DIR = HOME / ".social-content-mcp"
ENV_FILE = CFG_DIR / ".env"

BANNER = """
============================================================
 social-content-mcp — Setup Wizard
 Gen ảnh AI free + đăng đa nền tảng qua Claude/Codex/Gemini
============================================================
"""


def _prompt(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    val = input(f"{label}{suffix}: ").strip()
    return val or default


def _yesno(label: str, default: bool = True) -> bool:
    d = "Y/n" if default else "y/N"
    val = input(f"{label} ({d}): ").strip().lower()
    if not val:
        return default
    return val.startswith("y")


def _check_cmd(cmd: str) -> str | None:
    """Trả về version string nếu cmd tồn tại, None nếu không."""
    path = shutil.which(cmd)
    if not path:
        return None
    try:
        out = subprocess.run(
            [cmd, "--version"], capture_output=True, text=True, timeout=10
        )
        return (out.stdout + out.stderr).strip().splitlines()[0]
    except (OSError, subprocess.SubprocessError):
        return path


def _step_check_runtime() -> bool:
    print("\n[1/6] Kiểm tra Python + Node...")
    py = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"  Python: {py}")
    if sys.version_info < (3, 11):
        print("  ❌ Cần Python 3.11+. Cài lại Python rồi chạy lại wizard.")
        return False

    node = _check_cmd("node")
    if not node:
        print("  ❌ Không tìm thấy Node.js. Cài tại https://nodejs.org/ (cần v20+).")
        return False
    print(f"  Node: {node}")
    return True


def _step_install_ima2() -> None:
    print("\n[2/6] Cài ima2-gen (image generator dùng Codex OAuth — free)...")
    if shutil.which("ima2"):
        print("  ✓ ima2 đã có sẵn, skip.")
        return
    if not _yesno("  Cài ima2-gen global qua npm?", True):
        print("  Skip. Bạn tự cài sau: `npm install -g ima2-gen`")
        return
    npm = shutil.which("npm") or "npm"
    subprocess.run([npm, "install", "-g", "ima2-gen"], check=False)


def _step_codex_login() -> None:
    print("\n[3/6] Login Codex OAuth (để gen ảnh free, không cần API key)...")
    if not _yesno("  Mở Codex login flow?", True):
        print("  Skip. Bạn tự chạy sau: `npx @openai/codex login`")
        return
    npx = shutil.which("npx") or "npx"
    subprocess.run([npx, "-y", "@openai/codex", "login"], check=False)


def _step_collect_keys() -> dict[str, str]:
    print("\n[4/6] Khai báo AiToEarn + chọn CDN provider...")
    print("  Lấy AiToEarn API key tại: https://aitoearn.ai → Settings → API Key")
    aitoearn = _prompt("  AiToEarn API key (ak_...)")
    while not aitoearn.startswith("ak_"):
        print("  Key phải bắt đầu bằng 'ak_'. Thử lại.")
        aitoearn = _prompt("  AiToEarn API key (ak_...)")

    print("\n  CDN provider để upload ảnh local → URL public:")
    print("    1) catbox  — free, không cần key (mặc định)")
    print("    2) imgbb   — free, cần API key tại https://api.imgbb.com/")
    choice = _prompt("  Chọn 1 hoặc 2", "1")
    if choice == "2":
        imgbb = _prompt("  ImgBB API key")
        return {
            "AITOEARN_API_KEY": aitoearn,
            "IMGBB_API_KEY": imgbb,
            "STORAGE_PROVIDER": "imgbb",
        }
    return {"AITOEARN_API_KEY": aitoearn, "STORAGE_PROVIDER": "catbox"}


def _step_write_env(env: dict[str, str]) -> Path:
    CFG_DIR.mkdir(parents=True, exist_ok=True)
    lines = [f"{k}={v}" for k, v in env.items()]
    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n[5/6] Đã ghi config: {ENV_FILE}")
    return ENV_FILE


def _detect_ai_clients() -> list[str]:
    found = []
    if (HOME / ".claude.json").exists() or (HOME / ".claude").is_dir():
        found.append("claude")
    if (HOME / ".codex").is_dir():
        found.append("codex")
    if (HOME / ".gemini").is_dir():
        found.append("gemini")
    return found


def _step_register_mcp() -> None:
    print("\n[6/6] Đăng ký MCP server vào AI client...")
    clients = _detect_ai_clients()
    if not clients:
        print("  Không tìm thấy Claude/Codex/Gemini config. Bỏ qua bước này.")
        print("  Tham khảo README để gắn tay.")
        return
    print(f"  Đã detect: {', '.join(clients)}")
    python_bin = sys.executable
    args = [python_bin, "-m", "server"]

    if "claude" in clients and _yesno("  Gắn vào Claude Code?", True):
        _register_claude(args)
    if "codex" in clients and _yesno("  Gắn vào Codex CLI?", True):
        _register_codex(args)
    if "gemini" in clients and _yesno("  Gắn vào Gemini CLI?", True):
        _register_gemini(args)


def _register_claude(args: list[str]) -> None:
    cfg_path = HOME / ".claude.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}
    cfg.setdefault("mcpServers", {})["social-content"] = {
        "type": "stdio",
        "command": args[0],
        "args": args[1:],
    }
    cfg_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    print(f"    ✓ Claude Code: {cfg_path}")


def _register_codex(args: list[str]) -> None:
    cfg_path = HOME / ".codex" / "config.toml"
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    block = (
        f'\n[mcp_servers.social-content]\n'
        f'command = "{args[0].replace(chr(92), "/")}"\n'
        f'args = {json.dumps(args[1:])}\n'
    )
    existing = cfg_path.read_text(encoding="utf-8") if cfg_path.exists() else ""
    if "[mcp_servers.social-content]" not in existing:
        cfg_path.write_text(existing + block, encoding="utf-8")
    print(f"    ✓ Codex CLI: {cfg_path}")


def _register_gemini(args: list[str]) -> None:
    cfg_path = HOME / ".gemini" / "settings.json"
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}
    cfg.setdefault("mcpServers", {})["social-content"] = {
        "command": args[0],
        "args": args[1:],
    }
    cfg_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    print(f"    ✓ Gemini CLI: {cfg_path}")


def _print_done() -> None:
    print(
        "\n============================================================\n"
        " ✓ Setup xong. Mở AI client của bạn, chạy:\n"
        '   "Tạo bài đăng FB về AI productivity, ảnh phong cách minimal"\n\n'
        " Debug: `social-content-mcp doctor`\n"
        " Khởi động ima2-gen lần đầu: `ima2 serve`\n"
        "============================================================"
    )


def run() -> None:
    print(BANNER)
    if not _step_check_runtime():
        sys.exit(1)
    _step_install_ima2()
    _step_codex_login()
    env = _step_collect_keys()
    _step_write_env(env)
    _step_register_mcp()
    _print_done()
