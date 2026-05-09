# =============================================================================
# Telegram Leech Bot - Command Handlers
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Bot command handlers — all /command message handlers.
"""

import logging
from pyrogram import filters
from leechbot import app, OWNER
from leechbot.utility.variables import BOT, Queue, BotStats
from leechbot.utility.task_manager import task_starter
from leechbot.utility.handler import cancelTask
from leechbot.utility.helper import (
    message_deleter, send_settings, sysINFO,
)
import config

logger = logging.getLogger(__name__)


# =============================================================================
# Welcome Text
# =============================================================================
WELCOME_TEXT = """
**🤖 Leech Bot** — Advanced Telegram File Transloader

◈ **💪 Powerful • 🚀 Fast • 🔰 Secure**

───────────────────────────

**📥 Download From Anywhere**
`•` Direct Links, Google Drive, Telegram
`•` YouTube, Facebook, Instagram & 2000+ sites
`•` Terabox, Mega, Pixeldrain, Mediafire

**📤 Upload To Premium Destination**
`•` Telegram (Unlimited Storage)
`•` Google Drive (Mirror Mode)
`•` Local Directory Leech

**🛠️ Advance Tools**
`•` Video Converter (GPU Accelerated)
`•` Archive Extractor (Zip, Rar, 7z)
`•` Smart Splitting For Large Files
`•` Custom Thumbnails & Captions
`•` Download Queue & Bandwidth Control

───────────────────────────

**📋 Quick Commands**
`/tupload` — Upload To Telegram
`/gdupload` — Mirror To Google Drive
`/ytupload` — Download With Yt‑Dlp
`/queue` — View Download Queue
`/format` — Set YT-DLP Quality
`/speed` — Set Bandwidth Limit
`/settings` — Configure Bot Preferences

───────────────────────────

