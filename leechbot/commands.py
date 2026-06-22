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
from time import time
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from leechbot import app, OWNER, LOG_FILE, DUMP_ID
from leechbot.utility.variables import BOT, MSG, YTDL, BotStats, BotTimes, Transfer, Messages, Queue, Paths
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
    from asyncio import sleep as async_sleep
    import aiohttp

    start = datetime.now()
    msg = await message.reply_text("<b>⚡ Checking...</b>", quote=True)
    latency_ms = (datetime.now() - start).total_seconds() * 1000
    uptime = getTime(int((datetime.now() - BotStats.start_time).total_seconds()))

    if latency_ms < 200:
        quality = "Excellent"
        quality_icon = "🟢"
    elif latency_ms < 500:
        quality = "Good"
        quality_icon = "🟡"
    elif latency_ms < 1000:
        quality = "Average"
        quality_icon = "🟠"
    else:
        quality = "Poor"
        quality_icon = "🔴"

    server_status = "Online" if latency_ms < 5000 else "Slow"

    # Check API health
    api_results = []
    apis = [
        ("Miruro API", "https://mirurotvapi.vercel.app/api/health"),
        ("Animex API", "https://animexoneapi.vercel.app/api/health"),
    ]
    async with aiohttp.ClientSession() as session:
        for name, url in apis:
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        api_results.append(f"  🟢 <code>{name}</code> » Online")
                    else:
                        api_results.append(f"  🔴 <code>{name}</code> » Error {resp.status}")
            except Exception:
                api_results.append(f"  🔴 <code>{name}</code> » Offline")

    api_text = "\n".join(api_results)

    ping_text = f"""<b>⚡ PONG</b>

<b>🏓 Latency:</b> <code>{latency_ms:.1f} ms</code>
<b>{quality_icon} Quality:</b> <code>{quality}</code>
<b>⏱️ Uptime:</b> <code>{uptime}</code>
<b>🤖 Version:</b> <code>v{config.VERSION}</code>
<b>📡 Server:</b> <code>{server_status}</code>

<b>🌐 APIs:</b>
{api_text}"""
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
    """Search and download anime episodes.

    Quick mode: /anime <query> [ep/start-end] [sub/dub] [quality] [provider]
    Interactive: /anime <query>  (shows search results with buttons)
    """
    from leechbot.downloader.anime import anime_client

    if len(message.command) < 2:
        msg = await message.reply_text(
            "<b>🎬 Anime Episode Downloader</b>\n\n"
            "<b>⚠️ Usage:</b>\n"
            "• <code>/anime &lt;name&gt;</code> — interactive search\n"
            "• <code>/anime &lt;name&gt; ep 1-5 sub</code> — quick download\n\n"
            "<b>📝 Quick Examples:</b>\n"
            "• <code>/anime Solo Leveling ep 1-5 sub</code>\n"
            "• <code>/anime One Piece ep 1-10 dub 1080p</code>\n"
            "• <code>/anime Naruto ep 5 sub animex</code>\n\n"
            "<b>📋 Parameters (optional):</b>\n"
            "• <code>ep &lt;range&gt;</code> — episode(s): <code>5</code> or <code>1-13</code>\n"
            "• <code>sub</code> / <code>dub</code> — audio type\n"
            "• <code>480p</code> / <code>720p</code> / <code>1080p</code> — quality\n"
            "• <code>animex</code> / <code>miruro</code> — provider\n",
            quote=True,
        )
        await message_deleter(message, msg)
        return

    # Parse arguments
    raw_args = " ".join(message.command[1:])
    ep_start = ep_end = None
    category = "sub"
    quality = None
    provider = None
    query_parts = []

    tokens = raw_args.split()
    i = 0
    while i < len(tokens):
        tok = tokens[i].lower()
        if tok == "ep" and i + 1 < len(tokens):
            # Parse episode range: "5" or "1-5" or "1~5"
            ep_str = tokens[i + 1].replace("~", "-")
            if "-" in ep_str:
                parts = ep_str.split("-", 1)
                ep_start = int(parts[0])
                ep_end = int(parts[1])
            else:
                ep_start = ep_end = int(ep_str)
            i += 2
        elif tok in ("sub", "dub"):
            category = tok
            i += 1
        elif tok.endswith("p") and tok[:-1].isdigit():
            quality = tok
            i += 1
        elif tok in ("animex", "miruro"):
            provider = tok
            i += 1
        else:
            query_parts.append(tokens[i])
            i += 1

    query = " ".join(query_parts)

    if not query:
        await message.reply_text("<b>❌ Please provide an anime name.</b>", quote=True)
        return

    # ── Quick mode: episodes specified (batch: download 1, upload 1) ──
    if ep_start is not None:
        from asyncio import sleep as async_sleep
        from leechbot.uploader.telegram import upload_file
        from leechbot.utility.handler import SendLogs
        from leechbot.utility.helper import sysINFO, keyboard
        from os import makedirs, listdir, path as ospath
        import shutil
        import random

        status = await message.reply_text(
            f"<b>🔍 Searching:</b> <code>{query}</code>...\n"
            f"<b>📺 Episodes:</b> <code>{ep_start}-{ep_end}</code>\n"
            f"<b>🔊 Audio:</b> <code>{category}</code>",
            quote=True,
        )

        try:
            result = await anime_client.search(query)
            if not result.get("success"):
                await status.edit_text(f"<b>❌ Search failed:</b> <code>{result.get('message', 'Unknown error')}</code>")
                return

            results = result.get("results", [])
            if not results:
                await status.edit_text("<b>❌ No results found.</b>")
                return

            search_provider = result.get("provider", "animex")
            selected = results[0]
            formatted = anime_client.format_search_results(results[:1], provider=search_provider)
            display_title = formatted[0]["display_title"] if formatted else query

            if search_provider == "animex":
                anime_id = selected.get("anilistId") or selected.get("id", "")
            else:
                anime_id = selected.get("id")

            cover = selected.get("cover", "") or selected.get("coverImage", {}).get("extraLarge", "")

            await status.edit_text(
                f"<b>🎬 {display_title}</b>\n\n"
                f"<b>📺 Episodes:</b> <code>{ep_start}-{ep_end}</code>\n"
                f"<b>🔊 Audio:</b> <code>{category}</code>\n\n"
                f"<b>⏳ Loading episodes...</b>",
            )

            episodes_result = await anime_client.get_episodes(anime_id, search_provider)
            if not episodes_result.get("success"):
                await status.edit_text(f"<b>❌ Failed to load episodes:</b> <code>{episodes_result.get('message', 'Unknown error')}</code>")
                return

            episodes_list = episodes_result.get("results", [])
            BOT.State.anime_episodes = episodes_list

            # ── Set mode (matches normal task_starter) ──
            BOT.State.task_going = True
            BOT.State.shutting_down = False
            BOT.Mode.type = "normal"
            BOT.Mode.stream = True
            BOT.Mode.ytdl = True
            BOT.Mode.mode = "leech"
            BOT.Mode.is_leech = True
            BOT.Options.http_headers = {"Referer": "https://kwik.cx/", "Origin": "https://kwik.cx/"}

            ep_label_range = f"Ep {ep_start}" if ep_start == ep_end else f"Ep {ep_start}-{ep_end}"
            total = ep_end - ep_start + 1

            # ── Build Messages.dump_task (exact match to original task_starter) ──
            Messages.download_name = display_title
            Messages.task_msg = "<b>🎯 Task Mode:</b> "
            mode_label = "Leech"
            Messages.dump_task = Messages.task_msg + f"<code>{BOT.Mode.type.capitalize()} {mode_label} as {BOT.Setting.stream_upload}</code>\n\n<b>🔗 Sources:</b>"
            Messages.link_p = str(DUMP_ID)[4:]

            # ── Pick hero image ──
            try:
                import glob as _glob
                images = _glob.glob(ospath.join(Paths.ASSETS_IMAGES, "*.jpg")) + \
                         _glob.glob(ospath.join(Paths.ASSETS_IMAGES, "*.png")) + \
                         _glob.glob(ospath.join(Paths.ASSETS_IMAGES, "*.webp"))
                if images:
                    Paths.HERO_IMAGE = random.choice(images)
                    Paths.DEFAULT_HERO = images[0]
            except Exception:
                pass

            # ── Download poster as thumbnail ──
            if cover:
                from leechbot.callbacks import _download_anime_poster
                await _download_anime_poster(cover)

            # ── Send task log to dump channel (no date yet — sources come first) ──
            dump_msg = await app.send_message(chat_id=DUMP_ID, text=Messages.dump_task, disable_web_page_preview=True)
            Messages.src_link = f"https://t.me/c/{Messages.link_p}/{dump_msg.id}"
            Messages.task_msg += f"[{BOT.Mode.type.capitalize()} {mode_label} as {BOT.Setting.stream_upload}]({Messages.src_link})\n\n"

            # ── Create status message with thumbnail ──
            if BOT.Setting.thumbnail and ospath.exists(Paths.THMB_PATH):
                img = Paths.THMB_PATH
            else:
                anime_poster = getattr(BOT.State, "anime_poster_path", None)
                if anime_poster and ospath.exists(anime_poster):
                    img = anime_poster
                elif ospath.exists(Paths.THMB_PATH):
                    img = Paths.THMB_PATH
                else:
                    img = Paths.HERO_IMAGE

            caption = (
                Messages.task_msg
                + Messages.status_head
                + "\n📝 Initializing..." + sysINFO()
            )

            # Delete old status message
            try:
                await status.delete()
            except Exception:
                pass

            if img and ospath.exists(img):
                try:
                    MSG.status_msg = await app.send_photo(
                        chat_id=OWNER,
                        photo=img,
                        caption=caption,
                        reply_markup=keyboard()
                    )
                except Exception:
                    MSG.status_msg = await app.send_message(
                        chat_id=OWNER,
                        text=caption,
                        reply_markup=keyboard(),
                        disable_web_page_preview=True
                    )
            else:
                MSG.status_msg = await app.send_message(
                    chat_id=OWNER,
                    text=caption,
                    reply_markup=keyboard(),
                    disable_web_page_preview=True
                )

            # ── Initialize transfer tracking (matches original) ──
            BotTimes.current_time = time()
            Transfer.up_bytes = [0, 0]
            Transfer.sent_file = []
            Transfer.sent_file_names = []
            Transfer.down_bytes = [0, 0]
            Transfer.total_down_size = 0
            BotStats.total_tasks += 1

            # Set MSG.sent_msg for upload_file to reply to
            MSG.sent_msg = dump_msg

            uploaded = 0
            failed = 0

            for ep_num in range(ep_start, ep_end + 1):
                if BOT.State.shutting_down:
                    break

                ep_label = f"Ep {ep_num:02d}"
                file_name = f"{display_title} - {ep_label}"

                Messages.status_head = (
                    f"<b>📥 Downloading</b> <code>{ep_label}</code>\n\n"
                    f"<code>{display_title}</code>\n"
                )

                # Update status
                try:
                    await MSG.status_msg.edit_text(
                        text=Messages.task_msg + Messages.status_head + sysINFO(),
                        reply_markup=keyboard()
                    )
                except Exception:
                    pass

                # Fetch stream URL
                ep_info = anime_client.miruro.get_episode_stream_info(episodes_list, ep_num, category)
                if not ep_info:
                    failed += 1
                    continue

                ep_info["anilist_id"] = anime_id
                stream_result = await anime_client.get_stream_from_miruro(
                    ep_info["provider"], anime_id, category, ep_info["slug"]
                )
                if not stream_result.get("success"):
                    failed += 1
                    continue

                stream_url = stream_result["results"]["url"]
                ep_referer = stream_result["results"].get("referer", "https://kwik.cx/")
                BOT.Options.http_headers = {"Referer": ep_referer, "Origin": ep_referer}
                BOT.Options.custom_name = file_name

                # Add source link to dump task
                try:
                    code_link = f"\n\n🏮 `{stream_url[:100]}...`"
                    if len(Messages.dump_task + code_link) < 4000:
                        Messages.dump_task += code_link
                except Exception:
                    pass

                # Create temp folder for this episode
                ep_dir = ospath.join(str(config.DOWNLOADS_PATH), f"ep_{ep_num}")
                if ospath.exists(ep_dir):
                    shutil.rmtree(ep_dir)
                makedirs(ep_dir, exist_ok=True)
                Paths.down_path = ep_dir

                # Download with progress bar
                try:
                    Messages.download_name = file_name
                    from leechbot.downloader.ytdl import YTDL_Status, YTDL
                    await YTDL_Status(stream_url, ep_num - ep_start + 1)
                    # Wait for yt-dlp to fully finish (HLS fragments may still be merging)
                    for _ in range(30):
                        if YTDL.complete:
                            break
                        await async_sleep(1)
                except Exception as e:
                    logger.error("Episode %d download failed: %s", ep_num, e)
                    failed += 1
                    if ospath.exists(ep_dir):
                        shutil.rmtree(ep_dir)
                    continue

                # Find downloaded file
                files = [f for f in listdir(ep_dir) if ospath.isfile(ep_dir + "/" + f)]
                if not files:
                    failed += 1
                    shutil.rmtree(ep_dir)
                    continue

                # Set transfer total for progress tracking
                file_size = ospath.getsize(ep_dir + "/" + files[0])
                Transfer.total_down_size = file_size

                # Upload
                file_path = ep_dir + "/" + files[0]
                real_name = file_name + ospath.splitext(files[0])[1]

                # Apply autorename template if set
                if BOT.Setting.autorename_template:
                    from leechbot.utility.handler import _apply_autorename_template
                    quality = stream_result["results"].get("quality", "")
                    if not quality:
                        import re
                        q_match = re.search(r'(\d{3,4}p)', stream_url, re.IGNORECASE)
                        if q_match:
                            quality = q_match.group(1).upper()
                    file_metadata = {
                        'title': display_title,
                        'audio': category.upper(),
                        'episode': str(ep_num),
                        'season': '1',
                        'quality': quality,
                    }
                    new_name = _apply_autorename_template(real_name, BOT.Setting.autorename_template, file_metadata)
                    new_file_path = ospath.join(ep_dir, new_name)
                    try:
                        os.rename(file_path, new_file_path)
                        file_path = new_file_path
                        real_name = new_name
                    except OSError:
                        pass

                # Update status to show uploading
                Messages.status_head = (
                    f"<b>📤 Uploading</b> <code>{ep_label}</code>\n\n"
                    f"<code>{display_title}</code>\n"
                )
                try:
                    await MSG.status_msg.edit_text(
                        text=Messages.task_msg + Messages.status_head + sysINFO(),
                        reply_markup=keyboard()
                    )
                except Exception:
                    pass

                try:
                    await upload_file(file_path, real_name)
                    Transfer.up_bytes.append(file_size)
                    uploaded += 1
                except Exception as e:
                    logger.error("Episode %d upload failed: %s", ep_num, e)
                    failed += 1

                # Cleanup
                if ospath.exists(ep_dir):
                    shutil.rmtree(ep_dir)

                if ep_num < ep_end:
                    await async_sleep(3)

            # ── Add date and final update to dump message ──
            cdt = datetime.now()
            dt = cdt.strftime(" %d-%m-%Y")
            Messages.dump_task += f"\n\n<b>📅 Date:</b> <code>{dt}</code>"
            try:
                await dump_msg.edit_text(
                    text=Messages.dump_task,
                    disable_web_page_preview=True
                )
            except Exception:
                pass

            # ── SendLogs (completion summary with source link) ──
            BOT.Options.custom_name = ""
            BOT.Options.http_headers = None
            Messages.download_name = display_title
            await SendLogs(is_leech=True)

        except ValueError:
            await status.edit_text("<b>❌ Invalid episode format.</b> Use: <code>ep 5</code> or <code>ep 1-13</code>")
        except Exception as e:
            logger.error(f"Anime quick download error: {e}")
            await status.edit_text(f"<b>❌ Error:</b> <code>{e}</code>")
        return

    # ── Interactive mode: no episodes specified ──
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
        BOT.State.anime_search_provider = result.get("provider", "animex")

        # Format results and create inline keyboard
        search_provider = result.get("provider", "animex")
        formatted = anime_client.format_search_results(results[:8], provider=search_provider)

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
