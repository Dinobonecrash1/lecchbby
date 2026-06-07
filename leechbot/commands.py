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
import os
import signal
import sys
from datetime import datetime
from pyrogram import filters
from leechbot import app, OWNER, LOG_FILE
from leechbot.utility.variables import BOT, Queue, BotStats, Transfer, Messages, BotTimes
from leechbot.utility.task_manager import task_starter
from leechbot.utility.handler import cancelTask
from leechbot.utility.helper import (
    message_deleter, send_settings, sysINFO, format_stats, getTime, sizeUnit,
)
import config

logger = logging.getLogger(__name__)

# =============================================================================
# Welcome Text
# =============================================================================
WELCOME_TEXT = """**🤖 LeechBot** — Advanced Telegram File Transloader

◈ Powerful · Fast · Secure
◈ Download from 2000+ sources
◈ Upload to Telegram or Google Drive

**📥 Send any link to start downloading.**

Tap a button below to explore:"""

# =============================================================================
# /start
# =============================================================================
def _start_keyboard():
    """Inline keyboard for the /start welcome message."""
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
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
    """Send (or re-edit) the welcome message.

    Args:
        client: pyrogram Client
        message: pyrogram Message (or callback.message)
        edit: if True, edit the message in place; if False, delete + reply
    """
    if edit:
        try:
            await message.edit_text(
                WELCOME_TEXT,
                reply_markup=_start_keyboard(),
                disable_web_page_preview=True,
            )
            return
        except Exception:
            # Message edit failed (e.g. was a callback without message text)
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
    """Handle the /start command."""
    await _send_welcome(client, message, edit=False)

# =============================================================================
# /tupload
# =============================================================================
@app.on_message(filters.command("tupload") & filters.private)
async def telegram_upload_command(client, message):
    """Handle the /tupload command — leech mode."""
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
    """Handle the /gdupload command — mirror mode."""
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
    """Handle the /drupload command — directory leech mode."""
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
    """Handle the /ytupload command — YT-DLP mode."""
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
    """Handle the /glupload command — gallery-dl mode for image galleries."""
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
# /settings
# =============================================================================
@app.on_message(filters.command("settings") & filters.private)
async def settings_command(client, message):
    """Handle the /settings command."""
    if message.chat.id == OWNER:
        await message.delete()
        await send_settings(client, message, message.id, True)

# =============================================================================
# /help  (3.1.34 — category-button UI)
# =============================================================================
HELP_CATEGORIES = {
    "downloads": {
        "name": "📥 Downloads",
        "description": "Download from various sources",
        "commands": [
            "tupload", "gdupload", "drupload", "ytupload", "glupload",
            "setname", "format", "formats", "preview", "speed",
        ],
    },
    "files": {
        "name": "🗂 Files",
        "description": "Archive, queue and task control",
        "commands": [
            "zipaswd", "unzipaswd", "queue", "cancel", "cancel_all",
        ],
    },
    "status": {
        "name": "⚙️ Status & Settings",
        "description": "Bot status, configuration, maintenance",
        "commands": [
            "settings", "status", "stats", "logs", "ping",
            "restart", "update",
        ],
    },
    "account": {
        "name": "👤 Account",
        "description": "UserBot session management",
        "commands": [
            "userbot", "userbot_status", "userbot_logout",
        ],
    },
    "cookies": {
        "name": "🍪 Cookies",
        "description": "YT-DLP authentication",
        "commands": [
            "cookies", "setcookies", "clearcookies",
        ],
    },
    "admin": {
        "name": "🛠 Admin",
        "description": "Owner-only commands",
        "commands": [
            "admin", "broadcast",
        ],
    },
}