**🧑‍💻 Developer:** [Shinei Nouzen](https://t.me/Shineii86)
"""


# =============================================================================
# /start
# =============================================================================
@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    """Handle the /start command."""
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    await message.delete()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📂 GitHub Repository ✨", url="https://github.com/Shineii86/LeechBot")],
        [
            InlineKeyboardButton("🔔 Updates", url="https://t.me/MaximXBots"),
            InlineKeyboardButton("Support 💬", url="https://t.me/MaximXGroup"),
        ],
        [InlineKeyboardButton("🤖 Bot Settings ⚙️", callback_data="settings_menu")],
    ])

    await message.reply_text(WELCOME_TEXT, reply_markup=keyboard, disable_web_page_preview=True)


# =============================================================================
# /tupload
# =============================================================================
@app.on_message(filters.command("tupload") & filters.private)
async def telegram_upload_command(client, message):
    """Handle the /tupload command — leech mode."""
    BOT.Mode.mode = "leech"
    BOT.Mode.ytdl = False

    text = """
**⚡ Send Download Link(s)** 🔗

📋 **Follow The Pattern Below:**

<code>https://example.com/file1.mp4
https://example.com/file2.mp4
[Custom Name.mp4]
{Zip Password}
(Unzip Password)</code>

**💡 Tips:**
• Multiple Links Supported
• Use [] For Custom Filename
• Use {} For Zip Password
• Use () For Extract Password
"""
    src_request_msg = await task_starter(message, text)
    BOT._src_request_msg = src_request_msg


# =============================================================================
# /gdupload
# =============================================================================
@app.on_message(filters.command("gdupload") & filters.private)
async def gdrive_upload_command(client, message):
    """Handle the /gdupload command — mirror mode."""
    BOT.Mode.mode = "mirror"
    BOT.Mode.ytdl = False

    text = """
**⚡ Send Download Link(s)** 🔗

📋 **Follow The Pattern Below:**

<code>https://example.com/file1.mp4
https://example.com/file2.mp4
[Custom Name.mp4]
{Zip Password}
(Unzip Password)</code>

**💡 Tips:**
• Multiple Links Supported
• Files Will Be Mirrored To Your Gdrive
• Make Sure Gdrive Is Mounted
"""
    src_request_msg = await task_starter(message, text)
    BOT._src_request_msg = src_request_msg


# =============================================================================
# /drupload
# =============================================================================
@app.on_message(filters.command("drupload") & filters.private)
async def directory_upload_command(client, message):
    """Handle the /drupload command — directory leech mode."""
    BOT.Mode.mode = "dir-leech"
    BOT.Mode.ytdl = False

    text = """
**⚡ Send Folder Path** 📁

📋 **Example:**

<code>/home/user/Downloads/myfolder</code>

**💡 Note:**
• Provide Absolute Path To The Folder
• Ensure The Bot Has Read Permissions
"""
    src_request_msg = await task_starter(message, text)
    BOT._src_request_msg = src_request_msg


# =============================================================================
# /ytupload
# =============================================================================
@app.on_message(filters.command("ytupload") & filters.private)
async def ytdl_upload_command(client, message):
    """Handle the /ytupload command — YT-DLP mode."""
    BOT.Mode.mode = "leech"
    BOT.Mode.ytdl = True

    text = """
**⚡ Send Yt-Dlp Link(s)** 🔗

📋 **Follow The Pattern Below:**

<code>https://youtube.com/watch?v=xxxxx
https://youtu.be/xxxxx
[Custom Name.mp4]
{Zip Password}</code>

**💡 Supported Sites:**
• Youtube, Facebook, Instagram
• Twitter, Tiktok, And More...
"""
    src_request_msg = await task_starter(message, text)
    BOT._src_request_msg = src_request_msg


# =============================================================================
# /settings
# =============================================================================
@app.on_message(filters.command("settings") & filters.private)
async def settings_command(client, message):
    """Handle the /settings command."""
    if message.chat.id == OWNER:
        await message.delete()
        await send_settings(client, message, message.id, True)


# =============================================================================
# /help
# =============================================================================
@app.on_message(filters.command("help") & filters.private)
async def help_command(client, message):
    """Handle the /help command."""
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    help_text = """
**📖 Leechbot Help Menu**

**📥 Download Commands:**
/start — Start The Bot
/tupload — Upload To Telegram
/gdupload — Mirror To Google Drive
/drupload — Upload Local Directory
/ytupload — Download With Yt-Dlp

**📋 Queue & Control:**
/queue — View Download Queue
/cancel — Cancel Current Task
/cancel_all — Cancel & Clear Queue

**⚙️ Settings:**
/settings — Bot Settings Menu
/setname — Set Custom Filename
/zipaswd — Set Zip Password
/unzipaswd — Set Unzip Password
/format — Set YT-DLP Quality
/speed — Set Bandwidth Limit

**🛠️ Admin:**
/admin — Manage Allowed Users
/broadcast — Send File To Multiple Chats
/stats — System Statistics
/help — Show This Help Message

**🍪 YT-DLP Auth (auto PO tokens + cookie fallback):**
/cookies — Check auth status & setup guide
/setcookies — Upload cookies.txt as fallback
/clearcookies — Delete stored cookies

**🖼️ Thumbnail:**
Send Any Image To Set It As Thumbnail

**💡 Supported Sites:**
Direct Links, Google Drive, Telegram
YouTube, Facebook, Instagram & 2000+ sites
Terabox, Mega, Pixeldrain, Mediafire
"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📂 GitHub Repository ✨", url="https://github.com/Shineii86/LeechBot")],
        [
            InlineKeyboardButton("🔔 Updates", url="https://t.me/MaximXBots"),
            InlineKeyboardButton("Support 💬", url="https://t.me/MaximXGroup"),
        ],
        [InlineKeyboardButton("🧑‍💻 Developer ✨", url="https://t.me/Shineii86")],
    ])

    msg = await message.reply_text(help_text, reply_markup=keyboard)
    await message_deleter(message, msg)


# =============================================================================
# /setname
# =============================================================================
@app.on_message(filters.command("setname") & filters.private)
async def setname_command(client, message):
    """Handle the /setname command."""
    if len(message.command) < 2:
        msg = await message.reply_text(
            "**⚠️ Usage:**\n`/setname <filename.extension>`\n\n**Example:**\n`/setname myvideo.mp4`",
            quote=True,
        )
    else:
        BOT.Options.custom_name = " ".join(message.command[1:])
        msg = await message.reply_text(
            f"**✅ Custom Name Set:**\n`{BOT.Options.custom_name}`",
            quote=True,
        )
    await message_deleter(message, msg)


