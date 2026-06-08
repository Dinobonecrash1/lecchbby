# =============================================================================
# Telegram Leech Bot - Utility Commands
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Utility command handlers — /setname, /formats, /preview
"""

import logging
from pyrogram import filters
from leechbot import app, OWNER
from leechbot.utility.variables import BOT
from leechbot.utility.helper import message_deleter

logger = logging.getLogger(__name__)

# =============================================================================
# /setname
# =============================================================================
@app.on_message(filters.command("setname") & filters.private)
async def setname_command(client, message):
    """Set custom filename for next upload."""
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