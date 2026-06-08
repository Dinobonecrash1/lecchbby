# 📱 LeechBot on Termux — Complete Guide

Run LeechBot 24/7 on your Android phone via [Termux](https://termux.dev/).

> **Tested on:** Termux 0.118+ (F-Droid build, **not** Play Store), Python 3.11+, Android 10+.

> **⚠️ Play Store version is outdated and broken** — always install from [F-Droid](https://f-droid.org/en/packages/com.termux/).

---

## 📋 Table of Contents

- [Prerequisites](#-prerequisites)
- [Step 1 — Initial Termux Setup](#-step-1--initial-termux-setup)
- [Step 2 — Install System Packages](#-step-2--install-system-packages)
- [Step 3 — Clone the Repository](#-step-3--clone-the-repository)
- [Step 4 — Install Python Dependencies](#-step-4--install-python-dependencies)
- [Step 5 — Configure Credentials](#-step-5--configure-credentials)
- [Step 6 — First Run (Sanity Check)](#-step-6--first-run-sanity-check)
- [Step 7 — Keep It Running 24/7](#-step-7--keep-it-running-247)
- [Step 8 — Optional: Access Storage](#-step-8--optional-access-storage)
- [Common Issues & Fixes](#-common-issues--fixes)
- [Updating the Bot](#-updating-the-bot)
- [Uninstalling](#-uninstalling)

---

## ✅ Prerequisites

You need:

1. **Android 7.0+** phone (preferably 10+)
2. **Termux** — install from [F-Droid](https://f-droid.org/en/packages/com.termux/) (NOT Play Store)
3. **~500 MB free storage** for the bot + dependencies
4. **Telegram API credentials** — get from [my.telegram.org/apps](https://my.telegram.org/apps):
   - `API_ID` (number)
   - `API_HASH` (string)
5. **Bot token** from [@BotFather](https://t.me/BotFather)
6. Your **Telegram user ID** (message [@userinfobot](https://t.me/userinfobot))
7. A **dump channel ID** (create a private channel, add your bot as admin, the ID looks like `-100xxxxxxxxxx`)

> **Note:** Termux's `pkg` uses Ubuntu 24.04 (noble) packages on devices with Android 10+. Some packages may not be available — fallbacks are noted below.

---

## 🔧 Step 1 — Initial Termux Setup

Open Termux and run:

```bash
# Update package lists (do this ONCE after install, then once a month)
pkg update && pkg upgrade -y

# Grant storage access (so bot can save files to /sdcard if you want)
termux-setup-storage
```

The second command will pop up an Android permission dialog — **tap "Allow"**. This creates `~/storage/` with symlinks to your shared storage.

> **Skip `termux-setup-storage`** if you only want the bot to use Termux's private storage (`/data/data/com.termux/files/home/`) — it's faster and doesn't need permission.

---

## 📦 Step 2 — Install System Packages

```bash
pkg install -y python git ffmpeg aria2 p7zip unzip libffi openssl rust binutils
```

### What each package is for:

| Package | Required for |
|---------|--------------|
| `python` | Bot runtime (3.11+ recommended) |
| `git` | Clone repo + `/update` command |
| `ffmpeg` | Video conversion, thumbnails, audio extraction |
| `aria2` | Fast parallel HTTP/FTP downloads, torrent fallback |
| `p7zip` | `.7z` archive extraction |
| `unzip` | `.zip` archive extraction |
| `libffi`, `openssl` | Python `cryptography` wheels |
| `rust`, `binutils` | Compile `tgcrypto`, `cryptography`, `pillow` from source if prebuilt wheels unavailable |

### Verify installs:

```bash
python --version     # should be 3.11+
ffmpeg -version      # should print version + build info
aria2c --version     # should print 1.36+
```

> **If `ffmpeg` complains about codecs** (rare on Termux noble): `pkg install -y ffmpeg-tools`

> **If `aria2c` is missing**: download a static binary from [github.com/aria2/aria2/releases](https://github.com/aria2/aria2/releases) → `aria2-*android*` → extract → put in `~/bin/`.

---

## 📥 Step 3 — Clone the Repository

```bash
cd ~
git clone https://github.com/Shineii86/LeechBot.git
cd LeechBot
```

This creates `~/LeechBot/` with all the source code.

### Optional — pin to a specific version (recommended for stability):

```bash
cd ~/LeechBot
git tag                          # list available versions
git checkout 3.1.45              # replace with the version you want
```

Latest stable at the time of writing: **3.1.45**.

---

## 🐍 Step 4 — Install Python Dependencies

```bash
cd ~/LeechBot
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
```

### If a package fails to compile (rare):

```bash
# Make sure rust + binutils are installed (Step 2)
pip install --no-cache-dir tgcrypto pillow cryptography
```

### If you want torrent/magnet support (optional):

Termux doesn't have `apt` or `conda`, so `libtorrent` is tricky. Two options:

**Option A — Skip torrents entirely** (default — `ENABLE_TORRENTS=false` in `.env`). The bot will use `aria2c` as a fallback for magnet links.

**Option B — Build `libtorrent` from source** (advanced, ~30 min):
```bash
pkg install -y libtorrent-rasterbar
pip install python-libtorrent
```

> Note: Termux's `libtorrent-rasterbar` package may be missing on some architectures. Check availability with `pkg search libtorrent`.

### Verify everything imports:

```bash
cd ~/LeechBot
python -c "from leechbot import app; print('✓ Bot module loads OK')"
```

If this prints `✓ Bot module loads OK`, you're good. If it throws, see [Common Issues](#-common-issues--fixes) below.

---

## 🔐 Step 5 — Configure Credentials

```bash
cd ~/LeechBot
cp .env.example .env
nano .env    # or vim, whichever you prefer
```

Fill in **at minimum** these 5 required values:

```bash
API_ID=12345                                    # from my.telegram.org
API_HASH=abcdef1234567890abcdef1234567890       # from my.telegram.org
BOT_TOKEN=1234567890:AAH...                     # from @BotFather
OWNER_ID=123456789                              # your Telegram user ID
DUMP_ID=-1001234567890                          # your dump channel ID
```

### About DUMP_ID:
- Create a private Telegram channel
- Add your bot as **admin** (with "Post messages" permission)
- Forward any message from that channel to [@JsonDumpBot](https://t.me/JsonDumpBot) or [@RawDataBot](https://t.me/RawDataBot) — the `id` field is your `DUMP_ID`
- It must look like `-100xxxxxxxxxx` (13-14 digits, starts with `-100`)

### About paths:
Default base directory is `/tmp/leechbot` — this is RAM-backed (`/tmp` is `tmpfs` on most Android kernels), so files disappear on reboot. **Override it** to use Termux's persistent home:

```bash
LEECHBOT_BASE_DIR=/data/data/com.termux/files/home/leechbot_data
```

Or use shared storage (after `termux-setup-storage`):

```bash
LEECHBOT_BASE_DIR=/sdcard/leechbot_data
```

### Save and exit nano: `Ctrl+O` → `Enter` → `Ctrl+X`

---

## 🚀 Step 6 — First Run (Sanity Check)

Run in foreground first to see all startup logs:

```bash
cd ~/LeechBot
python -m leechbot
```

You should see:
```
[INFO] LeechBot starting...
[INFO] Loaded credentials from .env
[INFO] ✅ Registered 32 bot commands with Telegram
[INFO] Web server started on http://0.0.0.0:8080
[INFO] Bot is ready. Send /start in Telegram.
```

Now open Telegram → your bot → send `/start`. You should get the welcome message with inline buttons.

**Send `/ping`** — should reply with latency + uptime + version.

If both work → **bot is running correctly**. Press `Ctrl+C` to stop, then proceed to Step 7 to run it persistently.

---

## 🔁 Step 7 — Keep It Running 24/7

Termux is not a true server — Android may kill background processes. Three methods, pick one:

### Method A — `nohup` + `termux-wake-lock` (simplest)

```bash
# Prevent Android from killing Termux
termux-wake-lock

# Run bot in background, redirect output to log file
cd ~/LeechBot
nohup python -m leechbot > leechbot.log 2>&1 &

# Save the PID so you can stop it later
echo $! > leechbot.pid
```

Now you can close Termux and the bot keeps running. To check:

```bash
tail -f ~/LeechBot/leechbot.log       # live logs
kill $(cat ~/LeechBot/leechbot.pid)   # stop the bot
```

### Method B — `tmux` (recommended for active debugging)

```bash
pkg install -y tmux
tmux new -s leechbot
cd ~/LeechBot
python -m leechbot
```

Press **`Ctrl+B` then `D`** to detach. The session keeps running in the background. Re-attach with:

```bash
tmux attach -t leechbot
```

### Method C — `screen` (alternative to tmux)

```bash
pkg install -y screen
screen -S leechbot
cd ~/LeechBot
python -m leechbot
```

Detach: **`Ctrl+A` then `D`**. Re-attach: `screen -r leechbot`.

### 🔋 Battery optimization — IMPORTANT

Android aggressively kills apps to save battery. To prevent this:

1. **Termux → Long-press app icon → App Info → Battery → Unrestricted**
2. **Disable battery optimization** (Settings → Apps → Termux → Battery)
3. **Disable "Pause app activity if unused"** in developer options
4. **Lock Termux in Recents** (swipe down on the card → lock icon)

Without these, the bot will be killed after 5-30 minutes of screen-off.

### 📱 Termux:Boot (start bot on phone boot)

Install the [Termux:Boot](https://f-droid.org/en/packages/com.termux.boot/) add-on, then:

```bash
mkdir -p ~/.termux/boot
nano ~/.termux/boot/start-leechbot.sh
```

Paste:

```bash
#!/data/data/com.termux/files/usr/bin/sh
termux-wake-lock
cd ~/LeechBot
nohup python -m leechbot > ~/LeechBot/leechbot.log 2>&1 &
```

Save, then:

```bash
chmod +x ~/.termux/boot/start-leechbot.sh
```

Now the bot starts automatically every time your phone boots.

---

## 📂 Step 8 — Optional: Access Storage

If you ran `termux-setup-storage` in Step 1, you can access your phone's shared storage:

| Path | Maps to |
|------|---------|
| `~/storage/shared/` | `/sdcard/` (internal storage root) |
| `~/storage/downloads/` | `/sdcard/Download/` |
| `~/storage/dcim/` | `/sdcard/DCIM/` (camera photos) |
| `~/storage/movies/` | `/sdcard/Movies/` |

To make the bot save downloads to your phone's visible storage, set in `.env`:

```bash
LEECHBOT_BASE_DIR=/sdcard/leechbot_data
```

> **Note:** Files under `/sdcard/` are visible to other apps (file managers, gallery). Files under `/data/data/com.termux/files/home/` are private to Termux.

---

## 🧪 Running Offline Tests (no bot credentials needed)

Before starting the bot, run the diagnostic test suite to catch routing/parser bugs:

```bash
cd ~/LeechBot
python tests/test_diagnostics.py
```

**What it tests** (35+ checks, runs in ~2 seconds):

| # | Section | What it verifies |
|---|---------|------------------|
| 1 | Telegram link parser | `t.me/USERNAME/MSG_ID` (public) AND `t.me/c/CHAT/MSG_ID` (private) extract correctly |
| 2 | Thumbnail None-safety | `os.path.exists(None)` is safely short-circuited |
| 3 | All `is_*` helpers | YouTube, GDrive, Mega, Terabox, Pixeldrain, etc. all detect correctly |
| 4 | Command consistency | `# of handlers == # of registered BotCommand` (currently 32 each) |
| 7 | Version string | `VERSION` in config.py is valid semver |
| 8 | Python syntax | All 38 `.py` files parse without errors |

**Expected output:**
```
Results: 35/35 passed, 0 failed
✓ All checks passed.
```

If any check fails, the suite prints the exact file + line + expected vs actual — no need to read the code yourself.

**Verbose mode** (prints every individual Python file syntax check):
```bash
python tests/test_diagnostics.py --verbose
```

**Run before every `/update`** — catches regressions in 2 seconds. Pure offline, no API calls, no bot token, no network.

---

## 🛠 Common Issues & Fixes
### ❌ `ModuleNotFoundError: No module named 'tgcrypto'`

```bash
pkg install -y rust binutils libffi openssl
pip install --no-cache-dir tgcrypto
```

### ❌ `ffmpeg: command not found`

```bash
pkg install -y ffmpeg
# verify
which ffmpeg
```

### ❌ `aria2c: command not found`

```bash
pkg install -y aria2
# or use static binary from github.com/aria2/aria2/releases
```

### ❌ `libtorrent` import fails

Either:
- Build from source: `pkg install -y libtorrent-rasterbar && pip install python-libtorrent`

### ❌ Bot stops after closing Termux

- Run with `nohup ... &` or in `tmux`/`screen` (see Step 7)
- Set Termux battery to **Unrestricted**
- Install **Termux:Boot** for auto-start

### ❌ `Permission denied` when writing to `/sdcard/`

```bash
termux-setup-storage    # re-run and accept the permission
ls -la ~/storage/       # verify symlinks exist
```

### ❌ `Address already in use` (port 8080)

Another process is using the web dashboard port. Either kill it:

```bash
# Find what's using the port
lsof -i :8080
# or
fuser -k 8080/tcp
```

Or change the port in `.env`:
```bash
WEB_PORT=9090
```

### ❌ `RecursionError` or `MemoryError` on large files

Android's `lmkd` kills processes using too much RAM. Mitigate by:

```bash
# Edit .env
LEECHBOT_BASE_DIR=/sdcard/leechbot_data  # use storage, not tmpfs
```

### ❌ Bot stuck — no error in dump channel

Check the log file directly:
```bash
tail -100 ~/LeechBot/leechbot.log
```

Common causes:
- Wrong `DUMP_ID` (bot not admin in channel)
- Wrong `OWNER_ID` (Telegram ID is a number, not @username)
- Invalid `BOT_TOKEN`

### ❌ `GoogleAuthError` when enabling GDRIVE

Google Drive auth needs a browser on first run. On Termux, run this on a **separate machine** first to generate `token.pickle`, then `scp` it to the phone. Or use a service-account JSON instead.

### ❌ `Termux was denied superuser access` (during `pkg install`)

This is normal — Termux doesn't need root. `pkg` uses its own prefix at `/data/data/com.termux/files/usr/`.

---

## 🔄 Updating the Bot

### If running in background:

```bash
cd ~/LeechBot
git pull origin main
kill $(cat leechbot.pid 2>/dev/null) 2>/dev/null
sleep 2
nohup python -m leechbot > leechbot.log 2>&1 &
echo $! > leechbot.pid
```

### If running in tmux/screen:

```bash
# Re-attach
tmux attach -t leechbot
# Ctrl+C to stop, then:
cd ~/LeechBot
git pull
python -m leechbot
# Ctrl+B then D to detach
```

### Or send `/update` to the bot in Telegram

It will show the latest version available on GitHub. (Auto-update is **not** enabled to avoid surprise breakage — manual update recommended.)

### Pull only Python deps that changed:

```bash
cd ~/LeechBot
pip install --upgrade -r requirements.txt
```

---

## 🗑 Uninstalling

### Remove the bot:

```bash
# Stop first
kill $(cat ~/LeechBot/leechbot.pid 2>/dev/null) 2>/dev/null
rm -rf ~/LeechBot
```

### Remove all Termux packages (full reset):

```bash
# In Termux
apt purge -y python ffmpeg aria2
rm -rf ~/.termux/boot/
# Then uninstall Termux app from Android Settings
```

### Remove storage permission:

Android Settings → Apps → Termux → Permissions → Files and media → Deny

---

## 📊 Resource Usage (typical, idle)

| Resource | Usage |
|----------|-------|
| RAM | 80-150 MB |
| Storage | ~500 MB (deps) + your downloads |
| CPU | <1% idle, 5-15% during active download |
| Battery | ~2-3% per hour with `termux-wake-lock` |
| Network | depends on what you download |

> **Pro tip:** Run on a phone plugged into power with WiFi = essentially a free 24/7 server.

---

## 🔗 Related Guides

- 📖 [GUIDE.md](GUIDE.md) — General user guide (also covers Colab, Docker, etc.)
- 🏗️ [ARCHITECTURE.md](ARCHITECTURE.md) — Code architecture
- 🐛 [Common Issues](https://github.com/Shineii86/LeechBot/issues) — search the issue tracker

---

**Happy leeching from your pocket!** 📱🤖
