# =============================================================================
# Telegram Leech Bot - Command Handlers and Entry Point
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# You may use, modify, and distribute this code under the MIT License.
# Please retain this header when using or modifying the code.
# =============================================================================

"""
LeechBot command handlers and entry point

This module contains all Telegram bot command handlers, callback queries,
and the main bot execution loop. It handles user interactions
and orchestrates the download and upload processes.
"""

import logging
import os
from pyrogram import filters
from datetime import datetime
from asyncio import sleep, get_event_loop
from leechbot import leechbot, OWNER
from leechbot.utility.handler import cancelTask
from leechbot.utility.variables import BOT, MSG, BotTimes, Paths, Queue, BotStats
from leechbot.utility.task_manager import taskScheduler, task_starter
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from leechbot.utility.helper import (
    isLink, setThumbnail, message_deleter, send_settings,
    sysINFO, sysINFO_full, status_keyboard, extract_links
)
import config

logger = logging.getLogger(__name__)

# =============================================================================
# Global Variables
# =============================================================================
src_request_msg = None

# =============================================================================
# Welcome Message (Professional Markdown)
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
# Bot Commands
# =============================================================================
@leechbot.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    """
    Handle the /start command.
    Sends welcome message with repository and support links.
    """
    await message.delete()
    
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📂 GitHub Repository ✨", url="https://github.com/Shineii86/LeechBot")
            ],
            [
                InlineKeyboardButton("🔔 Updates", url="https://t.me/MaximXBots"),
                InlineKeyboardButton("Support 💬", url="https://t.me/MaximXGroup"),
            ],
            [
                InlineKeyboardButton("🤖 Bot Settings ⚙️", callback_data="settings_menu"),
            ]
        ]
    )
    
    await message.reply_text(WELCOME_TEXT, reply_markup=keyboard, disable_web_page_preview=True)


@leechbot.on_message(filters.command("tupload") & filters.private)
async def telegram_upload_command(client, message):
    """
    Handle the /tupload command.
    Sets up leech mode for uploading files to Telegram.
    """
    global BOT, src_request_msg
    
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


@leechbot.on_message(filters.command("gdupload") & filters.private)
async def gdrive_upload_command(client, message):
    """
    Handle the /gdupload command.
    Sets up mirror mode for uploading files to Google Drive.
    """
    global BOT, src_request_msg
    
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


@leechbot.on_message(filters.command("drupload") & filters.private)
async def directory_upload_command(client, message):
    """
    Handle the /drupload command.
    Sets up directory leech mode for uploading local folders.
    """
    global BOT, src_request_msg
    
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


@leechbot.on_message(filters.command("ytupload") & filters.private)
async def ytdl_upload_command(client, message):
    """
    Handle the /ytupload command.
    Sets up YT-DLP mode for downloading from YouTube and other sites.
    """
    global BOT, src_request_msg
    
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


@leechbot.on_message(filters.command("settings") & filters.private)
async def settings_command(client, message):
    """
    Handle the /settings command.
    Opens the bot settings menu (owner only).
    """
    if message.chat.id == OWNER:
        await message.delete()
        await send_settings(client, message, message.id, True)


@leechbot.on_message(filters.command("help") & filters.private)
async def help_command(client, message):
    """
    Handle the /help command.
    Displays help information and available commands.
    """
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

**🖼️ Thumbnail:**
Send Any Image To Set It As Thumbnail

