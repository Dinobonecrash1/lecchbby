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
All /command handlers for the bot.
"""

import logging
import os
import signal
import sys
from datetime import datetime
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from leechbot import app, OWNER, LOG_FILE
from leechbot.utility.variables import BOT, BotStats, BotTimes, Transfer, Messages, Queue, Paths
from leechbot.utility.task_manager import task_starter
from leechbot.utility.helper import (
    send_settings, message_deleter, format_stats, sysINFO, getTime, sizeUnit,
)
from leechbot.utility.handler import cancelTask
import config

logger = logging.getLogger(__name__)

# =============================================================================
# /start
# =============================================================================
WELCOME_TEXT = """**🤖 LeechBot** — Advanced Telegram File Transloader

◈ Powerful · Fast · Secure
◈ Download from 2000+ sources
◈ Upload to Telegram or Google Drive

**📥 Send any link to start downloading.**

Tap a button below to explore:"""


def _start_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📖 Help", callback_data="help_main"),
            InlineKeyboardButton("ℹ️ About", callback_data="about"),
        ],
        [InlineKeyboardButton("🤖 Bot Settings ⚙️", callback_data="settings_menu")],
        [
            InlineKeyboardButton("📂 GitHub", url="https://github.com/Shineii86/LeechBot"),
            InlineKeyboardButton("🔔 Updates", url="https://t.me/MaximXBots"),
        ],
        [InlineKeyboardButton("💬 Support", url="https://t.me/MaximXGroup")],
    ])


async def _send_welcome(client, message, edit: bool = False):
    if edit:
        try:
            await message.edit_text(
                WELCOME_TEXT,
                reply_markup=_start_keyboard(),
                disable_web_page_preview=True,
            )
            return
        except Exception:
            pass
    try:
        await message.delete()
    except Exception:
        pass
    await message.reply_text(
        WELCOME_TEXT,
        reply_markup=_start_keyboard(),
        disable_web_page_preview=True,
    )


@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    await _send_welcome(client, message, edit=False)

# =============================================================================
# /help
# =============================================================================
@app.on_message(filters.command("help") & filters.private)
async def help_command(client, message):
    help_text = """**📖 LeechBot Help Menu**

─── Download Commands ───
• `/start` — Start the bot
• `/tupload` — Upload to Telegram
• `/gdupload` — Mirror to Google Drive
• `/drupload` — Upload local directory
• `/ytupload` — Download with YT-DLP
• `/glupload` — Download image galleries
• `/preview` — Dry-run a gallery URL to see what would be downloaded

─── Queue & Control ───
• `/queue` — View download queue
• `/cancel` — Cancel current task
• `/cancel_all` — Cancel & clear queue

─── Settings ───
• `/settings` — Bot settings menu
• `/setname` — Set custom filename
• `/zipaswd` — Set zip password
• `/unzipaswd` — Set unzip password
• `/format` — Set YT-DLP quality
• `/formats` — List available formats for a video URL
• `/speed` — Set bandwidth limit

─── Admin ───
• `/admin` — Manage allowed users
• `/broadcast` — Send file to multiple chats
• `/stats` — Bot & system statistics
• `/update` — Check for updates
• `/help` — Show this help message

─── YT-DLP Auth ───
• `/cookies` — Check auth status & setup guide
• `/setcookies` — Upload cookies.txt as fallback
• `/clearcookies` — Delete stored cookies

**🖼️ Thumbnail:** Send any image to set as thumbnail

─── Supported Sites ───
Direct Links, Google Drive
YouTube, Facebook & 2000+ sites
Terabox, Mega, Pixeldrain, Mediafire"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📂 GitHub Repository ✨", url="https://github.com/Shineii86/LeechBot")],
        [
            InlineKeyboardButton("🔔 Updates", url="https://t.me/MaximXBots"),
            InlineKeyboardButton("Support 💬", url="https://t.me/MaximXGroup"),
        ],
        [InlineKeyboardButton("🧑‍💻 Developer ✨", url="https://t.me/Shineii86")],
    ])

    msg = await message.reply_text(help_text, reply_markup=keyboard, quote=True)
    await message_deleter(message, msg)

# =============================================================================
# /settings
# =============================================================================
@app.on_message(filters.command("settings") & filters.private)
async def settings_command(client, message):
    if message.chat.id == OWNER:
        await message.delete()
        await send_settings(client, message, message.id, True)

