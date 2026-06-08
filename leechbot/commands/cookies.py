# =============================================================================
# Telegram Leech Bot - Cookie Commands
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Cookie command handlers — /cookies, /setcookies, /clearcookies
"""

import logging
import os
from pyrogram import filters
from leechbot import app, OWNER
from leechbot.utility.variables import Paths
from leechbot.utility.helper import message_deleter
import config

logger = logging.getLogger(__name__)

# =============================================================================
# /cookies — Show YT-DLP authentication status
# =============================================================================
@app.on_message(filters.command("cookies") & filters.private)
async def cookies_command(client, message):
    """Show current YT-DLP authentication status."""
    import subprocess

    cookies_file = getattr(config, "YTDL_COOKIES_FILE", "")
    browser_cookies = getattr(config, "YTDL_BROWSER_COOKIES", "")
    default_path = Paths.COOKIE_FILE

    file_ok = cookies_file and os.path.isfile(cookies_file)
    uploaded_ok = os.path.isfile(default_path)
    browser_ok = bool(browser_cookies)

    # Check if PO token plugin is installed
    pot_installed = False
    try:
        result = subprocess.run(
            ["pip", "show", "bgutil-ytdlp-pot-provider"],
            capture_output=True, text=True, timeout=10
        )
        pot_installed = result.returncode == 0
    except Exception:
        pass

    # Build status
    auth_lines = []
    if pot_installed:
        auth_lines.append("✅ **PO Token Plugin** — auto-generating tokens (primary)")
    else:
        auth_lines.append("❌ **PO Token Plugin** — not installed")

    if file_ok:
        auth_lines.append(f"✅ **Cookies file** (env) — `{cookies_file}`")
    elif uploaded_ok:
        auth_lines.append(f"✅ **Cookies file** (uploaded) — `{default_path}`")
    elif browser_ok:
        auth_lines.append(f"✅ **Browser extract** — `{browser_cookies}`")
    else:
        auth_lines.append("⚠️ **Cookies** — not configured (fallback)")

    status = "\n".join(auth_lines)

    text = f"""**🍪 YT-DLP Authentication Status**

{status}

─── How It Works ───
• **PO Token Plugin** (auto) — generates tokens in background
• **Cookies** (manual fallback) — only needed if PO tokens fail

**If YouTube Still Fails:**
Upload a `cookies.txt` file here as a backup:
`1.` Install [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
`2.` Go to `youtube.com` • click extension • **Export**
`3.` Send the file here

📖 [PO Token Guide](https://github.com/yt-dlp/yt-dlp/wiki/PO-Token-Guide)"""

    msg = await message.reply_text(text, quote=True, disable_web_page_preview=True)
    await message_deleter(message, msg)

# =============================================================================
# /setcookies — Upload cookies.txt via Telegram
# =============================================================================
@app.on_message(filters.command("setcookies") & filters.private)
async def setcookies_command(client, message):
    """Prompt user to upload a cookies.txt file."""
    if message.chat.id != OWNER:
        return

    text = """**🍪 Upload Cookies File**

Send me your `cookies.txt` file **as a document** (not as text).

**Chrome / Edge / Brave:**
`1.` Install [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
`2.` Go to `youtube.com` (make sure you're logged in)
`3.` Click extension icon • **Export** • saves `cookies.txt`
`4.` Upload that file here

**Firefox:**
`1.` Install [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)
`2.` Go to `youtube.com` (logged in)
`3.` Click extension • **Export** • upload here

⚠️ **Security:** Cookies contain your session tokens. The bot stores them locally and never shares them. Delete with `/clearcookies` if needed."""

    msg = await message.reply_text(text, quote=True, disable_web_page_preview=True)
    await message_deleter(message, msg)

# =============================================================================
# /clearcookies — Delete uploaded cookies file
# =============================================================================
@app.on_message(filters.command("clearcookies") & filters.private)
async def clearcookies_command(client, message):
    """Delete the uploaded cookies file."""
    if message.chat.id != OWNER:
        return

    cookie_path = Paths.COOKIE_FILE
    if os.path.isfile(cookie_path):
        try:
            os.remove(cookie_path)
            msg = await message.reply_text("**✅ Cookies file deleted.**", quote=True)
        except OSError as e:
            msg = await message.reply_text(f"**❌ Failed:** `{e}`", quote=True)
    else:
        msg = await message.reply_text("**ℹ️ No cookies file to delete.**", quote=True)

    await message_deleter(message, msg)