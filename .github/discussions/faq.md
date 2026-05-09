# ❓ FAQ & Common Issues

> Before asking, check if your question is answered here.

---

## 🚀 Setup & Installation

### Q: Python packages fail to install
**A:** Make sure you have Python 3.10+. If `python-libtorrent` fails, it's optional — the bot uses aria2c as fallback for torrents.

### Q: `IndentationError` in Colab notebook
**A:** Update to the latest version: in the Deploy cell, select "Update & Restart".

### Q: Bot says "Token.pickle Not Found"
**A:** Run the Google Drive setup (cell 1, set `MOUNT_DRIVE = True`) or skip GDrive features.

### Q: How do I get YouTube cookies?
**A:** Two options:
1. **Automatic (recommended):** Install `bgutil-ytdlp-pot-provider` (already in requirements)
2. **Manual:** Export cookies from browser → `/setcookies` command

---

## 📥 Downloads

### Q: YouTube says "Sign in to confirm you're not a bot"
**A:** The PO Token plugin handles this automatically. If it still fails, export cookies from your browser and upload via `/setcookies`.

### Q: Mega.nz download fails
**A:** Install megatools:
```bash
sudo apt install megatools  # Linux
brew install megatools       # macOS
```

### Q: Torrent/magnet links don't work
**A:** Install libtorrent for best performance:
```bash
sudo apt install python3-libtorrent    # Linux
apt-get install -y python3-libtorrent  # Colab
```
Without it, torrents use aria2c (slower but functional).

### Q: Google Drive quota exceeded
**A:** Google limits downloads per day. Wait 24 hours or use a service account.

### Q: Terabox download fails
**A:** Terabox uses a third-party API that may be unreliable. Try again later or download directly from Terabox.

---

## 📤 Uploads

### Q: Upload is slow
**A:** Telegram limits upload speed. Large files (>1GB) take time. The bot shows ETA — be patient.

### Q: Files >2GB fail to upload
**A:** Telegram's limit is 2GB per file. The bot auto-splits files — check if splitting is enabled in settings.

### Q: Photos upload as documents
**A:** Use `/settings` → Upload Mode → "Media" (streaming). Or use `/tupload` with photo links.

---

## 🐳 Docker

### Q: Container exits immediately
**A:** Check logs: `docker logs leechbot`. Most common: missing `.env` file or invalid credentials.

### Q: How do I update Docker?
```bash
git pull origin main
docker compose up -d --build
```

---

## 🌐 Dashboard

### Q: Dashboard shows "Unauthorized"
**A:** Check your `WEB_TOKEN` in `.env`. If not set, it's auto-generated — check bot logs for the token.

### Q: Dashboard not updating
**A:** WebSocket might be blocked. The dashboard auto-falls back to REST polling (5s intervals).

---

## 🆘 Still Need Help?

1. **Check logs:** Bot logs are sent to your `DUMP_ID` channel
2. **Health Check:** Run the Health Check section in Setup cell
3. **Ask:** [Telegram Support Group](https://t.me/MaximXGroup)
4. **Report:** [GitHub Issues](https://github.com/Shineii86/LeechBot/issues)