# =============================================================================
# /zipaswd
# =============================================================================
@app.on_message(filters.command("zipaswd") & filters.private)
async def zipaswd_command(client, message):
    """Handle the /zipaswd command."""
    if len(message.command) != 2:
        msg = await message.reply_text(
            "**⚠️ Usage:**\n`/zipaswd <password>`\n\n**Example:**\n`/zipaswd mypassword123`",
            quote=True,
        )
    else:
        BOT.Options.zip_pswd = message.command[1]
        msg = await message.reply_text("**🔐 Zip Password Set Successfully**", quote=True)
    await message_deleter(message, msg)


# =============================================================================
# /unzipaswd
# =============================================================================
@app.on_message(filters.command("unzipaswd") & filters.private)
async def unzipaswd_command(client, message):
    """Handle the /unzipaswd command."""
    if len(message.command) != 2:
        msg = await message.reply_text(
            "**⚠️ Usage:**\n`/unzipaswd <password>`\n\n**Example:**\n`/unzipaswd mypassword123`",
            quote=True,
        )
    else:
        BOT.Options.unzip_pswd = message.command[1]
        msg = await message.reply_text("**🔓 Unzip Password Set Successfully**", quote=True)
    await message_deleter(message, msg)


# =============================================================================
# /stats
# =============================================================================
@app.on_message(filters.command("stats") & filters.private)
async def stats_command(client, message):
    """Handle the /stats command."""
    stats_text = f"**📊 Bot Statistics**{sysINFO()}"
    msg = await message.reply_text(stats_text, quote=True)
    await message_deleter(message, msg)


# =============================================================================
# /cancel
# =============================================================================
@app.on_message(filters.command("cancel") & filters.private)
async def cancel_command(client, message):
    """Handle the /cancel command."""
    if BOT.State.task_going:
        await cancelTask("User cancelled the task")
        msg = await message.reply_text("**🚫 Task Cancelled**", quote=True)
    else:
        msg = await message.reply_text("**⚠️ No Active Task To Cancel**", quote=True)
    await message_deleter(message, msg)


# =============================================================================
# /queue
# =============================================================================
@app.on_message(filters.command("queue") & filters.private)
async def queue_command(client, message):
    """Show the download queue."""
    if message.chat.id != OWNER and message.chat.id not in config.ALLOWED_USERS:
        return

    items = Queue.list_items()
    current = Queue.current

    text = "**📋 Download Queue**\n\n"
    if current:
        text += f"**🔄 Active:** `{current.get('name', 'Unknown')}`\n"
        text += f"**📦 Links:** `{len(current.get('links', []))}`\n\n"
    else:
        text += "**🔄 Active:** `None`\n\n"

    if items:
        for item in items:
            text += f"{item}\n"
        text += f"\n**📊 Total Queued:** `{Queue.size()}`"
    else:
        text += "**📭 Queue is empty**"

    stats_text = "\n\n**📈 Session Stats:**\n"
    stats_text += f"`•` Completed: `{BotStats.total_tasks}`\n"
    stats_text += f"`•` Failed: `{BotStats.failed_tasks}`\n"
    stats_text += f"`•` Downloaded: `{BotStats.total_downloaded}`\n"
    stats_text += f"`•` Uploaded: `{BotStats.total_uploaded}`"

    msg = await message.reply_text(text + stats_text, quote=True)
    await message_deleter(message, msg)


# =============================================================================
# /format
# =============================================================================
@app.on_message(filters.command("format") & filters.private)
async def format_command(client, message):
    """Set YT-DLP download format/quality."""
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    if message.chat.id != OWNER:
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎬 Best Quality", callback_data="fmt-bestvideo+bestaudio/best")],
        [
            InlineKeyboardButton("📺 1080p", callback_data="fmt-bestvideo[height<=1080]+bestaudio/best[height<=1080]"),
            InlineKeyboardButton("📺 720p", callback_data="fmt-bestvideo[height<=720]+bestaudio/best[height<=720]"),
        ],
        [
            InlineKeyboardButton("📱 480p", callback_data="fmt-bestvideo[height<=480]+bestaudio/best[height<=480]"),
            InlineKeyboardButton("📱 360p", callback_data="fmt-bestvideo[height<=360]+bestaudio/best[height<=360]"),
        ],
        [InlineKeyboardButton("🎵 Audio Only", callback_data="fmt-bestaudio/best")],
        [InlineKeyboardButton("❰ Back", callback_data="back")],
    ])

    current_fmt = getattr(BOT.Setting, "ytdl_format", "bestvideo+bestaudio/best")
    await message.reply_text(
        f"**🎬 YT-DLP Format Selection**\n\n"
        f"**Current:** `{current_fmt}`\n\n"
        f"Choose the quality for video downloads:\n\n"
        f"💡 **Tip:** Lower quality = faster download & smaller size",
        reply_markup=keyboard,
        quote=True,
    )


