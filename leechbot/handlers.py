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
import config
from pyrogram import filters

from leechbot import app, OWNER
from leechbot.utility.variables import BOT, Paths, MSG, BotTimes, BotStats, current_user_id, UserRegistry, get_ctx
from leechbot.utility.helper import (
    isLink, setThumbnail, message_deleter, send_settings, extract_links,
)

logger = logging.getLogger(__name__)


def set_handler_context(message):
    """Set per-user context for message handlers."""
    if message.from_user:
        uid = message.from_user.id

        # Rate limit check (normal users only — admins/owners bypass)
        is_admin = uid == config.OWNER_ID or uid in config.ALLOWED_ADMINS
        if not is_admin and not UserRegistry.check_rate_limit(uid):
            return None, "<b>⏳ Please slow down.</b> Wait a few seconds before sending another message."

        current_user_id.set(uid)
        ctx = UserRegistry.get(uid)

        # Check moderation access
        from leechbot.utility.moderation import Moderation
        allowed, reason = Moderation.check_access(uid)
        if not allowed:
            return None, reason

        return ctx, ""
    return None, ""


# =============================================================================
# Reply Handlers (prefix/suffix)
# =============================================================================
@app.on_message(filters.reply)
async def handle_reply(client, message):
    """Handle reply messages for setting prefix/suffix/autorename."""
    ctx, err = set_handler_context(message)
    if err:
        await message.reply_text(err)
        return
    text = message.text or message.caption
    if not text:
        return  # Ignore non-text replies (photos, stickers, etc.)

    if BOT.State.prefix:
        BOT.Setting.prefix = text
        BOT.State.prefix = False
        await send_settings(client, message, message.reply_to_message_id, False)
        await message.delete()
    elif BOT.State.suffix:
        BOT.Setting.suffix = text
        BOT.State.suffix = False
        await send_settings(client, message, message.reply_to_message_id, False)
        await message.delete()
    elif BOT.State.setting_autorename:
        BOT.Setting.autorename_template = text
        BOT.State.setting_autorename = False
        await message.reply_text(
            f"<b>🏷️ Auto-Rename Template Set</b>\n\n"
            f"<b>📝 Template:</b> <code>{BOT.Setting.autorename_template}</code>\n\n"
            f"<b>💡 The bot will use this pattern to rename files.</b>",
            quote=True,
        )
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

    # Set per-user context
    ctx, err = set_handler_context(message)
    if err:
        await message.reply_text(err)
        return

    # Reset options
    BOT.Options.custom_name = ""
    BOT.Options.zip_pswd = ""
    BOT.Options.unzip_pswd = ""
    BOT.Options.http_headers = None

    if MSG.src_request_msg:
        try:
            await MSG.src_request_msg.delete()
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

        # Extract all URLs (and magnets) from the remaining text. Handles
        # forwarded messages where multiple links may share a line, and
        # deduplicates while preserving first-seen order.
        get_ctx().task.source = extract_links("\n".join(temp_source))

        # Gallery mode: skip type selection, go straight to download
        if BOT.Mode.gallery:
            from datetime import datetime
            from asyncio import get_running_loop
            from leechbot.utility.task_manager import taskScheduler

            BOT.Mode.type = "normal"

            MSG.status_msg = await app.send_message(
                chat_id=message.from_user.id,
                text="<b>🚀 Initializing Gallery Download...</b>\n\nPlease wait while I prepare your download",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🚫 Cancel", callback_data="cancel")]]
                ),
                disable_web_page_preview=True
            )

            await message.delete()
            BOT.State.started = False
            ctx.start_time = datetime.now()

            import contextvars
            from leechbot.utility.user_state import TaskQueue

            BotStats.total_tasks += 1
            info = {
                "mode": BOT.Mode.mode,
                "type": BOT.Mode.type,
                "links": list(get_ctx().task.source),
            }
            started, position = TaskQueue.add(
                user_id=message.from_user.id,
                factory=taskScheduler,
                context=contextvars.copy_context(),
                info=info,
            )

            if not started:
                if position == -1:
                    try:
                        await MSG.status_msg.edit_text(
                            "<b>⚠️ Queue Limit Reached</b>\n\n"
                            "You have too many queued tasks. Please wait for one to finish.",
                            reply_markup=InlineKeyboardMarkup(
                                [[InlineKeyboardButton("🚫 Cancel", callback_data="cancel")]]
                            ),
                        )
                    except Exception:
                        pass
                    return
                try:
                    await MSG.status_msg.edit_text(
                        f"<b>⏳ Task Queued</b>\n\n"
                        f"Position: <code>{position}</code>\n"
                        f"Max concurrent tasks reached. Your task will start automatically.",
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton("🚫 Cancel", callback_data="cancel")]]
                        ),
                    )
                except Exception:
                    pass
            return

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📄 Regular ✨", callback_data="normal")],
            [
                InlineKeyboardButton("🗜️ Compress", callback_data="zip"),
                InlineKeyboardButton("Extract 📂", callback_data="unzip"),
            ],
            [InlineKeyboardButton("🔄 Unzip+Zip ✨", callback_data="undzip")],
        ])

        mode_text = BOT.Mode.mode.capitalize()
        options_text = f"""<b>🎯 Select Upload Type For {mode_text}</b>

📄 <b>Regular</b> — Normal file upload
🗜️ <b>Compress</b> — Zip file upload
📂 <b>Extract</b> — Extract archive before upload
🔄 <b>Unzip+Zip</b> — Extract then compress"""

        await message.reply_text(text=options_text, reply_markup=keyboard, quote=True)

    elif BOT.State.started:
        await message.delete()
        msg = await message.reply_text("<b>⏳ I'm Already Working! Please Wait...</b>")
        await message_deleter(message, msg)


