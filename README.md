# social-content-mcp

> **EN** · [VI](#tiếng-việt)

MCP server that bridges [ima2-gen](https://github.com/lidge-jun/ima2-gen) (free GPT image generation via Codex OAuth) and [AiToEarn](https://github.com/yikart/AiToEarn) (multi-platform social publishing) so any MCP-compatible AI assistant — **Claude Code, Codex CLI, Gemini CLI** — can compose, illustrate, and publish posts in one conversation.

**In one sentence:** chat with your AI → it generates the image, writes the caption, and posts to Facebook / Instagram / Threads / X / Pinterest.

## What you get

- 🎨 **Free image generation** via Codex OAuth — no OpenAI API key
- 📢 **Publish to 6 platforms** (Facebook, Instagram, TikTok\*, Threads, X, Pinterest)
- 🤖 **Works with any MCP client** — Claude Code, Codex CLI, Gemini CLI
- 🧙 **One-command setup wizard** — `social-content-mcp init` handles everything
- 🌐 **Free CDN by default** (Catbox) — no extra signup
- 💰 **Pay-as-you-go** via AiToEarn credits (50 free on signup, ~$0.50)

\* TikTok publishing is currently blocked by AiToEarn / TikTok policy — see [Known limitations](#known-limitations).

## First post in 10 minutes

### 1. Install prerequisites

| Required | Where to get | Install check |
|---|---|---|
| Python 3.11+ | https://python.org | `python --version` |
| Node.js 20+ | https://nodejs.org | `node --version` |
| Git | https://git-scm.com | `git --version` |

### 2. Clone and install this repo

```bash
git clone https://github.com/andyluu98/social-content-mcp.git
cd social-content-mcp

# Windows:
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate

pip install -e .
```

### 3. Sign up for the free upstream services

| Service | Why | How |
|---|---|---|
| ChatGPT / Codex | Free image generation | `npx @openai/codex login` (use your ChatGPT account) |
| AiToEarn | Publishing | Sign up at https://aitoearn.ai → Settings → API Key → copy the `ak_...` value |

You'll paste the AiToEarn key in the next step.

### 4. Run the wizard

```bash
social-content-mcp init
```

The wizard walks through 6 steps. Answer like this for the simplest path:

```
[1/6] Kiểm tra Python + Node...           → automatic
[2/6] Cài ima2-gen?                        → Y
[3/6] Login Codex OAuth?                   → Y (browser will open)
[4/6] AiToEarn API key: ak_xxxxx          → paste your key
      CDN provider: 1                      → 1 (catbox, no key needed)
[5/6] Writing config...                    → automatic
[6/6] Register MCP into Claude / Codex / Gemini? → Y for whichever you use
```

When you see `✓ Setup xong`, you're ready.

### 5. Start ima2-gen in a separate terminal

ima2-gen runs as a local image-generation service. Keep this terminal open while you use the MCP:

```bash
ima2 serve
```

### 6. Open your AI client and try

Open **Claude Code** (or Codex CLI / Gemini CLI). In a new chat, type:

> Generate an AI productivity image and post it to my Facebook page about modern marketing.

The AI will:
1. Call `list_accounts` → finds your Facebook page
2. Call `generate_image` → image saved to local file
3. Call `upload_image` → public URL via Catbox
4. Call `publish_post` → submits to Facebook
5. Call `check_status` → confirms post is live

If something goes wrong, run:

```bash
social-content-mcp doctor
```

It reports which piece is missing or unreachable.

## Example conversation

```
You: Đăng FB Aithetech VN bài về Productivity AI, ảnh phong cách minimal.

AI:  Got it. Let me find your Facebook accounts first.
     [calls list_accounts]
     Found "Aithetech VN" (id: facebook_997677576765087).
     Generating a minimal illustration...
     [calls generate_image with prompt "minimal vector illustration of
      AI assistant boosting productivity, clean white background"]
     Image saved to ./output/1747512345_abc.png
     [calls upload_image]
     Uploaded: https://files.catbox.moe/abc123.png
     [calls publish_post]
     Submitted (flowId: 78d5...). Waiting 6 seconds...
     [calls check_status]
     ✓ Posted: https://facebook.com/.../posts/12211...
```

## Tool catalog

| Tool | What it does |
|---|---|
| `generate_image` | Generate one AI image from a prompt (Codex OAuth, free) |
| `upload_image` | Upload local image → public URL (Catbox or ImgBB) |
| `list_accounts` | List social accounts you've connected on AiToEarn |
| `check_balance` | Show remaining AiToEarn credits |
| `publish_post` | Publish one post to one platform |
| `compose_and_publish` | One-shot: generate image + upload + publish |
| `check_status` | Track an in-flight publish task by flowId |
| `ima2_health` | Debug: ping ima2-gen service |

## Commands

```bash
social-content-mcp init       # interactive setup wizard
social-content-mcp serve      # run MCP stdio server (the default)
social-content-mcp doctor     # diagnose what's missing
```

## Manual setup (without the wizard)

```bash
# After git clone + pip install -e .:

npm install -g ima2-gen
npx @openai/codex login

# Write env (use your home directory):
mkdir -p ~/.social-content-mcp
cat > ~/.social-content-mcp/.env <<EOF
AITOEARN_API_KEY=ak_xxxxxxxxxxxxxxxx
STORAGE_PROVIDER=catbox
EOF

# Register MCP into Claude Code:
claude mcp add --scope user social-content -- python -m server
```

For Codex CLI, add to `~/.codex/config.toml`:

```toml
[mcp_servers.social-content]
command = "python"
args = ["-m", "server"]
```

For Gemini CLI, add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "social-content": { "command": "python", "args": ["-m", "server"] }
  }
}
```

## Troubleshooting

**`ima2-gen không reachable` in doctor**
Start `ima2 serve` in a separate terminal. It binds to port 3333 by default.
If you previously had multiple `ima2 serve` instances running, the autodiscovery file `~/.ima2/server.json` may point to a dead port (3334+). Kill all `node` / `ima2` processes, then run a single `ima2 serve` and re-check `doctor`.

**`AITOEARN_API_KEY chưa set`**
Check `~/.social-content-mcp/.env` exists and contains the key. Re-run `social-content-mcp init` to recreate it.

**Codex login fails on Windows behind a proxy**
Set `HTTP_PROXY` and `HTTPS_PROXY` in the terminal running `codex login`. Some Windows security tools block port 10531 — the wizard's `doctor` will surface this.

**Facebook publish error: `Image upload failed`**
Facebook requires at least one image — text-only posts fail. Generate or attach an image.

**TikTok publish fails every time**
Known limitation. AiToEarn's MCP hard-codes `PUBLIC_TO_EVERYONE` but TikTok blocks this for non-reviewed apps. Workaround: post via the AiToEarn web dashboard at https://aitoearn.ai and choose `SELF_ONLY` or `Followers Only` privacy.

**Image generation fails with `API_KEY_REQUIRED`**
You're using the API provider path instead of OAuth. Run `npx @openai/codex login` again, then restart `ima2 serve`.

## Known limitations

- **TikTok**: see Troubleshooting above. Until AiToEarn exposes `privacy_level` through MCP, every TikTok publish through this server fails.
- **Facebook text-only posts** are not supported — at least one image is required.
- **Catbox** has no published rate limit but throttles on burst — switch to ImgBB if you upload many images per minute.
- **Token costs** — gen ảnh free qua Codex OAuth tốn ChatGPT quota (gói Plus ~80 gen/3h). API path costs your OpenAI key.

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

Issues and PRs welcome. Maintained at weekend pace (~2 hours per week). For features needing heavier work, please open an issue first to discuss.

---

<a id="tiếng-việt"></a>

# social-content-mcp (Tiếng Việt)

MCP server kết nối [ima2-gen](https://github.com/lidge-jun/ima2-gen) (sinh ảnh GPT miễn phí qua Codex OAuth) và [AiToEarn](https://github.com/yikart/AiToEarn) (đăng đa nền tảng), để bất kỳ AI assistant nào hỗ trợ MCP — **Claude Code, Codex CLI, Gemini CLI** — có thể soạn bài, sinh ảnh, và đăng trong cùng một đoạn chat.

**Một câu:** chat với AI → nó tự tạo ảnh, viết caption, đăng lên Facebook / Instagram / Threads / X / Pinterest.

## Bạn nhận được gì

- 🎨 **Sinh ảnh AI miễn phí** qua Codex OAuth — không cần API key OpenAI
- 📢 **Đăng 6 nền tảng** (FB, IG, TikTok\*, Threads, X, Pinterest)
- 🤖 **Mọi MCP client đều dùng được** — Claude Code, Codex CLI, Gemini CLI
- 🧙 **Cài 1 lệnh duy nhất** — `social-content-mcp init`
- 🌐 **CDN free mặc định** (Catbox)
- 💰 **Trả theo dùng** qua credit AiToEarn (50 credit free khi signup)

\* TikTok hiện bị chặn do chính sách AiToEarn / TikTok — xem [Hạn chế đã biết](#hạn-chế-đã-biết).

## Bài đăng đầu tiên trong 10 phút

### 1. Cài prerequisite

| Cần | Lấy ở đâu | Check |
|---|---|---|
| Python 3.11+ | https://python.org | `python --version` |
| Node.js 20+ | https://nodejs.org | `node --version` |
| Git | https://git-scm.com | `git --version` |

### 2. Clone & install repo

```bash
git clone https://github.com/andyluu98/social-content-mcp.git
cd social-content-mcp

# Windows:
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate

pip install -e .
```

### 3. Signup 2 service free

| Dịch vụ | Để làm gì | Cách |
|---|---|---|
| ChatGPT / Codex | Gen ảnh free | `npx @openai/codex login` (dùng account ChatGPT) |
| AiToEarn | Đăng bài | https://aitoearn.ai → Settings → API Key → copy `ak_...` |

Paste AiToEarn key ở bước sau.

### 4. Chạy wizard

```bash
social-content-mcp init
```

Trả lời nhanh:

```
[1/6] Check Python + Node              → tự động
[2/6] Cài ima2-gen?                    → Y
[3/6] Login Codex OAuth?               → Y (browser sẽ mở)
[4/6] AiToEarn key: ak_xxx             → paste key
      CDN: 1                            → 1 (catbox, free)
[5/6] Ghi config                       → tự động
[6/6] Đăng ký vào Claude/Codex/Gemini  → Y cho cái nào bạn dùng
```

Khi thấy `✓ Setup xong` là OK.

### 5. Chạy ima2-gen ở terminal riêng

```bash
ima2 serve
```

Giữ terminal này mở khi đang dùng MCP.

### 6. Mở AI client thử

Trong **Claude Code** (hoặc Codex / Gemini), gõ:

> Đăng FB bài về AI productivity, ảnh phong cách minimal.

AI sẽ:
1. `list_accounts` → tìm Facebook Page của bạn
2. `generate_image` → ra file local
3. `upload_image` → URL public qua Catbox
4. `publish_post` → submit lên Facebook
5. `check_status` → confirm đăng thành công

Lỗi đâu, chạy:

```bash
social-content-mcp doctor
```

## Ví dụ hội thoại

```
Bạn: Đăng FB Aithetech VN bài về Productivity AI, ảnh phong cách minimal.

AI:  OK. Tôi tìm Facebook account của bạn trước.
     [gọi list_accounts]
     Tìm thấy "Aithetech VN" (id: facebook_997677576765087).
     Đang gen ảnh minimal...
     [gọi generate_image]
     Ảnh lưu ở ./output/1747512345_abc.png
     [gọi upload_image]
     URL: https://files.catbox.moe/abc123.png
     [gọi publish_post]
     Submit xong (flowId: 78d5...). Chờ 6 giây...
     [gọi check_status]
     ✓ Đã đăng: https://facebook.com/.../posts/12211...
```

## Danh sách tool

| Tool | Tác dụng |
|---|---|
| `generate_image` | Sinh 1 ảnh AI từ prompt (Codex OAuth, free) |
| `upload_image` | Upload ảnh local → URL public (Catbox/ImgBB) |
| `list_accounts` | List account đã connect AiToEarn |
| `check_balance` | Xem credit còn lại |
| `publish_post` | Đăng 1 bài 1 platform |
| `compose_and_publish` | One-shot: gen + upload + đăng |
| `check_status` | Track flowId |
| `ima2_health` | Debug ima2-gen |

## Lệnh

```bash
social-content-mcp init       # wizard
social-content-mcp serve      # MCP stdio (mặc định)
social-content-mcp doctor     # chẩn đoán
```

## Cài tay (không qua wizard)

```bash
# Sau git clone + pip install -e .:

npm install -g ima2-gen
npx @openai/codex login

mkdir -p ~/.social-content-mcp
cat > ~/.social-content-mcp/.env <<EOF
AITOEARN_API_KEY=ak_xxxxxxxxxxxx
STORAGE_PROVIDER=catbox
EOF

claude mcp add --scope user social-content -- python -m server
```

Codex CLI — thêm vào `~/.codex/config.toml`:

```toml
[mcp_servers.social-content]
command = "python"
args = ["-m", "server"]
```

Gemini CLI — thêm vào `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "social-content": { "command": "python", "args": ["-m", "server"] }
  }
}
```

## Lỗi hay gặp

**`ima2-gen không reachable` trong doctor**
Chạy `ima2 serve` ở terminal riêng. Port mặc định 3333.
Nếu trước đó từng chạy nhiều instance `ima2 serve`, file autodiscovery `~/.ima2/server.json` có thể trỏ vào port chết (3334+). Tắt hết process `node` / `ima2`, chạy lại 1 instance duy nhất, rồi `doctor` lại.

**`AITOEARN_API_KEY chưa set`**
Kiểm tra file `~/.social-content-mcp/.env`. Chạy lại `social-content-mcp init` để recreate.

**Codex login fail trên Windows do proxy**
Set `HTTP_PROXY` và `HTTPS_PROXY` trong terminal trước khi login. Tool bảo mật Windows hay chặn port 10531 — `doctor` sẽ chỉ ra.

**Facebook báo `Image upload failed`**
Facebook bắt buộc có ít nhất 1 ảnh. Gen hoặc đính kèm ảnh.

**TikTok luôn fail**
Hạn chế đã biết. AiToEarn hard-code privacy `PUBLIC_TO_EVERYONE`, TikTok chặn cho app bên thứ ba chưa qua App Review. Workaround: đăng tay qua web dashboard https://aitoearn.ai, chọn `SELF_ONLY` hoặc `Followers Only`.

**Gen ảnh báo `API_KEY_REQUIRED`**
Đang dùng provider API thay vì OAuth. Chạy lại `npx @openai/codex login` rồi restart `ima2 serve`.

## Hạn chế đã biết

- **TikTok**: xem mục Lỗi ở trên.
- **Facebook text-only**: không hỗ trợ — phải có ảnh.
- **Catbox**: throttle khi upload burst — dùng ImgBB nếu upload nhiều/phút.
- **Codex OAuth quota**: free qua ChatGPT Plus ~80 ảnh/3 giờ.

## Kiến trúc

```
AI client (Claude / Codex / Gemini)
        │ stdio MCP
        ▼
social-content-mcp (Python, FastMCP)
        ├── → ima2-gen (local :3333)   → gen ảnh qua Codex OAuth
        ├── → Catbox / ImgBB           → upload → URL public
        └── → AiToEarn (cloud MCP)     → đăng FB / IG / TikTok / ...
```

## License

MIT — code repo này. ima2-gen và AiToEarn theo license riêng.

## Contribute

Issue + PR luôn hoan nghênh. Maintain pace cuối tuần (~2 giờ/tuần). Feature lớn, mở issue thảo luận trước.
