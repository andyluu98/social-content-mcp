# Plan — social-content-mcp

Ngày bắt đầu: 2026-05-15
Trạng thái: in-progress

## Mục tiêu

Một MCP server đơn lẻ (Python, FastMCP) gắn vào Claude Code / Codex / Gemini, cho phép:

1. Generate ảnh free qua Codex OAuth (dùng ima2-gen)
2. Soạn caption AI cho social
3. Đăng bài (ảnh + caption) lên FB/IG/TikTok/YouTube/X/Threads/Pinterest qua AiToEarn

## Phạm vi (YAGNI)

- Bridge 2 service đã có (ima2-gen + AiToEarn) qua HTTP
- KHÔNG fork code gốc của 2 repo
- KHÔNG tự build auth/database — dựa vào auth của upstream
- KHÔNG hỗ trợ video gen ở v1 — chỉ ảnh (video sau)

## Tech stack

- Python 3.11+
- FastMCP (modelcontextprotocol Python SDK)
- httpx (HTTP client async)
- python-dotenv (config)
- ima2-gen chạy như subprocess Node local (`npx ima2-gen serve`)
- AiToEarn dùng MCP cloud (`https://aitoearn.ai/api/unified/mcp`)
- ImgBB free API làm CDN tạm cho ảnh local → public URL

## File structure

```
social-content-mcp/
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
├── server/
│   ├── __init__.py
│   ├── main.py           # FastMCP entry, định nghĩa tools
│   ├── config.py
│   ├── clients/
│   │   ├── ima2.py       # gọi ima2-gen HTTP API
│   │   ├── aitoearn.py   # gọi AiToEarn MCP qua JSON-RPC
│   │   └── imgbb.py      # upload ảnh local → URL public
│   └── tools/
│       ├── image.py      # generate_image
│       └── publish.py    # publish_post, compose_and_publish
├── aitoearn/             # repo gốc (reference, gitignore)
├── ima2-gen/             # repo gốc (cần npm install để chạy)
└── plans/
```

## Tools expose qua MCP

| Tool | Input | Output |
|------|-------|--------|
| `generate_image` | prompt, size, model | local file path + URL |
| `compose_caption` | topic, platform, tone | caption text + hashtags |
| `list_accounts` | (none) | list account đã connect ở AiToEarn |
| `publish_post` | accountId, title, desc, imgPath | flowId |
| `compose_and_publish` | topic, accountIds, platform | flowId |
| `check_status` | flowId | status + post URL |

## Acceptance criteria

- Cài: `pip install -e .` thành công
- Run: `python -m server` ra MCP stdio server không lỗi
- Tích hợp Claude Code: `claude mcp add social-content -- python -m server` → connected
- Test e2e: gen 1 ảnh + caption → đăng FB SELF_ONLY → status thành công

## Risk & mitigation

| Risk | Mitigation |
|------|------------|
| ima2-gen cần `npx codex login` trước | README hướng dẫn rõ; tool báo lỗi nếu chưa login |
| ImgBB rate limit (~50 ảnh/h free) | Document; cho phép swap CDN khác qua env |
| AiToEarn API key leak | `.env` + `.gitignore` strict |
| TikTok bug privacy đã biết | Đặt cảnh báo trong tool publish khi gọi TikTok |

## Câu hỏi chưa rõ

- User muốn tích hợp CDN nào ngoài ImgBB (R2/S3/Supabase)?
- Có cần persist gallery cục bộ hay xài luôn của ima2-gen?
- Multi-account selection: tự suy luận từ tên page hay yêu cầu accountId chính xác?
