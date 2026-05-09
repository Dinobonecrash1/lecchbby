# Changelog

All notable changes to this project will be documented in this file.

---

## [3.0.7] - 2026-05-09

### Added
- **Auto-register bot commands with Telegram** — `_register_commands()` in `__main__.py` calls `app.set_bot_commands()` on startup with all 23 bot commands; no need to manually set commands via @BotFather
- Commands are registered with emoji descriptions (e.g. "📥 Upload to Telegram", "♻️ Mirror to Google Drive")

### Changed
- **Upgraded all message styles** across the entire bot with consistent box-drawing characters (`┏┣┗` borders, `┏━━━━┓` panels)
- `WELCOME_TEXT` — replaced `───────` separators with `┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓` panels, bullet lists use `┣┗` tree
- `/help` menu — complete redesign with `┣┗` tree structure for all command categories
- `/tupload`, `/gdupload`, `/drupload`, `/ytupload`, `/glupload` — all use bordered instruction panels
- `/setname`, `/zipaswd`, `/unzipaswd` — usage messages use bordered example panels
- `/queue` — session stats use `┏━━━━ **Session Stats** ━━━━┓` bordered panel
- `/broadcast` — usage and completion messages use bordered panels
- `/admin` — command list uses bordered panel, user list uses `┣` tree
- `/cookies` — status display uses bordered panel, steps use numbered tree
- `/setcookies` — instructions use bordered panel with numbered steps
- `sysINFO()` — replaced `⌬─────` with `┏━━━━ **System Info** ━━━━┓` bordered panel
- `sysINFO_full()` — same bordered panel upgrade with `┣┗` tree items
- `_strip_sysinfo()` — handles both old (`⌬─────`) and new (`┏━━━━`) formats for backward compatibility
- Upload type selection message — bordered panel with descriptions
- All command responses now use consistent `✓` suffixes on success messages

---

## [3.0.6] - 2026-05-09

### Added
- **Colored buttons across the entire bot** using Telegram Bot API 9.4 `style` parameter on `InlineKeyboardButton`
  - 🔴 `danger` (red) — Cancel, Delete, Close, destructive actions
  - 🟢 `success` (green) — Confirm, Complete, positive/active states
  - 🔵 `primary` (blue) — Navigation, Back, Settings, main actions
  - ⚪ default — Secondary options, informational toggles
- Applied to all button instances across 5 files:
  - `callbacks.py` — upload type, video/caption/thumb/autodelete/photo menus, update confirm/cancel, format/speed back buttons
  - `commands.py` — /start settings button, /format best quality, /speed unlimited, /update confirm/cancel
  - `handlers.py` — upload type selection (Regular=success), gallery cancel button
  - `helper.py` — status cancel (danger), refresh (primary), settings close (danger), auto-delete toggle (success/danger)
  - `utility/handler.py` — cancel notification keyboard (URL buttons unchanged)

### Changed
- Auto-delete toggle button dynamically switches between `success` (ON) and `danger` (OFF)
- Photo mode buttons show `success` style on the currently active option
- Settings menu close button uses `danger` style for visual clarity
- Status bar cancel button uses `danger` style consistently across all download engines

---

## [3.0.5] - 2026-05-09

### Fixed
- **callbacks.py: Massive refactor** — split monolithic 400-line `handle_callback()` into focused async functions (`_handle_upload_type`, `_handle_video_settings`, `_handle_caption_settings`, `_handle_thumb_settings`, `_handle_delete_thumb`, `_handle_autodelete_menu`, `_handle_photo_mode_menu`, `_handle_ytdl_confirm`, `_handle_do_update`, `_handle_sys_refresh`, `_handle_sys_stats`)
- **All callbacks now answer properly** — added missing `callback_query.answer()` to every callback path; users no longer see a stuck loading spinner on button press
- **cancelTask() robustness** — wrapped all operations in individual try/except blocks so a single failure (e.g., status_msg.delete()) doesn't prevent the rest of the cancellation flow from completing
- **cancelTask() crash on missing src_link** — `Messages.src_link` could be empty if task was cancelled before source log was sent; now conditionally includes the source line
- **cancelTask() getTime() crash** — was calling `.seconds` on a timedelta which loses hours/days; now uses `int(...total_seconds())` for correct elapsed time
- **SendLogs() robustness** — wrapped source reply, status edit, and file list send in individual try/except blocks; a failure in one doesn't block the others
- **SendLogs() index safety** — added bounds check for `Transfer.sent_file_names` access
- **SendLogs() empty download_name** — falls back to "Unknown" if `Messages.download_name` is empty
- **callbacks.py redundant import** — removed duplicate `import config` (already imported at module level)
- **callbacks.py fragile sysinfo parsing** — extracted `_strip_sysinfo()` helper for cleaner text manipulation in sys_refresh/sys_stats callbacks
- **do_update restart safety** — wrapped `os.execv()` in try/except with user-facing fallback message if auto-restart fails
- **Unknown callback handling** — added catch-all with `show_alert=True` so users see a proper error for unhandled callback data

### Changed
- `callbacks.py` — dispatcher now logs callback data at DEBUG level for easier troubleshooting
- `callbacks.py` — all callback errors caught and shown to user as "❌ Something went wrong" alert instead of silent failure
- `handler.py` — `cancelTask()` logs reason at INFO level for debugging
- `handler.py` — `SendLogs()` logs individual failures at ERROR level instead of silently swallowing exceptions

---

## [3.0.4] - 2026-05-09

### Fixed
- **gallery-dl downloads now show a live progress bar** with speed, file count, total size, ETA, and elapsed time — matching the aria2c and yt-dlp status bar experience
- Removed `-q` (quiet) flag from gallery-dl command to enable real-time stderr output parsing
- Added async stderr reader task for non-blocking line-by-line output capture during gallery downloads
- Gallery completion message now includes elapsed time
- **Batch photo uploads now show a live progress bar** — `upload_photos_batch()` was missing the `progress` callback, so batch uploads showed no progress until completion; added `_batch_progress()` callback with speed, ETA, and percentage
- **GDrive downloader `down_msg` NameError** — `g_DownLoad()` defined `down_msg` as a local variable but `gDownloadFile()` referenced it out of scope; replaced with `Messages.status_head` which is the shared status message pattern used by all other downloaders

### Changed
- `gallery_download()` now uses `status_bar()` for consistent UI across all download engines
- Progress monitoring loop reads stderr in real-time instead of only polling file count
- Added `datetime` import for proper speed/elapsed time calculation
- Added `getTime` and `status_bar` imports to gallery module
- Batch photo upload now shows batch range label (e.g. "📤 Uploading Photos 1–10/25")

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
- `GUIDE.md` — comprehensive user guide covering credentials, installation, configuration, commands, settings, supported sites, Google Drive setup, YouTube auth, and troubleshooting
- 20 interactive demos in `GUIDE.md` showing real command flows: single file download, multi-link, YouTube, gallery, zip/extract, Telegram (public + private), Google Drive mirror, local directory, queuing, thumbnail, prefix/suffix, bandwidth limiting, multi-user, broadcast, update, cookie auth, cancel, auto-delete, and error recovery

### Changed
- Improved `media_Identifier()` in Telegram downloader with better error messages for public vs private channel access
- Added `message.empty` and `message.service` checks to prevent processing invalid messages
- Updated `GUIDE.md` Telegram section with clear public/private link distinction and membership requirements

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
