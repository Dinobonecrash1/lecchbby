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
"""

import os
import logging
from datetime import datetime
from asyncio import get_event_loop

from leechbot import app, OWNER
from leechbot.utility.variables import BOT, MSG, BotTimes, Paths
from leechbot.utility.handler import cancelTask
from leechbot.utility.helper import send_settings, sysINFO, sysINFO_full, status_keyboard
import config

logger = logging.getLogger(__name__)


@app.on_callback_query()
async def handle_callback(client, callback_query):
    """Handle all inline keyboard callbacks."""
    data = callback_query.data

    # =========================================================================
    # Upload type selection
    # =========================================================================
    if data in ["normal", "zip", "unzip", "undzip"]:
        BOT.Mode.type = data
        await callback_query.message.delete()
        await app.delete_messages(
            chat_id=callback_query.message.chat.id,
            message_ids=callback_query.message.reply_to_message_id,
        )

        from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

        MSG.status_msg = await app.send_message(
            chat_id=OWNER,
            text="**🚀 Initializing Task...**\n\nPlease Wait While I Prepare Your Download",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🚫 Cancel", callback_data="cancel")]]
            ),
        )

        BOT.State.task_going = True
        BOT.State.started = False
        BotTimes.start_time = datetime.now()

        from leechbot.utility.task_manager import taskScheduler

        event_loop = get_event_loop()
        BOT.TASK = event_loop.create_task(taskScheduler())
        try:
            await BOT.TASK
        finally:
            BOT.State.task_going = False

    # =========================================================================
    # Settings menu
    # =========================================================================
    elif data == "settings_menu":
        await send_settings(client, callback_query.message, callback_query.message.id, False)

    # =========================================================================
    # Video settings
    # =========================================================================
    elif data == "video":
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

    # =========================================================================
    # Caption settings
    # =========================================================================
    elif data == "caption":
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

    # =========================================================================
    # Thumbnail settings
    # =========================================================================
    elif data == "thumb":
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

    # =========================================================================
    # Delete thumbnail
    # =========================================================================
    elif data == "del-thumb":
        if BOT.Setting.thumbnail and os.path.exists(Paths.THMB_PATH):
            try:
                os.remove(Paths.THMB_PATH)
            except OSError as e:
                logger.warning(f"Failed to delete thumbnail: {e}")
        BOT.Setting.thumbnail = False
        await send_settings(client, callback_query.message, callback_query.message.id, False)

    # =========================================================================
    # Prefix / Suffix
    # =========================================================================
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

    # =========================================================================
    # Caption style
    # =========================================================================
    elif data in ["code-Monospace", "p-Regular", "b-Bold", "i-Italic", "u-Underlined"]:
        res = data.split("-")
        BOT.Options.caption = res[0]
        BOT.Setting.caption = res[1]
        await send_settings(client, callback_query.message, callback_query.message.id, False)

    # =========================================================================
    # Video split
    # =========================================================================
    elif data in ["split-true", "split-false"]:
        BOT.Options.is_split = data == "split-true"
        BOT.Setting.split_video = "Split" if data == "split-true" else "Zip"
        await send_settings(client, callback_query.message, callback_query.message.id, False)

    # =========================================================================
    # Video convert
    # =========================================================================
    elif data in ["convert-true", "convert-false"]:
        BOT.Options.convert_video = data == "convert-true"
        BOT.Setting.convert_video = "Yes" if data == "convert-true" else "No"
        await send_settings(client, callback_query.message, callback_query.message.id, False)

    # =========================================================================
    # Video format
    # =========================================================================
    elif data in ["mp4", "mkv"]:
        BOT.Options.video_out = data
        await send_settings(client, callback_query.message, callback_query.message.id, False)

    # =========================================================================
    # Quality
    # =========================================================================
    elif data in ["q-High", "q-Low"]:
        BOT.Setting.convert_quality = data.split("-")[-1]
        BOT.Options.convert_quality = BOT.Setting.convert_quality == "High"
        await send_settings(client, callback_query.message, callback_query.message.id, False)

    # =========================================================================
    # Upload mode
    # =========================================================================
    elif data in ["media", "document"]:
        BOT.Options.stream_upload = data == "media"
        BOT.Setting.stream_upload = "Media" if data == "media" else "Document"
        await send_settings(client, callback_query.message, callback_query.message.id, False)

    # =========================================================================
    # Auto-delete settings
    # =========================================================================
    elif data == "autodelete":
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

    elif data == "toggle_autodelete":
        BOT.Setting.auto_delete = not BOT.Setting.auto_delete
        callback_query.data = "autodelete"
        await handle_callback(client, callback_query)

    elif data == "set_autodelete_delay":
        from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

        await callback_query.message.edit_text(
            "**⏱️ Send the delay in seconds**\n\nReply to this message with a number between 5 and 300.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("❰ Back", callback_data="autodelete")]]
            ),
        )
        BOT.State.setting_autodelete_delay = True

    # =========================================================================
    # Photo Mode (Group vs Single)
    # =========================================================================
    elif data == "photo_mode":
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

    elif data in ["photo-group", "photo-single"]:
        BOT.Setting.photo_mode = "Group" if data == "photo-group" else "Single"
        await send_settings(client, callback_query.message, callback_query.message.id, False)

    # =========================================================================
    # Auto Update
    # =========================================================================
    elif data == "do_update":
        from leechbot.updater import perform_update

        await callback_query.message.edit_text("**🔄 Updating... Please wait.**")

        result = perform_update()

        if result["success"]:
            await callback_query.message.edit_text(
                f"**✅ Update Complete!**\n\n"
                f"**New commit:** `{result['new_commit']}`\n\n"
                f"⚠️ **Restart required.** The bot will restart automatically.\n\n"
                f"{result['message'][:1000]}"
            )
            # Restart the bot
            import sys
            logger.info("Restarting after update...")
            os.execv(sys.executable, [sys.executable, "-m", "leechbot"])
        else:
            await callback_query.message.edit_text(
                f"**❌ Update Failed**\n\n`{result['message'][:500]}`"
            )

    # =========================================================================
    # Close / Back
    # =========================================================================
    elif data == "close":
        await callback_query.message.delete()

    elif data == "back":
        await send_settings(client, callback_query.message, callback_query.message.id, False)

    # =========================================================================
    # YTDL confirmation
    # =========================================================================
    elif data in ["ytdl-true", "ytdl-false"]:
        from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

        BOT.Mode.ytdl = data == "ytdl-true"
        await callback_query.message.delete()
        await app.delete_messages(
            chat_id=callback_query.message.chat.id,
            message_ids=callback_query.message.reply_to_message_id,
        )

        MSG.status_msg = await app.send_message(
            chat_id=OWNER,
            text="**🚀 Initializing Task...**\n\nPlease Wait While I Prepare Your Download",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Cancel", callback_data="cancel")]]
            ),
        )

        BOT.State.task_going = True
        BOT.State.started = False
        BotTimes.start_time = datetime.now()

        from leechbot.utility.task_manager import taskScheduler

        event_loop = get_event_loop()
        BOT.TASK = event_loop.create_task(taskScheduler())
        try:
            await BOT.TASK
        finally:
            BOT.State.task_going = False

    # =========================================================================
    # Cancel
    # =========================================================================
    elif data == "cancel":
        await cancelTask("User cancelled the task")

    # =========================================================================
    # Format Selection
    # =========================================================================
    elif data.startswith("fmt-"):
        fmt = data[4:]
        BOT.Setting.ytdl_format = fmt
        await callback_query.message.edit_text(
            f"**✅ YT-DLP Format Updated**\n\n**Selected:** `{fmt}`"
        )
        await callback_query.answer("Format saved")

    # =========================================================================
    # Speed Limit
    # =========================================================================
    elif data.startswith("spd-"):
        speed_val = data[4:]
        config.BANDWIDTH_LIMIT = speed_val
        display_val = speed_val if speed_val else "Unlimited"
        await callback_query.message.edit_text(
            f"**✅ Bandwidth Limit Updated**\n\n**Limit:** `{display_val}`"
        )
        await callback_query.answer("Speed limit saved")

    # =========================================================================
    # System Info
    # =========================================================================
    elif data == "sys_refresh":
        original_text = callback_query.message.text or callback_query.message.caption or ""
        parts = original_text.split("⌬─────")
        if len(parts) >= 2:
            new_text = parts[0] + sysINFO()
        else:
            new_text = original_text + "\n" + sysINFO()
        await callback_query.message.edit_text(
            text=new_text,
            disable_web_page_preview=True,
            reply_markup=status_keyboard(),
        )
        await callback_query.answer("System info refreshed")

    elif data == "sys_stats":
        original_text = callback_query.message.text or callback_query.message.caption or ""
        parts = original_text.split("⌬─────")
        if len(parts) >= 2:
            new_text = parts[0] + sysINFO_full()
        else:
            new_text = original_text + "\n" + sysINFO_full()
        await callback_query.message.edit_text(
            text=new_text,
            disable_web_page_preview=True,
            reply_markup=status_keyboard(),
        )
        await callback_query.answer("Showing detailed stats")

    elif data == "sys_close":
        await callback_query.message.delete()
        await callback_query.answer("Closed")