# =============================================================================
# /speed
# =============================================================================
@app.on_message(filters.command("speed") & filters.private)
async def speed_command(client, message):
    """Set bandwidth limit for downloads."""
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    if message.chat.id != OWNER:
        return

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🚀 Unlimited", callback_data="spd-"),
            InlineKeyboardButton("💨 50 MB/s", callback_data="spd-50M"),
        ],
        [
            InlineKeyboardButton("⚡ 20 MB/s", callback_data="spd-20M"),
            InlineKeyboardButton("🔌 10 MB/s", callback_data="spd-10M"),
        ],
        [
            InlineKeyboardButton("🐢 5 MB/s", callback_data="spd-5M"),
            InlineKeyboardButton("🐌 1 MB/s", callback_data="spd-1M"),
        ],
        [InlineKeyboardButton("❰ Back", callback_data="back")],
    ])

    current = config.BANDWIDTH_LIMIT or "Unlimited"
    await message.reply_text(
        f"**⚡ Bandwidth Limiter**\n\n"
        f"**Current Limit:** `{current}`\n\n"
        f"Set maximum download speed to avoid saturating your connection.\n"
        f"This applies to aria2c and YT-DLP downloads.",
        reply_markup=keyboard,
        quote=True,
    )


# =============================================================================
# /broadcast
# =============================================================================
@app.on_message(filters.command("broadcast") & filters.private)
async def broadcast_command(client, message):
    """Send the last uploaded file to multiple chats."""
    from asyncio import sleep
    from leechbot.utility.variables import Transfer

    if message.chat.id != OWNER:
        return

    if not BOT.State.task_going and not Transfer.sent_file:
        msg = await message.reply_text(
            "**⚠️ No files to broadcast.**\n\nUpload something first with `/tupload`.",
            quote=True,
        )
        await message_deleter(message, msg)
        return

    if len(message.command) < 2:
        msg = await message.reply_text(
            "**📢 Broadcast Usage:**\n\n"
            "`/broadcast chat_id1, chat_id2, ...`\n\n"
            "**Example:**\n"
            "`/broadcast -1001234567890, -1009876543210`\n\n"
            "💡 Send the last uploaded file to multiple chats.",
            quote=True,
        )
        await message_deleter(message, msg)
        return

    chat_ids = []
    for cid in " ".join(message.command[1:]).split(","):
        cid = cid.strip()
        try:
            chat_ids.append(int(cid))
        except ValueError:
            pass

    if not chat_ids:
        msg = await message.reply_text("**⚠️ No valid chat IDs provided.**", quote=True)
        await message_deleter(message, msg)
        return

    last_file = Transfer.sent_file[-1] if Transfer.sent_file else None
    if not last_file:
        msg = await message.reply_text("**⚠️ No file to broadcast.**", quote=True)
        await message_deleter(message, msg)
        return

    msg = await message.reply_text(f"**📢 Broadcasting to {len(chat_ids)} chats...**", quote=True)

    success = 0
    failed = 0
    for chat_id in chat_ids:
        try:
            await last_file.copy(chat_id)
            success += 1
        except Exception as e:
            logger.error(f"Broadcast to {chat_id} failed: {e}")
            failed += 1
        await sleep(1)

    await msg.edit_text(
        f"**📢 Broadcast Complete**\n\n"
        f"✅ Success: `{success}`\n"
        f"❌ Failed: `{failed}`\n"
        f"📊 Total: `{len(chat_ids)}`"
    )


