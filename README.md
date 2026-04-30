<div align="center">

<!-- Animated Logo Banner -->
<img src="https://capsule-render.vercel.app/api?type=waving&height=300&color=gradient&text=𝗟𝗲𝗲𝗰𝗵%20𝗕𝗼𝘁&fontAlignY=30&fontSize=100&desc=𝖠𝖽𝗏𝖺𝗇𝖼𝖾𝖽%20𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗆%20𝖥𝗂𝗅𝖾%20𝖳𝗋𝖺𝗇𝗌𝗅𝗈𝖺𝖽𝖾𝗋&descSize=30" />

<p align="center">
  <strong>A Pyrogram‑based Telegram Bot to transfer files / folders to Telegram and Google Drive</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0-8B5CF6?style=for-the-badge&logo=semver&logoColor=white" alt="Version" />
  <img src="https://img.shields.io/badge/License-MIT-06B6D4?style=for-the-badge&logo=opensourceinitiative&logoColor=white" alt="License" />
</p>

</div>

---

## 📑 Table of Contents

- [✨ What's New in v1.0](#-whats-new-in-v10)
- [🚀 Features](#-features)
- [🔗 Supported Links](#-supported-links)
- [📋 Commands & Usage](#-commands--usage)
- [⚙️ Configuration](#%EF%B8%8F-configuration)
- [📥 How to Deploy](#-how-to-deploy)
- [🙏 Acknowledgements](#-acknowledgements)
- [📄 License](#-license)

---

## ✨ What's New in v1.0

This is a **major rewrite** with focus on **configurability, new download sources, and queue management**.

- 🔧 **`.env` Configuration** — No more hardcoded paths. All settings via environment variables with sensible defaults.
- 📋 **Download Queue** — Queue multiple links and process them sequentially with `/queue` command.
- 🎬 **YT-DLP Format Selection** — Choose quality (Best/1080p/720p/480p/Audio) via `/format` command.
- ⚡ **Bandwidth Limiter** — Set max download speed via `/speed` to avoid saturating your connection.
- 📂 **Pixeldrain Support** — Download from pixeldrain.com (single files and lists).
- 🔥 **Mediafire Support** — Download from mediafire.com with automatic direct link extraction.
- 📢 **Broadcast** — Send uploaded files to multiple chats with `/broadcast`.
- 👥 **Admin Panel** — Multi-user management with `/admin add|remove|list`.
- 🔄 **Auto-Retry** — Failed downloads automatically retry up to 3 times.
- 🐛 **Bug Fixes** — Fixed hardcoded paths, missing imports, uninitialized globals, and more.

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 📤 **Telegram Upload** | Upload any file/folder to Telegram (video, audio, document, photo) |
| ☁️ **Google Drive Mirror** | Mirror downloads directly to Google Drive |
| 📁 **Directory Leech** | Upload entire local directories recursively |
| 🎬 **Video Converter** | Convert to MP4/MKV with FFmpeg (GPU accelerated) |
| ✂️ **Smart Splitting** | Split files >2GB into chunks |
| 🗜️ **Archive Handling** | Create/extract ZIP, RAR, 7z, TAR, GZ with password support |
| 🖼️ **Auto Thumbnail** | Generate from video or use custom images |
| 📸 **Batch Photo Uploads** | Media groups of 10 for cleaner delivery |
| 📋 **Download Queue** | Queue multiple downloads, process sequentially |
| 🎬 **Format Selection** | Choose YT-DLP quality per-session |
| ⚡ **Bandwidth Control** | Limit download speed |
| 📢 **Broadcast** | Send files to multiple chats |
| 👥 **Multi-User** | Admin panel to allow/deny users |
| 🔄 **Auto-Retry** | Automatic retry on download failures |
| 🔒 **Password Protection** | ZIP/unzip passwords |
| 🏷️ **Custom Filename** | `/setname` or inline `[name]` syntax |
| ⏳ **Auto-Delete** | Configurable auto-delete for bot messages |

---

## 🔗 Supported Links

| Source | Status | Notes |
|--------|--------|-------|
| Direct HTTP/HTTPS | ✅ Full | Resume supported via aria2c |
| Google Drive | ✅ Full | Files, folders, shared drives |
| Telegram | ✅ Full | Public/private channel messages |
| YouTube / YT-DLP | ✅ Full | 2000+ sites with format selection |
| Terabox | ✅ Full | Using third-party API |
| Mega.nz | ✅ Full | Using megatools |
| Pixeldrain | ✅ **NEW** | Single files and lists |
| Mediafire | ✅ **NEW** | Auto-extracted direct links |
| Torrent / Magnet | ⚙️ Optional | Enable via `ENABLE_TORRENTS=true` |

---

## 📋 Commands & Usage

### 📥 Download Commands
| Command | Description |
|---------|-------------|
| `/start` | Show welcome message and main menu |
| `/tupload` | Leech files/folders to Telegram |
| `/gdupload` | Mirror files/folders to Google Drive |
| `/drupload` | Upload a local directory |
| `/ytupload` | Download using YT-DLP |

### 📋 Queue & Control
| Command | Description |
|---------|-------------|
| `/queue` | View download queue and session stats |
| `/cancel` | Cancel current running task |
| `/cancel_all` | Cancel task and clear queue |

### ⚙️ Settings
| Command | Description |
|---------|-------------|
| `/settings` | Open interactive settings menu |
| `/setname` | Set custom filename |
| `/zipaswd` | Set ZIP password |
| `/unzipaswd` | Set extraction password |
| `/format` | Set YT-DLP quality (Best/1080p/720p/480p/Audio) |
| `/speed` | Set bandwidth limit |

### 🛠️ Admin
| Command | Description |
|---------|-------------|
| `/admin` | Manage allowed users |
| `/broadcast` | Send last file to multiple chats |
| `/stats` | System resource usage |
| `/help` | Display all commands |

### 💡 Inline Options
When sending links, append:
- `[custom_name.mp4]` → Override filename
- `{zip_password}` → Password for ZIP creation
- `(unzip_password)` → Password for archive extraction

---

## ⚙️ Configuration

All settings are configured via **environment variables** or a `.env` file:

```bash
# Telegram Credentials (REQUIRED)
API_ID=12345
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
OWNER_ID=123456789
DUMP_ID=-1001234567890

# Paths (optional - defaults to /tmp/leechbot)
LEECHBOT_BASE_DIR=/tmp/leechbot

# Features
MAX_CONCURRENT_DOWNLOADS=3
AUTO_RETRY_COUNT=3
DEFAULT_UPLOAD_MODE=media
ENABLE_TORRENTS=false
BANDWIDTH_LIMIT=

# Google Drive
GDRIVE_ENABLED=false
TOKEN_PICKLE_PATH=

# Multi-user (comma-separated user IDs)
ALLOWED_USERS=123456789,987654321
```

---

## 📥 How to Deploy

### 1️⃣ Google Colab (One-Click)

<a href="https://colab.research.google.com/github/Shineii86/LeechBot/blob/main/notebooks/LeechBot.ipynb">
  <img src="https://user-images.githubusercontent.com/125879861/255389999-a0d261cf-893a-46a7-9a3d-2bb52811b997.png" alt="Open In Colab" width="200px">
</a>

### 2️⃣ Manual Setup (Local / VPS)

```bash
git clone https://github.com/Shineii86/LeechBot.git
cd LeechBot
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
python -m leechbot
```

### 3️⃣ Docker (Optional)

```bash
docker build -t leechbot .
docker run -d --env-file .env leechbot
```

---

## 🙏 Acknowledgements

- **Original Base:** [XronTrix10/Telegram-Leecher](https://github.com/XronTrix10/Telegram-Leecher)
- **Enhancements:** [kjeymax/Telegram-Leecher](https://github.com/kjeymax/Telegram-Leecher)
- **Forked Inspiration:** [ehraz786/tgdl](https://github.com/ehraz786/tgdl)

Special thanks to **Pyrogram**, **aria2**, **yt-dlp**, and **Google Colab**.

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE).

> ⚠️ Using this bot for downloading copyrighted content without permission may violate laws. The developer assumes no liability for misuse.

---

<div align="center">

**🧑‍💻 Developer:** [Shinei Nouzen](https://t.me/Shineii86)
**📂 GitHub:** [Shineii86/LeechBot](https://github.com/Shineii86/LeechBot)
**🔔 Updates:** [MaximXBots](https://t.me/MaximXBots)
**💬 Support:** [MaximXGroup](https://t.me/MaximXGroup)

</div>