HELP_COMMANDS = {
    "tupload": {
        "category": "downloads",
        "title": "Telegram to Telegram",
        "short": "Download a Telegram file and re-upload it.",
        "usage": "/tupload <link>",
        "examples": [
            "/tupload https://t.me/c/1234567890/123",
            "/tupload https://t.me/s/yunavip/28",
        ],
    },
    "gdupload": {
        "category": "downloads",
        "title": "Mirror to Google Drive",
        "short": "Download a link and mirror it to Google Drive.",
        "usage": "/gdupload <link>",
        "examples": ["/gdupload https://drive.google.com/file/d/..."],
    },
    "drupload": {
        "category": "downloads",
        "title": "Direct URL upload",
        "short": "Download a direct HTTP(S) link and re-upload.",
        "usage": "/drupload <direct_url>",
        "examples": ["/drupload https://example.com/file.zip"],
    },
    "ytupload": {
        "category": "downloads",
        "title": "YT-DLP video download",
        "short": "Download video/audio from YouTube and 2000+ sites.",
        "usage": "/ytupload <video_url>",
        "examples": ["/ytupload https://youtu.be/dQw4w9WgXcQ"],
    },
    "glupload": {
        "category": "downloads",
        "title": "Gallery download",
        "short": "Download image galleries (Imgur, Pixiv, etc.).",
        "usage": "/glupload <gallery_url>",
        "examples": ["/glupload https://imgur.com/a/abc123"],
    },
    "setname": {
        "category": "downloads",
        "title": "Set custom filename",
        "short": "Set a custom filename for the next download.",
        "usage": "/setname <filename>",
        "examples": ["/setname myvideo.mp4"],
    },
    "format": {
        "category": "downloads",
        "title": "Set YT-DLP quality",
        "short": "Pick video format/quality (best, worst, 720p, etc.).",
        "usage": "/format <quality>",
        "examples": ["/format 720p", "/format best", "/format worst"],
    },
    "formats": {
        "category": "downloads",
        "title": "List available formats",
        "short": "List all formats available for a video URL.",
        "usage": "/formats <video_url>",
        "examples": ["/formats https://youtu.be/dQw4w9WgXcQ"],
    },
    "preview": {
        "category": "downloads",
        "title": "Preview gallery",
        "short": "Dry-run a gallery URL to see what would be downloaded.",
        "usage": "/preview <gallery_url>",
        "examples": ["/preview https://imgur.com/a/abc123"],
    },
    "speed": {
        "category": "downloads",
        "title": "Set bandwidth limit",
        "short": "Throttle download speed (in MB/s). 0 = unlimited.",
        "usage": "/speed <mbps>",
        "examples": ["/speed 5", "/speed 0 (unlimited)"],
    },
    "zipaswd": {
        "category": "files",
        "title": "Set zip password",
        "short": "Password-protect the next .zip archive.",
        "usage": "/zipaswd <password>",
        "examples": ["/zipaswd mySecret123"],
    },
    "unzipaswd": {
        "category": "files",
        "title": "Set unzip password",
        "short": "Password to use when extracting the next archive.",
        "usage": "/unzipaswd <password>",
        "examples": ["/unzipaswd mySecret123"],
    },
    "queue": {
        "category": "files",
        "title": "View queue",
        "short": "Show current and pending tasks in the queue.",
        "usage": "/queue",
        "examples": ["/queue"],
    },
    "cancel": {
        "category": "files",
        "title": "Cancel current task",
        "short": "Cancel the currently running task.",
        "usage": "/cancel",
        "examples": ["/cancel"],
    },
    "cancel_all": {
        "category": "files",
        "title": "Cancel all tasks",
        "short": "Cancel the running task AND clear the queue.",
        "usage": "/cancel_all",
        "examples": ["/cancel_all"],
    },
    "settings": {
        "category": "status",
        "title": "Bot settings",
        "short": "Open the settings menu (thumb, caption, format, etc.).",
        "usage": "/settings",
        "examples": ["/settings"],
    },
    "status": {
        "category": "status",
        "title": "Current task status",
        "short": "Show live progress, speed, ETA of the current task.",
        "usage": "/status",
        "examples": ["/status"],
    },
    "stats": {
        "category": "status",
        "title": "Bot statistics",
        "short": "Lifetime stats: tasks, downloaded, uploaded, uptime.",
        "usage": "/stats",
        "examples": ["/stats"],
    },
    "logs": {
        "category": "status",
        "title": "View logs",
        "short": "Get the last 50 lines of bot logs as a file.",
        "usage": "/logs",
        "examples": ["/logs"],
    },
    "ping": {
        "category": "status",
        "title": "Latency check",
        "short": "Show Telegram API latency + bot uptime + version.",
        "usage": "/ping",
        "examples": ["/ping"],
    },
    "restart": {
        "category": "status",
        "title": "Restart bot",
        "short": "Restart the bot process (owner only).",
        "usage": "/restart",
        "examples": ["/restart"],
    },
    "update": {
        "category": "status",
        "title": "Check for updates",
        "short": "Pull latest code from GitHub and restart (owner only).",
        "usage": "/update",
        "examples": ["/update"],
    },
    "userbot": {
        "category": "account",
        "title": "UserBot login",
        "short": "Login as your user account to access private channels.",
        "usage": "/userbot",
        "examples": ["/userbot", "(then send phone number)"],
    },
    "userbot_status": {
        "category": "account",
        "title": "UserBot status",
        "short": "Check if a user session is active and which account.",
        "usage": "/userbot_status",
        "examples": ["/userbot_status"],
    },
    "userbot_logout": {
        "category": "account",
        "title": "UserBot logout",
        "short": "Log out the user session and delete the session file.",
        "usage": "/userbot_logout",
        "examples": ["/userbot_logout"],
    },
    "cookies": {
        "category": "cookies",
        "title": "Cookies status",
        "short": "Check cookie auth status and get a setup guide.",
        "usage": "/cookies",
        "examples": ["/cookies"],
    },
    "setcookies": {
        "category": "cookies",
        "title": "Upload cookies.txt",
        "short": "Upload a cookies.txt file as a YT-DLP auth fallback.",
        "usage": "/setcookies (then attach cookies.txt)",
        "examples": ["/setcookies", "(reply with cookies.txt)"],
    },
    "clearcookies": {
        "category": "cookies",
        "title": "Clear cookies",
        "short": "Delete stored cookies from disk.",
        "usage": "/clearcookies",
        "examples": ["/clearcookies"],
    },
    "admin": {
        "category": "admin",
        "title": "Admin panel",
        "short": "Manage authorized users (owner only).",
        "usage": "/admin",
        "examples": ["/admin"],
    },
    "broadcast": {
        "category": "admin",
        "title": "Broadcast message",
        "short": "Send a file or message to multiple chats (owner only).",
        "usage": "/broadcast <message>",
        "examples": ["/broadcast Hello all users!"],
    },
}


