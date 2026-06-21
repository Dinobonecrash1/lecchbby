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
WELCOME_TEXT = """<b>🤖 LeechBot</b> — Advanced Telegram File Transloader

◈ Powerful · Fast · Secure
◈ Download from 2000+ sources
◈ Upload to Telegram or Google Drive

<b>📥 Send any link to start downloading.</b>

Tap a button below to explore:"""


def _start_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📖 Help", callback_data="help_main"),
            InlineKeyboardButton("ℹ️ About", callback_data="about"),
        ],
        [InlineKeyboardButton("⚙️ Bot Settings", callback_data="settings_menu")],
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
    help_text = """<b>📖 LeechBot Help Menu</b>

<b>─── Download Commands ───</b>
• /start — Start the bot
• /tupload — Upload to Telegram
• /gdupload — Mirror to Google Drive
• /drupload — Upload local directory
• /ytupload — Download with YT-DLP
• /glupload — Download image galleries
• /anime — Search &amp; download anime episodes
• /preview — Dry-run a gallery URL to see what would be downloaded

<b>─── Queue &amp; Control ───</b>
• /queue — View download queue
• /cancel — Cancel current task
• /cancel_all — Cancel &amp; clear queue

<b>─── Settings ───</b>
• /settings — Bot settings menu
• /setname — Set custom filename
• /autorename — Set auto-rename template
• /zipaswd — Set zip password
• /unzipaswd — Set unzip password
• /format — Set YT-DLP quality
• /formats — List available formats for a video URL
• /speed — Set bandwidth limit

<b>─── Admin ───</b>
• /admin — Manage allowed users
• /broadcast — Send file to multiple chats
• /stats — Bot &amp; system statistics
• /update — Check for updates
• /help — Show this help message

<b>─── YT-DLP Auth ───</b>
• /cookies — Check auth status &amp; setup guide
• /setcookies — Upload cookies.txt as fallback
• /clearcookies — Delete stored cookies

<b>🖼️ Thumbnail:</b> Send any image to set as thumbnail

<b>─── Supported Sites ───</b>
Direct Links, Google Drive
YouTube, Facebook &amp; 2000+ sites
Terabox, Mega, Pixeldrain, Mediafire"""

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📂 GitHub", url="https://github.com/Shineii86/LeechBot"),
            InlineKeyboardButton("💬 Support", url="https://t.me/MaximXGroup"),
        ],
        [
            InlineKeyboardButton("🧑‍💻 Developer", url="https://t.me/Shineii86"),
            InlineKeyboardButton("🔔 Updates", url="https://t.me/MaximXBots"),
        ],
        [InlineKeyboardButton("⌂ Home", callback_data="start_back"),
         InlineKeyboardButton("🔒 Close", callback_data="close")],
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
        f"<b>🎬 YT-DLP Format Selection</b>\n\n"
        f"<b>Current:</b> <code>{current_fmt}</code>\n\n"
        f"Choose the quality for video downloads:\n\n"
        f"💡 <b>Tip:</b> Lower quality = faster download &amp; smaller size",
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
        f"<b>⚡ Bandwidth Limiter</b>\n\n"
        f"<b>Current Limit:</b> <code>{current}</code>\n\n"
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

    text = """<b>⚡ Send Download Link(s)</b> 🔗

📋 <b>Follow The Pattern Below:</b>

<code>https://example.com/file1.mp4
https://example.com/file2.mp4
[Custom Name.mp4]
{Zip Password}
(Unzip Password)</code>

<b>─── Tips ───</b>
• Multiple Links Supported
• Use [ ] For Custom Filename
• Use { } For Zip Password
• Use ( ) For Extract Password"""
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

    text = """<b>♻️ Send Download Link(s)</b> 🔗

📋 <b>Follow The Pattern Below:</b>

<code>https://example.com/file1.mp4
https://example.com/file2.mp4
[Custom Name.mp4]
{Zip Password}
(Unzip Password)</code>

<b>─── Tips ───</b>
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

    text = """<b>📁 Send Folder Path</b>

📋 <b>Example:</b>

<code>/home/user/Downloads/myfolder</code>

<b>─── Note ───</b>
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

    text = """<b>🏮 Send YT-DLP Link(s)</b> 🔗

📋 <b>Follow The Pattern Below:</b>

<code>https://youtube.com/watch?v=xxxxx
https://youtu.be/xxxxx
[Custom Name.mp4]
{Zip Password}</code>

<b>─── Supported Sites ───</b>
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

    text = """<b>📸 Send Gallery Link(s)</b> 🖼️

