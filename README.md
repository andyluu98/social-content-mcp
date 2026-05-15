# social-content-mcp

> **EN** · [VI](#tiếng-việt)

MCP server that bridges [ima2-gen](https://github.com/lidge-jun/ima2-gen) (free GPT image generation via Codex OAuth) and [AiToEarn](https://github.com/yikart/AiToEarn) (multi-platform social publishing) so any MCP-compatible AI assistant — **Claude Code, Codex CLI, Gemini CLI** — can compose, illustrate, and publish posts in one conversation.

**One sentence:** chat with your AI → it generates the image, writes the caption, and posts to Facebook / Instagram / Threads / X / Pinterest.

## Features

- 🎨 **Free image generation** via Codex OAuth (no OpenAI API key needed)
- 📢 **Publish to 6 platforms** (FB, IG, TikTok\*, Threads, X, Pinterest)
- 🤖 **Works with any MCP client** — Claude Code, Codex CLI, Gemini CLI
- 🧙 **One-command setup wizard** — `social-content-mcp init`
- 🌐 **Free CDN by default** (Catbox) — no extra signup required
- 💰 **Pay-as-you-go** through AiToEarn credits (50 free on signup)

\* TikTok publishing is limited to non-public privacy levels due to AiToEarn / TikTok policy — see [Known limitations](#known-limitations).

## Quick start

```bash
pip install social-content-mcp     # not yet on PyPI — clone for now
social-content-mcp init             # wizard handles everything
```

Then open your AI client and say:

> "Create a Facebook post about AI productivity, minimal illustration"

That's it.

## Requirements

| | Why |
|---|---|
| Python 3.11+ | The MCP server runtime |
| Node.js 20+ | For ima2-gen image generator |
| A ChatGPT account | Free Codex OAuth login (no API key needed) |
| An [AiToEarn](https://aitoearn.ai) account | 50 free credits, ~30¢ |
| An MCP-compatible AI client | Claude Code / Codex CLI / Gemini CLI |

## What the wizard does

`social-content-mcp init` walks through:

1. Verifies Python & Node versions
2. Offers to install `ima2-gen` globally via npm
3. Offers to run `npx @openai/codex login` for you
4. Asks for AiToEarn API key + storage provider (Catbox by default, no key)
5. Writes `~/.social-content-mcp/.env`
6. Detects Claude / Codex / Gemini configs and registers the MCP server
7. Validates the setup with `doctor`

## Manual setup (advanced)

```bash
# 1. Clone & install
git clone https://github.com/<you>/social-content-mcp
cd social-content-mcp
python -m venv .venv && .venv/Scripts/activate
pip install -e .

# 2. Install ima2-gen and login
npm install -g ima2-gen
npx @openai/codex login

# 3. Write env (or copy .env.example)
mkdir -p ~/.social-content-mcp
cat > ~/.social-content-mcp/.env <<EOF
AITOEARN_API_KEY=ak_xxxxxxxxxxxxxxxx
STORAGE_PROVIDER=catbox
EOF

# 4. Register MCP — Claude Code
claude mcp add --scope user social-content -- python -m server
```

## Tool catalog

| Tool | What it does |
|---|---|
| `generate_image` | Generate one AI image from a prompt (Codex OAuth, free) |
| `upload_image` | Upload local image → public URL (Catbox or ImgBB) |
| `list_accounts` | List social accounts you've connected on AiToEarn |
| `check_balance` | Show remaining AiToEarn credits |
| `publish_post` | Publish one post to one platform |
| `compose_and_publish` | One-shot: gen image + upload + publish |
| `check_status` | Track an in-flight publish task by flowId |
| `ima2_health` | Debug: ping ima2-gen service |

## Commands

```bash
social-content-mcp init       # interactive setup
social-content-mcp serve      # run MCP stdio server (default)
social-content-mcp doctor     # diagnose what's missing
```

## Known limitations

- **TikTok**: AiToEarn hard-codes privacy to `PUBLIC_TO_EVERYONE`, but TikTok blocks this for any non-reviewed third-party app. Every TikTok publish via this MCP fails today. Workaround: post via AiToEarn's web dashboard and pick `SELF_ONLY` or `Followers Only`.
- **Facebook text-only posts** are not supported — at least one image is required.
- **Catbox free tier** has no documented rate limit but can throttle on burst.

## Architecture

```
Your AI client (Claude / Codex / Gemini)
        │ stdio MCP
        ▼
social-content-mcp (Python, FastMCP)
        ├── → ima2-gen (local :3333)   → image gen via Codex OAuth
        ├── → Catbox / ImgBB           → upload local → public URL
        └── → AiToEarn (cloud MCP)     → publish to FB / IG / TikTok / ...
```

## License

MIT — code in this repo. ima2-gen and AiToEarn are governed by their own licenses.

## Contributing

Issues and PRs welcome. Maintained on weekend pace (~2 hours/week). For features needing heavier work, please open an issue first to discuss.

---

<a id="tiếng-việt"></a>

# social-content-mcp (Tiếng Việt)

MCP server kết nối [ima2-gen](https://github.com/lidge-jun/ima2-gen) (sinh ảnh GPT miễn phí qua Codex OAuth) và [AiToEarn](https://github.com/yikart/AiToEarn) (đăng đa nền tảng), để bất kỳ AI assistant nào hỗ trợ MCP — **Claude Code, Codex CLI, Gemini CLI** — có thể soạn bài, sinh ảnh, và đăng trong cùng một đoạn chat.

**Một câu:** chat với AI → nó tự tạo ảnh, viết caption, đăng lên Facebook / Instagram / Threads / X / Pinterest.

## Tính năng

- 🎨 **Sinh ảnh AI miễn phí** qua Codex OAuth (không cần API key OpenAI)
- 📢 **Đăng 6 nền tảng** (FB, IG, TikTok\*, Threads, X, Pinterest)
- 🤖 **Tương thích mọi MCP client** — Claude Code, Codex CLI, Gemini CLI
- 🧙 **Cài 1 lệnh duy nhất** — `social-content-mcp init`
- 🌐 **CDN free mặc định** (Catbox) — không cần đăng ký
- 💰 **Trả theo dùng** qua credit AiToEarn (50 credit free khi signup)

\* TikTok bị giới hạn privacy không public do chính sách AiToEarn / TikTok — xem [Hạn chế đã biết](#hạn-chế-đã-biết).

## Cài nhanh

```bash
pip install social-content-mcp     # chưa lên PyPI — clone tạm
social-content-mcp init             # wizard lo hết
```

Mở AI client của bạn, nói:

> "Tạo bài đăng Facebook về AI productivity, ảnh minimal"

Xong.

## Yêu cầu

| | Tại sao |
|---|---|
| Python 3.11+ | Runtime của MCP server |
| Node.js 20+ | Cho ima2-gen sinh ảnh |
| Tài khoản ChatGPT | Login Codex OAuth free (không cần API key) |
| Tài khoản [AiToEarn](https://aitoearn.ai) | Có 50 credit free (~7k VNĐ) |
| AI client tương thích MCP | Claude Code / Codex CLI / Gemini CLI |

## Wizard làm những gì

`social-content-mcp init` đi qua:

1. Check Python + Node version
2. Mời cài `ima2-gen` global qua npm
3. Mời chạy `npx @openai/codex login` giúp bạn
4. Hỏi AiToEarn API key + chọn CDN (mặc định Catbox, không cần key)
5. Ghi `~/.social-content-mcp/.env`
6. Detect Claude / Codex / Gemini config và đăng ký MCP server
7. Kiểm tra bằng `doctor`

## Cài tay (nâng cao)

```bash
# 1. Clone & install
git clone https://github.com/<bạn>/social-content-mcp
cd social-content-mcp
python -m venv .venv && .venv\Scripts\activate
pip install -e .

# 2. Cài ima2-gen + login
npm install -g ima2-gen
npx @openai/codex login

# 3. Ghi env
mkdir -p ~/.social-content-mcp
echo "AITOEARN_API_KEY=ak_xxxxxxxxxxxx" > ~/.social-content-mcp/.env
echo "STORAGE_PROVIDER=catbox" >> ~/.social-content-mcp/.env

# 4. Đăng ký MCP — Claude Code
claude mcp add --scope user social-content -- python -m server
```

## Danh sách tool

| Tool | Tác dụng |
|---|---|
| `generate_image` | Sinh 1 ảnh AI từ prompt (Codex OAuth, free) |
| `upload_image` | Upload ảnh local → URL public (Catbox hoặc ImgBB) |
| `list_accounts` | List account social đã connect AiToEarn |
| `check_balance` | Xem credit AiToEarn còn lại |
| `publish_post` | Đăng 1 bài lên 1 platform |
| `compose_and_publish` | One-shot: gen ảnh + upload + đăng |
| `check_status` | Track flowId của task publish |
| `ima2_health` | Debug ima2-gen |

## Lệnh

```bash
social-content-mcp init       # wizard
social-content-mcp serve      # run MCP stdio (mặc định)
social-content-mcp doctor     # chẩn đoán
```

## Hạn chế đã biết

- **TikTok**: AiToEarn hard-code privacy `PUBLIC_TO_EVERYONE`, mà TikTok lại chặn cho mọi app bên thứ ba chưa qua App Review. Mọi publish TikTok qua MCP đều fail. Workaround: đăng qua web dashboard aitoearn.ai và chọn `SELF_ONLY` hoặc `Followers Only`.
- **Facebook text-only**: không hỗ trợ — bắt buộc ít nhất 1 ảnh.
- **Catbox**: free, không công bố rate limit nhưng có thể throttle khi burst.

## Kiến trúc

```
AI client (Claude / Codex / Gemini)
        │ stdio MCP
        ▼
social-content-mcp (Python, FastMCP)
        ├── → ima2-gen (local :3333)   → gen ảnh qua Codex OAuth
        ├── → Catbox / ImgBB           → upload local → URL public
        └── → AiToEarn (cloud MCP)     → đăng FB / IG / TikTok / ...
```

## License

MIT — code repo này. ima2-gen và AiToEarn theo license riêng.

## Contribute

Issue + PR luôn hoan nghênh. Maintain pace cuối tuần (~2 giờ/tuần). Feature lớn, mở issue thảo luận trước.