**💡 Supported Sites:**
Direct Links, Google Drive, Telegram
YouTube, Facebook, Instagram & 2000+ sites
Terabox, Mega, Pixeldrain, Mediafire
"""
    
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📂 GitHub Repository ✨", url="https://github.com/Shineii86/LeechBot")
            ],
            [
                InlineKeyboardButton("🔔 Updates", url="https://t.me/MaximXBots"),
                InlineKeyboardButton("Support 💬", url="https://t.me/MaximXGroup"),
            ],
            [
                InlineKeyboardButton("🧑‍💻 Developer ✨", url="https://t.me/Shineii86")
            ]
        ]
    )
    
    msg = await message.reply_text(help_text, reply_markup=keyboard)
    await message_deleter(message, msg)


@leechbot.on_message(filters.command("setname") & filters.private)
async def setname_command(client, message):
    """
    Handle the /setname command.
    Sets a custom filename for downloads.
    """
    global BOT
    
    if len(message.command) < 2:
        msg = await message.reply_text(
            "**⚠️ Usage:**\n`/setname <filename.extension>`\n\n**Example:**\n`/setname myvideo.mp4`",
            quote=True
        )
    else:
        BOT.Options.custom_name = " ".join(message.command[1:])
        msg = await message.reply_text(
            f"**✅ Custom Name Set:**\n`{BOT.Options.custom_name}`",
            quote=True
        )
    
    await message_deleter(message, msg)


@leechbot.on_message(filters.command("zipaswd") & filters.private)
async def zipaswd_command(client, message):
    """
    Handle the /zipaswd command.
    Sets a password for zip compression.
    """
    global BOT
    
    if len(message.command) != 2:
        msg = await message.reply_text(
            "**⚠️ Usage:**\n`/zipaswd <password>`\n\n**Example:**\n`/zipaswd mypassword123`",
            quote=True
        )
    else:
        BOT.Options.zip_pswd = message.command[1]
        msg = await message.reply_text(
            "**🔐 Zip Password Set Successfully**",
            quote=True
        )
    
    await message_deleter(message, msg)


@leechbot.on_message(filters.command("unzipaswd") & filters.private)
async def unzipaswd_command(client, message):
    """
    Handle the /unzipaswd command.
    Sets a password for extracting archives.
    """
    global BOT
    
    if len(message.command) != 2:
        msg = await message.reply_text(
            "**⚠️ Usage:**\n`/unzipaswd <password>`\n\n**Example:**\n`/unzipaswd mypassword123`",
            quote=True
        )
    else:
        BOT.Options.unzip_pswd = message.command[1]
        msg = await message.reply_text(
            "**🔓 Unzip Password Set Successfully**",
            quote=True
        )
    
    await message_deleter(message, msg)


@leechbot.on_message(filters.command("stats") & filters.private)
async def stats_command(client, message):
    """
    Handle the /stats command.
    Displays bot statistics and system information.
    """
    stats_text = f"**📊 Bot Statistics**{sysINFO()}"
    
    msg = await message.reply_text(stats_text, quote=True)
    await message_deleter(message, msg)


@leechbot.on_message(filters.command("cancel") & filters.private)
async def cancel_command(client, message):
    """
    Handle the /cancel command.
    Cancels the current running task.
    """
    if BOT.State.task_going:
        await cancelTask("User cancelled the task")
        msg = await message.reply_text("**🚫 Task Cancelled**", quote=True)
    else:
        msg = await message.reply_text("**⚠️ No Active Task To Cancel**", quote=True)
    
    await message_deleter(message, msg)


# =============================================================================
# NEW COMMANDS
# =============================================================================
@leechbot.on_message(filters.command("queue") & filters.private)
async def queue_command(client, message):
    """Show the download queue."""
    if message.chat.id != OWNER and message.chat.id not in config.ALLOWED_USERS:
        return

    items = Queue.list_items()
    current = Queue.current()

    text = "**📋 Download Queue**\n\n"

    if current:
        text += f"**🔄 Active:** `{current.get('name', 'Unknown')}`\n"
        text += f"**📦 Links:** `{len(current.get('links', []))}`\n\n"
    else:
        text += "**🔄 Active:** `None`\n\n"

    if items:
        for i, item in enumerate(items, 1):
            text += f"`{i}.` `{item.get('name', 'Unknown')}` — `{len(item.get('links', []))}` links\n"
        text += f"\n**📊 Total Queued:** `{Queue.size()}`"
    else:
        text += "**📭 Queue is empty**"

    stats_text = f"\n\n**📈 Session Stats:**\n"
    stats_text += f"`•` Completed: `{BotStats.total_tasks}`\n"
    stats_text += f"`•` Failed: `{BotStats.failed_tasks}`\n"
    stats_text += f"`•` Downloaded: `{BotStats.total_downloaded}`\n"
    stats_text += f"`•` Uploaded: `{BotStats.total_uploaded}`"

    msg = await message.reply_text(text + stats_text, quote=True)
    await message_deleter(message, msg)


@leechbot.on_message(filters.command("format") & filters.private)
async def format_command(client, message):
    """Set YT-DLP download format/quality."""
    if message.chat.id != OWNER:
        return

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎬 Best Quality", callback_data="fmt-bestvideo+bestaudio/best"),
        ],
        [
            InlineKeyboardButton("📺 1080p", callback_data="fmt-bestvideo[height<=1080]+bestaudio/best[height<=1080]"),
            InlineKeyboardButton("📺 720p", callback_data="fmt-bestvideo[height<=720]+bestaudio/best[height<=720]"),
        ],
        [
            InlineKeyboardButton("📱 480p", callback_data="fmt-bestvideo[height<=480]+bestaudio/best[height<=480]"),
            InlineKeyboardButton("📱 360p", callback_data="fmt-bestvideo[height<=360]+bestaudio/best[height<=360]"),
        ],
        [
            InlineKeyboardButton("🎵 Audio Only", callback_data="fmt-bestaudio/best"),
        ],
        [
            InlineKeyboardButton("❰ Back", callback_data="back"),
        ],
    ])

    current_fmt = BOT.Setting.ytdl_format if hasattr(BOT.Setting, 'ytdl_format') else "bestvideo+bestaudio/best"

    await message.reply_text(
        f"**🎬 YT-DLP Format Selection**\n\n"
        f"**Current:** `{current_fmt}`\n\n"
        f"Choose the quality for video downloads:\n\n"
        f"💡 **Tip:** Lower quality = faster download & smaller size",
        reply_markup=keyboard,
        quote=True
    )


@leechbot.on_message(filters.command("speed") & filters.private)
async def speed_command(client, message):
    """Set bandwidth limit for downloads."""
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
        [
            InlineKeyboardButton("❰ Back", callback_data="back"),
        ],
    ])

    current = config.BANDWIDTH_LIMIT or "Unlimited"

    await message.reply_text(
        f"**⚡ Bandwidth Limiter**\n\n"
        f"**Current Limit:** `{current}`\n\n"
        f"Set maximum download speed to avoid saturating your connection.\n"
        f"This applies to aria2c and YT-DLP downloads.",
        reply_markup=keyboard,
        quote=True
    )


@leechbot.on_message(filters.command("broadcast") & filters.private)
async def broadcast_command(client, message):
    """Send the last uploaded file to multiple chats."""
    if message.chat.id != OWNER:
        return

    if not BOT.State.task_going and not Transfer.sent_file:
        msg = await message.reply_text(
            "**⚠️ No files to broadcast.**\n\nUpload something first with `/tupload`.",
            quote=True
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
            quote=True
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
        await sleep(1)  # Rate limit

    await msg.edit_text(
        f"**📢 Broadcast Complete**\n\n"
        f"✅ Success: `{success}`\n"
        f"❌ Failed: `{failed}`\n"
        f"📊 Total: `{len(chat_ids)}`"
    )


@leechbot.on_message(filters.command("admin") & filters.private)
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
            quote=True
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


@leechbot.on_message(filters.command("cancel_all") & filters.private)
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


# =============================================================================
# Reply Handlers
# =============================================================================
@leechbot.on_message(filters.reply)
async def handle_reply(client, message):
    """
    Handle reply messages for setting prefix/suffix.
    """
    global BOT
    
    if BOT.State.prefix:
        BOT.Setting.prefix = message.text
        BOT.State.prefix = False
        await send_settings(client, message, message.reply_to_message_id, False)
        await message.delete()
    elif BOT.State.suffix:
        BOT.Setting.suffix = message.text
        BOT.State.suffix = False
        await send_settings(client, message, message.reply_to_message_id, False)
        await message.delete()


# =============================================================================
# Link Handler
# =============================================================================
@leechbot.on_message(filters.create(isLink) & ~filters.photo)
async def handle_url(client, message):
    """
    Handle URL messages for download processing.
    Parses options like custom name, zip password, and unzip password.
    """
    global BOT, src_request_msg
    
    # Reset options
    BOT.Options.custom_name = ""
    BOT.Options.zip_pswd = ""
    BOT.Options.unzip_pswd = ""
    
    if src_request_msg:
        await src_request_msg.delete()
    
    if not BOT.State.task_going and BOT.State.started:
        temp_source = message.text.splitlines()
        
        # Parse options from message
        for _ in range(3):
            if not temp_source:
                break
            if temp_source[-1][0] == "[":
                BOT.Options.custom_name = temp_source[-1][1:-1]
                temp_source.pop()
            elif temp_source[-1][0] == "{":
                BOT.Options.zip_pswd = temp_source[-1][1:-1]
                temp_source.pop()
            elif temp_source[-1][0] == "(":
                BOT.Options.unzip_pswd = temp_source[-1][1:-1]
                temp_source.pop()
            else:
                break
        
        BOT.SOURCE = temp_source
        
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📄 Regular ✨", callback_data="normal")
                ],
                [
                    InlineKeyboardButton("🗜️ Compress", callback_data="zip"),
                    InlineKeyboardButton("Extract 📂", callback_data="unzip"),
                ],
                [
                    InlineKeyboardButton("🔄 Unzip+Zip ✨", callback_data="undzip")
                ],
            ]
        )
        
        mode_text = BOT.Mode.mode.capitalize()
        options_text = f"""