def _help_render_main():
    """Render the main help menu (category buttons)."""
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    lines = [
        "**📖 LeechBot Help**",
        "",
        f"_{len(HELP_COMMANDS)} commands across {len(HELP_CATEGORIES)} categories._",
        "",
        "**Pick a category to browse:**",
        "",
    ]

    buttons = []
    # 2-column grid of category buttons
    cat_items = list(HELP_CATEGORIES.items())
    for i in range(0, len(cat_items), 2):
        row = []
        for key, cat in cat_items[i:i + 2]:
            n_cmds = len(cat["commands"])
            row.append(InlineKeyboardButton(
                f"{cat['name']} ({n_cmds})",
                callback_data=f"help_cat_{key}",
            ))
        buttons.append(row)
    buttons.append([InlineKeyboardButton("❌ Close", callback_data="help_close")])

    # Footer info
    lines.extend([
        "**💡 Tips:**",
        "• `/help <cmd>` — direct help for one command",
        "• `/start` — welcome & main menu",
        "",
        "**🔗 Links:**",
    ])

    return (
        "\n".join(lines),
        InlineKeyboardMarkup(buttons + [
            [
                InlineKeyboardButton("📂 GitHub", url="https://github.com/Shineii86/LeechBot"),
                InlineKeyboardButton("🔔 Updates", url="https://t.me/MaximXBots"),
            ],
        ]),
    )


def _help_render_category(cat_key: str):
    """Render a category detail (command buttons in that category)."""
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    if cat_key not in HELP_CATEGORIES:
        return None, None

    cat = HELP_CATEGORIES[cat_key]
    lines = [
        f"**{cat['name']}**",
        f"_{cat['description']}_",
        "",
        f"_{len(cat['commands'])} commands. Pick one for details:_",
        "",
    ]

    buttons = []
    # 2-column grid of command buttons
    cmds = cat["commands"]
    for i in range(0, len(cmds), 2):
        row = []
        for cmd in cmds[i:i + 2]:
            row.append(InlineKeyboardButton(
                f"/{cmd}",
                callback_data=f"help_cmd_{cmd}",
            ))
        buttons.append(row)

    # Navigation row
    buttons.append([
        InlineKeyboardButton("⬅️ Back", callback_data="help_main"),
        InlineKeyboardButton("❌ Close", callback_data="help_close"),
    ])

    return ("\n".join(lines), InlineKeyboardMarkup(buttons))


