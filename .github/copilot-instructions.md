# GitHub Copilot Instructions for LeechBot

## Project
LeechBot is a Pyrogram 2.0.106-based Telegram bot for downloading files from 2000+ sites and uploading to Telegram/Google Drive. Python 3.10+, asyncio-based, ~8000 lines.

## Architecture
- Entry point: `leechbot/__main__.py` — imports handlers, starts bot
- Commands: `leechbot/commands.py` — all `/command` handlers
- Callbacks: `leechbot/callbacks.py` — inline keyboard handlers
- Messages: `leechbot/handlers.py` — URL/photo/text handlers
- Downloaders: `leechbot/downloader/*.py` — one adapter per source
- Uploaders: `leechbot/uploader/telegram.py` — single + batch photo upload
- State: `leechbot/utility/variables.py` — ALL mutable global state
- Config: `config.py` — env vars, paths, feature flags
- Web: `leechbot/web/server.py` + `public/index.html` — dashboard

## Key Patterns
- All state is in class attributes in `variables.py` — import and mutate directly
- `from leechbot import app` for Pyrogram client
- `@app.on_message(filters.command("cmd"))` for command handlers
- `@app.on_callback_query()` for button callbacks
- Async everywhere — this is an asyncio application
- `logger = logging.getLogger(__name__)` at module top
- FloodWait: `await sleep(e.value)` then retry

## Constraints
- Pyrogram 2.0.106: no `style` on buttons, no `progress` on `reply_media_group()`
- Telegram 2GB file limit — handled by splitting
- Media group max 10 photos — batch upload splits accordingly
- Batch photo upload uses per-photo upload + file_id grouping for progress tracking

## File Headers
Every `.py` file starts with the standard project header block (see any existing file).

## Changelog
Every change must add an entry to `CHANGELOG.md` at the top with Version, Date, and description.
