# =============================================================================
# Telegram Leech Bot - Queue Commands
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Queue command handlers — /queue, /cancel, /cancel_all
"""

import logging
from pyrogram import filters
from leechbot import app, OWNER
from leechbot.utility.variables import BOT, Queue, BotStats
from leechbot.utility.handler import cancelTask
from leechbot.utility.helper import message_deleter
import config

logger = logging.getLogger(__name__)

# =============================================================================
# /queue
# =============================================================================
@app.on_message(filters.command("queue") & filters.private)
async def queue_command(client, message):
    """Show the download queue."""
    if message.chat.id != OWNER and message.chat.id not in config.ALLOWED_USERS:
        return

    items = Queue.list_items()
    current = Queue.current

    text = "**📋 Download Queue**\n\n"
    if current:
        text += f"• 🔄 **Active:** `{current.get('name', 'Unknown')}`\n"
        text += f"• 📦 **Links:** `{len(current.get('links', []))}`\n\n"
    else:
        text += "**🔄 Active:** `None`\n\n"

    if items:
        for item in items:
            text += f"{item}\n"
        text += f"\n**📊 Total Queued:** `{Queue.size()}`"
    else:
        text += "**📭 Queue is empty**"

    stats_text = "\n\n─── Session Stats ───\n"
    stats_text += f"• Completed: `{BotStats.total_tasks}`\n"
    stats_text += f"• Failed: `{BotStats.failed_tasks}`\n"
    stats_text += f"• Downloaded: `{BotStats.total_downloaded}`\n"
    stats_text += f"• Uploaded: `{BotStats.total_uploaded}`"

    msg = await message.reply_text(text + stats_text, quote=True)
    await message_deleter(message, msg)

# =============================================================================
# /cancel
# =============================================================================
@app.on_message(filters.command("cancel") & filters.private)
async def cancel_command(client, message):
    """Handle the /cancel command."""
    if BOT.State.task_going:
        await cancelTask("User cancelled the task")
        msg = await message.reply_text("**🚫 Task Cancelled** ✓", quote=True)
    else:
        msg = await message.reply_text("**ℹ️ No Active Task To Cancel**", quote=True)
    await message_deleter(message, msg)

# =============================================================================
# /cancel_all
# =============================================================================
@app.on_message(filters.command("cancel_all") & filters.private)
async def cancel_all_command(client, message):
    """Cancel current task and clear the queue."""
    if message.chat.id != OWNER:
        return

    Queue.clear()

    if BOT.State.task_going:
        await cancelTask("User cancelled all tasks")
        msg = await message.reply_text("**🚫 All tasks cancelled and queue cleared.**", quote=True)
    else:
        msg = await message.reply_text("**📭 Queue cleared. No active task to cancel.**", quote=True)

    await message_deleter(message, msg)