📋 <b>Follow The Pattern Below:</b>

<code>https://twitter.com/username
https://pinterest.com/user/board
https://pixiv.net/users/123456
[Custom Name]
{Zip Password}</code>

<b>─── Supported Sites ───</b>
• Twitter / X, Pinterest
• Pixiv, DeviantArt, ArtStation, Flickr
• Reddit, Tumblr, Imgur, TikTok
• Bluesky, Newgrounds, Danbooru
• And 100+ more gallery sites

<b>─── Tips ───</b>
• Multiple Links Supported
• Use [ ] For Custom Folder Name
• Use { } For Zip Password"""
    src_request_msg = await task_starter(message, text)
    BOT._src_request_msg = src_request_msg

# =============================================================================
# /setname
# =============================================================================
@app.on_message(filters.command("setname") & filters.private)
async def setname_command(client, message):
    if len(message.command) < 2:
        msg = await message.reply_text(
            "<b>⚠️ Usage:</b> <code>/setname &lt;filename&gt;</code>\n\n"
            "<b>📝 Example:</b> <code>/setname movie.mp4</code>",
            quote=True,
        )
    else:
        BOT.Options.file_name = " ".join(message.command[1:])
        msg = await message.reply_text(f"<b>📝 Filename set to:</b> <code>{BOT.Options.file_name}</code> ✓", quote=True)
    await message_deleter(message, msg)

# =============================================================================
# /autorename
# =============================================================================
@app.on_message(filters.command("autorename") & filters.private)
async def autorename_command(client, message):
    if len(message.command) < 2:
        current_template = BOT.Setting.autorename_template
        status = f"<b>📝 Current Template:</b> <code>{current_template}</code>" if current_template else "<b>📝 No template set</b>"
        
        msg = await message.reply_text(
            f"<b>🏷️ Auto-Rename Template</b>\n\n"
            f"{status}\n\n"
            f"<b>⚠️ Usage:</b> <code>/autorename &lt;template&gt;</code>\n\n"
            f"<b>📝 Examples:</b>\n"
            f"• Manga: <code>/autorename [WF] [C{{chapter}}] One Piece @Webtoon_Flix</code>\n"
            f"• Anime: <code>/autorename [S{{season}} E{{episode}}] One Piece [{{quality}}] [{{audio}}]</code>\n\n"
            f"<b>💡 Note:</b> Don't put .mkv or .mp4 at the end.\n"
            f"The bot will use this template to rename your files automatically.\n\n"
            f"<b>🗑️ To clear:</b> <code>/autorename clear</code>",
            quote=True,
        )
    elif message.command[1].lower() == "clear":
        BOT.Setting.autorename_template = ""
        msg = await message.reply_text("<b>✅ Auto-rename template cleared.</b>", quote=True)
    else:
        BOT.Setting.autorename_template = " ".join(message.command[1:])
        msg = await message.reply_text(
            f"<b>🏷️ Auto-Rename Template Set</b>\n\n"
            f"<b>📝 Template:</b> <code>{BOT.Setting.autorename_template}</code>\n\n"
            f"<b>💡 The bot will use this pattern to rename files.</b>",
            quote=True,
        )
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
            "<b>⚠️ Usage:</b> <code>/formats &lt;url&gt;</code>\n\n"
            "Example: <code>/formats https://youtube.com/watch?v=...</code>",
            quote=True,
        )
        await message_deleter(message, msg)
        return

    url = parts[1].strip()
    status = await message.reply_text("<b>🔍 Fetching available formats...</b>", quote=True)
    try:
        text = await list_formats(url)
        await status.edit_text(text, disable_web_page_preview=True)
    except Exception as e:
        logger.exception("formats_command failed")
        await status.edit_text(f"<b>❌ Failed to fetch formats:</b> <code>{e}</code>")
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
            "<b>⚠️ Usage:</b> <code>/preview &lt;gallery_url&gt;</code>\n\n"
            "Example: <code>/preview https://imgur.com/a/abc123</code>",
            quote=True,
        )
        await message_deleter(message, msg)
        return

    url = parts[1].strip()
    status = await message.reply_text("<b>🔍 Inspecting gallery...</b>", quote=True)
    try:
        text = await list_gallery_content(url)
        await status.edit_text(text, disable_web_page_preview=True)
    except Exception as e:
        logger.exception("preview_command failed")
        await status.edit_text(f"<b>❌ Preview failed:</b> <code>{e}</code>")
    await message_deleter(message, status)

# =============================================================================
# /zipaswd
# =============================================================================
@app.on_message(filters.command("zipaswd") & filters.private)
async def zipaswd_command(client, message):
    if len(message.command) != 2:
        msg = await message.reply_text(
            "<b>⚠️ Usage</b>\n\n"
            "<code>/zipaswd &lt;password&gt;</code>\n\n"
            "<b>📝 Example:</b> <code>/zipaswd mypassword123</code>",
            quote=True,
        )
    else:
        BOT.Options.zip_pswd = message.command[1]
        msg = await message.reply_text("<b>🔐 Zip Password Set Successfully</b> ✓", quote=True)
    await message_deleter(message, msg)

# =============================================================================
# /unzipaswd
# =============================================================================
@app.on_message(filters.command("unzipaswd") & filters.private)
async def unzipaswd_command(client, message):
    if len(message.command) != 2:
        msg = await message.reply_text(
            "<b>⚠️ Usage</b>\n\n"
            "<code>/unzipaswd &lt;password&gt;</code>\n\n"
            "<b>📝 Example:</b> <code>/unzipaswd mypassword123</code>",
            quote=True,
        )
    else:
        BOT.Options.unzip_pswd = message.command[1]
        msg = await message.reply_text("<b>🔓 Unzip Password Set Successfully</b> ✓", quote=True)
    await message_deleter(message, msg)

# =============================================================================
# /ping
# =============================================================================
@app.on_message(filters.command("ping") & filters.private)
async def ping_command(client, message):
    start = datetime.now()
    msg = await message.reply_text("<b>🏓 Pinging...</b>", quote=True)
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

    ping_text = f"""<code>