# =============================================================================
# /format
# =============================================================================
@app.on_message(filters.command("format") & filters.private)
async def format_command(client, message):
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
# /tupload
# =============================================================================
@app.on_message(filters.command("tupload") & filters.private)
async def telegram_upload_command(client, message):
    BOT.Mode.mode = "leech"
    BOT.Mode.ytdl = False
    BOT.Mode.gallery = False

    text = """**⚡ Send Download Link(s)** 🔗

📋 **Follow The Pattern Below:**

<code>https://example.com/file1.mp4
https://example.com/file2.mp4
[Custom Name.mp4]
{Zip Password}
(Unzip Password)</code>

─── Tips ───
• Multiple Links Supported
• Use `[ ]` For Custom Filename
• Use `{ }` For Zip Password
• Use `( )` For Extract Password"""
    src_request_msg = await task_starter(message, text)
    BOT._src_request_msg = src_request_msg

# =============================================================================
# /gdupload
# =============================================================================
@app.on_message(filters.command("gdupload") & filters.private)
async def gdrive_upload_command(client, message):
    BOT.Mode.mode = "mirror"
    BOT.Mode.ytdl = False
    BOT.Mode.gallery = False

    text = """**♻️ Send Download Link(s)** 🔗

📋 **Follow The Pattern Below:**

<code>https://example.com/file1.mp4
https://example.com/file2.mp4
[Custom Name.mp4]
{Zip Password}
(Unzip Password)</code>

─── Tips ───
• Multiple Links Supported
• Files Will Be Mirrored To Your GDrive
• Make Sure GDrive Is Mounted"""
    src_request_msg = await task_starter(message, text)
    BOT._src_request_msg = src_request_msg

# =============================================================================
# /drupload
# =============================================================================
@app.on_message(filters.command("drupload") & filters.private)
async def directory_upload_command(client, message):
    BOT.Mode.mode = "dir-leech"
    BOT.Mode.ytdl = False
    BOT.Mode.gallery = False

    text = """**📁 Send Folder Path**

📋 **Example:**

<code>/home/user/Downloads/myfolder</code>

─── Note ───
• Provide Absolute Path To The Folder
• Ensure The Bot Has Read Permissions"""
    src_request_msg = await task_starter(message, text)
    BOT._src_request_msg = src_request_msg

# =============================================================================
# /ytupload
# =============================================================================
@app.on_message(filters.command("ytupload") & filters.private)
async def ytdl_upload_command(client, message):
    BOT.Mode.mode = "leech"
    BOT.Mode.ytdl = True
    BOT.Mode.gallery = False

    text = """**🏮 Send YT-DLP Link(s)** 🔗

📋 **Follow The Pattern Below:**

<code>https://youtube.com/watch?v=xxxxx
https://youtu.be/xxxxx
[Custom Name.mp4]
{Zip Password}</code>

─── Supported Sites ───
• YouTube, Facebook
• Twitter, TikTok, Vimeo, Dailymotion
• And 2000+ more sites"""
    src_request_msg = await task_starter(message, text)
    BOT._src_request_msg = src_request_msg

# =============================================================================
# /glupload
# =============================================================================
@app.on_message(filters.command("glupload") & filters.private)
async def gallery_upload_command(client, message):
    BOT.Mode.mode = "leech"
    BOT.Mode.ytdl = False
    BOT.Mode.gallery = True

    text = """**📸 Send Gallery Link(s)** 🖼️

📋 **Follow The Pattern Below:**

<code>https://twitter.com/username
https://pinterest.com/user/board
https://pixiv.net/users/123456
[Custom Name]
{Zip Password}</code>

─── Supported Sites ───
• Twitter / X, Pinterest
• Pixiv, DeviantArt, ArtStation, Flickr
• Reddit, Tumblr, Imgur, TikTok
• Bluesky, Newgrounds, Danbooru
• And 100+ more gallery sites

─── Tips ───
• Multiple Links Supported
• Use `[ ]` For Custom Folder Name
• Use `{ }` For Zip Password"""
    src_request_msg = await task_starter(message, text)
    BOT._src_request_msg = src_request_msg

# =============================================================================
# /setname
# =============================================================================
@app.on_message(filters.command("setname") & filters.private)
async def setname_command(client, message):
    if len(message.command) < 2:
        msg = await message.reply_text(
            "**⚠️ Usage:** `/setname <filename>`\n\n"
            "**📝 Example:** `/setname movie.mp4`",
            quote=True,
        )
    else:
        BOT.Options.file_name = " ".join(message.command[1:])
        msg = await message.reply_text(f"**📝 Filename set to:** `{BOT.Options.file_name}` ✓", quote=True)
    await message_deleter(message, msg)

