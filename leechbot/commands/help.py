# =============================================================================
# Telegram Leech Bot - Help & Info Commands
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Help & info command handlers — /start, /help, /about
"""

import logging
from pyrogram import filters
from leechbot import app
from leechbot.utility.helper import message_deleter

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
        "description": "Download files and upload to Telegram",
        "usage": "/tupload <link>",
        "example": "/tupload https://example.com/file.zip",
    },
    "gdupload": {
        "description": "Mirror files to Google Drive",
        "usage": "/gdupload <link>",
        "example": "/gdupload https://example.com/file.zip",
    },
    "drupload": {
        "description": "Leech entire folder to Telegram",
        "usage": "/drupload <folder_path>",
        "example": "/drupload /home/user/Downloads",
    },
    "ytupload": {
        "description": "Download from YouTube & 2000+ sites",
        "usage": "/ytupload <url>",
        "example": "/ytupload https://youtube.com/watch?v=...",
    },
    "glupload": {
        "description": "Download image galleries (Twitter, Pixiv, etc.)",
        "usage": "/glupload <url>",
        "example": "glupload https://twitter.com/user",
    },
    "setname": {
        "description": "Set custom filename for next upload",
        "usage": "/setname <filename>",
        "example": "/setname movie.mp4",
    },
    "format": {
        "description": "Set video quality for YT-DLP downloads",
        "usage": "/format",
        "example": "/format",
    },
    "formats": {
        "description": "List available formats for a video URL",
        "usage": "/formats <url>",
        "example": "/formats https://youtube.com/watch?v=...",
    },
    "preview": {
        "description": "Preview gallery content before downloading",
        "usage": "/preview <url>",
        "example": "/preview https://imgur.com/a/abc123",
    },
    "speed": {
        "description": "Set download bandwidth limit",
        "usage": "/speed",
        "example": "/speed",
    },
    "zipaswd": {
        "description": "Set password for zip archives",
        "usage": "/zipaswd <password>",
        "example": "/zipaswd mypassword123",
    },
    "unzipaswd": {
        "description": "Set password for extracting archives",
        "usage": "/unzipaswd <password>",
        "example": "/unzipaswd mypassword123",
    },
    "queue": {
        "description": "Show download queue",
        "usage": "/queue",
        "example": "/queue",
    },
    "cancel": {
        "description": "Cancel current download task",
        "usage": "/cancel",
        "example": "/cancel",
    },
    "cancel_all": {
        "description": "Cancel all tasks and clear queue",
        "usage": "/cancel_all",
        "example": "/cancel_all",
    },
    "settings": {
        "description": "Show bot settings panel",
        "usage": "/settings",
        "example": "/settings",
    },
    "status": {
        "description": "Show active task status",
        "usage": "/status",
        "example": "/status",
    },
    "stats": {
        "description": "Show lifetime statistics",
        "usage": "/stats",
        "example": "/stats",
    },
    "logs": {
        "description": "Show recent log entries",
        "usage": "/logs [count]",
        "example": "/logs 50",
    },
    "ping": {
        "description": "Check bot latency and uptime",
        "usage": "/ping",
        "example": "/ping",
    },
    "restart": {
        "description": "Restart the bot process",
        "usage": "/restart",
        "example": "/restart",
    },
    "update": {
        "description": "Check for and apply updates",
        "usage": "/update",
        "example": "/update",
    },
    "userbot": {
        "description": "Login with user account for private channels",
        "usage": "/userbot",
        "example": "/userbot",
    },
    "userbot_status": {
        "description": "Check UserBot session status",
        "usage": "/userbot_status",
        "example": "/userbot_status",
    },
    "userbot_logout": {
        "description": "Disconnect UserBot session",
        "usage": "/userbot_logout",
        "example": "/userbot_logout",
    },
    "cookies": {
        "description": "Show YT-DLP authentication status",
        "usage": "/cookies",
        "example": "/cookies",
    },
    "setcookies": {
        "description": "Upload cookies.txt for YT-DLP",
        "usage": "/setcookies",
        "example": "/setcookies",
    },
    "clearcookies": {
        "description": "Delete uploaded cookies file",
        "usage": "/clearcookies",
        "example": "/clearcookies",
    },
    "admin": {
        "description": "Manage allowed users",
        "usage": "/admin add|remove|list [user_id]",
        "example": "/admin add 123456789",
    },
    "broadcast": {
        "description": "Send last uploaded file to multiple chats",
        "usage": "/broadcast <chat_id1, chat_id2>",
        "example": "/broadcast -1001234567890",
    },
}


def _build_help_text(category: str = None) -> str:
    """Build help text for a category or all commands."""
    if category and category in HELP_CATEGORIES:
        cat = HELP_CATEGORIES[category]
        lines = [f"**{cat['name']}**\n_{cat['description']}_\n"]
        for cmd in cat["commands"]:
            info = HELP_COMMANDS.get(cmd, {})
            desc = info.get("description", "No description")
            lines.append(f"• `/{cmd}` — {desc}")
        return "\n".join(lines)

    # All categories
    lines = ["**📖 LeechBot Help**\n"]
    for cat_id, cat in HELP_CATEGORIES.items():
        lines.append(f"\n**{cat['name']}**")
        for cmd in cat["commands"][:3]:  # Show first 3 per category
            info = HELP_COMMANDS.get(cmd, {})
            desc = info.get("description", "No description")
            lines.append(f"• `/{cmd}` — {desc}")
        if len(cat["commands"]) > 3:
            lines.append(f"• _...and {len(cat['commands']) - 3} more_")
    return "\n".join(lines)


@app.on_message(filters.command("help") & filters.private)
async def help_command(client, message):
    """Handle the /help command — category-button UI."""
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(cat["name"], callback_data=f"help_{cat_id}")]
        for cat_id, cat in HELP_CATEGORIES.items()
    ] + [[InlineKeyboardButton("❰ Back", callback_data="back")]])

    await message.reply_text(
        "**📖 Help Menu**\n\nChoose a category:",
        reply_markup=keyboard,
        quote=True,
    )