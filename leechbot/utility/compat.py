# =============================================================================
# Telegram Leech Bot - Pyrogram Compatibility Layer
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Pyrogram compatibility layer.

Handles features that may not exist in older Pyrogram versions:
- Bot API 9.4 button styles (danger/success/primary)
- Graceful degradation when features are unavailable

Usage:
    from leechbot.utility.compat import InlineButton, safe_set_bot_commands

    btn = InlineButton("Cancel", callback_data="cancel", style="danger")
"""

import logging
from pyrogram.types import InlineKeyboardButton as _OrigInlineButton

logger = logging.getLogger(__name__)

# =============================================================================
# Detect style support
# =============================================================================
_STYLE_SUPPORTED = False

try:
    _test = _OrigInlineButton("test", callback_data="test", style="primary")
    _STYLE_SUPPORTED = True
    del _test
    logger.info("✅ Bot API 9.4 button styles supported")
except TypeError:
    logger.info("ℹ️ Button styles not supported (Pyrogram <2.0.x Bot API 9.4) — colors disabled")


# =============================================================================
# InlineButton — drop-in replacement with style support
# =============================================================================
def InlineButton(
    text: str,
    callback_data: str = None,
    url: str = None,
    style: str = None,
    **kwargs,
):
    """
    Create an InlineKeyboardButton, gracefully handling the `style` parameter.

    On Pyrogram versions that support Bot API 9.4+, the button will be
    colored (danger=red, success=green, primary=blue).
    On older versions, the style is silently ignored.

    Args:
        text: Button label
        callback_data: Callback data string
        url: URL to open on click
        style: "danger" (red), "success" (green), "primary" (blue), or None
        **kwargs: Any other InlineKeyboardButton parameters
    """
    if style and _STYLE_SUPPORTED:
        return _OrigInlineButton(text, callback_data=callback_data, url=url, style=style, **kwargs)
    else:
        return _OrigInlineButton(text, callback_data=callback_data, url=url, **kwargs)


# =============================================================================
# Safe set_bot_commands — handles missing method
# =============================================================================
async def safe_set_bot_commands(app, commands):
    """
    Register bot commands with Telegram.
    Silently handles Pyrogram versions that don't support set_bot_commands.
    """
    try:
        await app.set_bot_commands(commands)
        logger.info("✅ Registered %d bot commands with Telegram", len(commands))
    except AttributeError:
        logger.warning("⚠️ set_bot_commands not available — register commands via @BotFather")
    except Exception as e:
        logger.warning("⚠️ Failed to register commands: %s", e)