def _help_render_command(cmd_name: str):
    """Render a single command's detailed help."""
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    if cmd_name not in HELP_COMMANDS:
        return None, None

    cmd = HELP_COMMANDS[cmd_name]
    cat = HELP_CATEGORIES.get(cmd["category"], {})

    lines = [
        f"**/{cmd_name}** — {cmd['title']}",
        f"_{cat.get('name', 'Unknown')}_",
        "",
        f"**📝 Description:**",
        cmd["short"],
        "",
        f"**⌨️ Usage:**",
        f"`{cmd['usage']}`",
    ]

    if cmd.get("examples"):
        lines.extend(["", "**📚 Examples:**"])
        for ex in cmd["examples"]:
            lines.append(f"• `{ex}`")

    cat_key = cmd["category"]
    buttons = [[
        InlineKeyboardButton("⬅️ Back to category", callback_data=f"help_cat_{cat_key}"),
        InlineKeyboardButton("🏠 Main menu", callback_data="help_main"),
    ], [
        InlineKeyboardButton("❌ Close", callback_data="help_close"),
    ]]

    return ("\n".join(lines), InlineKeyboardMarkup(buttons))


@app.on_message(filters.command("help") & filters.private)
async def help_command(client, message):
    """
    Handle the /help command.

    Usage:
        /help           — show category menu
        /help <command> — show detailed help for that command
    """
    # Deep-link: /help <command>
    if len(message.command) > 1:
        cmd_name = message.command[1].lstrip("/").lower()
        if cmd_name in HELP_COMMANDS:
            text, keyboard = _help_render_command(cmd_name)
            msg = await message.reply_text(text, reply_markup=keyboard)
            await message_deleter(message, msg)
            return
        # Unknown command — fall through to category menu + mention the typo
        from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
        text, keyboard = _help_render_main()
        text = f"⚠️ Command `/{cmd_name}` not found.\n\n" + text
        msg = await message.reply_text(text, reply_markup=keyboard)
        await message_deleter(message, msg)
        return

    # Default: category menu
    text, keyboard = _help_render_main()
    msg = await message.reply_text(text, reply_markup=keyboard)
    await message_deleter(message, msg)

