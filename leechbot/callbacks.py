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


async def safe_answer(callback_query, *args, **kwargs):
    """Safe wrapper for callback_query.answer() to suppress QueryIdInvalid."""
    try:
        await safe_answer(callback_query, *args, **kwargs)
    except Exception:
        pass


# =============================================================================
# Main Dispatcher
# =============================================================================
@app.on_callback_query()
async def handle_callback(client, callback_query):
    """Route callback queries to the appropriate handler."""
    data = callback_query.data
    logger.debug("Callback: %s", data)

    try:
        # --- Help system (3.1.34) ---
        if data == "help_main" or data == "help_close":
            await _handle_help_main(client, callback_query)

        # --- About + Start navigation (3.1.35) ---
        elif data == "about":
            await _handle_about(client, callback_query)
        elif data == "start_back":
            await _handle_start_back(client, callback_query)

        # --- Upload type selection ---
        elif data in ("normal", "zip", "unzip", "undzip"):
            await _handle_upload_type(client, callback_query, data)

        # --- Settings navigation ---
        elif data == "settings_menu":
            await send_settings(client, callback_query.message, callback_query.message.id, False)
            await safe_answer(callback_query)

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
                "<b>⌨️ Set Prefix</b>\n\n"
                "Send your prefix text now.\n"
                "Reply to this message with it.\n\n"
                "<b>💡 Tip:</b> Prefix is prepended to file names."
            )
            BOT.State.prefix = True
            await safe_answer(callback_query, "Send your prefix now")

        elif data == "set-suffix":
            await callback_query.message.edit_text(
                "<b>⌨️ Set Suffix</b>\n\n"
                "Send your suffix text now.\n"
                "Reply to this message with it.\n\n"
                "<b>💡 Tip:</b> Suffix is appended to file names."
            )
            BOT.State.suffix = True
            await safe_answer(callback_query, "Send your suffix now")

        # --- Caption style ---
        elif data in ("code-Monospace", "p-Regular", "b-Bold", "i-Italic", "u-Underlined"):
            res = data.split("-")
            BOT.Options.caption = res[0]
            BOT.Setting.caption = res[1]
            await send_settings(client, callback_query.message, callback_query.message.id, False)
            await safe_answer(callback_query, f"Caption style: {res[1]}")

        # --- Video split ---
        elif data in ("split-true", "split-false"):
            BOT.Options.is_split = data == "split-true"
            BOT.Setting.split_video = "Split" if data == "split-true" else "Zip"
            await send_settings(client, callback_query.message, callback_query.message.id, False)
            await safe_answer(callback_query)

        # --- Video convert ---
        elif data in ("convert-true", "convert-false"):
            BOT.Options.convert_video = data == "convert-true"
            BOT.Setting.convert_video = "Yes" if data == "convert-true" else "No"
            await send_settings(client, callback_query.message, callback_query.message.id, False)
            await safe_answer(callback_query)

        # --- Video format ---
        elif data in ("mp4", "mkv"):
            BOT.Options.video_out = data
            await send_settings(client, callback_query.message, callback_query.message.id, False)
            await safe_answer(callback_query, f"Format: {data.upper()}")

        # --- Quality ---
        elif data in ("q-High", "q-Low"):
            quality = data.split("-")[-1]
            BOT.Setting.convert_quality = quality
            BOT.Options.convert_quality = quality == "High"
            await send_settings(client, callback_query.message, callback_query.message.id, False)
            await safe_answer(callback_query, f"Quality: {quality}")

        # --- Upload mode ---
        elif data in ("media", "document"):
            BOT.Options.stream_upload = data == "media"
            BOT.Setting.stream_upload = "Media" if data == "media" else "Document"
            await send_settings(client, callback_query.message, callback_query.message.id, False)
            await safe_answer(callback_query, f"Upload as: {BOT.Setting.stream_upload}")

        # --- Auto-delete ---
        elif data == "autodelete":
            await _handle_autodelete_menu(client, callback_query)

        elif data == "toggle_autodelete":
            BOT.Setting.auto_delete = not BOT.Setting.auto_delete
            await _handle_autodelete_menu(client, callback_query)
            await safe_answer(callback_query, f"Auto-delete: {'ON' if BOT.Setting.auto_delete else 'OFF'}")

        elif data == "set_autodelete_delay":
            from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
            await callback_query.message.edit_text(
                "<b>⏱️ Set Auto-Delete Delay</b>\n\n"
                "Send a number between 5 and 300.\n"
                "This is the delay in <b>seconds</b>.\n\n"
                "<b>💡 Tip:</b> 30s is a good default.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("❰ Back", callback_data="autodelete")]]
                ),
            )
            BOT.State.setting_autodelete_delay = True
            await safe_answer(callback_query)

        # --- Photo mode ---
        elif data == "photo_mode":
            await _handle_photo_mode_menu(client, callback_query)

        elif data in ("photo-group", "photo-single"):
            BOT.Setting.photo_mode = "Group" if data == "photo-group" else "Single"
            await send_settings(client, callback_query.message, callback_query.message.id, False)
            await safe_answer(callback_query, f"Photo mode: {BOT.Setting.photo_mode}")

        # --- Auto update ---
        elif data == "do_update":
            await _handle_do_update(client, callback_query)

        # --- Close / Back ---
        elif data == "close":
            await callback_query.message.delete()
            await safe_answer(callback_query, "Closed")

        elif data == "back":
            await send_settings(client, callback_query.message, callback_query.message.id, False)
            await safe_answer(callback_query)

        # --- YTDL confirmation ---
        elif data in ("ytdl-true", "ytdl-false"):
            await _handle_ytdl_confirm(client, callback_query, data)

        # --- Cancel ---
        elif data == "cancel":
            await safe_answer(callback_query, "Cancelling...")
            await cancelTask("User cancelled the task")

        # --- Format selection ---
        elif data.startswith("fmt-"):
            fmt = data[4:]
            BOT.Setting.ytdl_format = fmt
            await callback_query.message.edit_text(
                f"<b>✅ Format Updated</b>\n\n"
                f"<b>Selected:</b> <code>{fmt}</code>"
            )
            await safe_answer(callback_query, "Format saved ✓")

        # --- Speed limit ---
        elif data.startswith("spd-"):
            speed_val = data[4:]
            config.BANDWIDTH_LIMIT = speed_val
            display_val = speed_val if speed_val else "Unlimited"
            await callback_query.message.edit_text(
                f"<b>✅ Bandwidth Limit Updated</b>\n\n"
                f"<b>Limit:</b> <code>{display_val}</code>"
            )
            await safe_answer(callback_query, "Speed limit saved ✓")
            await safe_answer(callback_query, "Speed limit saved ✓")

        # --- System info ---
        elif data == "sys_refresh":
            await _handle_sys_refresh(client, callback_query)

        elif data == "sys_stats":
            await _handle_sys_stats(client, callback_query)

        elif data == "sys_close":
            await callback_query.message.delete()
            await safe_answer(callback_query, "Closed")

        else:
            await safe_answer(callback_query, "⚠️ Unknown action", show_alert=True)

    except Exception as e:
        logger.error("Callback error [%s]: %s", data, e, exc_info=True)
        try:
            await safe_answer(callback_query, "❌ Something went wrong", show_alert=True)
        except Exception:
            pass

