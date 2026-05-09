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
from asyncio import get_event_loop

from leechbot import app, OWNER
from leechbot.utility.variables import BOT, MSG, BotTimes, Paths
from leechbot.utility.handler import cancelTask
from leechbot.utility.helper import send_settings, sysINFO, sysINFO_full, status_keyboard
import config

logger = logging.getLogger(__name__)


# =============================================================================
# Main Dispatcher
# =============================================================================
@app.on_callback_query()
async def handle_callback(client, callback_query):
    """Route callback queries to the appropriate handler."""
    data = callback_query.data
    logger.debug("Callback: %s", data)

    try:
        # --- Upload type selection ---
        if data in ("normal", "zip", "unzip", "undzip"):
            await _handle_upload_type(client, callback_query, data)

        # --- Settings navigation ---
        elif data == "settings_menu":
            await send_settings(client, callback_query.message, callback_query.message.id, False)
            await callback_query.answer()

        # --- Video settings ---
        elif data == "video":
            await _handle_video_settings(client, callback_query)

        # --- Caption settings ---
        elif data == "caption":
            await _handle_caption_settings(client, callback_query)

        # --- Thumbnail settings ---
        elif data == "thumb":
            await _handle_thumb_settings(client, callback_query)

        elif data == "del-thumb":
            await _handle_delete_thumb(client, callback_query)

        # --- Prefix / Suffix ---
        elif data == "set-prefix":
            await callback_query.message.edit_text(
                "**⌨️ Send Text To Set As Prefix**\n\nReply To This Message With Your Prefix"
            )
            BOT.State.prefix = True
            await callback_query.answer("Send your prefix now")

        elif data == "set-suffix":
            await callback_query.message.edit_text(
                "**⌨️ Send Text To Set As Suffix**\n\nReply To This Message With Your Suffix"
            )
            BOT.State.suffix = True
            await callback_query.answer("Send your suffix now")

        # --- Caption style ---
        elif data in ("code-Monospace", "p-Regular", "b-Bold", "i-Italic", "u-Underlined"):
            res = data.split("-")
            BOT.Options.caption = res[0]
            BOT.Setting.caption = res[1]
            await send_settings(client, callback_query.message, callback_query.message.id, False)
            await callback_query.answer(f"Caption style: {res[1]}")

        # --- Video split ---
        elif data in ("split-true", "split-false"):
            BOT.Options.is_split = data == "split-true"
            BOT.Setting.split_video = "Split" if data == "split-true" else "Zip"
            await send_settings(client, callback_query.message, callback_query.message.id, False)
            await callback_query.answer()

        # --- Video convert ---
        elif data in ("convert-true", "convert-false"):
            BOT.Options.convert_video = data == "convert-true"
            BOT.Setting.convert_video = "Yes" if data == "convert-true" else "No"
            await send_settings(client, callback_query.message, callback_query.message.id, False)
            await callback_query.answer()

        # --- Video format ---
        elif data in ("mp4", "mkv"):
            BOT.Options.video_out = data
            await send_settings(client, callback_query.message, callback_query.message.id, False)
            await callback_query.answer(f"Format: {data.upper()}")

        # --- Quality ---
        elif data in ("q-High", "q-Low"):
            quality = data.split("-")[-1]
            BOT.Setting.convert_quality = quality
            BOT.Options.convert_quality = quality == "High"
            await send_settings(client, callback_query.message, callback_query.message.id, False)
            await callback_query.answer(f"Quality: {quality}")

        # --- Upload mode ---
        elif data in ("media", "document"):
            BOT.Options.stream_upload = data == "media"
            BOT.Setting.stream_upload = "Media" if data == "media" else "Document"
            await send_settings(client, callback_query.message, callback_query.message.id, False)
            await callback_query.answer(f"Upload as: {BOT.Setting.stream_upload}")

        # --- Auto-delete ---
        elif data == "autodelete":
            await _handle_autodelete_menu(client, callback_query)

        elif data == "toggle_autodelete":
            BOT.Setting.auto_delete = not BOT.Setting.auto_delete
            callback_query.data = "autodelete"
            await handle_callback(client, callback_query)
            await callback_query.answer(f"Auto-delete: {'ON' if BOT.Setting.auto_delete else 'OFF'}")

        elif data == "set_autodelete_delay":
            from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
            await callback_query.message.edit_text(
                "**⏱️ Send the delay in seconds**\n\nReply to this message with a number between 5 and 300.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("❰ Back", callback_data="autodelete")]]
                ),
            )
            BOT.State.setting_autodelete_delay = True
            await callback_query.answer()

        # --- Photo mode ---
        elif data == "photo_mode":
            await _handle_photo_mode_menu(client, callback_query)

        elif data in ("photo-group", "photo-single"):
            BOT.Setting.photo_mode = "Group" if data == "photo-group" else "Single"
            await send_settings(client, callback_query.message, callback_query.message.id, False)
            await callback_query.answer(f"Photo mode: {BOT.Setting.photo_mode}")

        # --- Auto update ---
        elif data == "do_update":
            await _handle_do_update(client, callback_query)

        # --- Close / Back ---
        elif data == "close":
            await callback_query.message.delete()
            await callback_query.answer("Closed")

        elif data == "back":
            await send_settings(client, callback_query.message, callback_query.message.id, False)
            await callback_query.answer()

        # --- YTDL confirmation ---
        elif data in ("ytdl-true", "ytdl-false"):
            await _handle_ytdl_confirm(client, callback_query, data)

        # --- Cancel ---
        elif data == "cancel":
            await callback_query.answer("Cancelling...")
            await cancelTask("User cancelled the task")

        # --- Format selection ---
        elif data.startswith("fmt-"):
            fmt = data[4:]
            BOT.Setting.ytdl_format = fmt
            await callback_query.message.edit_text(
                f"**✅ YT-DLP Format Updated**\n\n**Selected:** `{fmt}`"
            )
            await callback_query.answer("Format saved ✓")

        # --- Speed limit ---
        elif data.startswith("spd-"):
            speed_val = data[4:]
            config.BANDWIDTH_LIMIT = speed_val
            display_val = speed_val if speed_val else "Unlimited"
            await callback_query.message.edit_text(
                f"**✅ Bandwidth Limit Updated**\n\n**Limit:** `{display_val}`"
            )
            await callback_query.answer("Speed limit saved ✓")

        # --- System info ---
        elif data == "sys_refresh":
            await _handle_sys_refresh(client, callback_query)

        elif data == "sys_stats":
            await _handle_sys_stats(client, callback_query)

        elif data == "sys_close":
            await callback_query.message.delete()
            await callback_query.answer("Closed")

        else:
            await callback_query.answer("⚠️ Unknown action", show_alert=True)

    except Exception as e:
        logger.error("Callback error [%s]: %s", data, e, exc_info=True)
        try:
            await callback_query.answer("❌ Something went wrong", show_alert=True)
        except Exception:
            pass


