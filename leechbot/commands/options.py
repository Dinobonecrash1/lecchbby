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

