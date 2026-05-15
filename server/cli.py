"""CLI dispatcher cho social-content-mcp.

Subcommands:
  init    — chạy wizard cài đặt 1 lần
  serve   — chạy MCP stdio server (mặc định khi không có subcommand)
  doctor  — kiểm tra cài đặt
"""

from __future__ import annotations

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="social-content-mcp",
        description="MCP server bridging ima2-gen + AiToEarn for AI-powered social publishing.",
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("init", help="Run interactive setup wizard.")
    sub.add_parser("serve", help="Run MCP stdio server (default).")
    sub.add_parser("doctor", help="Diagnose installation and credentials.")

    args = parser.parse_args()
    cmd = args.command or "serve"

    if cmd == "init":
        from server.wizard import run as wizard_run
        wizard_run()
    elif cmd == "doctor":
        from server.doctor import run as doctor_run
        doctor_run()
    elif cmd == "serve":
        from server.main import serve
        serve()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
