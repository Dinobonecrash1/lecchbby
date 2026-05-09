# =============================================================================
# Telegram Leech Bot - UserBot Session Manager
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
UserBot session manager.

Allows the bot to download from private channels/groups using the
user's own Telegram account. The user logs in once via phone number
+ OTP code, and the session is saved for future use.

This is the standard approach used by all Telegram downloader bots
to access private content without needing the bot to be a member.

Usage:
  1. User sends /userbot to start the login flow
  2. User provides phone number → receives OTP code on Telegram
  3. User provides OTP code → session is saved
  4. All subsequent private channel downloads use the user session
"""

import os
import logging
from pyrogram import Client
from pyrogram.errors import (
    PhoneCodeInvalid, PhoneCodeExpired,
    PhoneNumberInvalid, SessionPasswordNeeded,
)

import config

logger = logging.getLogger(__name__)

# User client singleton
_user_client: Client = None
_user_authorized: bool = False

# Session file path
SESSION_PATH = str(config.SESSIONS_PATH / "userbot_session")

# Pending auth state (for multi-step login flow)
_auth_state = {
    "active": False,
    "phone": None,
    "phone_code_hash": None,
    "step": None,  # "phone" | "code" | "2fa"
}


def get_user_client() -> Client:
    """Get or create the user client."""
    global _user_client
    if _user_client is None:
        _user_client = Client(
            name="userbot_session",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            workdir=str(config.SESSIONS_PATH),
            no_updates=True,  # Don't register handlers on user client
        )
    return _user_client


async def check_user_session() -> bool:
    """Check if a valid user session exists."""
    global _user_authorized

    session_file = SESSION_PATH + ".session"
    if not os.path.exists(session_file):
        return False

    try:
        client = get_user_client()
        if not client.is_connected:
            await client.connect()
        _user_authorized = await client.is_authorized()
        if _user_authorized:
            me = await client.get_me()
            logger.info(f"UserBot session active: {me.first_name} ({me.id})")
        return _user_authorized
    except Exception as e:
        logger.warning(f"UserBot session check failed: {e}")
        _user_authorized = False
        return False


async def start_auth_flow(phone: str) -> str:
    """
    Start the login flow by requesting OTP.

    Args:
        phone: phone number with country code (e.g. +1234567890)

    Returns:
        status message
    """
    global _auth_state

    client = get_user_client()
    if not client.is_connected:
        await client.connect()

    try:
        result = await client.send_code(phone)
        _auth_state = {
            "active": True,
            "phone": phone,
            "phone_code_hash": result.phone_code_hash,
            "step": "code",
        }
        return (
            f"📱 **OTP sent to** `{phone}`\n\n"
            f"Enter the code you received on Telegram.\n"
            f"_Code expires in a few minutes._"
        )
    except PhoneNumberInvalid:
        return "❌ **Invalid phone number.** Use international format: `+1234567890`"
    except Exception as e:
        return f"❌ **Error:** `{e}`"


async def verify_code(code: str) -> str:
    """
    Verify the OTP code.

    Args:
        code: the OTP code from Telegram

    Returns:
        status message
    """
    global _auth_state, _user_authorized

    if not _auth_state["active"] or _auth_state["step"] != "code":
        return "❌ **No active login flow.** Send `/userbot` to start."

    client = get_user_client()

    try:
        await client.sign_in(
            phone_number=_auth_state["phone"],
            phone_code_hash=_auth_state["phone_code_hash"],
            phone_code=code,
        )

        me = await client.get_me()
        _user_authorized = True
        _auth_state = {"active": False, "phone": None, "phone_code_hash": None, "step": None}

        return (
            f"✅ **UserBot authorized!**\n\n"
            f"👤 **Account:** {me.first_name} {me.last_name or ''}\n"
            f"🆔 **ID:** `{me.id}`\n\n"
            f"Private channel downloads will now use your account.\n"
            f"_You can delete the login messages for security._"
        )

    except PhoneCodeInvalid:
        return "❌ **Invalid code.** Try again with the correct code."
    except PhoneCodeExpired:
        _auth_state = {"active": False, "phone": None, "phone_code_hash": None, "step": None}
        return "❌ **Code expired.** Send `/userbot` to start over."
    except SessionPasswordNeeded:
        _auth_state["step"] = "2fa"
        return "🔐 **2FA enabled.** Enter your cloud password:"
    except Exception as e:
        _auth_state = {"active": False, "phone": None, "phone_code_hash": None, "step": None}
        return f"❌ **Error:** `{e}`"


async def verify_2fa(password: str) -> str:
    """
    Verify 2FA password.

    Args:
        password: cloud password

    Returns:
        status message
    """
    global _user_authorized, _auth_state

    if not _auth_state["active"] or _auth_state["step"] != "2fa":
        return "❌ **No active 2FA flow.** Send `/userbot` to start."

    client = get_user_client()

    try:
        await client.check_password(password)

        me = await client.get_me()
        _user_authorized = True
        _auth_state = {"active": False, "phone": None, "phone_code_hash": None, "step": None}

        return (
            f"✅ **UserBot authorized!**\n\n"
            f"👤 **Account:** {me.first_name} {me.last_name or ''}\n"
            f"🆔 **ID:** `{me.id}`\n\n"
            f"Private channel downloads will now use your account."
        )
    except Exception as e:
        return f"❌ **Wrong password:** `{e}`"


async def get_user_messages(chat_id, message_id):
    """
    Get a message using the user client.

    Falls back to bot client if user session is not available.

    Returns:
        message object or None
    """
    global _user_authorized

    if _user_authorized:
        try:
            client = get_user_client()
            if not client.is_connected:
                await client.connect()
            return await client.get_messages(chat_id, message_id)
        except Exception as e:
            logger.warning(f"UserBot get_messages failed: {e}")

    # Fallback to bot client
    from leechbot import app
    return await app.get_messages(chat_id, message_id)


async def disconnect_user():
    """Disconnect the user client and clear session."""
    global _user_client, _user_authorized

    if _user_client and _user_client.is_connected:
        await _user_client.disconnect()

    _user_client = None
    _user_authorized = False

    # Remove session file
    for ext in [".session", ".session-journal"]:
        path = SESSION_PATH + ext
        if os.path.exists(path):
            os.remove(path)

    logger.info("UserBot session disconnected and removed")
