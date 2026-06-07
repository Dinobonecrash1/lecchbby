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

Parsing logic ported from xditya/GetRestrictedMessages (AGPL-3.0) to Pyrogram.
The original Telethon-based approach is here adapted to our Pyrogram + UserBot
session stack so the project keeps a single framework (Pyrogram 2.0.106).

Supported link formats:
  - Public  : https://t.me/USERNAME/MSG_ID
  - Slug    : https://t.me/s/USERNAME/MSG_ID      (public channel slug form)
  - Private : https://t.me/c/CHAT_ID/MSG_ID
  - Thread  : https://t.me/c/CHAT_ID/MSG_ID/THREAD_ID  (discussion reply)
  - Legacy  : http://t.me/USERNAME/MSG_ID  (also accepted)

For private channels the UserBot session is tried first (user's own account);
on failure the bot client is used as a fallback.
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
# Link Parsing  (ported from xditya/GetRestrictedMessages)
# =============================================================================
def _parse_telegram_link(link: str):
    """
    Parse a t.me link into ``(peer, message_id)``.

    Algorithm ported from xditya/GetRestrictedMessages
    (https://github.com/xditya/GetRestrictedMessages) — the original used
    Telethon's StringSession, this version emits a Pyrogram-compatible
    peer (int with -100 prefix for channels, or username string).

    Args:
        link: Full t.me URL (or already-stripped variant).

    Returns:
        ``(peer, message_id)`` tuple, or ``(None, None)`` on parse error.
    """
    if not link or not isinstance(link, str):
        return None, None

    try:
        # Strip both http:// and https:// prefixes, and any trailing slash
        cleaned = link.strip()
        for prefix in ("https://", "http://"):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):]
        cleaned = cleaned.rstrip("/")

        # Quick sanity check: must look like a t.me link
        if not cleaned.startswith("t.me/") and not cleaned.startswith("telegram.me/"):
            return None, None

        parts = cleaned.split("/")
        # parts[0] = "t.me" (or "telegram.me")
        # parts[1] = "c" | "s" | USERNAME
        # parts[2] = CHAT_ID | USERNAME | MSG_ID
        # parts[3] = MSG_ID (only for c/s forms) | THREAD_ID
        if len(parts) < 3:
            return None, None

        if parts[1] in ("c", "s"):
            # Private or slug: t.me/c/CHAT_ID/MSG_ID[/THREAD_ID]
            if len(parts) < 4:
                return None, None
            chat_id_str = parts[2]
            message_id_str = parts[3]
        else:
            # Public: t.me/USERNAME/MSG_ID
            chat_id_str = parts[1]
            message_id_str = parts[2] if len(parts) > 2 else None

        if not message_id_str or not message_id_str.isdigit():
            return None, None

        message_id = int(message_id_str)

        # Determine peer type
        # - Pure digits (e.g. "1234567890" from t.me/c/1234567890/123) → int.
        #   Telegram channel IDs in Pyrogram always have the -100 prefix;
        #   t.me strips it, so we re-add it for any 10+ digit number.
        # - Anything else → keep as username string.
        if chat_id_str.lstrip("-").isdigit():
            peer = int(chat_id_str)
            if peer > 0 and len(str(peer)) >= 10:
                # t.me/c/1234567890/123 → real chat_id is -1001234567890
                peer = int(f"-100{peer}")
        else:
            peer = chat_id_str

        return peer, message_id

    except (IndexError, ValueError, AttributeError):
        return None, None


# =============================================================================
# Media Identification
# =============================================================================
async def media_Identifier(link: str):
    """
    Identify media from a Telegram message link.

    Supports:
      - Public:  https://t.me/USERNAME/MSG_ID
      - Slug:    https://t.me/s/USERNAME/MSG_ID
      - Private: https://t.me/c/CHAT_ID/MSG_ID[/THREAD_ID]
        → Uses UserBot session if available (user's own account)
        → Falls back to bot client (requires bot to be a member)

    Args:
        link: Telegram message link

    Returns:
        tuple: (media, message) or (None, None) on failure
    """
    peer, message_id = _parse_telegram_link(link)

    if peer is None or message_id is None:
        logger.error(
            f"Invalid Telegram link: {link!r}\n"
            f"Expected formats:\n"
            f"  - https://t.me/USERNAME/MSG_ID\n"
            f"  - https://t.me/s/USERNAME/MSG_ID\n"
            f"  - https://t.me/c/CHAT_ID/MSG_ID"
        )
        return None, None

    # The link is private (peer is a -100XXXX int). UserBot session can
    # help for restricted/joined channels where the bot isn't a member.
    is_private = isinstance(peer, int) and str(peer).startswith("-100")

    try:
        message = None

        if is_private:
            from leechbot.userbot import get_user_messages, check_user_session
            if await check_user_session():
                try:
                    message = await get_user_messages(peer, message_id)
                    if message and not message.empty:
                        logger.info(
                            "Fetched message via UserBot session "
                            "(chat_id=%s, msg_id=%d)",
                            peer, message_id,
                        )
                except Exception as e:
                    logger.warning(
                        "UserBot fetch failed, falling back to bot: %s", e
                    )

        # Fallback to bot client (always runs for public links;
        # also covers private links when UserBot isn't available)
        if message is None or message.empty:
            try:
                message = await app.get_messages(peer, message_id)
            except Exception as e:
                err = str(e).lower()
                if "peer" in err or "channel" in err or "chat" in err:
                    logger.error(
                        "Cannot access chat. Options:\n"
                        "1. Send /userbot to login with your Telegram account\n"
                        "2. Add the bot as a member of the chat/channel\n"
                        "Error: %s", e,
                    )
                else:
                    logger.error("Telegram message fetch error: %s", e)
                return None, None

        if message is None or message.empty:
            logger.error(
                "Message not found (chat_id=%s, msg_id=%d). "
                "Either the link is invalid, the message was deleted, "
                "or your account is not a member.",
                peer, message_id,
            )
            return None, None

        if message.service:
            logger.error("Message is a service message (no media)")
            return None, None

    except Exception as e:
        logger.error("Unexpected error fetching Telegram message: %s", e)
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
        logger.error(
            "No downloadable media in message (chat_id=%s, msg_id=%d). "
            "Message may be text-only.",
            peer, message_id,
        )
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
        link: Telegram message link (any supported format)
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
