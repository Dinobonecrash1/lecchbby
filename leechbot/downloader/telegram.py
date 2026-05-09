# =============================================================================
# Telegram Leech Bot - Telegram Downloader
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Telegram downloader module.

Handles downloads from Telegram messages via message links.
"""

import logging
from datetime import datetime
from os import path as ospath

from leechbot import app
from leechbot.utility.variables import Transfer, Paths, Messages
from leechbot.utility.helper import speedETA, getTime, sizeUnit, status_bar

logger = logging.getLogger(__name__)

# Module-level start time (properly scoped, not a bare global)
_download_start_time: datetime = datetime.now()


# =============================================================================
# Media Identification
# =============================================================================
async def media_Identifier(link: str):
    """
    Identify media from a Telegram message link.

    Supports:
      - Public:  https://t.me/USERNAME/MSG_ID  (no membership needed)
      - Private: https://t.me/c/CHAT_ID/MSG_ID
        → Uses UserBot session if available (user's own account)
        → Falls back to bot client (requires bot to be a member)

    Args:
        link: Telegram message link

    Returns:
        tuple: (media, message) or (None, None) on failure
    """
    try:
        parts = link.rstrip("/").split("/")
        message_id = int(parts[-1])

        # Private channel: t.me/c/CHAT_ID/MSG_ID
        if "/c/" in link:
            chat_id = int("-100" + parts[4])
        else:
            # Public channel: t.me/USERNAME/MSG_ID
            chat_id = parts[4]

        # For private channels, try UserBot session first
        message = None
        if "/c/" in link:
            from leechbot.userbot import get_user_messages, check_user_session
            if await check_user_session():
                try:
                    message = await get_user_messages(chat_id, message_id)
                    if message and not message.empty:
                        logger.info("Fetched message via UserBot session")
                except Exception as e:
                    logger.warning(f"UserBot fetch failed, falling back to bot: {e}")

        # Fallback to bot client
        if message is None or message.empty:
            message = await app.get_messages(chat_id, message_id)

        if message is None or message.empty:
            logger.error(f"Message not found: {link}")
            return None, None

        if message.service:
            logger.error("Message is a service message (no media)")
            return None, None

    except Exception as e:
        error_text = str(e).lower()
        if "peer" in error_text or "channel" in error_text or "chat" in error_text:
            logger.error(
                f"Cannot access private channel. Options:\n"
                f"1. Send /userbot to login with your Telegram account\n"
                f"2. Add the bot as a member of the channel\n"
                f"Error: {e}"
            )
        else:
            logger.error(f"Telegram message fetch error: {e}")
        return None, None

    media = (
        message.document
        or message.photo
        or message.video
        or message.audio
        or message.voice
        or message.video_note
        or message.sticker
        or message.animation
    )

    if media is None:
        logger.error(f"No downloadable media in message: {link}")
        return None, None

    return media, message


# =============================================================================
# Download Progress Callback
# =============================================================================
async def download_progress(current: int, total: int):
    """Update download progress bar."""
    speed_string, eta, percentage = speedETA(_download_start_time, current, total)

    await status_bar(
        down_msg=Messages.status_head,
        speed=speed_string,
        percentage=percentage,
        eta=getTime(eta),
        done=sizeUnit(sum(Transfer.down_bytes) + current),
        left=sizeUnit(Transfer.total_down_size),
        engine="Telegram 💬",
    )


# =============================================================================
# Main Download Function
# =============================================================================
async def TelegramDownload(link: str, num: int):
    """
    Download file from a Telegram message.

    Args:
        link: Telegram message link
        num: link number for display
    """
    global _download_start_time

    media, message = await media_Identifier(link)

    if media is None:
        from leechbot.utility.handler import cancelTask
        await cancelTask("Could Not Identify Telegram Media")
        return

    name = getattr(media, "file_name", None) or "Telegram_File"
    Messages.status_head = (
        f"**📥 Downloading** `Link {str(num).zfill(2)}`\n\n`{name}`\n"
    )

    _download_start_time = datetime.now()
    file_path = ospath.join(Paths.down_path, name)

    await message.download(
        progress=download_progress,
        in_memory=False,
        file_name=file_path,
    )

    if hasattr(media, "file_size"):
        Transfer.down_bytes.append(media.file_size)