**🎯 Select Upload Type For {mode_text}**

📄 **Regular** - Normal File Upload
🗜️ **Compress** - Zip File Upload
📂 **Extract** - Extract Archive Before Upload
🔄 **Unzip+Zip** - Extract Then Compress
"""
        
        await message.reply_text(
            text=options_text,
            reply_markup=keyboard,
            quote=True
        )
    elif BOT.State.started:
        await message.delete()
        msg = await message.reply_text("**⏳ I'm Already Working! Please Wait...**")
        await message_deleter(message, msg)


# =============================================================================
# Callback Query Handler
# =============================================================================
@leechbot.on_callback_query()
async def handle_callback(client, callback_query):
    """
    Handle all inline keyboard callbacks.
    """
    global BOT, MSG
    
    data = callback_query.data
    
    # Upload type selection
    if data in ["normal", "zip", "unzip", "undzip"]:
        BOT.Mode.type = data
        await callback_query.message.delete()
        await leechbot.delete_messages(
            chat_id=callback_query.message.chat.id,
            message_ids=callback_query.message.reply_to_message_id
        )
        
        MSG.status_msg = await leechbot.send_message(
            chat_id=OWNER,
            text="**🚀 Initializing Task...**\n\nPlease Wait While I Prepare Your Download",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🚫 Cancel", callback_data="cancel")]]
            )
        )
        
        BOT.State.task_going = True
        BOT.State.started = False
        BotTimes.start_time = datetime.now()
        
        event_loop = get_event_loop()
        BOT.TASK = event_loop.create_task(taskScheduler())
        
        try:
            await BOT.TASK
        finally:
            BOT.State.task_going = False
    
    # Settings menu
    elif data == "settings_menu":
        await send_settings(client, callback_query.message, callback_query.message.id, False)
    
    # Video settings
    elif data == "video":
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("✂️ Split", callback_data="split-true"),
                    InlineKeyboardButton("Zip 🗜️", callback_data="split-false"),
                ],
                [
                    InlineKeyboardButton("🔄 Convert", callback_data="convert-true"),
                    InlineKeyboardButton("Skip ⏭️", callback_data="convert-false"),
                ],
                [
                    InlineKeyboardButton("🎬 Mp4", callback_data="mp4"),
                    InlineKeyboardButton("Mkv 📼", callback_data="mkv"),
                ],
                [
                    InlineKeyboardButton("👍 High Quality", callback_data="q-High"),
                    InlineKeyboardButton("Low Quality 👎", callback_data="q-Low"),
                ],
                [
                    InlineKeyboardButton("❰ Back", callback_data="back")
                ],
            ]
        )
        
        await callback_query.message.edit_text(
            f"""**⚙️ Video Settings**