┌───────────────────────────────┐
        🏓  PONG
├───────────────────────────────┤
  ⚡  Latency   »  {latency_ms:.1f} ms
  📊  Quality   »  {quality}
  {bar}  {pct}%
  ⏱️  Uptime    »  {uptime}
  🤖  Version   »  v{config.VERSION}
  📡  Server    »  {server_status}
└───────────────────────────────┘
</code>"""
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

        active_section = f"""<b>🎯 Active Task</b>

• <b>Mode:</b> <code>{mode}</code>
• <b>Running:</b> <code>{task_elapsed}</code>
• <b>Downloaded:</b> <code>{down_total}</code> ({len(Transfer.down_bytes)} chunks)
• <b>Uploaded:</b> <code>{up_total}</code> ({len(Transfer.up_bytes)} chunks)
• <b>Remaining:</b> <code>{remaining}</code>
• <b>Files sent:</b> <code>{len(Transfer.sent_file)}</code>"""
        if Messages.status_head:
            import re
            head_clean = re.sub(r'<[^>]+>', '', Messages.status_head).replace("\n", " · ")[:120]
            active_section += f"\n• <b>Current:</b> <code>{head_clean}</code>"
    else:
        active_section = "<b>🎯 Active Task</b>\n\n• <code>No task running</code>"

    pending = Queue.pending
    current = Queue.current
    if pending or current:
        queue_lines = [f"<b>📋 Queue</b> (<code>{pending} pending</code>)"]
        if current:
            link = current["links"][0][:60] + ("..." if len(current["links"][0]) > 60 else "")
            queue_lines.append(f"• 🔄 <b>Current:</b> <code>{link}</code> ({len(current['links'])} link(s))")
        for line in Queue.list_items()[:5]:
            queue_lines.append(line)
        if pending > 5:
            queue_lines.append(f"• _... and {pending - 5} more_")
        queue_section = "\n".join(queue_lines)
    else:
        queue_section = "<b>📋 Queue</b>\n\n• <code>Empty</code>"

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

    text = "<b>📋 Download Queue</b>\n\n"
    if current:
        text += f"• 🔄 <b>Active:</b> <code>{current.get('name', 'Unknown')}</code>\n"
        text += f"• 📦 <b>Links:</b> <code>{len(current.get('links', []))}</code>\n\n"
    else:
        text += "<b>🔄 Active:</b> <code>None</code>\n\n"

    if items:
        for item in items:
            text += f"{item}\n"
        text += f"\n<b>📊 Total Queued:</b> <code>{Queue.size()}</code>"
    else:
        text += "<b>📭 Queue is empty</b>"

    stats_text = "\n\n<b>─── Session Stats ───</b>\n"
    stats_text += f"• Completed: <code>{BotStats.total_tasks}</code>\n"
    stats_text += f"• Failed: <code>{BotStats.failed_tasks}</code>\n"
    stats_text += f"• Downloaded: <code>{BotStats.total_downloaded}</code>\n"
    stats_text += f"• Uploaded: <code>{BotStats.total_uploaded}</code>"

    msg = await message.reply_text(text + stats_text, quote=True)
    await message_deleter(message, msg)

# =============================================================================
# /cancel
# =============================================================================
@app.on_message(filters.command("cancel") & filters.private)
async def cancel_command(client, message):
    if BOT.State.task_going:
        await cancelTask("User cancelled the task")
        msg = await message.reply_text("<b>🚫 Task Cancelled</b> ✓", quote=True)
    else:
        msg = await message.reply_text("<b>ℹ️ No Active Task To Cancel</b>", quote=True)
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
        msg = await message.reply_text("<b>🚫 All tasks cancelled and queue cleared.</b>", quote=True)
    else:
        msg = await message.reply_text("<b>📭 Queue cleared. No active task to cancel.</b>", quote=True)

    await message_deleter(message, msg)

# =============================================================================
# /admin
# =============================================================================
@app.on_message(filters.command("admin") & filters.private)
async def admin_command(client, message):
    if message.chat.id != OWNER:
        return

    if len(message.command) < 2:
        users_list = "\n".join([f"• <code>{uid}</code>" for uid in config.ALLOWED_USERS]) or "<code>None</code>"
        msg = await message.reply_text(
            f"<b>👥 Admin Panel</b>\n\n"
            f"<b>Allowed Users:</b>\n{users_list}\n\n"
            f"<code>/admin add &lt;user_id&gt;</code> — Allow a user\n"
            f"<code>/admin remove &lt;user_id&gt;</code> — Deny a user\n"
            f"<code>/admin list</code> — Show allowed users",
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
                msg = await message.reply_text(f"✅ User <code>{new_uid}</code> added to allowed list ✓", quote=True)
            else:
                msg = await message.reply_text(f"ℹ️ User <code>{new_uid}</code> is already allowed", quote=True)
        except ValueError:
            msg = await message.reply_text("⚠️ Invalid user ID", quote=True)

    elif action == "remove" and len(message.command) >= 3:
        try:
            rm_uid = int(message.command[2])
            if rm_uid in config.ALLOWED_USERS:
                config.ALLOWED_USERS.remove(rm_uid)
                msg = await message.reply_text(f"✅ User <code>{rm_uid}</code> removed from allowed list ✓", quote=True)
            else:
                msg = await message.reply_text(f"ℹ️ User <code>{rm_uid}</code> is not in the allowed list", quote=True)
        except ValueError:
            msg = await message.reply_text("⚠️ Invalid user ID", quote=True)

    elif action == "list":
        users_list = "\n".join([f"• <code>{uid}</code>" for uid in config.ALLOWED_USERS]) or "<code>None</code>"
        msg = await message.reply_text(f"<b>👥 Allowed Users:</b>\n{users_list}", quote=True)

    else:
        msg = await message.reply_text("<b>⚠️ Usage:</b> <code>/admin add|remove|list [user_id]</code>", quote=True)

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
            "<b>ℹ️ No files to broadcast.</b>\n\nUpload something first with <code>/tupload</code>.",
            quote=True,
        )
        await message_deleter(message, msg)
        return

    if len(message.command) < 2:
        msg = await message.reply_text(
            "<b>📢 Broadcast Usage</b>\n\n"
            "<code>/broadcast chat_id1, chat_id2, ...</code>\n\n"
            "<b>📝 Example:</b>\n"
            "<code>/broadcast -1001234567890, -1009876543210</code>\n\n"
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
        msg = await message.reply_text("<b>⚠️ No valid chat IDs provided.</b>", quote=True)
        await message_deleter(message, msg)
        return

    last_file = Transfer.sent_file[-1] if Transfer.sent_file else None
    if not last_file:
        msg = await message.reply_text("<b>⚠️ No file to broadcast.</b>", quote=True)
        await message_deleter(message, msg)
        return

    msg = await message.reply_text(f"<b>📢 Broadcasting to {len(chat_ids)} chats...</b>", quote=True)

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
        f"<b>📢 Broadcast Complete</b>\n\n"
        f"• ✅ <b>Success:</b> <code>{success}</code>\n"
        f"• ❌ <b>Failed:</b> <code>{failed}</code>\n"
        f"• 📊 <b>Total:</b> <code>{len(chat_ids)}</code>"
    )

# =============================================================================
# /cookies
# =============================================================================
@app.on_message(filters.command("cookies") & filters.private)
async def cookies_command(client, message):
    import subprocess

    cookies_file = getattr(config, "YTDL_COOKIES_FILE", "")
    default_path = Paths.COOKIE_FILE

    file_ok = cookies_file and os.path.isfile(cookies_file)
    uploaded_ok = os.path.isfile(default_path)

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
        auth_lines.append("✅ <b>PO Token Plugin</b> — auto-generating tokens (primary)")
    else:
        auth_lines.append("❌ <b>PO Token Plugin</b> — not installed")

    if file_ok:
        auth_lines.append(f"✅ <b>Cookies file</b> (env) — <code>{cookies_file}</code>")
    elif uploaded_ok:
        auth_lines.append(f"✅ <b>Cookies file</b> (uploaded) — <code>{default_path}</code>")
    else:
        auth_lines.append("⚠️ <b>Cookies</b> — not configured (fallback)")

    status = "\n".join(auth_lines)

    text = f"""<b>🍪 YT-DLP Authentication Status</b>

