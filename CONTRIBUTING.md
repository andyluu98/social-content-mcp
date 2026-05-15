# Contributing to social-content-mcp

Issues and pull requests welcome. This project is maintained at weekend pace (~2 hours/week), so please be patient on responses — open issues stay on the radar.

## Dev setup

```bash
git clone https://github.com/andyluu98/social-content-mcp.git
cd social-content-mcp

python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate

pip install -e .
```

Verify it works:

```bash
python -m py_compile server/*.py server/clients/*.py
python -m server --help
python -m server doctor
```

## Project layout

```
server/
├── cli.py          # argparse dispatcher (init / serve / doctor)
├── main.py         # FastMCP server, all tool definitions
├── wizard.py       # interactive setup wizard
├── doctor.py       # diagnostic command
├── config.py       # env loading (priority: env > ~/.social-content-mcp/.env > ./.env)
└── clients/
    ├── ima2.py     # ima2-gen HTTP client
    ├── aitoearn.py # AiToEarn MCP JSON-RPC client
    ├── catbox.py   # free CDN upload (no API key)
    └── imgbb.py    # CDN upload with API key
```

Each file kept under ~200 LOC per the modularization rule. If a file grows past that, split it.

## Coding conventions

- **Python 3.11+** syntax (use `|` for union types, `dict[str, X]` instead of `Dict[str, X]`).
- **Type hints everywhere** in public function signatures.
- **`from __future__ import annotations`** at top of every module.
- **Descriptive snake_case** for file/function names.
- **Errors raise `XxxError(RuntimeError)`** subclasses per client — don't return None for failures.

## What's easy to contribute

- **New CDN provider** — add `server/clients/<name>.py` following the catbox.py pattern, register in `clients/__init__.py`
- **New social platform** — add async function in `aitoearn.py`, register in `_PUBLISH_DISPATCH` in `main.py`, add to `PLATFORMS` Literal
- **Bug fixes** — open an issue first with reproduction steps
- **Docs improvements** — README clarifications, additional troubleshooting entries
- **Translations** — currently EN + VI; other languages welcome as separate sections in README

## Pull request flow

1. Fork the repo
2. Create a branch: `git checkout -b feat/your-thing`
3. Make changes, ensure `python -m py_compile server/*.py server/clients/*.py` still passes
4. Test the wizard locally if your change touches `init` / `serve` / `doctor` flow
5. Commit with conventional commit style: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
6. Open a PR with a description of what changed and why

CI (GitHub Actions) runs on Ubuntu, Windows, and macOS across Python 3.11 and 3.12. All three OSes must pass before merge.

## Security & privacy

- **Never commit secrets**: `.env` is gitignored. If you accidentally commit a key, rotate it immediately at the upstream provider (AiToEarn / ImgBB / etc.) and force-push the redaction.
- **User keys live locally** in `~/.social-content-mcp/.env`. The server only forwards them to the documented upstream services (ima2-gen, AiToEarn, Catbox/ImgBB).
- **No telemetry** — this project does not collect usage data.

## Community

- Issues: https://github.com/andyluu98/social-content-mcp/issues
- Discussions are not enabled yet; use issues for questions too.
