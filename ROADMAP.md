# 🗺️ LeechBot — Roadmap

Future plans and ideas for LeechBot. Not promises — just direction.

> Have a suggestion? [Open an issue](https://github.com/Shineii86/LeechBot/issues) or [join the discussion](https://github.com/Shineii86/LeechBot/discussions).

<p align="center">
  <img src="assets/divider.svg" width="600" alt="---divider---"/>
</p>

## 📋 Planned

### 🔌 rclone Integration (Optional)
- One module covers 40+ cloud providers: OneDrive, Dropbox, S3, Backblaze, Google Drive (alternative), WebDAV, and more
- CLI wrapper pattern (same as megatools): `rclone copy` + stderr progress parsing
- Requires `rclone config` one-time setup (user-guided via `/rclone` command)
- Download from cloud → upload to Telegram, or mirror between providers

### 📊 Unit Tests
- Currently zero tests — everything is manual
- Start with core modules: `helper.py`, `variables.py`, `manager.py`
- Mock Pyrogram client for handler tests
- GitHub Actions CI on push/PR

### 🌍 Internationalization (i18n)
- Currently English-only
- Support for Arabic, Hindi, Turkish, Spanish, Portuguese (most-requested)
- Translation files in `locales/` directory
- User selects language via `/language` command

### 📱 Mobile Dashboard
- Current dashboard is desktop-focused
- Responsive improvements for mobile browsers
- Push notifications via Telegram bot (task complete, errors)

### 🔄 Resume Interrupted Uploads
- If bot crashes mid-upload, resume from last chunk instead of re-uploading
- Track upload progress in session state
- Telegram supports `file_id` reuse — leverage this

---

## 💡 Considering

### ☁️ Multi-Cloud Mirror
- Download from any source → upload to multiple targets simultaneously
- Example: YouTube → Telegram + Google Drive + OneDrive in one command
- Depends on rclone integration

### 📦 Archive Streaming
- Extract archives on-the-fly during upload (stream, don't extract to disk)
- Reduces disk usage for large archives
- Requires `7z` piped to upload

### 🎵 Audio Processing
- Convert video to audio (extract soundtrack)
- Audio format conversion (FLAC → MP3, WAV → AAC)
- Tag editing for music files

### 📸 Image Processing
- Resize/compress images before upload
- Format conversion (HEIC → JPG, WebP → PNG)
- Watermark support

### 🔗 Link Shortener Integration
- Generate short links for uploaded files
- Support: bit.ly, tinyurl, is.gd
- Useful for sharing uploaded content

---

## ❌ Not Planned

| Feature | Reason |
|---------|--------|
| OneDrive/Dropbox direct API | rclone covers it with less code |
| S3/MinIO direct | Niche, rclone covers it |
| Web UI file manager | Out of scope — bot is a transloader, not a file manager |
| Multi-bot cluster | Complexity vs benefit doesn't justify it |
| User registration system | No accounts, no database — keep it simple |

<p align="center">
  <img src="assets/divider.svg" width="600" alt="---divider---"/>
</p>

## ✅ Done (Recent)

| Feature | Version |
|---------|---------|
| **Removed Bunkr + Instagram downloaders (broken, untestable)** — see [CHANGELOG 3.1.31](CHANGELOG.md) | **3.1.31** |
| 3 utility commands: `/status`, `/restart`, `/logs` + rotating file logger | 3.1.30 |
| 35-check offline diagnostic test suite (`tests/test_diagnostics.py`) | 3.1.29 |
| `TERMUX.md` deployment guide (513 lines) | 3.1.27 |
| `/ping` command (latency bar + uptime + version) | 3.1.25 |
| `thumbMaintainer` None crash fix | 3.1.24 |
| Telegram public-link parser off-by-one fix (`parts[4]` → `parts[-2]`) | 3.1.23 |
| 4 unwired features exposed: `/formats`, `/preview`, multi-link URL extraction, lifetime stats in `/stats` | 3.1.21 |
| YTDL thread-safety (`loop.call_soon_threadsafe` for progress hook) | 3.1.21 |
| `/cancel` mid-ffmpeg no longer leaks orphan subprocesses (`_terminate_subprocess`) | 3.1.20 |
| `/stats` cumulative bytes now show real totals (was always 0) | 3.1.20 |
| Comprehensive static analysis report (`AUDIT_REPORT.md`) — 1 critical, 8 dead, 1 thread-safety, 4 resource-leak | 3.1.19 |
| Latent `NameError` fix in `task_manager.py` (would have crashed first task) | 3.1.18 |
| YouTube thumbnail bug fix (used original filename instead of truncated) | 3.1.17 |
| Bot completely unresponsive fix (`__main__.py` didn't import handlers) + 18 other fixes | 3.1.15 |
| Full downloader/uploader audit (14 bugs fixed) | 3.1.14 |
| Mega.nz folder support + async rewrite | 3.1.14 |
| Google Drive pagination + async | 3.1.14 |
| Colab notebook consolidation (6→3 cells) | 3.1.14 |
| Dockerfile: libtorrent, tini, signal handling | 3.1.12 |
| Torrent/magnet aria2c fallback | 3.1.14 |
| libtorrent magnet/torrent downloader | 3.1.7 |
| 4 new downloaders (GoFile, Bunkr*, Catbox, StreamTape) — *Bunkr removed in 3.1.31 | 3.1.1 |
| Web dashboard (REST + WebSocket) | 3.1.0 |
| UserBot for private channels | 3.1.1 |
| YouTube PO Token auto-generation | 3.0.2 |
| gallery-dl integration (100+ sites) | 3.0.3 |

<p align="center">
  <img src="assets/divider.svg" width="600" alt="---divider---"/>
</p>

> 📋 Full history: [CHANGELOG.md](CHANGELOG.md)
