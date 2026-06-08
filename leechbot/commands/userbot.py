# =============================================================================
# Telegram Leech Bot - UserBot Commands
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
UserBot command handlers — /userbot, /userbot_status, /userbot_logout
"""

import logging
from pyrogram import filters
from leechbot import app, OWNER
from leechbot.utility.variables import BOT

logger = logging.getLogger(__name__)

# =============================================================================
# /userbot — Login with user account for private channel access
# =============================================================================
@app.on_message(filters.command("userbot") & filters.private)
async def userbot_command(client, message):
    """Start UserBot login flow for private channel access."""
    if message.chat.id != OWNER:
        return

    from leechbot.userbot import check_user_session, start_auth_flow, _auth_state

    # Check if already authorized
    if await check_user_session():
        await message.reply_text(
            "✅ **UserBot already authorized!**\n\n"
            "Private channel downloads use your account automatically.\n"
            "Send `/userbot_logout` to disconnect.",
            quote=True,
        )
        return

    # If there's a pending auth, show status
    if _auth_state["active"]:
        await message.reply_text(
            f"⏳ **Login in progress.** Current step: `{_auth_state['step']}`\n\n"
            f"Send the required code/password to continue.",
            quote=True,
        )
        return

    # Ask for phone number
    await message.reply_text(
        "📱 **UserBot Login** — Private Channel Access\n\n"
        "Login with your Telegram account to download from private channels.\n"
        "Your session is saved locally — no data is shared.\n\n"
        "**Send your phone number** with international code:\n"
        "Example: `+1234567890`\n\n"
        "_Send /cancel to abort._",
        quote=True,
    )

    BOT.State.prefix = False
    BOT.State.suffix = False
    # Set flag so next text message is treated as phone number
    BOT.State.userbot_waiting = "phone"

@app.on_message(filters.command("userbot_logout") & filters.private)
async def userbot_logout_command(client, message):
    """Disconnect UserBot session."""
    if message.chat.id != OWNER:
        return

    from leechbot.userbot import disconnect_user
    await disconnect_user()
    await message.reply_text("🔓 **UserBot session disconnected** and removed.", quote=True)

@app.on_message(filters.command("userbot_status") & filters.private)
async def userbot_status_command(client, message):
    """Check UserBot session status."""
    if message.chat.id != OWNER:
        return

    from leechbot.userbot import check_user_session
    if await check_user_session():
        await message.reply_text("✅ **UserBot session is active.** Private channel downloads supported.", quote=True)
    else:
        await message.reply_text("❌ **No UserBot session.** Send `/userbot` to login.", quote=True)