┏🔄 **Convert:** `{BOT.Setting.convert_video}`
┣✂️ **Split:** `{BOT.Setting.split_video}`
┣🎬 **Format:** `{BOT.Options.video_out}`
┗🔴 **Quality:** `{BOT.Setting.convert_quality}`""",
            reply_markup=keyboard
        )
    
    # Caption settings
    elif data == "caption":
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Monospace", callback_data="code-Monospace"),
                    InlineKeyboardButton("Bold", callback_data="b-Bold"),
                ],
                [
                    InlineKeyboardButton("Italic", callback_data="i-Italic"),
                    InlineKeyboardButton("Underline", callback_data="u-Underlined"),
                ],
                [
                    InlineKeyboardButton("Regular", callback_data="p-Regular")
                ],
                [
                    InlineKeyboardButton("❰ Back", callback_data="back")
                ],
            ]
        )
        
        await callback_query.message.edit_text(
            """**📝 Caption Font Style**

<code>Monospace</code>
Regular
**Bold**
__Italic__
__Underline__""",
            reply_markup=keyboard
        )
    
    # Thumbnail settings
    elif data == "thumb":
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🗑️ Delete Thumbnail", callback_data="del-thumb")
                ],
                [
                    InlineKeyboardButton("❰ Back", callback_data="back")
                ],
            ]
        )
        
        thmb_status = "✅ Set" if BOT.Setting.thumbnail else "🚫 None"
        
        await callback_query.message.edit_text(
            f"""**🖼️ Thumbnail Settings**

