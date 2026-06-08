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
        "category": "downloads",
        "title": "Telegram to Telegram",
        "short": "Download a Telegram file and re-upload it.",
        "description": "Download files and upload to Telegram",
        "usage": "/tupload <link>",
        "example": "/tupload https://example.com/file.zip",
    },
    "gdupload": {
        "category": "downloads",
        "title": "Mirror to Google Drive",
        "short": "Mirror downloads directly to Google Drive.",
        "description": "Mirror files to Google Drive",
        "usage": "/gdupload <link>",
        "example": "/gdupload https://example.com/file.zip",
    },
    "drupload": {
        "category": "downloads",
        "title": "Directory Leech",
        "short": "Upload entire local directories recursively.",
        "description": "Leech entire folder to Telegram",
        "usage": "/drupload <folder_path>",
        "example": "/drupload /home/user/Downloads",
    },
    "ytupload": {
        "category": "downloads",
        "title": "YouTube & 2000+ Sites",
        "short": "Download from YouTube, Facebook, Twitter, and 2000+ sites via yt-dlp.",
        "description": "Download from YouTube & 2000+ sites",
        "usage": "/ytupload <url>",
        "example": "/ytupload https://youtube.com/watch?v=...",
    },
    "glupload": {
        "category": "downloads",
        "title": "Photo Galleries",
        "short": "Download image galleries from Twitter, Pinterest, Pixiv, and 100+ sites.",
        "description": "Download image galleries (Twitter, Pixiv, etc.)",
        "usage": "/glupload <url>",
        "example": "/glupload https://twitter.com/user",
    },
    "setname": {
        "category": "downloads",
        "title": "Custom Filename",
        "short": "Set a custom filename for the next upload.",
        "description": "Set custom filename for next upload",
        "usage": "/setname <filename>",
        "example": "/setname movie.mp4",
    },
    "format": {
        "category": "downloads",
        "title": "Video Quality",
        "short": "Set video quality for YT-DLP downloads.",
        "description": "Set video quality for YT-DLP downloads",
        "usage": "/format",
        "example": "/format",
    },
    "formats": {
        "category": "downloads",
        "title": "List Formats",
        "short": "List available formats for a video URL.",
        "description": "List available formats for a video URL",
        "usage": "/formats <url>",
        "example": "/formats https://youtube.com/watch?v=...",
    },
    "preview": {
        "category": "downloads",
        "title": "Preview Gallery",
        "short": "Show what a gallery URL contains without downloading.",
        "description": "Preview gallery content before downloading",
        "usage": "/preview <url>",
        "example": "/preview https://imgur.com/a/abc123",
    },
    "speed": {
        "category": "downloads",
        "title": "Bandwidth Limit",
        "short": "Set maximum download speed.",
        "description": "Set download bandwidth limit",
        "usage": "/speed",
        "example": "/speed",
    },
    "zipaswd": {
        "category": "files",
        "title": "Zip Password",
        "short": "Set password for zip archives.",
        "description": "Set password for zip archives",
        "usage": "/zipaswd <password>",
        "example": "/zipaswd mypassword123",
    },
    "unzipaswd": {
        "category": "files",
        "title": "Unzip Password",
        "short": "Set password for extracting archives.",
        "description": "Set password for extracting archives",
        "usage": "/unzipaswd <password>",
        "example": "/unzipaswd mypassword123",
    },
    "queue": {
        "category": "files",
        "title": "Download Queue",
        "short": "Show pending downloads.",
        "description": "Show download queue",
        "usage": "/queue",
        "example": "/queue",
    },
    "cancel": {
        "category": "files",
        "title": "Cancel Task",
        "short": "Stop the current download.",
        "description": "Cancel current download task",
        "usage": "/cancel",
        "example": "/cancel",
    },
    "cancel_all": {
        "category": "files",
        "title": "Cancel All",
        "short": "Cancel current task and clear queue.",
        "description": "Cancel all tasks and clear queue",
        "usage": "/cancel_all",
        "example": "/cancel_all",
    },
    "settings": {
        "category": "status",
        "title": "Bot Settings",
        "short": "Open the settings panel.",
        "description": "Show bot settings panel",
        "usage": "/settings",
        "example": "/settings",
    },
    "status": {
        "category": "status",
        "title": "Active Task Status",
        "short": "Show current task progress, speed, and ETA.",
        "description": "Show active task status",
        "usage": "/status",
        "example": "/status",
    },
    "stats": {
        "category": "status",
        "title": "Lifetime Statistics",
        "short": "Show total tasks completed, downloaded, uploaded.",
        "description": "Show lifetime statistics",
        "usage": "/stats",
        "example": "/stats",
    },
    "logs": {
        "category": "status",
        "title": "Recent Logs",
        "short": "Show last N log lines (default 30, max 100).",
        "description": "Show recent log entries",
        "usage": "/logs [count]",
        "example": "/logs 50",
    },
    "ping": {
        "category": "status",
        "title": "Latency & Uptime",
        "short": "Check bot response time and uptime.",
        "description": "Check bot latency and uptime",
        "usage": "/ping",
        "example": "/ping",
    },
    "restart": {
        "category": "status",
        "title": "Restart Bot",
        "short": "Gracefully restart the bot process.",
        "description": "Restart the bot process",
        "usage": "/restart",
        "example": "/restart",
    },
    "update": {
        "category": "status",
        "title": "Check Updates",
        "short": "Check for and apply updates.",
        "description": "Check for and apply updates",
        "usage": "/update",
        "example": "/update",
    },
    "userbot": {
        "category": "account",
        "title": "UserBot Login",
        "short": "Login with your Telegram account for private channels.",
        "description": "Login with user account for private channels",
        "usage": "/userbot",
        "example": "/userbot",
    },
    "userbot_status": {
        "category": "account",
        "title": "UserBot Status",
        "short": "Check if UserBot session is active.",
        "description": "Check UserBot session status",
        "usage": "/userbot_status",
        "example": "/userbot_status",
    },
    "userbot_logout": {
        "category": "account",
        "title": "UserBot Logout",
        "short": "Disconnect and remove UserBot session.",
        "description": "Disconnect UserBot session",
        "usage": "/userbot_logout",
        "example": "/userbot_logout",
    },
    "cookies": {
        "category": "cookies",
        "title": "Auth Status",
        "short": "Show YT-DLP authentication status.",
        "description": "Show YT-DLP authentication status",
        "usage": "/cookies",
        "example": "/cookies",
    },
    "setcookies": {
        "category": "cookies",
        "title": "Upload Cookies",
        "short": "Upload a cookies.txt file for YT-DLP.",
        "description": "Upload cookies.txt for YT-DLP",
        "usage": "/setcookies",
        "example": "/setcookies",
    },
    "clearcookies": {
        "category": "cookies",
        "title": "Delete Cookies",
        "short": "Remove the uploaded cookies file.",
        "description": "Delete uploaded cookies file",
        "usage": "/clearcookies",
        "example": "/clearcookies",
    },
    "admin": {
        "category": "admin",
        "title": "Manage Users",
        "short": "Add or remove allowed users.",
        "description": "Manage allowed users",
        "usage": "/admin add|remove|list [user_id]",
        "example": "/admin add 123456789",
    },
    "broadcast": {
        "category": "admin",
        "title": "Broadcast File",
        "short": "Send last uploaded file to multiple chats.",
        "description": "Send last uploaded file to multiple chats",
        "usage": "/broadcast <chat_id1, chat_id2>",
        "example": "/broadcast -1001234567890",
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
    cmds = cat["commands"]
    for i in range(0, len(cmds), 2):
        row = []
        for cmd in cmds[i:i + 2]:
            row.append(InlineKeyboardButton(
                f"/{cmd}",
                callback_data=f"help_cmd_{cmd}",
            ))
        buttons.append(row)

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

    if cmd.get("example"):
        lines.extend(["", "**📚 Example:**", f"`{cmd['example']}`"])

    cat_key = cmd["category"]
    buttons = [[
        InlineKeyboardButton("⬅️ Back to category", callback_data=f"help_cat_{cat_key}"),
        InlineKeyboardButton("🏠 Main menu", callback_data="help_main"),
    ], [
        InlineKeyboardButton("❌ Close", callback_data="help_close"),
    ]]

    return ("\n".join(lines), InlineKeyboardMarkup(buttons))


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

    lines = ["**📖 LeechBot Help**\n"]
    for cat_id, cat in HELP_CATEGORIES.items():
        lines.append(f"\n**{cat['name']}**")
        for cmd in cat["commands"][:3]:
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

    if len(message.command) > 1:
        cmd_name = message.command[1].lstrip("/").lower()
        if cmd_name in HELP_COMMANDS:
            text, keyboard = _help_render_command(cmd_name)
            msg = await message.reply_text(text, reply_markup=keyboard, quote=True)
            await message_deleter(message, msg)
            return
        text, keyboard = _help_render_main()
        text = f"⚠️ Command `/{cmd_name}` not found.\n\n" + text
        msg = await message.reply_text(text, reply_markup=keyboard, quote=True)
        await message_deleter(message, msg)
        return

    text, keyboard = _help_render_main()
    msg = await message.reply_text(text, reply_markup=keyboard, quote=True)
    await message_deleter(message, msg)