# =============================================================================
# /formats <url>
# =============================================================================
@app.on_message(filters.command("formats") & filters.private)
async def formats_command(client, message):
    from leechbot.downloader.ytdl import list_formats

    if message.chat.id != OWNER:
        return

    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        msg = await message.reply_text(
            "**⚠️ Usage:** `/formats <url>`\n\n"
            "Example: `/formats https://youtube.com/watch?v=...`",
            quote=True,
        )
        await message_deleter(message, msg)
        return

    url = parts[1].strip()
    status = await message.reply_text("**🔍 Fetching available formats...**", quote=True)
    try:
        text = await list_formats(url)
        await status.edit_text(text, disable_web_page_preview=True)
    except Exception as e:
        logger.exception("formats_command failed")
        await status.edit_text(f"**❌ Failed to fetch formats:** `{e}`")
    await message_deleter(message, status)

# =============================================================================
# /preview <url>
# =============================================================================
@app.on_message(filters.command("preview") & filters.private)
async def preview_command(client, message):
    from leechbot.downloader.gallery import list_gallery_content

    if message.chat.id != OWNER:
        return

    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        msg = await message.reply_text(
            "**⚠️ Usage:** `/preview <gallery_url>`\n\n"
            "Example: `/preview https://imgur.com/a/abc123`",
            quote=True,
        )
        await message_deleter(message, msg)
        return

    url = parts[1].strip()
    status = await message.reply_text("**🔍 Inspecting gallery...**", quote=True)
    try:
        text = await list_gallery_content(url)
        await status.edit_text(text, disable_web_page_preview=True)
    except Exception as e:
        logger.exception("preview_command failed")
        await status.edit_text(f"**❌ Preview failed:** `{e}`")
    await message_deleter(message, status)

# =============================================================================
# /zipaswd
# =============================================================================
@app.on_message(filters.command("zipaswd") & filters.private)
async def zipaswd_command(client, message):
    if len(message.command) != 2:
        msg = await message.reply_text(
            "**⚠️ Usage**\n\n"
            "\n"
            "`/zipaswd <password>`\n"
            "\n\n"
            "**📝 Example:** `/zipaswd mypassword123`",
            quote=True,
        )
    else:
        BOT.Options.zip_pswd = message.command[1]
        msg = await message.reply_text("**🔐 Zip Password Set Successfully** ✓", quote=True)
    await message_deleter(message, msg)

# =============================================================================
# /unzipaswd
# =============================================================================
@app.on_message(filters.command("unzipaswd") & filters.private)
async def unzipaswd_command(client, message):
    if len(message.command) != 2:
        msg = await message.reply_text(
            "**⚠️ Usage**\n\n"
            "\n"
            "`/unzipaswd <password>`\n"
            "\n\n"
            "**📝 Example:** `/unzipaswd mypassword123`",
            quote=True,
        )
    else:
        BOT.Options.unzip_pswd = message.command[1]
        msg = await message.reply_text("**🔓 Unzip Password Set Successfully** ✓", quote=True)
    await message_deleter(message, msg)

# =============================================================================
# /ping
# =============================================================================
@app.on_message(filters.command("ping") & filters.private)
async def ping_command(client, message):
    start = datetime.now()
    msg = await message.reply_text("**🏓 Pinging...**", quote=True)
    latency_ms = (datetime.now() - start).total_seconds() * 1000
    uptime = getTime(int((datetime.now() - BotStats.start_time).total_seconds()))

    if latency_ms < 200:
        quality = "Excellent"
    elif latency_ms < 500:
        quality = "Good"
    elif latency_ms < 1000:
        quality = "Average"
    else:
        quality = "Poor"

    pct = max(5, min(100, int((1 - latency_ms / 2000) * 100)))
    filled = pct // 5
    empty = 20 - filled
    bar = f"{'█' * filled}{'░' * empty}"

    server_status = "Online" if latency_ms < 5000 else "Slow"

    ping_text = f"""```
┌───────────────────────────────┐
        🏓  PONG
├───────────────────────────────┤
  ⚡  Latency   →  {latency_ms:.1f} ms
  📊  Quality   →  {quality}
  {bar}  {pct}%
  ⏱️  Uptime    →  {uptime}
  🤖  Version   →  v{config.VERSION}
  📡  Server    →  {server_status}
└───────────────────────────────┘
```"""
    await msg.edit(ping_text, disable_web_page_preview=True)
    await message_deleter(message, msg)