**Status:** {thmb_status}

💡 Send An Image To Set As Thumbnail""",
            reply_markup=keyboard
        )
    
    # Delete thumbnail
    elif data == "del-thumb":
        if BOT.Setting.thumbnail and os.path.exists(Paths.THMB_PATH):
            os.remove(Paths.THMB_PATH)
        BOT.Setting.thumbnail = False
        await send_settings(client, callback_query.message, callback_query.message.id, False)
    
    # Set prefix/suffix
    elif data == "set-prefix":
        await callback_query.message.edit_text(
            "**⌨️ Send Text To Set As Prefix**\n\nReply To This Message With Your Prefix"
        )
        BOT.State.prefix = True
    
    elif data == "set-suffix":
        await callback_query.message.edit_text(
            "**⌨️ Send Text To Set As Suffix**\n\nReply To This Message With Your Suffix"
        )
        BOT.State.suffix = True
    
    # Caption style selection
    elif data in ["code-Monospace", "p-Regular", "b-Bold", "i-Italic", "u-Underlined"]:
        res = data.split("-")
        BOT.Options.caption = res[0]
        BOT.Setting.caption = res[1]
        await send_settings(client, callback_query.message, callback_query.message.id, False)
    
    # Video split selection
    elif data in ["split-true", "split-false"]:
        BOT.Options.is_split = data == "split-true"
        BOT.Setting.split_video = "Split" if data == "split-true" else "Zip"
        await send_settings(client, callback_query.message, callback_query.message.id, False)
    
    # Video convert selection
    elif data in ["convert-true", "convert-false"]:
        BOT.Options.convert_video = data == "convert-true"
        BOT.Setting.convert_video = "Yes" if data == "convert-true" else "No"
        await send_settings(client, callback_query.message, callback_query.message.id, False)
    
    # Video format selection
    elif data in ["mp4", "mkv"]:
        BOT.Options.video_out = data
        await send_settings(client, callback_query.message, callback_query.message.id, False)
    
    # Quality selection
    elif data in ["q-High", "q-Low"]:
        BOT.Setting.convert_quality = data.split("-")[-1]
        BOT.Options.convert_quality = BOT.Setting.convert_quality == "High"
        await send_settings(client, callback_query.message, callback_query.message.id, False)
    
    # Upload mode selection
    elif data in ["media", "document"]:
        BOT.Options.stream_upload = data == "media"
        BOT.Setting.stream_upload = "Media" if data == "media" else "Document"
        await send_settings(client, callback_query.message, callback_query.message.id, False)
    
    # Auto-delete settings (NEW)
    elif data == "autodelete":
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        f"✅ Auto-Delete: {'ON' if BOT.Setting.auto_delete else 'OFF'}",
                        callback_data="toggle_autodelete"
                    )
                ],
                [
                    InlineKeyboardButton("⏱️ Set Delay", callback_data="set_autodelete_delay")
                ],
                [
                    InlineKeyboardButton("❰ Back", callback_data="back")
                ],
            ]
        )
        await callback_query.message.edit_text(
            f"""**⏳ Auto-Delete Messages**

**Status:** {'Enabled' if BOT.Setting.auto_delete else 'Disabled'}
**Delay:** {BOT.Setting.auto_delete_delay} seconds

