# =============================================================================
# Telegram Leech Bot - System Commands
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
System command handlers — /restart, /update, /logs
"""

import logging
import os
import signal
import sys
from pyrogram import filters
from leechbot import app, OWNER, LOG_FILE
from leechbot.utility.variables import BOT
from leechbot.utility.handler import cancelTask
from leechbot.utility.helper import message_deleter
import config

logger = logging.getLogger(__name__)

# =============================================================================
# /restart
# =============================================================================
@app.on_message(filters.command("restart") & filters.private)
async def restart_command(client, message):
    """Handle the /restart command — gracefully exit so the wrapper can respawn."""
    if message.chat.id != OWNER:
        return

    # Cancel any active task first
    if BOT.State.task_going:
        try:
            await cancelTask("Bot restarting")
        except Exception:
            pass

    restart_text = (
        "**🔄 Restarting LeechBot...**\n\n"
        f"• **Version:** `v{config.VERSION}`\n"
        "• **Action:** Sending SIGTERM to self\n"
        "• **Wrapper:** Will respawn the process\n\n"
        "⏳ Bot will be back in 5-10 seconds."
    )
    msg = await message.reply_text(restart_text, quote=True)
    await message_deleter(message, msg)

    logger.warning(
        "🔄 Restart requested by user %s — exiting for wrapper respawn",
        message.from_user.id if message.from_user else "unknown",
    )

    # Give the message a moment to send, then exit.
    # The process supervisor (systemd, docker --restart, pm2, tmux respawn,
    # Colab auto-reconnect, nohup loop, etc.) should bring it back.
    import asyncio
    await asyncio.sleep(1)

    # Try graceful exit first
    try:
        os.kill(os.getpid(), signal.SIGTERM)
    except Exception:
        # Fallback: hard exit
        sys.exit(0)

# =============================================================================
# /logs
# =============================================================================
@app.on_message(filters.command("logs") & filters.private)
async def logs_command(client, message):
    """Handle the /logs command — show last N log lines (default 30, max 100)."""
    if message.chat.id != OWNER:
        return

    # Parse optional count: /logs 50
    args = message.text.split(maxsplit=1)
    try:
        n_lines = int(args[1]) if len(args) > 1 else 30
        n_lines = max(1, min(n_lines, 100))  # clamp 1..100
    except ValueError:
        n_lines = 30

    # Find log file
    log_file = LOG_FILE or str(config.LOGS_PATH / "leechbot.log")

    if not os.path.isfile(log_file):
        msg = await message.reply_text(
            f"**📋 Logs**\n\n`Log file not found: {log_file}`\n\n"
            "_File logging may be disabled (read-only filesystem)._",
            quote=True,
        )
        await message_deleter(message, msg)
        return

    # Tail the last N lines efficiently (read from end, no full file load)
    try:
        # Get file size
        fsize = os.path.getsize(log_file)
        # Read up to ~256 KB from the end (enough for ~500 lines of INFO)
        read_size = min(fsize, 256 * 1024)

        with open(log_file, "rb") as f:
            if fsize > read_size:
                f.seek(fsize - read_size)
                _ = f.readline()  # discard partial first line
            data = f.read().decode("utf-8", errors="replace")

        all_lines = data.splitlines()
        tail_lines = all_lines[-n_lines:]

        if not tail_lines:
            tail_lines = ["(log file is empty)"]

        log_text = (
            f"**📋 Last `{len(tail_lines)}` log lines**\n"
            f"`({log_file})`\n\n"
            f"```\n" + "\n".join(tail_lines) + "\n```"
        )

        # Telegram has 4096 char limit per message — truncate if needed
        if len(log_text) > 4000:
            # Drop from the middle, keep first and last lines
            half = (4000 - 200) // 2
            log_text = (
                f"**📋 Last `{len(tail_lines)}` log lines** (truncated)\n"
                f"`({log_file})`\n\n"
                f"```\n"
                + "\n".join(tail_lines[:half // 80])  # ~80 chars per line avg
                + "\n\n... [truncated] ...\n\n"
                + "\n".join(tail_lines[-(half // 80):])
                + "\n```"
            )

        msg = await message.reply_text(log_text, quote=True)
        await message_deleter(message, msg)
    except Exception as e:
        logger.error(f"Failed to read log file: {e}")
        msg = await message.reply_text(
            f"**❌ Error reading logs:**\n`{e}`", quote=True,
        )
        await message_deleter(message, msg)

# =============================================================================
# /update — Check for updates and auto-update
# =============================================================================
@app.on_message(filters.command("update") & filters.private)
async def update_command(client, message):
    """Check for updates and optionally update the bot."""
    from leechbot.updater import check_for_updates, perform_update, get_local_version, get_local_commit, get_changelog_since

    if message.chat.id != OWNER:
        return

    msg = await message.reply_text("**🔄 Checking for updates...**", quote=True)

    info = check_for_updates()
    version = get_local_version()
    local = info["local"]

    if not info["available"]:
        await msg.edit_text(
            f"**✅ Already up to date!**\n\n"
            f"**Version:** `{version}`\n"
            f"**Commit:** `{local}`"
        )
        await message_deleter(message, msg)
        return

    # Show available update
    changelog = get_changelog_since(local)
    changelog_text = f"\n\n**📋 Changes:**\n```\n{changelog[:1500]}\n```" if changelog else ""

    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Update Now", callback_data="do_update"),
            InlineKeyboardButton("❌ Cancel", callback_data="close"),
        ]
    ])

    await msg.edit_text(
        f"**🔄 Update Available!**\n\n"
        f"**Current:** `{local}`\n"
        f"**Latest:** `{info['remote']}`\n"
        f"**Behind:** `{info['behind']} commits`"
        f"{changelog_text}",
        reply_markup=keyboard,
    )