# =============================================================================
# /status
# =============================================================================
@app.on_message(filters.command("status") & filters.private)
async def status_command(client, message):
    if message.chat.id != OWNER and message.chat.id not in config.ALLOWED_USERS:
        return

    if BOT.State.task_going:
        task_elapsed = ""
        try:
            secs = (datetime.now() - BotTimes.task_start).total_seconds()
            task_elapsed = getTime(int(secs))
        except Exception:
            pass

        down_total = sizeUnit(sum(Transfer.down_bytes))
        up_total = sizeUnit(sum(Transfer.up_bytes))
        remaining = sizeUnit(max(Transfer.total_down_size - sum(Transfer.down_bytes), 0))

        mode = f"{BOT.Mode.type.capitalize()} {BOT.Mode.mode.capitalize()}"
        if BOT.Mode.ytdl:
            mode += " (yt-dlp)"
        elif BOT.Mode.gallery:
            mode += " (gallery-dl)"

        active_section = f"""**🎯 Active Task**

• **Mode:** `{mode}`
• **Running:** `{task_elapsed}`
• **Downloaded:** `{down_total}` ({len(Transfer.down_bytes)} chunks)
• **Uploaded:** `{up_total}` ({len(Transfer.up_bytes)} chunks)
• **Remaining:** `{remaining}`
• **Files sent:** `{len(Transfer.sent_file)}`"""
        if Messages.status_head:
            head_clean = Messages.status_head.replace("**", "").replace("\n", " · ")[:120]
            active_section += f"\n• **Current:** `{head_clean}`"
    else:
        active_section = "**🎯 Active Task**\n\n• `No task running`"

    pending = Queue.pending
    current = Queue.current
    if pending or current:
        queue_lines = [f"**📋 Queue** (`{pending} pending`)"]
        if current:
            link = current["links"][0][:60] + ("..." if len(current["links"][0]) > 60 else "")
            queue_lines.append(f"• 🔄 **Current:** `{link}` ({len(current['links'])} link(s))")
        for line in Queue.list_items()[:5]:
            queue_lines.append(line)
        if pending > 5:
            queue_lines.append(f"• _... and {pending - 5} more_")
        queue_section = "\n".join(queue_lines)
    else:
        queue_section = "**📋 Queue**\n\n• `Empty`"

    status_text = f"{active_section}\n\n{queue_section}"
    msg = await message.reply_text(status_text, quote=True)
    await message_deleter(message, msg)

# =============================================================================
# /stats
# =============================================================================
@app.on_message(filters.command("stats") & filters.private)
async def stats_command(client, message):
    stats_text = f"{format_stats()}{sysINFO()}"
    msg = await message.reply_text(stats_text, quote=True)
    await message_deleter(message, msg)

# =============================================================================
# /queue
# =============================================================================
@app.on_message(filters.command("queue") & filters.private)
async def queue_command(client, message):
    if message.chat.id != OWNER and message.chat.id not in config.ALLOWED_USERS:
        return

    items = Queue.list_items()
    current = Queue.current

    text = "**📋 Download Queue**\n\n"
    if current:
        text += f"• 🔄 **Active:** `{current.get('name', 'Unknown')}`\n"
        text += f"• 📦 **Links:** `{len(current.get('links', []))}`\n\n"
    else:
        text += "**🔄 Active:** `None`\n\n"

    if items:
        for item in items:
            text += f"{item}\n"
        text += f"\n**📊 Total Queued:** `{Queue.size()}`"
    else:
        text += "**📭 Queue is empty**"

    stats_text = "\n\n─── Session Stats ───\n"
    stats_text += f"• Completed: `{BotStats.total_tasks}`\n"
    stats_text += f"• Failed: `{BotStats.failed_tasks}`\n"
    stats_text += f"• Downloaded: `{BotStats.total_downloaded}`\n"
    stats_text += f"• Uploaded: `{BotStats.total_uploaded}`"

    msg = await message.reply_text(text + stats_text, quote=True)
    await message_deleter(message, msg)

# =============================================================================
# /cancel
# =============================================================================
@app.on_message(filters.command("cancel") & filters.private)
async def cancel_command(client, message):
    if BOT.State.task_going:
        await cancelTask("User cancelled the task")
        msg = await message.reply_text("**🚫 Task Cancelled** ✓", quote=True)
    else:
        msg = await message.reply_text("**ℹ️ No Active Task To Cancel**", quote=True)
    await message_deleter(message, msg)