# =============================================================================
# Upload Type Selection
# =============================================================================
async def _handle_upload_type(client, callback_query, data: str):
    """Handle upload type selection (normal/zip/unzip/undzip)."""
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    from leechbot.utility.task_manager import taskScheduler

    BOT.Mode.type = data
    await callback_query.message.delete()
    await app.delete_messages(
        chat_id=callback_query.message.chat.id,
        message_ids=callback_query.message.reply_to_message_id,
    )

    type_labels = {
        "normal": "📄 Regular",
        "zip": "🗜️ Compress",
        "unzip": "📂 Extract",
        "undzip": "🔄 Unzip+Zip",
    }

    MSG.status_msg = await app.send_message(
        chat_id=OWNER,
        text=f"**🚀 Starting {type_labels.get(data, data)} Upload...**\n\nPlease wait while I prepare your download",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🚫 Cancel", callback_data="cancel")]]
        ),
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


# =============================================================================
# Video Settings
# =============================================================================
async def _handle_video_settings(client, callback_query):
    """Show video settings submenu."""
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    keyboard = InlineKeyboardMarkup([
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
        [InlineKeyboardButton("❰ Back", callback_data="back")],
    ])

    await callback_query.message.edit_text(
        f"""**⚙️ Video Settings**

┏🔄 **Convert:** `{BOT.Setting.convert_video}`
┣✂️ **Split:** `{BOT.Setting.split_video}`
┣🎬 **Format:** `{BOT.Options.video_out}`
┗🔴 **Quality:** `{BOT.Setting.convert_quality}`""",
        reply_markup=keyboard,
    )
    await callback_query.answer()