# =============================================================================
# Photo Handler (Thumbnail)
# =============================================================================
@app.on_message(filters.photo & filters.private)
async def handle_photo(client, message):
    """Handle photo messages to set thumbnail."""
    ctx, err = set_handler_context(message)
    if err:
        await message.reply_text(err)
        return

    msg = await message.reply_text("<b>🖼️ Processing Thumbnail...</b>")
    success = await setThumbnail(message)
    if success:
        await msg.edit_text("<b>✅ Thumbnail Set Successfully</b>")
        await message.delete()
    else:
        await msg.edit_text("<b>❎ Failed To Set Thumbnail</b>")
    await message_deleter(message, msg)


# =============================================================================
# Document Handler (Cookies.txt upload)
# =============================================================================
@app.on_message(filters.document & filters.private)
async def handle_document(client, message):
    """Handle document uploads — auto-detect cookies.txt for yt-dlp."""
    if message.chat.id != OWNER:
        return

    ctx, err = set_handler_context(message)
    if err:
        await message.reply_text(err)
        return

    file_name = message.document.file_name or ""
    if file_name.lower() == "cookies.txt":
        msg = await message.reply_text("<b>🍪 Downloading cookies file...</b>")
        try:
            await message.download(file_name=Paths.COOKIE_FILE)
            await msg.edit_text(
                "<b>✅ Cookies file saved!</b>\n\n"
                "YouTube downloads should now work.\n"
                "Use <code>/cookies</code> to verify status."
            )
            logger.info("Cookies file uploaded and saved to %s", Paths.COOKIE_FILE)
        except Exception as e:
            await msg.edit_text(f"<b>❌ Failed to save cookies:</b> <code>{e}</code>")
            logger.error("Cookie file save error: %s", e)
        await message_deleter(message, msg)


# =============================================================================
# Text Input Handler (Auto-Delete Delay)
# =============================================================================
@app.on_message(filters.text & filters.private & ~filters.command([
    "start", "tupload", "gdupload", "drupload", "ytupload", "glupload",
    "settings", "help", "setname", "autorename", "anime", "zipaswd", "unzipaswd",
    "stats", "cancel", "cancel_all", "queue", "format", "formats", "preview",
    "speed", "broadcast", "admin", "cookies", "setcookies",
    "clearcookies", "update",
]))
async def handle_text_input(client, message):
    """Handle text inputs for settings flow."""
    ctx, err = set_handler_context(message)
    if err:
        await message.reply_text(err)
        return

    # Auto-delete delay
    if getattr(BOT.State, "setting_autodelete_delay", False):
        try:
            delay = int(message.text.strip())
            if 5 <= delay <= 300:
                BOT.Setting.auto_delete_delay = delay
                BOT.State.setting_autodelete_delay = False
                await message.reply_text(f"<b>✅ Auto-delete delay set to {delay} seconds.</b>")
                await message.delete()
            else:
                await message.reply_text("<b>⚠️ Please enter a number between 5 and 300.</b>")
                await message.delete()
        except ValueError:
            await message.reply_text("<b>⚠️ Invalid number. Please try again.</b>")
            await message.delete()