# =============================================================================
# /cancel_all
# =============================================================================
@app.on_message(filters.command("cancel_all") & filters.private)
async def cancel_all_command(client, message):
    if message.chat.id != OWNER:
        return

    Queue.clear()

    if BOT.State.task_going:
        await cancelTask("User cancelled all tasks")
        msg = await message.reply_text("**🚫 All tasks cancelled and queue cleared.**", quote=True)
    else:
        msg = await message.reply_text("**📭 Queue cleared. No active task to cancel.**", quote=True)

    await message_deleter(message, msg)

# =============================================================================
# /admin
# =============================================================================
@app.on_message(filters.command("admin") & filters.private)
async def admin_command(client, message):
    if message.chat.id != OWNER:
        return

    if len(message.command) < 2:
        users_list = "\n".join([f"• `{uid}`" for uid in config.ALLOWED_USERS]) or "`None`"
        msg = await message.reply_text(
            f"**👥 Admin Panel**\n\n"
            f"**Allowed Users:**\n{users_list}\n\n"
            f"\n"
            f"`/admin add <user_id>` — Allow a user\n"
            f"`/admin remove <user_id>` — Deny a user\n"
            f"`/admin list` — Show allowed users\n"
            f"",
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
                msg = await message.reply_text(f"✅ User `{new_uid}` added to allowed list ✓", quote=True)
            else:
                msg = await message.reply_text(f"ℹ️ User `{new_uid}` is already allowed", quote=True)
        except ValueError:
            msg = await message.reply_text("⚠️ Invalid user ID", quote=True)

    elif action == "remove" and len(message.command) >= 3:
        try:
            rm_uid = int(message.command[2])
            if rm_uid in config.ALLOWED_USERS:
                config.ALLOWED_USERS.remove(rm_uid)
                msg = await message.reply_text(f"✅ User `{rm_uid}` removed from allowed list ✓", quote=True)
            else:
                msg = await message.reply_text(f"ℹ️ User `{rm_uid}` is not in the allowed list", quote=True)
        except ValueError:
            msg = await message.reply_text("⚠️ Invalid user ID", quote=True)

    elif action == "list":
        users_list = "\n".join([f"• `{uid}`" for uid in config.ALLOWED_USERS]) or "`None`"
        msg = await message.reply_text(f"**👥 Allowed Users:**\n{users_list}", quote=True)

    else:
        msg = await message.reply_text("**⚠️ Usage:** `/admin add|remove|list [user_id]`", quote=True)

    await message_deleter(message, msg)

# =============================================================================
# /broadcast
# =============================================================================
@app.on_message(filters.command("broadcast") & filters.private)
async def broadcast_command(client, message):
    from asyncio import sleep

    if message.chat.id != OWNER:
        return

    if not BOT.State.task_going and not Transfer.sent_file:
        msg = await message.reply_text(
            "**ℹ️ No files to broadcast.**\n\nUpload something first with `/tupload`.",
            quote=True,
        )
        await message_deleter(message, msg)
        return

    if len(message.command) < 2:
        msg = await message.reply_text(
            "**📢 Broadcast Usage**\n\n"
            "\n"
            "`/broadcast chat_id1, chat_id2, ...`\n"
            "\n\n"
            "**📝 Example:**\n"
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
        f"📢 **Broadcast Complete**\n\n"
        f"• ✅ **Success:** `{success}`\n"
        f"• ❌ **Failed:** `{failed}`\n"
        f"• 📊 **Total:** `{len(chat_ids)}`"
    )

# =============================================================================
# /cookies
# =============================================================================
@app.on_message(filters.command("cookies") & filters.private)
async def cookies_command(client, message):
    import subprocess

    cookies_file = getattr(config, "YTDL_COOKIES_FILE", "")
    browser_cookies = getattr(config, "YTDL_BROWSER_COOKIES", "")
    default_path = Paths.COOKIE_FILE

    file_ok = cookies_file and os.path.isfile(cookies_file)
    uploaded_ok = os.path.isfile(default_path)
    browser_ok = bool(browser_cookies)

    pot_installed = False
    try:
        result = subprocess.run(
            ["pip", "show", "bgutil-ytdlp-pot-provider"],
            capture_output=True, text=True, timeout=10
        )
        pot_installed = result.returncode == 0
    except Exception:
        pass

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
# /setcookies
# =============================================================================
@app.on_message(filters.command("setcookies") & filters.private)
async def setcookies_command(client, message):
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
# /clearcookies
# =============================================================================
@app.on_message(filters.command("clearcookies") & filters.private)
async def clearcookies_command(client, message):
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
# /restart
# =============================================================================
@app.on_message(filters.command("restart") & filters.private)
async def restart_command(client, message):
    if message.chat.id != OWNER:
        return

    if BOT.State.task_going:
        try:
            await cancelTask("Bot restarting")
        except Exception:
            pass

    restart_text = (
        "**🔄 Restarting LeechBot...**\n\n"
        f"• **Version:** `v{config.VERSION}`\n"
        "• **Action:** Sending SIGTERM to self\n"
        "• **Wrapper:** Will respawn the process\n\n"
        "⏳ Bot will be back in 5-10 seconds."
    )
    msg = await message.reply_text(restart_text, quote=True)
    await message_deleter(message, msg)

    logger.warning(
        "🔄 Restart requested by user %s — exiting for wrapper respawn",
        message.from_user.id if message.from_user else "unknown",
    )

    import asyncio
    await asyncio.sleep(1)

    try:
        os.kill(os.getpid(), signal.SIGTERM)
    except Exception:
        sys.exit(0)

# =============================================================================
# /logs
# =============================================================================
@app.on_message(filters.command("logs") & filters.private)
async def logs_command(client, message):
    if message.chat.id != OWNER:
        return

    args = message.text.split(maxsplit=1)
    try:
        n_lines = int(args[1]) if len(args) > 1 else 30
        n_lines = max(1, min(n_lines, 100))
    except ValueError:
        n_lines = 30

    log_file = LOG_FILE or str(config.LOGS_PATH / "leechbot.log")

    if not os.path.isfile(log_file):
        msg = await message.reply_text(
            f"**📋 Logs**\n\n`Log file not found: {log_file}`\n\n"
            "_File logging may be disabled (read-only filesystem)._",
            quote=True,
        )
        await message_deleter(message, msg)
        return

    try:
        fsize = os.path.getsize(log_file)
        read_size = min(fsize, 256 * 1024)

        with open(log_file, "rb") as f:
            if fsize > read_size:
                f.seek(fsize - read_size)
                _ = f.readline()
            data = f.read().decode("utf-8", errors="replace")

        all_lines = data.splitlines()
        tail_lines = all_lines[-n_lines:]

        if not tail_lines:
            tail_lines = ["(log file is empty)"]

        log_text = (
            f"📋 Last `{len(tail_lines)}` log lines\n"
            f"`({log_file})`\n\n"
            f"```\n" + "\n".join(tail_lines) + "\n```"
        )

        if len(log_text) > 4000:
            half = (4000 - 200) // 2
            log_text = (
                f"📋 Last `{len(tail_lines)}` log lines (truncated)\n"
                f"`({log_file})`\n\n"
                f"```\n"
                + "\n".join(tail_lines[:half // 80])
                + "\n\n... [truncated] ...\n\n"
                + "\n".join(tail_lines[-(half // 80):])
                + "\n```"
            )

        msg = await message.reply_text(log_text, quote=True)
        await message_deleter(message, msg)
    except Exception as e:
        logger.error(f"Failed to read log file: {e}")
        msg = await message.reply_text(
            f"**❌ Error reading logs:**\n`{e}`", quote=True,
        )
        await message_deleter(message, msg)

# =============================================================================
# /update
# =============================================================================
@app.on_message(filters.command("update") & filters.private)
async def update_command(client, message):
    from leechbot.updater import check_for_updates, get_local_version, get_changelog_since

    if message.chat.id != OWNER:
        return

    msg = await message.reply_text("**🔄 Checking for updates...**", quote=True)

    info = check_for_updates()
    version = get_local_version()
    local = info["local"]

    if not info["available"]:
        await msg.edit_text(
            f"**✅ Already up to date!**\n\n"
            f"**Version:** `{version}`\n"
            f"**Commit:** `{local}`"
        )
        await message_deleter(message, msg)
        return

    changelog = get_changelog_since(local)
    changelog_text = f"\n\n**📋 Changes:**\n```\n{changelog[:1500]}\n```" if changelog else ""

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Update Now", callback_data="do_update"),
            InlineKeyboardButton("❌ Cancel", callback_data="close"),
        ]
    ])

    await msg.edit_text(
        f"**🔄 Update Available!**\n\n"
        f"**Current:** `{local}`\n"
        f"**Latest:** `{info['remote']}`\n"
        f"**Behind:** `{info['behind']} commits`"
        f"{changelog_text}",
        reply_markup=keyboard,
    )
