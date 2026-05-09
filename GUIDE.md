# 📖 LeechBot — Complete User Guide

Everything you need to set up, configure, and use LeechBot from scratch.

---

## 📋 Table of Contents

- [Prerequisites](#-prerequisites)
- [Getting Credentials](#-getting-credentials)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Bot](#-running-the-bot)
- [Commands Reference](#-commands-reference)
- [Settings Menu](#-settings-menu)
- [Supported Sites](#-supported-sites)
- [Google Drive Setup](#-google-drive-setup)
- [YouTube Authentication](#-youtube-authentication)
- [Troubleshooting](#-troubleshooting)

---

## 🔧 Prerequisites

Before you start, make sure you have:

| Requirement | Why You Need It |
|-------------|----------------|
| **Python 3.10+** | Runtime environment |
| **Telegram Account** | To create a bot and get API keys |
| **A Server or VPS** | To run the bot 24/7 (or use Google Colab) |
| **aria2** | HTTP/FTP/torrent downloader |
| **ffmpeg** | Video/audio processing |
| **7zip / p7zip** | Archive handling |
| **unrar** | RAR extraction |
| **megatools** | Mega.nz downloads |

### System Dependencies (Ubuntu/Debian)

```bash
sudo apt update && sudo apt install -y ffmpeg aria2 p7zip-full unzip python3 python3-pip
```

### System Dependencies (Arch)

```bash
sudo pacman -S ffmpeg aria2 p7zip unzip python python-pip
```

### System Dependencies (macOS)

```bash
brew install ffmpeg aria2 p7zip python
```

---

## 🔐 Getting Credentials

You need **5 values** to run the bot. Here's how to get each one:

### 1. API_ID & API_HASH

1. Go to [https://my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Click **"API development tools"**
4. Fill in the form (App title can be anything, e.g., "My LeechBot")
5. Click **"Create Application"**
6. Copy `api_id` (number) and `api_hash` (string)

> ⚠️ **Keep these secret.** Anyone with your API keys can access your Telegram account.

### 2. BOT_TOKEN

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Choose a display name for your bot (e.g., "My Leech Bot")
4. Choose a username ending in `bot` (e.g., `my_leech_bot`)
5. BotFather will send you a token like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
6. Copy the entire token

> 💡 You can create multiple bots with BotFather. Use `/mybots` to manage them.

### 3. OWNER_ID

This is **your personal Telegram user ID** (not your phone number).

1. Open Telegram and search for [@userinfobot](https://t.me/userinfobot)
2. Send `/start`
3. It will reply with your numeric ID (e.g., `123456789`)

### 4. DUMP_ID

This is a **Telegram channel or group** where the bot sends download logs and task history.

1. Create a new Telegram channel (or use an existing one)
2. **Make the bot an admin** of that channel (it needs to send messages)
3. Get the channel ID:
   - Forward any message from the channel to [@userinfobot](https://t.me/userinfobot)
   - It will show the channel ID (e.g., `-1001234567890`)
   - Channel IDs always start with `-100`

> 💡 **Private channels work fine.** The bot just needs to be an admin with "Post Messages" permission.

---

## 📦 Installation

### Option A: Standard Setup

```bash
# Clone the repository
git clone https://github.com/Shineii86/LeechBot.git
cd LeechBot

# Install Python dependencies
pip install -r requirements.txt

# Create your config file
cp .env.example .env
```

Now edit `.env` with your credentials (see [Configuration](#-configuration)).

### Option B: Google Colab (No Server Needed)

1. Open `notebooks/LeechBot.ipynb` in Google Colab
2. Add your credentials to Colab Secrets (recommended) or fill in the form
3. Click **Runtime → Run all**

### Option C: Docker (Coming Soon)

Docker support is planned for a future release.

---

## ⚙️ Configuration

Edit the `.env` file in the project root. Here's every option explained:

### Required Settings

```env
# Your Telegram API credentials (from my.telegram.org)
API_ID=12345
API_HASH=your_api_hash_here

# Your bot token (from @BotFather)
BOT_TOKEN=your_bot_token_here

# Your personal Telegram user ID
OWNER_ID=123456789

# Channel ID for logs and task history (bot must be admin)
DUMP_ID=-1001234567890
```

### Optional Settings

```env
# --- Paths ---
# Base directory for all bot files (downloads, temp, thumbnails)
# Default: /tmp/leechbot (auto-created)
LEECHBOT_BASE_DIR=/tmp/leechbot

# --- Download Settings ---
# How many files to download at once (default: 3)
MAX_CONCURRENT_DOWNLOADS=3

# How many times to retry a failed download (default: 3)
AUTO_RETRY_COUNT=3

# Upload mode: "media" (streaming, plays in Telegram) or "document" (raw file)
DEFAULT_UPLOAD_MODE=media

# Enable torrent/magnet link support (default: false)
# ⚠️ May violate ToS on some hosting providers
ENABLE_TORRENTS=false

# Speed limit for downloads (empty = unlimited)
# Examples: "10M" (10 MB/s), "500K" (500 KB/s)
BANDWIDTH_LIMIT=

# --- Multi-User Support ---
# Comma-separated Telegram user IDs (OWNER_ID is always allowed)
# Example: ALLOWED_USERS=123456789,987654321
ALLOWED_USERS=

# --- YouTube Cookies (optional, for bot detection issues) ---
# Option 1: Path to cookies.txt file
# YTDL_COOKIES_FILE=/path/to/cookies.txt

# Option 2: Extract from browser directly
# Supported: chrome, firefox, edge, brave, opera, safari
# YTDL_BROWSER_COOKIES=chrome

# --- Google Drive (optional) ---
# Set to "true" to enable Google Drive mirror
GDRIVE_ENABLED=false

# Path to Google Drive token file
# Default: <BASE_DIR>/token.pickle
TOKEN_PICKLE_PATH=
```

---

## 🚀 Running the Bot

### Start the bot

```bash
cd LeechBot
python3 -m leechbot
```

### First run

On first start:
1. The bot creates a session file in `sessions/` directory
2. It resolves your DUMP_ID and OWNER_ID peers
3. You'll see "LeechBot started successfully" in the console
4. Send `/start` to your bot in Telegram

### Keep it running

**Option 1: Screen (simple)**
```bash
screen -S leechbot
python3 -m leechbot
# Press Ctrl+A, then D to detach
# Re-attach with: screen -r leechbot
```

**Option 2: tmux**
```bash
tmux new -s leechbot
python3 -m leechbot
# Press Ctrl+B, then D to detach
# Re-attach with: tmux attach -t leechbot
```

**Option 3: systemd (recommended for VPS)**

Create `/etc/systemd/system/leechbot.service`:
```ini
[Unit]
Description=LeechBot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/LeechBot
ExecStart=/usr/bin/python3 -m leechbot
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable leechbot
sudo systemctl start leechbot

# Check status
sudo systemctl status leechbot

# View logs
sudo journalctl -u leechbot -f
```

---

## 📥 Commands Reference

### Download Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Show welcome message and main menu | `/start` |
| `/tupload` | Download files and upload to Telegram | `/tupload` → send link(s) |
| `/gdupload` | Download files and mirror to Google Drive | `/gdupload` → send link(s) |
| `/drupload` | Upload a local directory to Telegram | `/drupload` → send path |
| `/ytupload` | Download using YT-DLP (YouTube, etc.) | `/ytupload` → send URL |
| `/glupload` | Download image galleries via gallery-dl | `/glupload` → send URL |

### Queue & Control

| Command | Description |
|---------|-------------|
| `/queue` | View download queue and session stats |
| `/cancel` | Cancel the current running task |
| `/cancel_all` | Cancel task and clear the queue |

### Settings

| Command | Description |
|---------|-------------|
| `/settings` | Open interactive settings menu |
| `/setname <name>` | Set custom filename for next download |
| `/zipaswd <pass>` | Set password for zip compression |
| `/unzipaswd <pass>` | Set password for extraction |
| `/format` | Choose YT-DLP quality (1080p/720p/480p/audio) |
| `/speed` | Set bandwidth limit |

### Authentication

| Command | Description |
|---------|-------------|
| `/cookies` | Check YouTube authentication status |
| `/setcookies` | Upload a cookies.txt file |
| `/clearcookies` | Delete stored cookies file |

### Admin

| Command | Description |
|---------|-------------|
| `/admin` | Manage allowed users |
| `/admin add <id>` | Allow a user |
| `/admin remove <id>` | Remove a user |
| `/admin list` | Show allowed users |
| `/broadcast <ids>` | Send last file to multiple chats |
| `/stats` | Show system statistics |
| `/update` | Check for bot updates |
| `/help` | Show help menu |

---

## ⚙️ Settings Menu

Access via `/settings`. Here's what each option does:

### Upload Mode
- **Media** — Files stream inline (videos play in chat, photos display)
- **Document** — Files sent as raw downloads

### Video Settings
- **Split** — Split large videos into parts (Telegram 2GB limit)
- **Zip** — Archive videos instead of splitting
- **Convert** — Convert videos to MP4/MKV before upload
- **Quality** — High (slow, better quality) or Low (fast, smaller size)

### Caption
Choose the caption style for uploaded files:
- **Code** — Monospace `<code>filename</code>`
- **Bold** — `**filename**`
- **Italic** — `*filename*`
- **Underline** — `__filename__`
- **Regular** — Plain text

### Prefix / Suffix
Add custom text before/after the filename in captions.
Example: Set prefix to `🎬` → caption becomes `🎬 filename.mp4`

### Thumbnail
- Send any photo to the bot to set it as the default thumbnail
- Thumbnails apply to video and document uploads
- Use "Delete Thumbnail" to remove it

### Photo Upload Mode
- **Group** — Sends photos in batches of 10 (faster, uses media groups)
- **Single** — Sends photos one by one (slower, individual messages)

### Auto-Delete
- Automatically deletes the bot's status messages after a delay
- Set delay between 5-300 seconds
- Useful for keeping chats clean

---

## 🌐 Supported Sites

### Direct Downloads (aria2c)
Any HTTP/FTP link works. Examples:
- Direct file URLs: `https://example.com/file.zip`
- FTP links: `ftp://files.example.com/data.tar.gz`
- Torrent files and magnet links (if `ENABLE_TORRENTS=true`)

### Video Platforms (YT-DLP)
2000+ sites including:
- YouTube (videos, shorts, playlists)
- Facebook, Instagram, Twitter/X
- TikTok, Reddit, Vimeo
- Twitch, Dailymotion, Streamable
- And thousands more → [full list](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

### File Hosters
| Site | Notes |
|------|-------|
| Google Drive | Files and folders, shared links |
| Mega.nz | Requires `megatools` installed |
| Terabox | Direct links |
| Pixeldrain | Single files and lists |
| Mediafire | Automatic direct link extraction |

### Photo Galleries (gallery-dl)
| Site | Content |
|------|---------|
| Instagram | Posts, carousels, profiles |
| Twitter / X | Timelines, likes, bookmarks |
| Pinterest | Boards, pins |
| Pixiv | Artworks, user galleries |
| DeviantArt | Art galleries |
| ArtStation | Portfolios |
| Flickr | Albums, photostreams |
| Reddit | Image subreddits |
| Tumblr | Blogs, tags |
| TikTok | Image posts |
| Bluesky | Posts with images |
| Danbooru, Gelbooru, Yande.re | Anime image boards |
| Furaffinity, Weasyl | Art communities |
| 100+ more | [full list](https://github.com/mikf/gallery-dl/blob/master/docs/supportedsites.md) |

### Telegram
- Any Telegram message link (`https://t.me/c/...`)
- Bot must be a member of the source chat/channel

---

## ☁️ Google Drive Setup

To mirror files to Google Drive:

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the **Google Drive API**
4. Create **OAuth 2.0 credentials** (Desktop app)
5. Download the `credentials.json` file

### Step 2: Generate Token

Run this once to generate `token.pickle`:

```python
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle, os

SCOPES = ['https://www.googleapis.com/auth/drive']

flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

with open('token.pickle', 'wb') as f:
    pickle.dump(creds, f)
```

### Step 3: Configure

```env
GDRIVE_ENABLED=true
TOKEN_PICKLE_PATH=/path/to/token.pickle
```

### Step 4: Mount in Colab (if using Colab)

Check the "Mount Google Drive" option in the notebook, or mount manually:
```python
from google.colab import drive
drive.mount('/content/drive')
```

---

## 🎬 YouTube Authentication

YouTube may block downloads with "Sign in to confirm you're not a bot." Here's how to fix it:

### Method 1: PO Token Plugin (Automatic)

This is already included in `requirements.txt`. No setup needed — it generates tokens automatically.

### Method 2: Cookies File (Manual Fallback)

If PO tokens stop working:

1. Install a browser extension: [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) (Chrome) or [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/) (Firefox)
2. Go to `youtube.com` (make sure you're logged in)
3. Click the extension icon → **Export** → saves `cookies.txt`
4. Upload the file to the bot:
   - Send `/setcookies`
   - Upload the `cookies.txt` file as a document

### Method 3: Browser Cookie Extraction

Set in `.env`:
```env
YTDL_BROWSER_COOKIES=chrome
```

Supported browsers: `chrome`, `firefox`, `edge`, `brave`, `opera`, `safari`, `vivaldi`

> ⚠️ **Close the browser before running the bot** — it can't read cookies from a running browser.

### Check Status

Send `/cookies` to see which authentication method is active.

---

## ❓ Troubleshooting

### Bot doesn't respond to commands

- **Check credentials:** Make sure `API_ID`, `API_HASH`, `BOT_TOKEN`, `OWNER_ID`, and `DUMP_ID` are correct
- **Check bot is running:** Look for "LeechBot started successfully" in console
- **Check permissions:** The bot needs to be able to send messages to you and the DUMP_ID channel
- **Session file:** Delete `sessions/leechbot_session.session` and restart (forces fresh login)

### "Peer id invalid" error

- Make sure the bot is a **member** of the DUMP_ID channel/group
- Make sure the bot has **admin permissions** (at minimum: "Post Messages")
- Restart the bot — it resolves peers on startup

### YouTube downloads fail

- Run `/cookies` to check authentication status
- Try uploading a `cookies.txt` file via `/setcookies`
- Update yt-dlp: `pip install -U yt-dlp`

### "Flood wait" errors

- Telegram rate-limits bots that send too many messages too fast
- The bot handles this automatically (waits and retries)
- Reduce `MAX_CONCURRENT_DOWNLOADS` if it happens frequently

### Google Drive upload fails

- Check that `GDRIVE_ENABLED=true` in `.env`
- Verify `token.pickle` exists and is valid
- Re-generate the token if it's expired (tokens expire after ~7 days of inactivity)

### gallery-dl unsupported URL

- Not all sites are supported. Check the [full list](https://github.com/mikf/gallery-dl/blob/master/docs/supportedsites.md)
- Manga/manhwa sites (Asura Scans, MangaDex, etc.) load images via JavaScript — gallery-dl can't handle those
- For unsupported sites, try `/tupload` with direct image URLs instead

### Upload fails with "request entity too large"

- Telegram has a **2GB file size limit**
- Enable video splitting in `/settings` → Video → Split
- Or use Document mode instead of Media mode

### Bot crashes on startup

- Check Python version: `python3 --version` (need 3.10+)
- Install missing dependencies: `pip install -r requirements.txt`
- Check the console output for specific error messages

---

## 📂 Project Structure

```
LeechBot/
├── main.py                 # Colab deployer (Google Colab only)
├── config.py               # Central configuration (loads .env)
├── requirements.txt        # Python dependencies
├── .env                    # Your configuration (create from .env.example)
├── .env.example            # Example configuration
├── CHANGELOG.md            # Version history
├── GUIDE.md                # This file
├── README.md               # Project overview
├── leechbot/
│   ├── __init__.py         # Pyrogram client setup
│   ├── __main__.py         # Entry point (run with: python3 -m leechbot)
│   ├── commands.py         # All /command handlers
│   ├── callbacks.py        # Inline keyboard callback handlers
│   ├── handlers.py         # Message handlers (URL, photo, text)
│   ├── updater.py          # Auto-update from GitHub
│   ├── debug.py            # Error reporting to Telegram
│   ├── downloader/
│   │   ├── aria2.py        # HTTP/FTP/torrent downloads
│   │   ├── gallery.py      # Photo galleries (gallery-dl)
│   │   ├── gdrive.py       # Google Drive downloads
│   │   ├── manager.py      # Download router & orchestrator
│   │   ├── mega.py         # Mega.nz downloads
│   │   ├── mediafire.py    # Mediafire downloads
│   │   ├── pixeldrain.py   # Pixeldrain downloads
│   │   ├── telegram.py     # Telegram file downloads
│   │   ├── terabox.py      # Terabox downloads
│   │   ├── ytdl.py         # YouTube/video platform downloads
│   │   └── __init__.py
│   ├── uploader/
│   │   ├── telegram.py     # Telegram uploads (single + batch)
│   │   └── __init__.py
│   └── utility/
│       ├── converters.py   # Video conversion, archive handling
│       ├── handler.py      # Task handlers (leech, zip, unzip, logs)
│       ├── helper.py       # Utilities (settings, status bar, link detection)
│       ├── style.py        # Text styling
│       ├── task_manager.py # Task scheduler & orchestrator
│       ├── variables.py    # Global state (BOT, Transfer, Queue, etc.)
│       └── __init__.py
├── notebooks/
│   └── LeechBot.ipynb      # Google Colab notebook
└── public/
    └── index.html           # Web interface placeholder
```

---

## 🤝 Credits

- **Developer:** [Shinei Nouzen](https://t.me/Shineii86)
- **GitHub:** [Shineii86/LeechBot](https://github.com/Shineii86/LeechBot)
- **Updates:** [MaximXBots](https://t.me/MaximXBots)
- **Support:** [MaximXGroup](https://t.me/MaximXGroup)

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