When enabled, bot messages will be automatically deleted after the specified delay.""",
            reply_markup=keyboard
        )
    
    elif data == "toggle_autodelete":
        BOT.Setting.auto_delete = not BOT.Setting.auto_delete
        # Refresh menu by re-calling autodelete callback
        callback_query.data = "autodelete"
        await handle_callback(client, callback_query)
    
    elif data == "set_autodelete_delay":
        await callback_query.message.edit_text(
            "**⏱️ Send the delay in seconds**\n\nReply to this message with a number between 5 and 300.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❰ Back", callback_data="autodelete")]])
        )
        BOT.State.setting_autodelete_delay = True
    
    # Close menu
    elif data == "close":
        await callback_query.message.delete()
    
    # Go back
    elif data == "back":
        await send_settings(client, callback_query.message, callback_query.message.id, False)
    
    # YTDL confirmation
    elif data in ["ytdl-true", "ytdl-false"]:
        BOT.Mode.ytdl = data == "ytdl-true"
        await callback_query.message.delete()
        await leechbot.delete_messages(
            chat_id=callback_query.message.chat.id,
            message_ids=callback_query.message.reply_to_message_id
        )
        
        MSG.status_msg = await leechbot.send_message(
            chat_id=OWNER,
            text="**🚀 Initializing Task...**\n\nPlease Wait While I Prepare Your Download",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Cancel", callback_data="cancel")
                    ]
                ]
            )
        )
        
        BOT.State.task_going = True
        BOT.State.started = False
        BotTimes.start_time = datetime.now()
        
        event_loop = get_event_loop()
        BOT.TASK = event_loop.create_task(taskScheduler())
        
        try:
            await BOT.TASK
        finally:
            BOT.State.task_going = False
    
    # Cancel task
    elif data == "cancel":
        await cancelTask("User cancelled the task")

    # =========================================================================
    # Format Selection Callbacks
    # =========================================================================
    elif data.startswith("fmt-"):
        fmt = data[4:]
        BOT.Setting.ytdl_format = fmt
        config.BANDWIDTH_LIMIT = config.BANDWIDTH_LIMIT  # keep current
        await callback_query.message.edit_text(
            f"**✅ YT-DLP Format Updated**\n\n**Selected:** `{fmt}`"
        )
        await callback_query.answer("Format saved")

    # =========================================================================
    # Speed Limit Callbacks
    # =========================================================================
    elif data.startswith("spd-"):
        speed_val = data[4:]
        config.BANDWIDTH_LIMIT = speed_val
        display = speed_val if speed_val else "Unlimited"
        await callback_query.message.edit_text(
            f"**✅ Bandwidth Limit Updated**\n\n**Limit:** `{display}`"
        )
        await callback_query.answer("Speed limit saved")

    # =========================================================================
    # System Info Callbacks
    # =========================================================================
    elif data == "sys_refresh":
        original_text = callback_query.message.text
        parts = original_text.split("⌬─────")
        if len(parts) >= 2:
            new_text = parts[0] + sysINFO()
            await callback_query.message.edit_text(
                text=new_text,
                disable_web_page_preview=True,
                reply_markup=status_keyboard()
            )
        else:
            await callback_query.message.edit_text(
                text=original_text + "\n" + sysINFO(),
                disable_web_page_preview=True,
                reply_markup=status_keyboard()
            )
        await callback_query.answer("System info refreshed")
    
    elif data == "sys_stats":
        original_text = callback_query.message.text
        parts = original_text.split("⌬─────")
        if len(parts) >= 2:
            new_text = parts[0] + sysINFO_full()
        else:
            new_text = original_text + "\n" + sysINFO_full()
        await callback_query.message.edit_text(
            text=new_text,
            disable_web_page_preview=True,
            reply_markup=status_keyboard()
        )
        await callback_query.answer("Showing detailed stats")
    
    elif data == "sys_close":
        await callback_query.message.delete()
        await callback_query.answer("Closed")


# =============================================================================
# Photo Handler (Thumbnail)
# =============================================================================
@leechbot.on_message(filters.photo & filters.private)
async def handle_photo(client, message):
    """
    Handle photo messages to set thumbnail.
    """
    msg = await message.reply_text("**🖼️ Processing Thumbnail...**")
    
    success = await setThumbnail(message)
    
    if success:
        await msg.edit_text("**✅ Thumbnail Set Successfully**")
        await message.delete()
    else:
        await msg.edit_text("**❎ Failed To Set Thumbnail**")
    
    await message_deleter(message, msg)


# =============================================================================
# Additional Reply Handler for Auto-Delete Delay Input
# =============================================================================
@leechbot.on_message(filters.text & filters.private)
async def handle_text_input(client, message):
    """
    Handle text inputs for setting auto-delete delay.
    """
    global BOT
    if hasattr(BOT.State, 'setting_autodelete_delay') and BOT.State.setting_autodelete_delay:
        try:
            delay = int(message.text.strip())
            if 5 <= delay <= 300:
                BOT.Setting.auto_delete_delay = delay
                BOT.State.setting_autodelete_delay = False
                await message.reply_text(f"**✅ Auto-delete delay set to {delay} seconds.**")
                await message.delete()
            else:
                await message.reply_text("**⚠️ Please enter a number between 5 and 300.**")
                await message.delete()
        except ValueError:
            await message.reply_text("**⚠️ Invalid number. Please try again.**")
            await message.delete()


# =============================================================================
# Bot Startup
# =============================================================================
logger.info("=" * 60)
logger.info("LeechBot started successfully")
logger.info("Developer: Shinei Nouzen")
logger.info("GitHub: https://github.com/Shineii86/LeechBot")
logger.info("=" * 60)

leechbot.run()