# =============================================================================
# Upload Type Selection
# =============================================================================
async def _handle_upload_type(client, callback_query, data: str):
    """Handle upload type selection (normal/zip/unzip/undzip)."""
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    from leechbot.utility.task_manager import taskScheduler

    # Bail if bot is shutting down — the dispatcher drains pending callbacks
    # before app.stop() completes, and starting a long task here will be
    # cancelled mid-flight (noisy CancelledError traceback).
    if BOT.State.shutting_down:
        logger.warning(
            "Callback %s ignored: bot is shutting down",
            data,
        )
        try:
            await safe_answer(callback_query, "⏳ Bot is shutting down, try again later.", show_alert=True)
        except Exception:
            pass
        return

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
        text=f"<b>🚀 Starting {type_labels.get(data, data)} Upload...</b>\n\nPlease wait while I prepare your download",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🚫 Cancel", callback_data="cancel")]]
        ),
        disable_web_page_preview=True
    )

    BOT.State.task_going = True
    BOT.State.started = False
    BotTimes.start_time = datetime.now()

    event_loop = get_running_loop()
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
        f"<b>⚙️ Video Settings</b>\n\n"
        f"• 🔄 <b>Convert:</b> <code>{BOT.Setting.convert_video}</code>\n"
        f"• ✂️ <b>Split:</b> <code>{BOT.Setting.split_video}</code>\n"
        f"• 🎬 <b>Format:</b> <code>{BOT.Options.video_out}</code>\n"
        f"• 🔴 <b>Quality:</b> <code>{BOT.Setting.convert_quality}</code>",
        reply_markup=keyboard,
    )
    await safe_answer(callback_query)

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
        "<b>📝 Caption Font Style</b>\n\n"
        "<code>Monospace</code>\n"
        "Regular\n"
        "<b>Bold</b>\n"
        "<i>Italic</i>\n"
        "<u>Underline</u>",
        reply_markup=keyboard,
    )
    await safe_answer(callback_query)

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
        f"<b>🖼️ Thumbnail Settings</b>\n\n"
        f"<b>Status:</b> {thmb_status}\n\n"
        f"💡 Send an image to set as thumbnail.",
        reply_markup=keyboard,
    )
    await safe_answer(callback_query)

