<div align="center">

<!-- Animated Logo Banner -->
<img src="https://capsule-render.vercel.app/api?type=waving&height=300&color=gradient&text=𝗟𝗲𝗲𝗰𝗵%20𝗕𝗼𝘁&fontAlignY=30&fontSize=100&desc=𝖠𝖽𝗏𝖺𝗇𝖼𝖾𝖽%20𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗆%20𝖥𝗂𝗅𝖾%20𝖳𝗋𝖺𝗇𝗌𝗅𝗈𝖺𝖽𝖾𝗋&descSize=30" />

<p align="center">
  <strong>A Pyrogram‑based Telegram Bot to transfer files / folders to Telegram and Google Drive, powered by Google Colab</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-3.1.0-8B5CF6?style=for-the-badge&logo=semver&logoColor=white" alt="Version" />
  <img src="https://img.shields.io/badge/License-MIT-06B6D4?style=for-the-badge&logo=opensourceinitiative&logoColor=white" alt="License" />

![Last Commit](https://img.shields.io/github/last-commit/Shineii86/LeechBot?style=for-the-badge)
![Repo Size](https://img.shields.io/github/repo-size/Shineii86/LeechBot?style=for-the-badge)
[![GitHub Stars](https://img.shields.io/github/stars/Shineii86/LeechBot?style=for-the-badge)](https://github.com/Shineii86/LeechBot/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/Shineii86/LeechBot?style=for-the-badge)](https://github.com/Shineii86/LeechBot/fork)

</div>

---

## 📑 **Table of Contents**

- [📖 Complete User Guide](GUIDE.md) ← **Start here if you're new**
- [✨ What's New?](#-whats-new-in-v3)
- [🚀 Features](#-features)
- [⚙️ Configuration](#-configuration)
- [🔗 Supported Links](#-supported-links)
- [💡 Benefits](#-benefits)
- [🛠️ Technology Stack](#️-technology-stack)
- [📥 How to Deploy](#-how-to-deploy)
- [📋 Commands & Usage](#-commands--usage)
- [🆚 Changelog – Old vs New](#-changelog--old-vs-new)
- [🙏 Acknowledgements](#-acknowledgements)
- [📄 License & Disclaimer](#-license--disclaimer)
- [🫂 Updates & Support](#-updates--support)
- [👤 Developer & Credits](#-developer--credits)

---

## ✨ What's New in v3.X.X

### 🌐 v3.1.0 — Web Dashboard

- **Web Dashboard** — real-time browser dashboard for monitoring and controlling the bot
- **Live stats** — CPU, RAM, disk, speed, uptime, download/upload totals
- **Queue management** — view pending downloads, clear queue from browser
- **Active task monitoring** — real-time progress bar with speed, ETA, elapsed time
- **Settings viewer** — view current bot settings from the dashboard
- **WebSocket** — real-time updates pushed to browser every 3 seconds
- **Token auth** — secure access via `WEB_TOKEN` environment variable
- **Runs on Colab** — dashboard accessible via Colab's public URL or ngrok tunnel

> 📋 **Full history:** [CHANGELOG.md](CHANGELOG.md)

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
| 📸 **Photo Upload Mode** | Group (batch of 10) or Single (one by one) via `/settings` |
| 📋 **Download Queue** | Queue multiple downloads, process sequentially |
| 🎬 **Format Selection** | Choose YT-DLP quality per-session |
| ⚡ **Bandwidth Control** | Limit download speed |
| 📢 **Broadcast** | Send files to multiple chats |
| 👥 **Multi-User** | Admin panel to allow/deny users |
| 🔄 **Auto-Retry** | Automatic retry on download failures |
| 🔒 **Password Protection** | ZIP/unzip passwords |
| 🏷️ **Custom Filename** | `/setname` or inline `[name]` syntax |
| ⏳ **Auto-Delete** | Configurable auto-delete for bot messages |
| 🎬 **YouTube PO Tokens** | Auto-generated via plugin — no manual cookie setup |
| 📸 **Photo Galleries** | Instagram, Twitter, Pinterest, Pixiv, DeviantArt via gallery-dl |

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

# YT-DLP Cookie Authentication (optional fallback)
# YTDL_COOKIES_FILE=/path/to/cookies.txt
# YTDL_BROWSER_COOKIES=chrome

# Multi-user (comma-separated user IDs)
ALLOWED_USERS=123456789,987654321
```

## 🔗 Supported Links

| Source | Status | Notes |
|--------|--------|-------|
| Direct HTTP/HTTPS | ✅ Full | Resume supported via aria2c |
| Google Drive | ✅ Full | Files, folders, shared drives |
| Telegram | ✅ Full | Public/private channel messages |
| YouTube / YT-DLP | ✅ Full | 2000+ sites with PO Token auto-auth |
| Instagram | ✅ **NEW** | Posts, carousels via gallery-dl |
| Twitter / X | ✅ **NEW** | Media timelines via gallery-dl |
| Pinterest | ✅ **NEW** | Boards, pins via gallery-dl |
| Pixiv / DeviantArt | ✅ **NEW** | Art galleries via gallery-dl |
| Terabox | ✅ Full | Using third-party API |
| Mega.nz | ✅ Full | Using megatools |
| Pixeldrain | ✅ Full | Single files and lists |
| Mediafire | ✅ Full | Auto-extracted direct links |
| Reddit / Flickr / Tumblr | ✅ **NEW** | Image galleries via gallery-dl |
| Torrent / Magnet | ⚙️ Optional | Enable via `ENABLE_TORRENTS=true` |

---

## 💡 **Benefits**

- ☁️ **No VPS Needed** – Runs entirely on **Google Colab** free tier.
- 🌐 **Blazing Speeds** – Google’s backbone delivers up to **200 MiB/s download** and **30 MiB/s upload**.
- ♾️ **Unlimited Storage** – Telegram provides free, unlimited cloud storage.
- 🔧 **Easy Setup** – One‑click Colab notebook, no complex configurations.
- 🎯 **User‑Friendly** – Fully interactive with buttons, menus, and clear progress messages.

---

## 🛠️ **Technology Stack**

| Component           | Technology                                                              |
| ------------------- | ----------------------------------------------------------------------- |
| Bot Framework       | [Pyrogram](https://docs.pyrogram.org/) (MTProto API)                    |
| Download Manager    | [aria2c](https://aria2.github.io/) + [yt‑dlp](https://github.com/yt-dlp/yt-dlp) |
| YouTube Auth        | [bgutil-ytdlp-pot-provider](https://github.com/Brainicism/bgutil-ytdlp-pot-provider) (PO Token auto-gen) |
| Photo Galleries     | [gallery-dl](https://github.com/mikf/gallery-dl) (Instagram, Twitter, Pinterest, 100+ sites) |
| Video Processing    | FFmpeg, MoviePy, GPUtil (GPU acceleration)                              |
| Archive Handling    | 7z, unrar, zip, tar                                                    |
| Cloud Environment   | Google Colab (Python 3.10+, Ubuntu 22.04)                               |
| Google Drive API    | google‑api‑python‑client                                                |
| Thumbnail Generator | PIL / Pillow                                                            |

### 📁 Project Structure

```
leechbot/
├── __init__.py          # Pyrogram client initialization
├── __main__.py          # Entry point (imports handlers, runs bot, registers commands)
├── commands.py          # All /command handlers
├── callbacks.py         # Inline keyboard callback handlers (split into focused functions)
├── debug.py             # Error reporting & debug logging to Telegram
├── handlers.py          # Message handlers (URL, photo, text, reply)
├── updater.py           # Auto-update from GitHub
├── downloader/
│   ├── aria2.py         # HTTP/FTP/torrent via aria2c
│   ├── gallery.py       # Photo galleries via gallery-dl (with progress bar)
│   ├── gdrive.py        # Google Drive downloads
│   ├── manager.py       # Download router & retry logic
│   ├── mediafire.py     # Mediafire downloads
│   ├── mega.py          # Mega.nz downloads
│   ├── pixeldrain.py    # Pixeldrain downloads
│   ├── telegram.py      # Telegram message downloads
│   ├── terabox.py       # Terabox downloads
│   └── ytdl.py          # YT-DLP (YouTube, 2000+ sites)
├── uploader/
│   └── telegram.py      # Telegram upload with progress (including batch photo)
├── web/
│   ├── server.py        # Web dashboard server (REST API + WebSocket)
│   └── __init__.py
└── utility/
    ├── converters.py    # Video conversion, archive/extract
    ├── handler.py       # Task handlers (Leech, Zip, Unzip, SendLogs, cancelTask)
    ├── helper.py        # Formatting, link detection, UI helpers
    ├── style.py         # Unicode small caps styling
    ├── task_manager.py  # Task scheduler & orchestrator
    └── variables.py     # Global state & configuration classes
```

---

## 📥 **How to Deploy**

### 1️⃣ **One‑Click Colab**

<a href="https://colab.research.google.com/github/Shineii86/LeechBot/blob/main/notebooks/LeechBot.ipynb">
  <img src="https://user-images.githubusercontent.com/125879861/255389999-a0d261cf-893a-46a7-9a3d-2bb52811b997.png" alt="Open In Colab" width="200px">
</a>

### 2️⃣ **Manual Setup (Local / VPS)**

```bash
git clone https://github.com/Shineii86/LeechBot.git
cd LeechBot
pip install -r requirements.txt
```

Create a `credentials.json` file with your API details:

```json
{
  "API_ID": 12345,
  "API_HASH": "your_api_hash",
  "BOT_TOKEN": "your_bot_token",
  "USER_ID": 123456789,
  "DUMP_ID": -1001234567890
}
```

Run the bot:

```bash
python -m leechbot
```

### 3️⃣ **Detailed Instructions**

- 📘 [Full Deployment Guide](https://github.com/XronTrix10/Telegram-Leecher/wiki/INSTRUCTIONS) (original base)
- 📖 [Complete User Guide](GUIDE.md) — credentials, setup, commands, troubleshooting
- 🎥 [YouTube Tutorial](https://www.youtube.com/watch?v=6LvYd-oO3U0)

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
| `/glupload` | Download image galleries via gallery-dl |

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
| `/stats` | System resource usage |
| `/help` | Display all commands |

### 🍪 YouTube Auth
| Command | Description |
|---------|-------------|
| `/cookies` | Check YouTube authentication status |
| `/setcookies` | Upload cookies.txt for YouTube fallback |
| `/clearcookies` | Delete stored cookies file |

### 💡 Inline Options
When sending links, append:
- `[custom_name.mp4]` → Override filename
- `{zip_password}` → Password for ZIP creation
- `(unzip_password)` → Password for archive extraction

---

## 🆚 **Changelog – Old vs New**

| **Aspect**             | **Telegram Leecher**                 | **LeechBot**                                         |
| ---------------------- | ------------------------------------ | ---------------------------------------------------- |
| **UI / UX**            | Plain text messages                  | Box-drawing panels (`┏┣┗`), clean Markdown with inline menus |
| **Auto‑Delete**        | None                                 | Configurable auto‑delete for bot messages            |
| **Batch Photo Upload** | One‑by‑one photos                    | Media groups of 10 with live progress bar            |
| **Code Structure**     | Monolithic, less documented          | Modular (`commands` / `callbacks` / `handlers`), split callbacks, fully typed, clean docstrings |
| **Video Converter**    | Basic FFmpeg                         | GPU‑accelerated FFmpeg + MoviePy fallback            |
| **Archive Support**    | Limited to ZIP                       | Full 7z, RAR, TAR, GZ, multipart extraction          |
| **Settings Menu**      | None                                 | Interactive inline menu with toggle switches         |
| **Thumbnail**          | Manual only                          | Auto‑generate from video, YT‑DLP thumb support       |
| **Link Support**       | HTTP, GDrive, YT, Telegram           | Added Terabox, Mediafire, Pixeldrain, Mega, gallery-dl (100+ sites) |
| **Progress Updates**   | Basic text                           | Real‑time speed, ETA, percentage, system stats for ALL engines |
| **Commands**           | Manual via @BotFather                | Auto-registered on startup (23 commands)             |
| **Error Handling**     | Single try/except                    | Individual try/except per operation, robust cancellation |
| **License**            | GPL‑3.0                              | MIT (more permissive)                                |

---

## 🙏 **Acknowledgements**

This project stands on the shoulders of giants:

- **Original Base:** [XronTrix10/Telegram‑Leecher](https://github.com/XronTrix10/Telegram-Leecher)  
- **Minor Fixes & Enhancements:** [kjeymax/Telegram‑Leecher](https://github.com/kjeymax/Telegram-Leecher)  
- **Forked Inspiration:** [ehraz786/tgdl](https://github.com/ehraz786/tgdl)  

> [!NOTE]
> Special thanks to the developers of **Pyrogram**, **aria2**, **yt‑dlp**, and **Google Colab** for making this possible.
> This project is a community‑driven enhancement of the original Telegram Leecher.

---

## 📄 **License & Disclaimer**

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

> [!IMPORTANT]  
> Using this bot for downloading copyrighted content without permission may violate laws.  
> **You should NOT use it in a way that goes against Google Colab's Terms of Service**, such as running torrents, hosting web services, or engaging in bulk compute.  
> The developer assumes no liability for misuse.

---

## **Updates & Support**

<div align="center">
  
##### **Updates Channel**

<a href="https://t.me/MaximXBots"><img src="https://telegramcard.vercel.app/?username=MaximXBots&theme=light" alt="Channel"></a>

##### **Support Group**

<a href="https://t.me/MaximXGroup"><img src="https://telegramcard.vercel.app/?username=MaximxGroup&theme=light&theme=light" alt="Group"></a>

</div>

## 💕 Loved My Work?

🚨 [Follow me on GitHub](https://github.com/Shineii86)

⭐ [Give a star to this project](https://github.com/Shineii86/LeechBot)

<div align="center">

<a href="https://github.com/Shineii86/LeechBot">
<img src="https://github.com/Shineii86/AniPay/blob/main/Source/Banner6.png" alt="Banner">
</a>
  
  *For inquiries or collaborations*
     
[![Telegram Badge](https://img.shields.io/badge/-Telegram-2CA5E0?style=flat&logo=Telegram&logoColor=white)](https://telegram.me/Shineii86 "Contact on Telegram")
[![Instagram Badge](https://img.shields.io/badge/-Instagram-C13584?style=flat&logo=Instagram&logoColor=white)](https://instagram.com/ikx7.a "Follow on Instagram")
[![Pinterest Badge](https://img.shields.io/badge/-Pinterest-E60023?style=flat&logo=Pinterest&logoColor=white)](https://pinterest.com/ikx7a "Follow on Pinterest")
[![Gmail Badge](https://img.shields.io/badge/-Gmail-D14836?style=flat&logo=Gmail&logoColor=white)](mailto:ikx7a@hotmail.com "Send an Email")

  <sup><b>Copyright © 2026 <a href="https://telegram.me/Shineii86">Shinei Nouzen</a> All Rights Reserved</b></sup>

![Last Commit](https://img.shields.io/github/last-commit/Shineii86/LeechBot?style=for-the-badge)

<sub>Pull Requests And Contributions Are Warmly Welcomed</sub>

</div>
