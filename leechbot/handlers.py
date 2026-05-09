# =============================================================================
# Telegram Leech Bot - Message Handlers
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Message handlers for replies, URLs, photos, and text input.
"""

import logging
from pyrogram import filters

from leechbot import app
from leechbot.utility.variables import BOT
from leechbot.utility.helper import (
    isLink, setThumbnail, message_deleter, send_settings,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Reply Handlers (prefix/suffix)
# =============================================================================
@app.on_message(filters.reply)
async def handle_reply(client, message):
    """Handle reply messages for setting prefix/suffix."""
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
@app.on_message(filters.create(isLink) & ~filters.photo)
async def handle_url(client, message):
    """
    Handle URL messages for download processing.
    Parses options like custom name, zip password, and unzip password.
    """
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    # Reset options
    BOT.Options.custom_name = ""
    BOT.Options.zip_pswd = ""
    BOT.Options.unzip_pswd = ""

    if hasattr(BOT, '_src_request_msg') and BOT._src_request_msg:
        try:
            await BOT._src_request_msg.delete()
        except Exception:
            pass

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

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📄 Regular ✨", callback_data="normal")],
            [
                InlineKeyboardButton("🗜️ Compress", callback_data="zip"),
                InlineKeyboardButton("Extract 📂", callback_data="unzip"),
            ],
            [InlineKeyboardButton("🔄 Unzip+Zip ✨", callback_data="undzip")],
        ])

        mode_text = BOT.Mode.mode.capitalize()
        options_text = f"""
**🎯 Select Upload Type For {mode_text}**

📄 **Regular** - Normal File Upload
🗜️ **Compress** - Zip File Upload
📂 **Extract** - Extract Archive Before Upload
🔄 **Unzip+Zip** - Extract Then Compress
"""

        await message.reply_text(text=options_text, reply_markup=keyboard, quote=True)

    elif BOT.State.started:
        await message.delete()
        msg = await message.reply_text("**⏳ I'm Already Working! Please Wait...**")
        await message_deleter(message, msg)


# =============================================================================
# Photo Handler (Thumbnail)
# =============================================================================
@app.on_message(filters.photo & filters.private)
async def handle_photo(client, message):
    """Handle photo messages to set thumbnail."""
    msg = await message.reply_text("**🖼️ Processing Thumbnail...**")
    success = await setThumbnail(message)
    if success:
        await msg.edit_text("**✅ Thumbnail Set Successfully**")
        await message.delete()
    else:
        await msg.edit_text("**❎ Failed To Set Thumbnail**")
    await message_deleter(message, msg)


# =============================================================================
# Text Input Handler (Auto-Delete Delay)
# =============================================================================
@app.on_message(filters.text & filters.private & ~filters.command([
    "start", "tupload", "gdupload", "drupload", "ytupload",
    "settings", "help", "setname", "zipaswd", "unzipaswd",
    "stats", "cancel", "cancel_all", "queue", "format",
    "speed", "broadcast", "admin",
]))
async def handle_text_input(client, message):
    """Handle text inputs for setting auto-delete delay."""
    if getattr(BOT.State, "setting_autodelete_delay", False):
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
