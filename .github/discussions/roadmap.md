# 🗺️ LeechBot Roadmap — What's Next

> Track upcoming features, vote on priorities, and suggest new ideas.

---

## 📋 Planned (In Development)

### 🔌 rclone Integration
**Status:** Planned | **Priority:** High

One module covers **40+ cloud providers**: OneDrive, Dropbox, S3, Backblaze, Google Drive (alternative), WebDAV, and more.

- CLI wrapper pattern (same as megatools)
- `rclone config` one-time setup via `/rclone` command
- Download from cloud → upload to Telegram
- Mirror between providers

**Vote:** 👍 if you want this

---

### 📊 Unit Tests + CI
**Status:** Planned | **Priority:** Medium

Currently zero tests — everything is manual.

- Core modules: `helper.py`, `variables.py`, `manager.py`
- Mock Pyrogram client for handler tests
- GitHub Actions CI on push/PR

---

### 🌍 Multi-Language Support (i18n)
**Status:** Planned | **Priority:** Medium

Currently English-only. Planned languages:
- Arabic, Hindi, Turkish, Spanish, Portuguese (most-requested)
- Translation files in `locales/` directory
- User selects via `/language` command

**Vote:** 🌍 react with your language flag

---

### 📱 Mobile Dashboard
**Status:** Considering | **Priority:** Low

- Responsive improvements for mobile browsers
- Push notifications via Telegram bot (task complete, errors)

---

### 🔄 Resume Interrupted Uploads
**Status:** Planned | **Priority:** Medium

- Resume from last chunk instead of re-uploading
- Track upload progress in session state
- Leverage Telegram `file_id` reuse

---

## 💡 Under Consideration

| Feature | Description | Votes Needed |
|---------|-------------|:---:|
| Multi-cloud mirror | Download → upload to Telegram + GDrive + OneDrive simultaneously | 👍 |
| Archive streaming | Extract on-the-fly during upload (no disk usage) | 👍 |
| Audio processing | Extract audio, convert formats, edit tags | 👍 |
| Image processing | Resize, compress, format conversion, watermark | 👍 |
| Link shortener | bit.ly, tinyurl, is.gd integration | 👍 |
| Cookie manager UI | Upload/manage cookies via web dashboard | 👍 |

---

## ❌ Not Planned

| Feature | Why Not |
|---------|---------|
| OneDrive/Dropbox direct API | rclone covers it with less code |
| S3/MinIO direct | Niche, rclone covers it |
| Web file manager | Out of scope — bot is a transloader |
| Multi-bot cluster | Complexity vs benefit |
| User registration/accounts | No database — keep it simple |

---

## ✅ Recently Completed

| Feature | Version | Date |
|---------|---------|------|
| Full downloader/uploader audit (14 bugs) | 3.1.14 | 2026-05-10 |
| Mega.nz folder support + async | 3.1.14 | 2026-05-10 |
| Google Drive pagination + async | 3.1.14 | 2026-05-10 |
| Dockerfile: libtorrent, tini | 3.1.12 | 2026-05-10 |
| Torrent/magnet aria2c fallback | 3.1.14 | 2026-05-10 |
| 4 new downloaders | 3.1.1 | 2026-05-10 |
| Web dashboard | 3.1.0 | 2026-05-09 |
| UserBot private channels | 3.1.1 | 2026-05-10 |

---

**💬 Suggest something:** Comment below or [open an issue](https://github.com/Shineii86/LeechBot/issues)