{status}

<b>─── How It Works ───</b>
• <b>PO Token Plugin</b> (auto) — generates tokens in background
• <b>Cookies</b> (manual fallback) — only needed if PO tokens fail

<b>If YouTube Still Fails:</b>
Upload a <code>cookies.txt</code> file here as a backup:
1. Install <a href="https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc">Get cookies.txt LOCALLY</a>
2. Go to <code>youtube.com</code> • click extension • <b>Export</b>
3. Send the file here

📖 <a href="https://github.com/yt-dlp/yt-dlp/wiki/PO-Token-Guide">PO Token Guide</a>"""

    msg = await message.reply_text(text, quote=True, disable_web_page_preview=True)
    await message_deleter(message, msg)

# =============================================================================
# /setcookies
# =============================================================================
@app.on_message(filters.command("setcookies") & filters.private)
async def setcookies_command(client, message):
    if message.chat.id != OWNER:
        return

    text = """<b>🍪 Upload Cookies File</b>

Send me your <code>cookies.txt</code> file <b>as a document</b> (not as text).

<b>Chrome / Edge / Brave:</b>
1. Install <a href="https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc">Get cookies.txt LOCALLY</a>
2. Go to <code>youtube.com</code> (make sure you're logged in)
3. Click extension icon • <b>Export</b> • saves <code>cookies.txt</code>
4. Upload that file here

<b>Firefox:</b>
1. Install <a href="https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/">cookies.txt</a>
2. Go to <code>youtube.com</code> (logged in)
3. Click extension • <b>Export</b> • upload here

⚠️ <b>Security:</b> Cookies contain your session tokens. The bot stores them locally and never shares them. Delete with <code>/clearcookies</code> if needed."""

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
            msg = await message.reply_text("<b>✅ Cookies file deleted.</b>", quote=True)
        except OSError as e:
            msg = await message.reply_text(f"<b>❌ Failed:</b> <code>{e}</code>", quote=True)
    else:
        msg = await message.reply_text("<b>ℹ️ No cookies file to delete.</b>", quote=True)

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
        "<b>🔄 Restarting LeechBot...</b>\n\n"
        f"• <b>Version:</b> <code>v{config.VERSION}</code>\n"
        "• <b>Action:</b> Sending SIGTERM to self\n"
        "• <b>Wrapper:</b> Will respawn the process\n\n"
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
            f"<b>📋 Logs</b>\n\n<code>Log file not found: {log_file}</code>\n\n"
            "<i>File logging may be disabled (read-only filesystem).</i>",
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
            f"📋 Last <code>{len(tail_lines)}</code> log lines\n"
            f"<code>({log_file})</code>\n\n"
            f"<pre>\n" + "\n".join(tail_lines) + "\n</pre>"
        )

        if len(log_text) > 4000:
            half = (4000 - 200) // 2
            log_text = (
                f"📋 Last <code>{len(tail_lines)}</code> log lines (truncated)\n"
                f"<code>({log_file})</code>\n\n"
                f"<pre>\n"
                + "\n".join(tail_lines[:half // 80])
                + "\n\n... [truncated] ...\n\n"
                + "\n".join(tail_lines[-(half // 80):])
                + "\n</pre>"
            )

        msg = await message.reply_text(log_text, quote=True)
        await message_deleter(message, msg)
    except Exception as e:
        logger.error(f"Failed to read log file: {e}")
        msg = await message.reply_text(
            f"<b>❌ Error reading logs:</b>\n<code>{e}</code>", quote=True,
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

    msg = await message.reply_text("<b>🔄 Checking for updates...</b>", quote=True)

    info = check_for_updates()
    version = get_local_version()
    local = info["local"]

    if not info["available"]:
        await msg.edit_text(
            f"<b>✅ Already up to date!</b>\n\n"
            f"<b>Version:</b> <code>{version}</code>\n"
            f"<b>Commit:</b> <code>{local}</code>"
        )
        await message_deleter(message, msg)
        return

    changelog = get_changelog_since(local)
    changelog_text = f"\n\n<b>📋 Changes:</b>\n<pre>\n{changelog[:1500]}\n</pre>" if changelog else ""

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Update Now", callback_data="do_update"),
            InlineKeyboardButton("❌ Cancel", callback_data="close"),
        ]
    ])

    await msg.edit_text(
        f"<b>🔄 Update Available!</b>\n\n"
        f"<b>Current:</b> <code>{local}</code>\n"
        f"<b>Latest:</b> <code>{info['remote']}</code>\n"
        f"<b>Behind:</b> <code>{info['behind']} commits</code>"
        f"{changelog_text}",
        reply_markup=keyboard,
    )

# =============================================================================
# /anime - Anime Episode Downloader
# =============================================================================
@app.on_message(filters.command("anime") & filters.private)
async def anime_command(client, message):
    """Search and download anime episodes."""
    from leechbot.downloader.anime import anime_client
    
    if len(message.command) < 2:
        msg = await message.reply_text(
            "<b>🎬 Anime Episode Downloader</b>\n\n"
            "<b>⚠️ Usage:</b> <code>/anime &lt;anime_name&gt;</code>\n\n"
            "<b>📝 Examples:</b>\n"
            "• <code>/anime One Piece</code>\n"
            "• <code>/anime Naruto Shippuden</code>\n"
            "• <code>/anime Attack on Titan</code>\n\n"
            "<b>💡 Features:</b>\n"
            "• Search anime from MiruroAPI & AniKotoAPI\n"
            "• Download episodes with subtitles\n"
            "• Auto-rename with <code>/autorename</code> template",
            quote=True,
        )
        await message_deleter(message, msg)
        return
    
    query = " ".join(message.command[1:])
    status = await message.reply_text(f"<b>🔍 Searching:</b> <code>{query}</code>...", quote=True)
    
    try:
        result = await anime_client.search(query)
        
        if not result.get("success"):
            await status.edit_text(f"<b>❌ Search failed:</b> <code>{result.get('message', 'Unknown error')}</code>")
            return
        
        results = result.get("results", [])
        if not results:
            await status.edit_text("<b>❌ No results found.</b> Try a different search term.")
            return
        
        # Store results for callback handling
        BOT.State.anime_search_results = results
        BOT.State.anime_search_query = query
        
        # Format results and create inline keyboard
        formatted = anime_client.format_search_results(results[:8])
        
        buttons = []
        for i, item in enumerate(formatted):
            title = item["title"][:40] + ("..." if len(item["title"]) > 40 else "")
            buttons.append([InlineKeyboardButton(
                f"{'🎬' if i == 0 else '📺'} {title}",
                callback_data=f"anime_select_{i}"
            )])
        
        buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="close")])
        
        result_text = f"<b>🔍 Search Results for:</b> <code>{query}</code>\n\n"
        for i, item in enumerate(formatted):
            result_text += f"<b>{i+1}.</b> {item['display']}\n\n"
        
        await status.edit_text(
            result_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )
    except Exception as e:
        logger.error(f"Anime search error: {e}")
        await status.edit_text(f"<b>❌ Search error:</b> <code>{e}</code>")