# =============================================================================
# Caption Settings
# =============================================================================
async def _handle_caption_settings(client, callback_query):
    """Show caption style submenu."""
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Monospace", callback_data="code-Monospace"),
            InlineKeyboardButton("Bold", callback_data="b-Bold"),
        ],
        [
            InlineKeyboardButton("Italic", callback_data="i-Italic"),
            InlineKeyboardButton("Underline", callback_data="u-Underlined"),
        ],
        [InlineKeyboardButton("Regular", callback_data="p-Regular")],
        [InlineKeyboardButton("❰ Back", callback_data="back")],
    ])

    await callback_query.message.edit_text(
        """**📝 Caption Font Style**

<code>Monospace</code>
Regular
**Bold**
__Italic__
__Underline__""",
        reply_markup=keyboard,
    )
    await callback_query.answer()


# =============================================================================
# Thumbnail Settings
# =============================================================================
async def _handle_thumb_settings(client, callback_query):
    """Show thumbnail settings submenu."""
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗑️ Delete Thumbnail", callback_data="del-thumb")],
        [InlineKeyboardButton("❰ Back", callback_data="back")],
    ])

    thmb_status = "✅ Set" if BOT.Setting.thumbnail else "🚫 None"
    await callback_query.message.edit_text(
        f"**🖼️ Thumbnail Settings**\n\n**Status:** {thmb_status}\n\n💡 Send An Image To Set As Thumbnail",
        reply_markup=keyboard,
    )
    await callback_query.answer()


async def _handle_delete_thumb(client, callback_query):
    """Delete the stored thumbnail."""
    if BOT.Setting.thumbnail and os.path.exists(Paths.THMB_PATH):
        try:
            os.remove(Paths.THMB_PATH)
        except OSError as e:
            logger.warning("Failed to delete thumbnail: %s", e)
    BOT.Setting.thumbnail = False
    await send_settings(client, callback_query.message, callback_query.message.id, False)
    await callback_query.answer("Thumbnail deleted ✓")


# =============================================================================
# Auto-Delete Menu
# =============================================================================
async def _handle_autodelete_menu(client, callback_query):
    """Show auto-delete settings submenu."""
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"✅ Auto-Delete: {'ON' if BOT.Setting.auto_delete else 'OFF'}",
                callback_data="toggle_autodelete",
            )
        ],
        [InlineKeyboardButton("⏱️ Set Delay", callback_data="set_autodelete_delay")],
        [InlineKeyboardButton("❰ Back", callback_data="back")],
    ])
    await callback_query.message.edit_text(
        f"**⏳ Auto-Delete Messages**\n\n"
        f"**Status:** {'Enabled' if BOT.Setting.auto_delete else 'Disabled'}\n"
        f"**Delay:** {BOT.Setting.auto_delete_delay} seconds\n\n"
        f"When enabled, bot messages will be automatically deleted after the specified delay.",
        reply_markup=keyboard,
    )
    await callback_query.answer()