# =============================================================================
# /setname
# =============================================================================
@app.on_message(filters.command("setname") & filters.private)
async def setname_command(client, message):
    """Handle the /setname command."""
    if len(message.command) < 2:
        msg = await message.reply_text(
            "**⚠️ Usage**\n\n"
            "\n"
            "`/setname <filename.extension>`\n"
            "\n\n"
            "**📝 Example:** `/setname myvideo.mp4`",
            quote=True,
        )
    else:
        BOT.Options.custom_name = " ".join(message.command[1:])
        msg = await message.reply_text(
            f"**✅ Custom Name Set**\n\n`{BOT.Options.custom_name}`",
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
    """Handle the /unzipaswd command."""
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
# /stats
# =============================================================================
@app.on_message(filters.command("stats") & filters.private)
async def stats_command(client, message):
    """Handle the /stats command — shows lifetime task counts + system info."""
    stats_text = f"{format_stats()}{sysINFO()}"
    msg = await message.reply_text(stats_text, quote=True)
    await message_deleter(message, msg)

# =============================================================================
# /ping
# =============================================================================
@app.on_message(filters.command("ping") & filters.private)
async def ping_command(client, message):
    """Handle the /ping command — measures Telegram round-trip latency + shows uptime."""
    start = datetime.now()
    msg = await message.reply_text("**🏓 Pinging...**", quote=True)
    latency_ms = (datetime.now() - start).total_seconds() * 1000
    uptime = getTime(int((datetime.now() - BotStats.start_time).total_seconds()))

    if latency_ms < 200:
        bar = "🟢🟢🟢🟢🟢"
        quality = "Excellent"
    elif latency_ms < 500:
        bar = "🟢🟢🟢🟢⚪"
        quality = "Good"
    elif latency_ms < 1000:
        bar = "🟡🟡🟡⚪⚪"
        quality = "Average"
    else:
        bar = "🔴🔴⚪⚪⚪"
        quality = "Poor"

    ping_text = f"""**🏓 Pong!**

• ⚡ **Latency:** `{latency_ms:.1f} ms` {bar} _{quality}_
• ⏱️ **Uptime:** `{uptime}`
• 🤖 **Version:** `v{config.VERSION}`"""
    await msg.edit(ping_text, disable_web_page_preview=True)
    await message_deleter(message, msg)

# =============================================================================
# /status
# =============================================================================
@app.on_message(filters.command("status") & filters.private)
async def status_command(client, message):
    """Handle the /status command — show active task detail + queue + transfer stats."""
    if message.chat.id != OWNER and message.chat.id not in config.ALLOWED_USERS:
        return

    # ── Active task section ──
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
            # Trim the status head for display
            head_clean = Messages.status_head.replace("**", "").replace("\n", " · ")[:120]
            active_section += f"\n• **Current:** `{head_clean}`"
    else:
        active_section = "**🎯 Active Task**\n\n• `No task running`"

    # ── Queue section ──
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
# /restart
# =============================================================================
@app.on_message(filters.command("restart") & filters.private)
async def restart_command(client, message):
    """Handle the /restart command — gracefully exit so the wrapper can respawn."""
    if message.chat.id != OWNER:
        return

    # Cancel any active task first
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

    # Give the message a moment to send, then exit.
    # The process supervisor (systemd, docker --restart, pm2, tmux respawn,
    # Colab auto-reconnect, nohup loop, etc.) should bring it back.
    import asyncio
    await asyncio.sleep(1)

    # Try graceful exit first
    try:
        os.kill(os.getpid(), signal.SIGTERM)
    except Exception:
        # Fallback: hard exit
        sys.exit(0)

# =============================================================================
# /logs
# =============================================================================
@app.on_message(filters.command("logs") & filters.private)
async def logs_command(client, message):
    """Handle the /logs command — show last N log lines (default 30, max 100)."""
    if message.chat.id != OWNER:
        return

    # Parse optional count: /logs 50
    args = message.text.split(maxsplit=1)
    try:
        n_lines = int(args[1]) if len(args) > 1 else 30
        n_lines = max(1, min(n_lines, 100))  # clamp 1..100
    except ValueError:
        n_lines = 30

    # Find log file
    log_file = LOG_FILE or str(config.LOGS_PATH / "leechbot.log")

    if not os.path.isfile(log_file):
        msg = await message.reply_text(
            f"**📋 Logs**\n\n`Log file not found: {log_file}`\n\n"
            "_File logging may be disabled (read-only filesystem)._",
            quote=True,
        )
        await message_deleter(message, msg)
        return

    # Tail the last N lines efficiently (read from end, no full file load)
    try:
        # Get file size
        fsize = os.path.getsize(log_file)
        # Read up to ~256 KB from the end (enough for ~500 lines of INFO)
        read_size = min(fsize, 256 * 1024)

        with open(log_file, "rb") as f:
            if fsize > read_size:
                f.seek(fsize - read_size)
                _ = f.readline()  # discard partial first line
            data = f.read().decode("utf-8", errors="replace")

        all_lines = data.splitlines()
        tail_lines = all_lines[-n_lines:]

        if not tail_lines:
            tail_lines = ["(log file is empty)"]

        log_text = (
            f"**📋 Last `{len(tail_lines)}` log lines**\n"
            f"`({log_file})`\n\n"
            f"```\n" + "\n".join(tail_lines) + "\n```"
        )

        # Telegram has 4096 char limit per message — truncate if needed
        if len(log_text) > 4000:
            # Drop from the middle, keep first and last lines
            half = (4000 - 200) // 2
            log_text = (
                f"**📋 Last `{len(tail_lines)}` log lines** (truncated)\n"
                f"`({log_file})`\n\n"
                f"```\n"
                + "\n".join(tail_lines[:half // 80])  # ~80 chars per line avg
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
# /cancel
# =============================================================================
@app.on_message(filters.command("cancel") & filters.private)
async def cancel_command(client, message):
    """Handle the /cancel command."""
    if BOT.State.task_going:
        await cancelTask("User cancelled the task")
        msg = await message.reply_text("**🚫 Task Cancelled** ✓", quote=True)
    else:
        msg = await message.reply_text("**ℹ️ No Active Task To Cancel**", quote=True)
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
# /formats <url> — list available formats for a video URL
# =============================================================================
@app.on_message(filters.command("formats") & filters.private)
async def formats_command(client, message):
    """List available yt-dlp formats for a given video URL."""
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
# /preview <url> — show what a gallery URL contains (dry run)
# =============================================================================
@app.on_message(filters.command("preview") & filters.private)
async def preview_command(client, message):
    """Show the file list a gallery URL would produce, without downloading."""
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
# /admin
# =============================================================================
@app.on_message(filters.command("admin") & filters.private)
async def admin_command(client, message):
    """Admin panel for managing allowed users."""
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
                msg = await message.reply_text(f"**✅ User `{new_uid}` added to allowed list** ✓", quote=True)
            else:
                msg = await message.reply_text(f"**ℹ️ User `{new_uid}` is already allowed**", quote=True)
        except ValueError:
            msg = await message.reply_text("**⚠️ Invalid user ID**", quote=True)

    elif action == "remove" and len(message.command) >= 3:
        try:
            rm_uid = int(message.command[2])
            if rm_uid in config.ALLOWED_USERS:
                config.ALLOWED_USERS.remove(rm_uid)
                msg = await message.reply_text(f"**✅ User `{rm_uid}` removed from allowed list** ✓", quote=True)
            else:
                msg = await message.reply_text(f"**ℹ️ User `{rm_uid}` is not in the allowed list**", quote=True)
        except ValueError:
            msg = await message.reply_text("**⚠️ Invalid user ID**", quote=True)

    elif action == "list":
        users_list = "\n".join([f"• `{uid}`" for uid in config.ALLOWED_USERS]) or "`None`"
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
# /update — Check for updates and auto-update
# =============================================================================
@app.on_message(filters.command("update") & filters.private)
async def update_command(client, message):
    """Check for updates and optionally update the bot."""
    from leechbot.updater import check_for_updates, perform_update, get_local_version, get_local_commit, get_changelog_since

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

    # Show available update
    changelog = get_changelog_since(local)
    changelog_text = f"\n\n**📋 Changes:**\n```\n{changelog[:1500]}\n```" if changelog else ""

    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
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

# =============================================================================
# /userbot — Login with user account for private channel access
# =============================================================================
@app.on_message(filters.command("userbot") & filters.private)
async def userbot_command(client, message):
    """Start UserBot login flow for private channel access."""
    if message.chat.id != OWNER:
        return

    from leechbot.userbot import check_user_session, start_auth_flow, _auth_state

    # Check if already authorized
    if await check_user_session():
        await message.reply_text(
            "✅ **UserBot already authorized!**\n\n"
            "Private channel downloads use your account automatically.\n"
            "Send `/userbot_logout` to disconnect.",
            quote=True,
        )
        return

    # If there's a pending auth, show status
    if _auth_state["active"]:
        await message.reply_text(
            f"⏳ **Login in progress.** Current step: `{_auth_state['step']}`\n\n"
            f"Send the required code/password to continue.",
            quote=True,
        )
        return

    # Ask for phone number
    await message.reply_text(
        "📱 **UserBot Login** — Private Channel Access\n\n"
        "Login with your Telegram account to download from private channels.\n"
        "Your session is saved locally — no data is shared.\n\n"
        "**Send your phone number** with international code:\n"
        "Example: `+1234567890`\n\n"
        "_Send /cancel to abort._",
        quote=True,
    )

    BOT.State.prefix = False
    BOT.State.suffix = False
    # Set flag so next text message is treated as phone number
    BOT.State.userbot_waiting = "phone"

@app.on_message(filters.command("userbot_logout") & filters.private)
async def userbot_logout_command(client, message):
    """Disconnect UserBot session."""
    if message.chat.id != OWNER:
        return

    from leechbot.userbot import disconnect_user
    await disconnect_user()
    await message.reply_text("🔓 **UserBot session disconnected** and removed.", quote=True)

@app.on_message(filters.command("userbot_status") & filters.private)
async def userbot_status_command(client, message):
    """Check UserBot session status."""
    if message.chat.id != OWNER:
        return

    from leechbot.userbot import check_user_session
    if await check_user_session():
        await message.reply_text("✅ **UserBot session is active.** Private channel downloads supported.", quote=True)
    else:
        await message.reply_text("❌ **No UserBot session.** Send `/userbot` to login.", quote=True)
