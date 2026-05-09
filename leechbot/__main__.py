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

import logging

from leechbot import app

logger = logging.getLogger(__name__)

# =============================================================================
# Import handlers to register them with Pyrogram
# =============================================================================
# Each module uses @app.on_message / @app.on_callback_query decorators,
# so importing them is sufficient to register the handlers.
import leechbot.commands   # noqa: F401
import leechbot.callbacks  # noqa: F401
import leechbot.handlers   # noqa: F401

# =============================================================================
# Startup
# =============================================================================
logger.info("=" * 60)
logger.info("LeechBot started successfully")
logger.info("Developer: Shinei Nouzen")
logger.info("GitHub: https://github.com/Shineii86/LeechBot")
logger.info("=" * 60)

app.run()