# =============================================================================
# Photo Mode Menu
# =============================================================================
async def _handle_photo_mode_menu(client, callback_query):
    """Show photo upload mode submenu."""
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    current = BOT.Setting.photo_mode
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"{'✅ ' if current == 'Group' else ''}📦 Group (batch of 10)",
                callback_data="photo-group",
            ),
        ],
        [
            InlineKeyboardButton(
                f"{'✅ ' if current == 'Single' else ''}📷 Single (one by one)",
                callback_data="photo-single",
            ),
        ],
        [InlineKeyboardButton("❰ Back", callback_data="back")],
    ])
    await callback_query.message.edit_text(
        f"**📸 Photo Upload Mode**\n\n"
        f"**Current:** `{current}`\n\n"
        f"📦 **Group** — Send photos in batches of 10 (faster, cleaner)\n"
        f"📷 **Single** — Send each photo individually\n\n"
        f"💡 Group mode uses Telegram's media groups (max 10 per batch).",
        reply_markup=keyboard,
    )
    await callback_query.answer()


# =============================================================================
# YTDL Confirmation
# =============================================================================
async def _handle_ytdl_confirm(client, callback_query, data: str):
    """Handle YT-DLP mode confirmation."""
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    from leechbot.utility.task_manager import taskScheduler

    BOT.Mode.ytdl = data == "ytdl-true"
    await callback_query.message.delete()
    await app.delete_messages(
        chat_id=callback_query.message.chat.id,
        message_ids=callback_query.message.reply_to_message_id,
    )

    MSG.status_msg = await app.send_message(
        chat_id=OWNER,
        text="**🚀 Initializing YT-DLP Download...**\n\nPlease wait while I prepare your download",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🚫 Cancel", callback_data="cancel")]]
        ),
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


# =============================================================================
# Do Update
# =============================================================================
async def _handle_do_update(client, callback_query):
    """Handle the update action."""
    from leechbot.updater import perform_update

    await callback_query.message.edit_text("**🔄 Updating... Please wait.**")
    await callback_query.answer("Updating...")

    result = perform_update()

    if result["success"]:
        await callback_query.message.edit_text(
            f"**✅ Update Complete!**\n\n"
            f"**New commit:** `{result['new_commit']}`\n\n"
            f"⚠️ **Restart required.** The bot will restart automatically.\n\n"
            f"{result['message'][:1000]}"
        )
        # Restart the bot
        logger.info("Restarting after update...")
        try:
            os.execv(sys.executable, [sys.executable, "-m", "leechbot"])
        except Exception as e:
            logger.error("Restart failed: %s", e)
            await callback_query.message.edit_text(
                f"**✅ Update Complete!**\n\n"
                f"**New commit:** `{result['new_commit']}`\n\n"
                f"⚠️ **Auto-restart failed.** Please restart the bot manually.\n"
                f"`python3 -m leechbot`"
            )
    else:
        await callback_query.message.edit_text(
            f"**❌ Update Failed**\n\n`{result['message'][:500]}`"
        )


# =============================================================================
# System Info Refresh
# =============================================================================
def _strip_sysinfo(text: str) -> str:
    """Strip existing system info block from message text."""
    parts = text.split("⌬─────")
    return parts[0].rstrip() if len(parts) >= 2 else text


async def _handle_sys_refresh(client, callback_query):
    """Refresh system info display."""
    original_text = callback_query.message.text or callback_query.message.caption or ""
    new_text = _strip_sysinfo(original_text) + sysINFO()
    try:
        await callback_query.message.edit_text(
            text=new_text,
            disable_web_page_preview=True,
            reply_markup=status_keyboard(),
        )
        await callback_query.answer("Refreshed ✓")
    except Exception as e:
        logger.debug("Sys refresh error: %s", e)
        await callback_query.answer("No changes", show_alert=False)


async def _handle_sys_stats(client, callback_query):
    """Show detailed system stats."""
    original_text = callback_query.message.text or callback_query.message.caption or ""
    new_text = _strip_sysinfo(original_text) + sysINFO_full()
    try:
        await callback_query.message.edit_text(
            text=new_text,
            disable_web_page_preview=True,
            reply_markup=status_keyboard(),
        )
        await callback_query.answer("Detailed stats ✓")
    except Exception as e:
        logger.debug("Sys stats error: %s", e)
        await callback_query.answer("No changes", show_alert=False)
