# Changelog

All notable changes to this project will be documented in this file.

---

## [3.0.3] - 2026-05-09

### Fixed
- **Critical:** `upload_photos_batch()` used wrong parameter name `media_group` for Pyrogram's `reply_media_group()` — changed to `media` (the correct Pyrogram API parameter)
- **Critical:** Batch photo retry logic used `i -= batch_size` inside a `for` loop which had no effect — refactored to `while` loop with manual index control for proper FloodWait retries
- **Critical:** Batch-uploaded photos were never cleaned up when `remove=True` — added `os.remove()` cleanup after successful batch upload
- Missing `Transfer.up_bytes` tracking in batch photo mode — upload progress now accurately reflects batch uploads
- `upload_photos_batch` was not exported from `leechbot.uploader.__init__` — added to `__all__`

### Added
- `/glupload` command — dedicated gallery-dl download mode for image galleries from Instagram, Twitter, Pinterest, Pixiv, DeviantArt, ArtStation, Flickr, Reddit, Tumblr, TikTok, Bluesky, and 100+ sites
- `BOT.Mode.gallery` flag to track gallery-dl mode state across the task pipeline
- Gallery mode label in task status display (shows "Gallery" instead of generic "Leech")

### Changed
- `upload_photos_batch()` now accepts `remove` parameter to match `upload_file()` cleanup behavior
- Added `import os` to `telegram.py` for file cleanup support
- Updated `/start` welcome text and `/help` menu with `/glupload` command
- All upload commands (`/tupload`, `/gdupload`, `/drupload`, `/ytupload`) now explicitly reset `gallery` flag to prevent mode leakage between tasks
- Gallery mode skips zip/unzip/undzip type selection — goes straight to download since gallery-dl only fetches images, not archives

---

## [3.0.2] - 2026-05-09

### Fixed
- **Critical:** YouTube downloads fail with "Sign in to confirm you're not a bot" error — added PO Token plugin (`bgutil-ytdlp-pot-provider`) for automatic token generation, no user action required
- **Critical:** Updated `yt-dlp` minimum version to `2025.5.22` for PO Token Provider Framework support
- `YouTubeDL()`, `get_YT_Name()`, and `list_formats()` now all use cookie options when configured
- Removed explicit `mweb` client restriction — yt-dlp auto-selects best client with full format support

### Added
- **PO Token auto-generation** via `bgutil-ytdlp-pot-provider` plugin — fully automated, no manual setup
- **🔄 Auto-Update** — `/update` command checks GitHub for new versions, shows changelog, one-click update with auto-restart
- **📸 gallery-dl integration** — download photo galleries from Instagram, Twitter, Pinterest, Pixiv, DeviantArt, ArtStation, Flickr, Reddit, Tumblr, and 100+ sites
- **📸 Photo Upload Mode** setting — choose between Group (batch of 10) or Single (one by one) via `/settings` menu
- **YT-DLP Cookie Authentication** — fallback methods to pass cookies to yt-dlp:
  - `YTDL_COOKIES_FILE` env var — path to a Netscape-format cookies.txt file
  - `YTDL_BROWSER_COOKIES` env var — extract cookies directly from a browser (chrome, firefox, edge, brave, opera, safari, vivaldi)
- `/cookies` command — shows PO token + cookie authentication status
- `/setcookies` command — step-by-step browser export instructions for cookie fallback
- `/clearcookies` command — delete stored cookies file
- **Document handler** — auto-detects `cookies.txt` uploads and saves them for yt-dlp
- Cookie options documented in `.env.example` with inline comments
- Cookie file path exposed in `Paths.ytdl_cookies` and `Paths.COOKIE_FILE` for cross-module access
- Default cookie save path: `<SESSIONS_PATH>/cookies.txt`

### Changed
- Updated `/help` command with PO token + cookie configuration section
- Updated VERSION to 3.0.2

---

## [3.0.1] - 2026-05-09

### Fixed
- **Critical:** `Transfer` undefined in `/broadcast` command — would crash at runtime
- **Critical:** `Queue.size()` method missing — `/queue` command would raise `AttributeError`
- **Critical:** All `global` declarations in `handler.py`, `task_manager.py`, `converters.py`, `mega.py`, `gdrive.py` were incorrect (used `global` on class objects from another module instead of importing them)
- **Critical:** `task_manager.py` used synchronous `os.system()` for aria2c — blocked the async event loop; replaced with `asyncio.create_subprocess_exec()`
- **Critical:** `.gitignore` only contained `__pycache__/` — missing `.env`, `*.session`, `credentials.json`, `*.pickle`, IDE files, OS files
- **Critical:** `moviepy` 2.x removed `moviepy.editor` — added fallback imports in `converters.py` and `helper.py` for `moviepy` 1.x and 2.x compatibility
- **Critical:** Pyrogram Client variable named `leechbot` shadowed the `leechbot` package — renamed to `app` across all modules
- `config.py` VERSION was `1.0.0` with BUILD_DATE `2026-05-01` — mismatched README v3; updated to `3.0.0`
- `broadcast_command` referenced undefined `Transfer.sent_file` — added proper import
- `handle_text_input` handler caught ALL private text messages — now excludes known commands via `~filters.command()`

### Changed
- **Modularized `__main__.py`** (1,149 lines → 48 lines) — split into three focused modules:
  - `leechbot/commands.py` (611 lines) — all `/command` handlers
  - `leechbot/callbacks.py` (375 lines) — all inline keyboard callback handlers
  - `leechbot/handlers.py` (156 lines) — message handlers (URL, photo, text, reply)
  - `leechbot/__main__.py` (48 lines) — thin entry point that imports handlers and runs the bot
- Stored `src_request_msg` on `BOT._src_request_msg` for cross-module access between commands and handlers
- Cleaned up unused imports across `commands.py`, `handlers.py`, `downloader/mediafire.py`, `downloader/manager.py`
- All async functions now properly import their dependencies instead of using incorrect `global` declarations

### Added
- `Queue.size()` method to `DownloadQueue` class in `variables.py`
- `src_request_msg` stored on `BOT` object for cross-module handler communication

### Docs
- Updated README with v3.0.1 changelog section
- Added project structure tree to README
- Updated "Code Structure" in comparison table to reflect modularization

### Fixed (continued)
- **Critical:** Pyrogram rejects large channel IDs (>2147483647) due to 32-bit limits — patched `MIN_CHANNEL_ID` to support 15-digit Telegram IDs
- Bot startup now resolves DUMP_ID and OWNER_ID peers at launch to prevent 'Peer id invalid' errors on restarts
- System Info callbacks (`sys_refresh`, `sys_stats`) crashed on photo messages — `message.text` is `None` for photos; now falls back to `message.caption`
- `handle_reply` in handlers.py crashed on non-text replies (photo/sticker) — now checks `message.text or message.caption` and returns early if None
- Upload `progress_bar` division by zero when `Transfer.total_down_size` is 0 — added `max(..., 1)` guard
- Unguarded `os.remove()` / `os.rename()` / `shutil.rmtree()` calls across `handler.py`, `converters.py`, `helper.py`, `callbacks.py` — wrapped with try/except or `ignore_errors=True`

### Added
- `leechbot/debug.py` — Debug logging and error reporting module:
  - `TelegramLogHandler` — sends ERROR/CRITICAL logs to DUMP_ID channel in real-time
  - `AsyncExceptionHandler` — catches unhandled asyncio task exceptions and reports to Telegram
  - `send_debug()` — manual debug message sender for testing
  - All errors now appear in the DUMP_ID channel with emoji severity, timestamps, module names, and tracebacks
