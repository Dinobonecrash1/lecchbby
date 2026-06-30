# =============================================================================
# Telegram Leech Bot - Main Module Initialization
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
LeechBot main module initialization.

Initializes the Pyrogram client, loads configuration from config.py,
and sets up logging.
"""

import asyncio
import logging
import warnings
import sys

from pyrogram import Client

import config

# =============================================================================
# Logging Configuration
# =============================================================================
_log_handlers = [logging.StreamHandler(sys.stdout)]

# File handler for /logs command — writes to LOGS_PATH/leechbot.log
# Rotated manually (or could be RotatingFileHandler if size grows)
try:
    from logging.handlers import RotatingFileHandler
    _log_file = config.LOGS_PATH / "leechbot.log"
    _log_file.parent.mkdir(parents=True, exist_ok=True)
    _file_handler = RotatingFileHandler(
        _log_file,
        maxBytes=2 * 1024 * 1024,  # 2 MB per file
        backupCount=3,             # keep 3 backups
        encoding="utf-8",
    )
    _file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                          datefmt="%Y-%m-%d %H:%M:%S")
    )
    _log_handlers.append(_file_handler)
    LOG_FILE = str(_log_file)
except Exception as _e:
    # If file logging fails (e.g. read-only fs), continue with stdout only
    LOG_FILE = None
    print(f"[leechbot] file logging disabled: {_e}", file=sys.stderr)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=_log_handlers,
)
logger = logging.getLogger(__name__)

# =============================================================================
# Re-export config values for backward compatibility
# =============================================================================
API_ID = config.API_ID
API_HASH = config.API_HASH
BOT_TOKEN = config.BOT_TOKEN
OWNER = config.OWNER_ID
DUMP_ID = config.DUMP_ID

# =============================================================================
# Event Loop Setup
# =============================================================================
def _setup_event_loop():
    """Ensure an event loop exists (needed for some environments like Colab)."""
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

_setup_event_loop()

# =============================================================================
# Pyrogram Client Creation
# =============================================================================
app = Client(
    name="leechbot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir=str(config.SESSIONS_PATH),
    workers=100,
    max_concurrent_transmissions=10,
)

logger.info("LeechBot client initialized (v%s)", config.VERSION)