async def _handle_delete_thumb(client, callback_query):
    """Delete the stored thumbnail."""
    if BOT.Setting.thumbnail and os.path.exists(Paths.THMB_PATH):
        try:
            os.remove(Paths.THMB_PATH)
        except OSError as e:
            logger.warning("Failed to delete thumbnail: %s", e)
    BOT.Setting.thumbnail = False
    await send_settings(client, callback_query.message, callback_query.message.id, False)
    await safe_answer(callback_query, "Thumbnail deleted ✓")

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
        f"<b>⏳ Auto-Delete Messages</b>\n\n"
        f"<b>Status:</b> {'Enabled' if BOT.Setting.auto_delete else 'Disabled'}\n"
        f"<b>Delay:</b> {BOT.Setting.auto_delete_delay} seconds\n\n"
        f"When enabled, bot messages will be auto-deleted after the delay.",
        reply_markup=keyboard,
    )
    await safe_answer(callback_query)

# =============================================================================
# Photo Mode Menu
# =============================================================================
async def _handle_photo_mode_menu(client, callback_query):
    """Show photo upload mode submenu."""
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    current = BOT.Setting.photo_mode
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            f"{'✅ ' if current == 'Group' else ''}📦 Group (batch of 10)",
            callback_data="photo-group",
        )],
        [InlineKeyboardButton(
            f"{'✅ ' if current == 'Single' else ''}📷 Single (one by one)",
            callback_data="photo-single",
        )],
        [InlineKeyboardButton("❰ Back", callback_data="back")],
    ])
    await callback_query.message.edit_text(
        f"<b>📸 Photo Upload Mode</b>\n\n"
        f"<b>Current:</b> <code>{current}</code>\n\n"
        f"📦 <b>Group</b> — Send photos in batches of 10 (faster)\n"
        f"📷 <b>Single</b> — Send each photo individually\n\n"
        f"💡 Group mode uses Telegram media groups (max 10).",
        reply_markup=keyboard,
    )
    await safe_answer(callback_query)

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
        text="<b>🚀 Initializing YT-DLP Download...</b>\n\nPlease wait while I prepare your download",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🚫 Cancel", callback_data="cancel")]]
        ),
        disable_web_page_preview=True
    )

    BOT.State.task_going = True
    BOT.State.started = False
    BotTimes.start_time = datetime.now()

    event_loop = get_running_loop()
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

    await callback_query.message.edit_text("<b>🔄 Updating... Please wait.</b>")
    await safe_answer(callback_query, "Updating...")

    result = perform_update()

    if result["success"]:
        await callback_query.message.edit_text(
            f"<b>✅ Update Complete!</b>\n\n"
            f"<b>New commit:</b> <code>{result['new_commit']}</code>\n\n"
            f"⚠️ <b>Restart required.</b> Bot will restart automatically.\n\n"
            f"{result['message'][:1000]}"
        )
        logger.info("Restarting after update...")
        try:
            os.execv(sys.executable, [sys.executable, "-m", "leechbot"])
        except Exception as e:
            logger.error("Restart failed: %s", e)
            await callback_query.message.edit_text(
                f"<b>✅ Update Complete!</b>\n\n"
                f"<b>New commit:</b> <code>{result['new_commit']}</code>\n\n"
                f"⚠️ <b>Auto-restart failed.</b> Please restart manually.\n"
                f"<code>python3 -m leechbot</code>"
            )
    else:
        await callback_query.message.edit_text(
            f"<b>❌ Update Failed</b>\n\n<code>{result['message'][:500]}</code>"
        )

# =============================================================================
# System Info Refresh
# =============================================================================
def _strip_sysinfo(text: str) -> str:
    """Strip existing system info block from message text."""
    for separator in ("<b>─── System ───</b>", "┏━━━━ **System Info", "⌬─────"):
        parts = text.split(separator)
        if len(parts) >= 2:
            return parts[0].rstrip()
    return text

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
        await safe_answer(callback_query, "Refreshed ✓")
    except Exception as e:
        logger.debug("Sys refresh error: %s", e)
        await safe_answer(callback_query, "No changes", show_alert=False)

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
        await safe_answer(callback_query, "Detailed stats ✓")
    except Exception as e:
        logger.debug("Sys stats error: %s", e)
        await safe_answer(callback_query, "No changes", show_alert=False)


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
• /autorename — Set auto-rename template
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
