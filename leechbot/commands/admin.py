# =============================================================================
# Telegram Leech Bot - Admin Commands
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Admin command handlers — /admin, /broadcast
"""

import logging
from pyrogram import filters
from leechbot import app, OWNER
from leechbot.utility.variables import BOT, Transfer
from leechbot.utility.helper import message_deleter
import config

logger = logging.getLogger(__name__)

# =============================================================================
# /admin
# =============================================================================
@app.on_message(filters.command("admin") & filters.private)
async def admin_command(client, message):
    """Admin panel for managing allowed users."""
    if message.chat.id != OWNER:
        return

    if len(message.command) < 2:
        users_list = "\n".join([f"• `{uid}`" for uid in config.ALLOWED_USERS]) or "`None`"
        msg = await message.reply_text(
            f"**👥 Admin Panel**\n\n"
            f"**Allowed Users:**\n{users_list}\n\n"
            f"\n"
            f"`/admin add <user_id>` — Allow a user\n"
            f"`/admin remove <user_id>` — Deny a user\n"
            f"`/admin list` — Show allowed users\n"
            f"",
            quote=True,
        )
        await message_deleter(message, msg)
        return

    action = message.command[1].lower()

    if action == "add" and len(message.command) >= 3:
        try:
            new_uid = int(message.command[2])
            if new_uid not in config.ALLOWED_USERS:
                config.ALLOWED_USERS.append(new_uid)
                msg = await message.reply_text(f"**✅ User `{new_uid}` added to allowed list** ✓", quote=True)
            else:
                msg = await message.reply_text(f"**ℹ️ User `{new_uid}` is already allowed**", quote=True)
        except ValueError:
            msg = await message.reply_text("**⚠️ Invalid user ID**", quote=True)

    elif action == "remove" and len(message.command) >= 3:
        try:
            rm_uid = int(message.command[2])
            if rm_uid in config.ALLOWED_USERS:
                config.ALLOWED_USERS.remove(rm_uid)
                msg = await message.reply_text(f"**✅ User `{rm_uid}` removed from allowed list** ✓", quote=True)
            else:
                msg = await message.reply_text(f"**ℹ️ User `{rm_uid}` is not in the allowed list**", quote=True)
        except ValueError:
            msg = await message.reply_text("**⚠️ Invalid user ID**", quote=True)

    elif action == "list":
        users_list = "\n".join([f"• `{uid}`" for uid in config.ALLOWED_USERS]) or "`None`"
        msg = await message.reply_text(f"**👥 Allowed Users:**\n{users_list}", quote=True)

    else:
        msg = await message.reply_text("**⚠️ Usage:** `/admin add|remove|list [user_id]`", quote=True)

    await message_deleter(message, msg)

# =============================================================================
# /broadcast
# =============================================================================
@app.on_message(filters.command("broadcast") & filters.private)
async def broadcast_command(client, message):
    """Send the last uploaded file to multiple chats."""
    from asyncio import sleep

    if message.chat.id != OWNER:
        return

    if not BOT.State.task_going and not Transfer.sent_file:
        msg = await message.reply_text(
            "**ℹ️ No files to broadcast.**\n\nUpload something first with `/tupload`.",
            quote=True,
        )
        await message_deleter(message, msg)
        return

    if len(message.command) < 2:
        msg = await message.reply_text(
            "**📢 Broadcast Usage**\n\n"
            "\n"
            "`/broadcast chat_id1, chat_id2, ...`\n"
            "\n\n"
            "**📝 Example:**\n"
            "`/broadcast -1001234567890, -1009876543210`\n\n"
            "💡 Send the last uploaded file to multiple chats.",
            quote=True,
        )
        await message_deleter(message, msg)
        return

    chat_ids = []
    for cid in " ".join(message.command[1:]).split(","):
        cid = cid.strip()
        try:
            chat_ids.append(int(cid))
        except ValueError:
            pass

    if not chat_ids:
        msg = await message.reply_text("**⚠️ No valid chat IDs provided.**", quote=True)
        await message_deleter(message, msg)
        return

    last_file = Transfer.sent_file[-1] if Transfer.sent_file else None
    if not last_file:
        msg = await message.reply_text("**⚠️ No file to broadcast.**", quote=True)
        await message_deleter(message, msg)
        return

    msg = await message.reply_text(f"**📢 Broadcasting to {len(chat_ids)} chats...**", quote=True)

    success = 0
    failed = 0
    for chat_id in chat_ids:
        try:
            await last_file.copy(chat_id)
            success += 1
        except Exception as e:
            logger.error(f"Broadcast to {chat_id} failed: {e}")
            failed += 1
        await sleep(1)

    await msg.edit_text(
        f"📢 **Broadcast Complete**\n\n"
        f"• ✅ **Success:** `{success}`\n"
        f"• ❌ **Failed:** `{failed}`\n"
        f"• 📊 **Total:** `{len(chat_ids)}`"
    )