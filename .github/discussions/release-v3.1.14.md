# 📣 LeechBot v3.1.14 — Major Stability Release

> **10 commits, 70+ bugs fixed, every module audited.**

This release focused entirely on reliability, correctness, and developer experience. No new features — just making everything that exists work properly.

---

## 🔥 Highlights

### 🐛 14 Critical Bugs Fixed in Downloaders & Uploaders
- **aria2c** no longer blocks the event loop (was freezing the entire bot)
- **Mega.nz** fully async with folder support and regex progress parser
- **TeraBox** hardened with proper timeouts and clean error messages
- **Upload speed/ETA** correct past 1 hour (`.seconds` → `.total_seconds()`)
- **FloodWait** no longer stack overflows (max 10 retries)
- **3 broken imports** in `__init__.py` fixed

### 📦 Google Drive Overhaul
- Folder size now accurate for 1000+ files (was only first 100)
- All API calls async — bot stays responsive during GDrive operations
- Google Docs/Sheets/Slides skipped instead of crashing
- All GDrive URL formats supported

### 🧲 Torrent/Magnet Works Everywhere
- Full libtorrent support when available (DHT, peers, resume)
- Automatic aria2c fallback when libtorrent is missing
- Works out-of-the-box on Colab, Docker, VPS — no configuration needed

### 🐳 Dockerfile Improvements
- `python3-libtorrent` included — torrent support works in Docker
- `tini` as PID 1 — clean shutdown on `docker stop`
- Proper signal handling (no more 10s timeout kill)

### 📒 Colab Notebook Simplified
- 6 cells → 3 cells
- Setup: credentials → clone → deps → libtorrent → GPU → config → GDrive → health check
- Deploy: Start Bot / Update & Restart / Stop Bot dropdown

---

## 📊 Full Changelog

### Fixed
- `__init__.py` broken imports (`is_gofile`, `is_bunkr`, `is_catbox`)
- aria2c blocks event loop → `asyncio.create_subprocess_exec`
- aria2c tracker download at import time → lazy loading
- Upload `.seconds` → `.total_seconds()` (wrong ETA after 1hr)
- Upload FloodWait recursion → max 10 retries
- StreamTape `url` used before assignment
- GoFile/Bunkr/Catbox `__import__` hacks → proper imports
- GoFile/Bunkr/Catbox/Pixeldrain/Mediafire — added request timeouts
- Pixeldrain list status shows before download, not after
- GDrive folder size pagination (was first 100 files only)
- GDrive blocks event loop → async wrappers
- GDrive Google Apps types crash → skip with log
- GDrive recursion limit → `MAX_FOLDER_DEPTH = 50`
- GDrive URL regex → covers all formats
- Colab notebook missing libtorrent → conda install
- Mega.nz event loop blocking → async subprocess
- TeraBox fragile API handling → proper timeouts + error extraction

### Added
- Mega.nz folder support + error extraction + recursive file tracking
- Torrent/magnet aria2c fallback when libtorrent missing
- `ROADMAP.md` — future plans and priorities
- Health check for libtorrent + megatools
- Request timeouts on all HTTP clients (30s–300s)

### Changed
- Dockerfile: libtorrent, tini, signal handling, labels
- Colab notebook: 6 cells → 3 cells
- All documentation updated to v3.1.14

---

## 🙏 Thanks

To everyone who reported bugs and tested the bleeding edge. This release makes LeechBot production-ready.

**📦 Update:** `git pull origin main` or re-run the Colab Setup cell
**🐛 Report:** [Issues](https://github.com/Shineii86/LeechBot/issues)
**💬 Discuss:** [Telegram Group](https://t.me/MaximXGroup)
