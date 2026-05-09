# Changelog

All notable changes to this project will be documented in this file.

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