# =============================================================================
# /admin
# =============================================================================
@app.on_message(filters.command("admin") & filters.private)
async def admin_command(client, message):
    """Admin panel for managing allowed users."""
    if message.chat.id != OWNER:
        return

    if len(message.command) < 2:
        users_list = "\n".join([f"`•` `{uid}`" for uid in config.ALLOWED_USERS]) or "`None`"
        msg = await message.reply_text(
            f"**👥 Admin Panel**\n\n"
            f"**Allowed Users:**\n{users_list}\n\n"
            f"**Commands:**\n"
            f"`/admin add <user_id>` — Allow a user\n"
            f"`/admin remove <user_id>` — Deny a user\n"
            f"`/admin list` — Show allowed users",
            quote=True,
        )
        await message_deleter(message, msg)
        return

    action = message.command[1].lower()

    if action == "add" and len(message.command) >= 3:
        try:
            new_uid = int(message.command[2])
            if new_uid not in config.ALLOWED_USERS:
                config.ALLOWED_USERS.append(new_uid)
                msg = await message.reply_text(f"**✅ User `{new_uid}` added to allowed list.**", quote=True)
            else:
                msg = await message.reply_text(f"**ℹ️ User `{new_uid}` is already allowed.**", quote=True)
        except ValueError:
            msg = await message.reply_text("**⚠️ Invalid user ID.**", quote=True)

    elif action == "remove" and len(message.command) >= 3:
        try:
            rm_uid = int(message.command[2])
            if rm_uid in config.ALLOWED_USERS:
                config.ALLOWED_USERS.remove(rm_uid)
                msg = await message.reply_text(f"**✅ User `{rm_uid}` removed from allowed list.**", quote=True)
            else:
                msg = await message.reply_text(f"**ℹ️ User `{rm_uid}` is not in the allowed list.**", quote=True)
        except ValueError:
            msg = await message.reply_text("**⚠️ Invalid user ID.**", quote=True)

    elif action == "list":
        users_list = "\n".join([f"`•` `{uid}`" for uid in config.ALLOWED_USERS]) or "`None`"
        msg = await message.reply_text(f"**👥 Allowed Users:**\n{users_list}", quote=True)

    else:
        msg = await message.reply_text("**⚠️ Usage:** `/admin add|remove|list [user_id]`", quote=True)

    await message_deleter(message, msg)


# =============================================================================
# /cookies — Show YT-DLP authentication status
# =============================================================================
@app.on_message(filters.command("cookies") & filters.private)
async def cookies_command(client, message):
    """Show current YT-DLP authentication status."""
    import os
    import subprocess
    from leechbot.utility.variables import Paths

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

**How it works:**
1. **PO Token Plugin** (auto) — generates tokens in the background, no user action needed
2. **Cookies** (manual fallback) — only needed if PO tokens stop working

**If YouTube still fails:**
Upload a `cookies.txt` file here as a backup:
1. Install [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) (Chrome)
2. Go to `youtube.com` → click extension → **Export**
3. Send the file here

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

**How to get it:**

**Chrome / Edge / Brave:**
1. Install extension: [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
2. Go to `https://www.youtube.com` (make sure you're logged in)
3. Click the extension icon → **Export** → saves `cookies.txt`
4. Upload that file here

**Firefox:**
1. Install extension: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)
2. Go to `https://www.youtube.com` (logged in)
3. Click extension → **Export** → upload here

⚠️ **Security:** Cookies contain your session tokens. The bot stores them locally and never shares them. Delete with `/clearcookies` if needed."""

    msg = await message.reply_text(text, quote=True, disable_web_page_preview=True)
    await message_deleter(message, msg)


# =============================================================================
# /clearcookies — Delete uploaded cookies file
# =============================================================================
@app.on_message(filters.command("clearcookies") & filters.private)
async def clearcookies_command(client, message):
    """Delete the uploaded cookies file."""
    import os
    from leechbot.utility.variables import Paths

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


# =============================================================================
# /cancel_all
# =============================================================================
@app.on_message(filters.command("cancel_all") & filters.private)
async def cancel_all_command(client, message):
    """Cancel current task and clear the queue."""
    if message.chat.id != OWNER:
        return

    Queue.clear()

    if BOT.State.task_going:
        await cancelTask("User cancelled all tasks")
        msg = await message.reply_text("**🚫 All tasks cancelled and queue cleared.**", quote=True)
    else:
        msg = await message.reply_text("**📭 Queue cleared. No active task to cancel.**", quote=True)

    await message_deleter(message, msg)
