# =============================================================================
# Telegram Leech Bot - Callback Query Handlers
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
All inline keyboard callback query handlers.

Each callback category is handled by a dedicated async function
for clarity, testability, and maintainability.
"""

import os
import sys
import logging
from datetime import datetime
from asyncio import get_running_loop

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from leechbot import app, OWNER
from leechbot.utility.variables import BOT, MSG, BotTimes, Paths
from leechbot.utility.handler import cancelTask
from leechbot.utility.helper import send_settings, sysINFO, sysINFO_full, status_keyboard
import config

logger = logging.getLogger(__name__)



from .common import safe_answer

# =============================================================================
# /help inline keyboard handlers  (3.1.34)
# =============================================================================
HELP_TEXT = """<b>📖 LeechBot Help Menu</b>

<b>─── Download Commands ───</b>
• /start — Start the bot
• /tupload — Upload to Telegram
• /gdupload — Mirror to Google Drive
• /drupload — Upload local directory
• /ytupload — Download with YT-DLP
• /glupload — Download image galleries
• /preview — Dry-run a gallery URL

<b>─── Queue &amp; Control ───</b>
• /queue — View download queue
• /cancel — Cancel current task
• /cancel_all — Cancel &amp; clear queue

<b>─── Settings ───</b>
• /settings — Bot settings menu
• /setname — Set custom filename
• /zipaswd — Set zip password
• /unzipaswd — Set unzip password
• /format — Set YT-DLP quality
• /formats — List available formats
• /speed — Set bandwidth limit

<b>─── Admin ───</b>
• /admin — Manage allowed users
• /broadcast — Send file to multiple chats
• /stats — Bot &amp; system statistics
• /update — Check for updates

<b>─── YT-DLP Auth ───</b>
• /cookies — Check auth status
• /setcookies — Upload cookies.txt
• /clearcookies — Delete stored cookies

<b>🖼️ Thumbnail:</b> Send any image to set thumbnail"""

HELP_KEYBOARD = InlineKeyboardMarkup([
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


async def _handle_help_main(client, callback_query):
    """Show the help main menu, or close the help message."""
    if callback_query.data == "help_close":
        try:
            await callback_query.message.delete()
        except Exception as e:
            logger.debug("Help close (delete) failed: %s", e)
            await callback_query.message.edit_text("<b>✅ Help closed.</b>")
        await safe_answer(callback_query, "Closed")
        return

    try:
        await callback_query.message.edit_text(
            text=HELP_TEXT,
            reply_markup=HELP_KEYBOARD,
            disable_web_page_preview=True,
        )
    except Exception as e:
        logger.debug("Help main edit failed: %s", e)
    try:
        await safe_answer(callback_query)
    except Exception:
        pass


# =============================================================================
# About + Start navigation  (3.1.35)
# =============================================================================
ABOUT_TEXT = """<b>ℹ️ About LeechBot</b>

<b>Version:</b> <code>{version}</code>
<b>Build:</b> {build_date}

<b>👨‍💻 Developer:</b> <a href="https://t.me/Shineii86">Shinei Nouzen</a>
<b>📂 GitHub:</b> <a href="https://github.com/Shineii86/LeechBot">Shineii86/LeechBot</a>
<b>📜 License:</b> MIT

<b>📊 Stats:</b>
• Supports <b>2000+</b> download sources
• <b>Pyrogram</b> 2.0.106 + asyncio

<b>🛠 Features:</b>
• Telegram, Google Drive, direct-URL, YouTube, galleries
• Video conversion, archive extract, custom thumbnails
• Per-task settings, queue, bandwidth control

<b>⚖️ Disclaimer:</b>
This bot is for personal use only. Respect copyright
laws in your jurisdiction. The developer is not
responsible for misuse."""


async def _handle_about(client, callback_query):
    """Show the About card (edits the message in place)."""
    import config

    version = config.VERSION
    build_date = config.BUILD_DATE

    text = ABOUT_TEXT.format(
        version=version,
        build_date=build_date,
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📖 Help", callback_data="help_main"),
            InlineKeyboardButton("⚙️ Settings", callback_data="settings_menu"),
        ],
        [
            InlineKeyboardButton("📂 GitHub", url="https://github.com/Shineii86/LeechBot"),
            InlineKeyboardButton("💬 Support", url="https://t.me/MaximXGroup"),
        ],
        [InlineKeyboardButton("⌂ Home", callback_data="start_back"),
         InlineKeyboardButton("🔒 Close", callback_data="close")],
    ])

    try:
        await callback_query.message.edit_text(
            text=text,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
        await safe_answer(callback_query)
    except Exception as e:
        logger.debug("About edit failed: %s", e)
        await safe_answer(callback_query, "No changes", show_alert=False)


async def _handle_start_back(client, callback_query):
    """Re-show the /start welcome message in place."""
    from leechbot.commands import _send_welcome

    try:
        await _send_welcome(client, callback_query.message, edit=True)
        await safe_answer(callback_query, "Welcome ✓")
    except Exception as e:
        logger.debug("Start back failed: %s", e)
        await safe_answer(callback_query, "Use /start", show_alert=False)
