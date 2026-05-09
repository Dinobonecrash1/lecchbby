# 📣 LeechBot v3.1.15 — Colab Reliability Fix

> **2 commits, 4 bugs fixed — Colab notebook actually works now.**

This release fixes the two issues that made the Colab notebook unusable: libtorrent install failing with `conda not found`, and the Deploy cell disconnecting the runtime.

---

## 🔥 Highlights

### 🧲 libtorrent Install Fixed on Colab
The notebook tried `conda install` first — but Google Colab doesn't have conda. Every user hit `/bin/sh: 1: conda not found` and setup failed. Now tries `apt-get install python3-libtorrent` first (works on Colab), conda as fallback.

### 📒 Deploy Cell No Longer Disconnects Runtime
The Deploy cell had a JS keep-alive encoded character-by-character (`"f","u","n","c","t","i","o","n"...`), making it ~9000 lines of JSON. This was too heavy — Colab's idle detection fired and disconnected the runtime. Replaced with a clean, compact JS function. Notebook reduced by **60%** (9365 → 252 lines).

### 🐛 Two More libtorrent Bugs Squashed
- `manager.py` called `info()` (a notebook-only function) when libtorrent falls back to aria2c → `NameError` crash at runtime. Fixed to `logger.warning()`.
- `_check_libtorrent()` error message still told users `!conda install` for Colab — same wrong instruction. Fixed to `!apt-get install`.

---

## 📊 Full Changelog

### Fixed
- **Colab notebook libtorrent install order** — `conda` → `apt-get` first (conda doesn't exist on Colab)
- **Colab runtime disconnects on Deploy cell** — bloated JS keep-alive replaced with lean daemon thread
- **`info()` NameError in torrent fallback** — `manager.py` called undefined `info()`, replaced with `logger.warning()`
- **Wrong Colab install instruction in `_check_libtorrent()`** — `torrent.py` error message said conda, fixed to apt-get
- **Wrong Colab install instruction in FAQ** — `.github/discussions/faq.md` had same conda error
- **Notebook cell count mismatch** — header said 5 cells, actual is 2 (Setup → Deploy)
- **Notebook version badge** — 3.1.5 → 3.1.15

### Changed
- **Notebook Deploy cell streamlined** — 60% smaller, same functionality

---

## 🐛 Bugs Found (Root Cause Analysis)

| # | File | Line | Bug | Severity |
|---|------|------|-----|----------|
| 1 | `notebooks/LeechBot.ipynb` | Setup cell | `conda install` tried first — Colab has no conda | 🔴 Critical |
| 2 | `notebooks/LeechBot.ipynb` | Deploy cell | JS keep-alive encoded as individual chars → 9000 lines → Colab idle detection fires | 🔴 Critical |
| 3 | `leechbot/downloader/manager.py` | 192 | `info()` not imported → `NameError` when libtorrent missing | 🟠 High |
| 4 | `leechbot/downloader/torrent.py` | 59 | `_check_libtorrent()` error says `!conda install` for Colab | 🟡 Medium |
| 5 | `.github/discussions/faq.md` | 41 | FAQ says `conda install` for Colab | 🟡 Medium |

---

## 🔄 Migration

No breaking changes. Just pull and restart:

```bash
git pull origin main
```

**Colab users:** Re-run the Setup cell, then Deploy cell. libtorrent installs via apt now (no conda needed).

---

## 🙏 Thanks

To everyone who reported the `conda not found` error and runtime disconnects. Colab deployment should be rock solid now.

**📦 Update:** `git pull origin main` or re-run the Colab Setup cell
**🐛 Report:** [Issues](https://github.com/Shineii86/LeechBot/issues)
**💬 Discuss:** [Telegram Group](https://t.me/MaximXGroup)
