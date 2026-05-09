# =============================================================================
# Telegram Leech Bot - Entry Point
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# You may use, modify, and distribute this code under the MIT License.
# Please retain this header when using or modifying the code.
# =============================================================================

"""
LeechBot entry point.

This module imports all handler modules to register Pyrogram handlers,
then starts the bot. Handlers are organized in:
  - leechbot.commands  — /command handlers
  - leechbot.callbacks — inline keyboard callback handlers
  - leechbot.handlers  — message handlers (URL, photo, text, reply)
"""

import asyncio
import logging

# =============================================================================
# Patch Pyrogram's 32-bit peer ID limits
# Telegram supports 64-bit channel/supergroup IDs, but Pyrogram defaults
# to 32-bit MAX_INT (2147483647). This patches the limits to support
# larger channel IDs like 3030595089.
# =============================================================================
import pyrogram.utils as _pyro_utils
_pyro_utils.MIN_CHANNEL_ID = -100999999999999  # Support up to 15-digit IDs

from leechbot import app
import config

logger = logging.getLogger(__name__)

# =============================================================================
# Import handlers to register them with Pyrogram
# =============================================================================
import leechbot.commands   # noqa: F401
import leechbot.callbacks  # noqa: F401
import leechbot.handlers   # noqa: F401


# =============================================================================
# Peer Resolution Helper
# =============================================================================
async def _resolve_peer(peer_id: int, label: str):
    """
    Resolve a Telegram peer ID and cache it in Pyrogram's storage.
    Tries multiple methods to handle fresh sessions and restarts.
    """
    if not peer_id:
        return

    # Method 1: Direct resolve (fast, works if peer is already cached)
    try:
        await app.resolve_peer(peer_id)
        logger.info("✅ %s peer resolved: %s", label, peer_id)
        return
    except Exception:
        pass

    # Method 2: get_chat (fetches full chat info, caches automatically)
    try:
        chat = await app.get_chat(peer_id)
        logger.info("✅ %s peer resolved via get_chat: %s (%s)", label, peer_id, getattr(chat, 'title', 'user'))
        return
    except Exception:
        pass

    # Method 3: Send a silent message to force peer resolution
    try:
        msg = await app.send_message(peer_id, "🔄 Bot restarted — peer cache refreshed.")
        await msg.delete()
        logger.info("✅ %s peer resolved via test message: %s", label, peer_id)
        return
    except Exception:
        pass

    logger.warning(
        "⚠️ Could not resolve %s (%s). "
        "Make sure the bot is a member of the chat and has permission to send messages. "
        "The bot will retry when sending the first task message.",
        label, peer_id,
    )


# =============================================================================
# Startup — resolve peers, install error reporting, enter idle loop
# =============================================================================
async def startup():
    """
    Runs once after the bot connects to Telegram.
    1. Resolves DUMP_ID and OWNER_ID peers
    2. Installs debug/error reporting to Telegram
    3. Enters idle loop
    """
    from pyrogram import idle
    from leechbot.debug import setup_error_reporting

    # Start the client first (required before resolve_peer)
    await app.start()

    # Resolve critical peers at startup
    await _resolve_peer(config.DUMP_ID, "DUMP_ID")
    await _resolve_peer(config.OWNER_ID, "OWNER_ID")

    # Install error reporting (sends errors to DUMP_ID channel)
    await setup_error_reporting(app, config.DUMP_ID, config.OWNER_ID)

    logger.info("=" * 60)
    logger.info("LeechBot started successfully")
    logger.info("Developer: Shinei Nouzen")
    logger.info("GitHub: https://github.com/Shineii86/LeechBot")
    logger.info("Debug: Error reporting → DUMP_ID channel")
    logger.info("=" * 60)

    # Keep the bot running
    await idle()

    # Graceful shutdown
    await app.stop()


# =============================================================================
# Entry Point
# =============================================================================
asyncio.get_event_loop().run_until_complete(startup())
