<div align="center">

<!-- Animated Logo Banner -->
<img src="https://capsule-render.vercel.app/api?type=waving&height=300&color=gradient&text=𝗟𝗲𝗲𝗰𝗵%20𝗕𝗼𝘁&fontAlignY=30&fontSize=100&desc=𝖠𝖽𝗏𝖺𝗇𝖼𝖾𝖽%20𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗆%20𝖥𝗂𝗅𝖾%20𝖳𝗋𝖺𝗇𝗌𝗅𝗈𝖺𝖽𝖾𝗋&descSize=30" />

<p align="center">
  <strong>A Pyrogram‑based Telegram Bot to transfer files / folders to Telegram and Google Drive, powered by Google Colab</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-3.1.21-8B5CF6?style=for-the-badge&logo=semver&logoColor=white" alt="Version" />
  <img src="https://img.shields.io/badge/License-MIT-06B6D4?style=for-the-badge&logo=opensourceinitiative&logoColor=white" alt="License" />

![Last Commit](https://img.shields.io/github/last-commit/Shineii86/LeechBot?style=for-the-badge)
![Repo Size](https://img.shields.io/github/repo-size/Shineii86/LeechBot?style=for-the-badge)
[![GitHub Stars](https://img.shields.io/github/stars/Shineii86/LeechBot?style=for-the-badge)](https://github.com/Shineii86/LeechBot/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/Shineii86/LeechBot?style=for-the-badge)](https://github.com/Shineii86/LeechBot/fork)

</div>

---

## 📑 **Table of Contents**

- [📖 Complete User Guide](GUIDE.md) ← **Start here if you're new**
- [🗺️ Roadmap](ROADMAP.md) — what's planned
- [✨ What's New?](#-whats-new-in-v3121)
- [🚀 Features](#-features)
- [🔗 Supported Sources](#-supported-sources)
- [👤 UserBot — Private Channels](#-userbot--private-channels)
- [🌐 Web Dashboard](#-web-dashboard)
- [📥 How to Deploy](#-how-to-deploy)
- [📋 Commands](#-commands)
- [🛠️ Technology Stack](#️-technology-stack)
- [🙏 Acknowledgements](#-acknowledgements)
- [📄 License](#-license)
- [🫂 Updates & Support](#-updates--support)
- [👤 Developer & Credits](#-developer--credits)

---

## ✨ What's New in v3.1.21

### 🎬 New Commands — `/formats` and `/preview`
- **`/formats <url>`** — list all available yt-dlp formats (resolution / codec / size) for a video URL before downloading. Picks up the previously-unused `ytdl.list_formats()` helper.
- **`/preview <url>`** — dry-run a gallery URL with `gallery-dl -K` to see what would be downloaded, without actually downloading. Picks up the previously-unused `gallery.list_gallery_content()` helper.

### 🛠️ Multi-link URL Extraction
- Forwarded messages with multiple URLs on the same line (e.g. `https://a.com https://b.com`) or scattered through paragraphs now process **all** of them in series, not just the first. Wires up the previously-unused `helper.extract_links()` helper.

### 📊 `/stats` Now Shows Lifetime Totals
- `/stats` now shows lifetime task counts (total tasks, total bytes downloaded, total bytes uploaded, failed tasks, uptime) in addition to the existing system resource info (CPU, RAM, disk).

### 🧵 YTDL Thread-Safety Hardening
- The yt-dlp progress hook and logger no longer mutate global `YTDL` state directly from the worker thread. Every update is marshaled through `loop.call_soon_threadsafe` so the asyncio event loop is the single owner of `YTDL.*` attributes. Removes a subtle data-race window under PyPy / no-GIL CPython.

### 🔴 Critical Bug Fix — `/stats` Always Showed 0 Bytes (3.1.20)
- The cumulative byte counters (`BotStats.total_downloaded`, `total_uploaded`) were reading `Transfer.down_bytes[0]` which was always `0` because per-file sizes are `.append()`-ed to the list, not stored at index 0. Fixed by using `sum(Transfer.down_bytes)`. Now lifetime totals actually accumulate.

### 🛡️ Resource-Leak Fix — `/cancel` Mid-ffmpeg (3.1.20)
- Hitting `/cancel` while ffmpeg/zip/7z was running would orphan the subprocess. Added a `_terminate_subprocess()` helper (SIGTERM → 5s wait → SIGKILL) and wrapped all 4 `subprocess.Popen()` polling loops in `try/except CancelledError` cleanup.

### 📋 Earlier Releases
- **3.1.17** — YouTube thumbnail not showing on video uploads
- **3.1.18** — `NameError: 'os' is not defined` latent bug in `task_manager.py` (would have crashed the first task)
- **3.1.19** — Comprehensive `AUDIT_REPORT.md` (1 critical bug, 8 dead functions, 1 thread-safety concern, 4 resource-leak risks)
- **3.1.15** — Bot was completely unresponsive (`__main__.py` never imported handler modules) + 18 other fixes

> 📋 **Full history:** [CHANGELOG.md](CHANGELOG.md)

---

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 📤 **Telegram Upload** | Upload any file/folder to Telegram (video, audio, document, photo) |
| ☁️ **Google Drive Mirror** | Mirror downloads directly to Google Drive |
| 👤 **UserBot Session** | Access private channels via your own Telegram account |
| 📡 **HLS/DASH Streams** | Download `.m3u8` and `.mpd` streaming URLs |
| 📁 **Directory Leech** | Upload entire local directories recursively |
| 🎬 **Video Converter** | Convert to MP4/MKV with FFmpeg (GPU accelerated) |
| ✂️ **Smart Splitting** | Split files >2GB into chunks |
| 🗜️ **Archive Handling** | Create/extract ZIP, RAR, 7z, TAR, GZ with password support |
| 🖼️ **Auto Thumbnail** | Generate from video or use custom images |
| 📸 **Photo Upload Mode** | Group (batch of 10) or Single (one by one) |
| 📋 **Download Queue** | Queue multiple downloads, process sequentially |
| 🎬 **Format Selection** | Choose YT-DLP quality per-session |
| ⚡ **Bandwidth Control** | Limit download speed |
| 📢 **Broadcast** | Send files to multiple chats |
| 👥 **Multi-User** | Admin panel to allow/deny users |
| 🔄 **Auto-Retry** | Automatic retry on download failures |
| 🔒 **Password Protection** | ZIP/unzip passwords |
| 🏷️ **Custom Filename** | `/setname` or inline `[name]` syntax |
| ⏳ **Auto-Delete** | Configurable auto-delete for bot messages |
| 🎬 **YouTube PO Tokens** | Auto-generated — no manual cookie setup |
| 📸 **Photo Galleries** | Instagram, Twitter, Pinterest, Pixiv via gallery-dl |
| 🌐 **Web Dashboard** | Real-time browser monitoring and control |

---

## 🔗 Supported Sources

### 📥 Download From

| Source | Method | Status |
|--------|--------|--------|
| Direct HTTP/HTTPS/FTP | aria2c | ✅ Full — resume supported |
| Torrent / Magnet | libtorrent | ✅ Full — DHT, resume, progress |
| HLS / DASH (`.m3u8` / `.mpd`) | yt-dlp | ✅ Full — live + VOD |
| YouTube, Facebook, Instagram | yt-dlp | ✅ 2000+ sites |
| Kick, Rumble, Bilibili, Twitch | yt-dlp | ✅ |
| SoundCloud, Spotify, Bandcamp | yt-dlp | ✅ |
| Crunchyroll, TubiTV, Odysee | yt-dlp | ✅ |
| Reddit, VK, Dailymotion, Vimeo | yt-dlp | ✅ |
| Google Drive | GDrive API | ✅ Files, folders, shared drives |
| Telegram (public + private) | Pyrogram | ✅ With UserBot support |
| Instagram, Twitter, Pinterest | gallery-dl | ✅ 100+ gallery sites |
| Pixiv, DeviantArt, ArtStation | gallery-dl | ✅ Art galleries |
| Mega.nz | megatools | ✅ Files + folders, async |
| Terabox | API | ✅ |
| Pixeldrain | API | ✅ Single files + lists |
| Mediafire | Scraping | ✅ Auto-extracted direct links |
| GoFile.io | API | ✅ **NEW** — folders, multi-file |
| Bunkr (la/ru/si/is) | Scraping | ✅ **NEW** — albums + single |
| Catbox.moe / Litterbox | Direct | ✅ **NEW** — direct download |
| StreamTape | Extraction | ✅ **NEW** — video links |

### 📤 Upload To

| Destination | Method |
|-------------|--------|
| Telegram | Pyrogram (single + batch photo) |
| Google Drive | GDrive API |

---

## 👤 UserBot — Private Channels

Download from private Telegram channels/groups **without adding the bot as a member**.

```
Normal:  Bot → Private Channel → ❌ not a member
UserBot: Bot → Your Account → Private Channel → ✅ you're a member
```

### Setup (one-time)
1. Send `/userbot` to the bot
2. Enter your phone number (`+1234567890`)
3. Enter the OTP code from Telegram
4. Enter 2FA password if enabled
5. Done! Session saved locally

### Commands
| Command | Description |
|---------|-------------|
| `/userbot` | Start login flow |
| `/userbot_status` | Check session status |
| `/userbot_logout` | Disconnect and remove session |

📖 [Full UserBot guide](GUIDE.md#-userbot-setup-for-private-channels)

---

## 🌐 Web Dashboard

Real-time browser dashboard runs alongside the bot on port `8080`.

| Feature | Description |
|---------|-------------|
| 📊 Status Cards | Idle/active, downloads, uploads, tasks |
| 🔄 Active Task | Mode, engine, progress, speed, ETA, total size |
| 📋 Queue | View pending, clear queue |
| 📁 Files | Recent uploads list |
| ⚙️ Settings | Current bot configuration |
| 💻 System | CPU, RAM, disk usage |
| 📖 Commands | Quick reference for all 28 commands |
| 🟢 WebSocket | Real-time updates every 3s |

```bash
# Access
http://your-server:8080/dashboard

# API
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8080/api/status
```

📖 [Full dashboard guide](GUIDE.md#-web-dashboard)

---

## 📥 How to Deploy

### 1️⃣ One‑Click Colab

<a href="https://colab.research.google.com/github/Shineii86/LeechBot/blob/main/notebooks/LeechBot.ipynb">
  <img src="https://user-images.githubusercontent.com/125879861/255389999-a0d261cf-893a-46a7-9a3d-2bb52811b997.png" alt="Open In Colab" width="200px">
</a>

1. Open notebook → fill credentials (or use Colab Secrets)
2. **Runtime → Run all** — bot starts automatically
3. Send `/start` on Telegram

### 2️⃣ Docker

```bash
git clone https://github.com/Shineii86/LeechBot.git
cd LeechBot

# Create .env with your credentials
cp .env.example .env
nano .env

# Build and run
docker compose up -d
```

### 3️⃣ Railway (One-Click)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/Shineii86/LeechBot)

1. Click the button above → set environment variables → deploy
2. Bot starts automatically, web dashboard on port 8080

### 4️⃣ Fly.io

```bash
# Install flyctl: https://fly.io/docs/hands-on/install-flyctl/
fly launch --copy-config --name leechbot
fly secrets set API_ID=xxx API_HASH=xxx BOT_TOKEN=xxx OWNER_ID=xxx DUMP_ID=xxx
fly scale memory 512
fly deploy
```

### 5️⃣ Render

1. Push repo to GitHub
2. Go to [render.com](https://render.com) → New → Blueprint Instance
3. Select your repo → it auto-detects `render.yaml`
4. Add environment variables → Deploy

### 6️⃣ VPS / Local

```bash
git clone https://github.com/Shineii86/LeechBot.git
cd LeechBot
pip install -r requirements.txt

# Create .env with your credentials
cp .env.example .env
nano .env

python3 -m leechbot
```

### 7️⃣ Oracle Cloud Free Tier (Free Forever)

1. Create a free ARM instance at [cloud.oracle.com](https://cloud.oracle.com) (4 cores, 24GB RAM)
2. SSH into the instance
3. Follow the **VPS / Local** steps above
4. Run with `screen` or `tmux` to keep it alive

### 8️⃣ Heroku

```bash
heroku create leechbot
heroku buildpacks:add heroku/python
heroku config:set API_ID=xxx API_HASH=xxx BOT_TOKEN=xxx OWNER_ID=xxx DUMP_ID=xxx
git push heroku main
heroku ps:scale worker=1
```

### System Dependencies

```bash
# Ubuntu/Debian
sudo apt install -y ffmpeg aria2 p7zip-full unrar unzip python3-libtorrent megatools

# macOS
brew install ffmpeg aria2 p7zip megatools

# Conda (libtorrent)
conda install -c conda-forge libtorrent
```

> 💡 Docker users: all dependencies (including libtorrent and megatools) are included in the image — no manual install needed.

📖 [Full setup guide](GUIDE.md#-installation)

---

## 📋 Commands

### 📥 Downloads
| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/tupload` | Leech to Telegram |
| `/gdupload` | Mirror to Google Drive |
| `/ytupload` | YouTube / yt-dlp |
| `/glupload` | Photo galleries |
| `/drupload` | Local directory |
| `/formats <url>` | List available formats for a video URL |
| `/preview <url>` | Dry-run a gallery URL to preview its content |

### 👤 UserBot
| Command | Description |
|---------|-------------|
| `/userbot` | Login for private channel access |
| `/userbot_status` | Check session |
| `/userbot_logout` | Disconnect |

### ⚙️ Settings
| Command | Description |
|---------|-------------|
| `/settings` | Bot preferences |
| `/setname` | Custom filename |
| `/zipaswd` | Zip password |
| `/unzipaswd` | Extract password |
| `/format` | YT-DLP quality |
| `/speed` | Bandwidth limit |

### 📋 Control
| Command | Description |
|---------|-------------|
| `/queue` | View queue |
| `/cancel` | Cancel task |
| `/cancel_all` | Cancel + clear |

### 🛠️ Admin
| Command | Description |
|---------|-------------|
| `/admin` | Manage users |
| `/stats` | Bot & system statistics (lifetime totals) |
| `/broadcast` | Send to multiple chats |
| `/update` | Check for updates |
| `/cookies` | YouTube auth status |
| `/setcookies` | Upload cookies.txt |
| `/clearcookies` | Delete cookies |
| `/help` | All commands |

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Framework | [Pyrogram](https://docs.pyrogram.org/) 2.0.106 |
| Downloads | [aria2c](https://aria2.github.io/) + [yt-dlp](https://github.com/yt-dlp/yt-dlp) + [gallery-dl](https://github.com/mikf/gallery-dl) |
| YouTube Auth | [bgutil-ytdlp-pot-provider](https://github.com/Brainicism/bgutil-ytdlp-pot-provider) |
| Video Processing | FFmpeg, MoviePy, GPUtil |
| Archives | 7z, unrar, zip, tar |
| Cloud | Google Colab / VPS |
| Dashboard | aiohttp (REST + WebSocket) + Tailwind CSS |
| Google Drive | google-api-python-client |
| Images | PIL / Pillow |

### 📁 Project Structure

```
LeechBot/
├── main.py                  # Colab deployer
├── config.py                # Configuration (env vars, paths)
├── requirements.txt         # Dependencies
├── AGENTS.md                # AI agent instructions
├── ARCHITECTURE.md          # Technical deep dive
├── CONTRIBUTING.md          # Contribution guide
├── GUIDE.md                 # Complete user guide
├── CHANGELOG.md             # Version history
├── .github/
│   └── copilot-instructions.md
├── .cursorrules / .clinerules / .windsurfrules
├── pyproject.toml           # Tooling config
├── .editorconfig            # Formatting rules
├── leechbot/
│   ├── __init__.py          # Pyrogram client
│   ├── __main__.py          # Entry point
│   ├── commands.py          # /command handlers (28 commands)
│   ├── callbacks.py         # Button callbacks
│   ├── handlers.py          # Message handlers
│   ├── userbot.py           # UserBot session manager
│   ├── debug.py             # Error reporting
│   ├── updater.py           # Auto-update
│   ├── downloader/
│   │   ├── aria2.py         # HTTP/FTP downloads
│   │   ├── torrent.py       # Magnet/torrent (libtorrent)
│   │   ├── ytdl.py          # YouTube, 2000+ sites
│   │   ├── gallery.py       # Photo galleries (100+ sites)
│   │   ├── gdrive.py        # Google Drive
│   │   ├── telegram.py      # Telegram file downloads
│   │   ├── mega.py          # Mega.nz
│   │   ├── terabox.py       # Terabox
│   │   ├── pixeldrain.py    # Pixeldrain
│   │   ├── mediafire.py     # Mediafire
│   │   ├── gofile.py        # GoFile.io        ← NEW
│   │   ├── bunkr.py         # Bunkr            ← NEW
│   │   ├── catbox.py        # Catbox.moe       ← NEW
│   │   ├── streamtape.py    # StreamTape       ← NEW
│   │   └── manager.py       # Download router
│   ├── uploader/
│   │   └── telegram.py      # Upload with progress
│   ├── web/
│   │   └── server.py        # Dashboard API + WebSocket
│   ├── utility/
│   │   ├── variables.py     # Global state
│   │   ├── handler.py       # Task handlers
│   │   ├── helper.py        # UI, links, formatting
│   │   ├── converters.py    # Video/archive conversion
│   │   ├── task_manager.py  # Task orchestrator
│   │   └── style.py         # Text styling
│   └── public/
│       └── index.html        # Dashboard frontend
└── notebooks/
    └── LeechBot.ipynb        # Colab notebook
```

---

## 🙏 Acknowledgements

- **Original Base:** [XronTrix10/Telegram‑Leecher](https://github.com/XronTrix10/Telegram-Leecher)
- **Minor Fixes:** [kjeymax/Telegram‑Leecher](https://github.com/kjeymax/Telegram-Leecher)
- **Forked Inspiration:** [ehraz786/tgdl](https://github.com/ehraz786/tgdl)

> [!NOTE]
> Special thanks to **Pyrogram**, **aria2**, **yt-dlp**, **gallery-dl**, and **Google Colab**.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

> [!IMPORTANT]
> Using this bot for downloading copyrighted content without permission may violate laws.
> Do not violate Google Colab's Terms of Service.
> The developer assumes no liability for misuse.

---

## 🫂 Updates & Support

<div align="center">

##### Updates Channel
<a href="https://t.me/MaximXBots"><img src="https://telegramcard.vercel.app/?username=MaximXBots&theme=light" alt="Channel"></a>

##### Support Group
<a href="https://t.me/MaximXGroup"><img src="https://telegramcard.vercel.app/?username=MaximxGroup&theme=light" alt="Group"></a>

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
