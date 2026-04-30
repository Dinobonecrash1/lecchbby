# =============================================================================
# Telegram Leech Bot - Central Configuration
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Central configuration module.

All settings are loaded from environment variables with sensible defaults.
Create a .env file in the project root to override defaults.
"""

import os
import sys
import logging
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv is optional; env vars still work

logger = logging.getLogger(__name__)

# =============================================================================
# Base Paths (configurable via LEECHBOT_BASE_DIR env var)
# =============================================================================
BASE_DIR = Path(os.getenv("LEECHBOT_BASE_DIR", "/tmp/leechbot"))
WORK_PATH = BASE_DIR / "work"
DOWNLOADS_PATH = WORK_PATH / "downloads"
TEMP_PATH = BASE_DIR / "temp"
THUMBNAIL_PATH = BASE_DIR / "thumbnails"
SESSIONS_PATH = BASE_DIR / "sessions"
LOGS_PATH = BASE_DIR / "logs"

# Create all directories on import
for _p in [WORK_PATH, DOWNLOADS_PATH, TEMP_PATH, THUMBNAIL_PATH, SESSIONS_PATH, LOGS_PATH]:
    _p.mkdir(parents=True, exist_ok=True)

# =============================================================================
# Telegram Credentials
# =============================================================================
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
DUMP_ID = int(os.getenv("DUMP_ID", "0"))

# Validate critical credentials
if not API_ID or not API_HASH or not BOT_TOKEN:
    logger.warning(
        "API_ID, API_HASH, or BOT_TOKEN not set. "
        "Set them in .env or as environment variables."
    )

# =============================================================================
# Feature Flags & Limits
# =============================================================================
MAX_CONCURRENT_DOWNLOADS = int(os.getenv("MAX_CONCURRENT_DOWNLOADS", "3"))
MAX_FILE_SIZE = 2097152000  # 2GB Telegram limit
MAX_VIDEO_SPLIT_SIZE = 1992294400  # 1.9GB for safe splitting
AUTO_RETRY_COUNT = int(os.getenv("AUTO_RETRY_COUNT", "3"))
DEFAULT_UPLOAD_MODE = os.getenv("DEFAULT_UPLOAD_MODE", "media")  # media or document
ENABLE_TORRENTS = os.getenv("ENABLE_TORRENTS", "false").lower() == "true"
BANDWIDTH_LIMIT = os.getenv("BANDWIDTH_LIMIT", "")  # e.g., "10M" for aria2c

# =============================================================================
# Google Drive
# =============================================================================
GDRIVE_ENABLED = os.getenv("GDRIVE_ENABLED", "false").lower() == "true"
TOKEN_PICKLE_PATH = os.getenv("TOKEN_PICKLE_PATH", str(BASE_DIR / "token.pickle"))

# =============================================================================
# Multi-User Support
# =============================================================================
ALLOWED_USERS = [
    int(x.strip())
    for x in os.getenv("ALLOWED_USERS", "").split(",")
    if x.strip()
]

# =============================================================================
# Version Info
# =============================================================================
VERSION = "1.0.0"
BUILD_DATE = "2026-05-01"
