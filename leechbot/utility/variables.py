# =============================================================================
# Telegram Leech Bot - Global Variables and Configuration
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Global variables and configuration classes for the bot.

All mutable state lives here. Import the class you need and mutate
its attributes directly — this module is the single source of truth.

For multi-user: Use UserContext from user_state.py for per-user isolation.
"""

import config
import contextvars
from time import time
from datetime import datetime
from pathlib import Path
from collections import deque
from pyrogram.types import Message

# Import per-user state system
from leechbot.utility.user_state import (
    UserContext, UserRegistry, TaskQueue, UserPaths
)


# =============================================================================
# Context variable for current user (async-safe)
# =============================================================================
current_user_id: contextvars.ContextVar[int] = contextvars.ContextVar("current_user_id", default=0)


def get_ctx() -> UserContext:
    """Get current user's context. Falls back to owner if no context set."""
    uid = current_user_id.get()
    if uid:
        return UserRegistry.get(uid)
    return UserRegistry.get(config.OWNER_ID)


# =============================================================================
# Proxy Objects — forward attribute access to per-user context
# =============================================================================
class _SettingProxy:
    """Proxy that forwards BOT.Setting.xxx to get_ctx().settings.xxx"""
    def __getattr__(self, name):
        return getattr(get_ctx().settings, name)
    def __setattr__(self, name, value):
        setattr(get_ctx().settings, name, value)


class _OptionsProxy:
    """Proxy that forwards BOT.Options.xxx to get_ctx().task.xxx"""
    def __getattr__(self, name):
        return getattr(get_ctx().task, name)
    def __setattr__(self, name, value):
        setattr(get_ctx().task, name, value)


class _ModeProxy:
    """Proxy that forwards BOT.Mode.xxx to get_ctx().task.xxx"""
    def __getattr__(self, name):
        return getattr(get_ctx().task, name)
    def __setattr__(self, name, value):
        setattr(get_ctx().task, name, value)


class _StateProxy:
    """Proxy that forwards BOT.State.xxx to get_ctx().task.xxx (except global flags)"""
    def __getattr__(self, name):
        if name == "shutting_down":
            return BOT._shutting_down
        return getattr(get_ctx().task, name)
    def __setattr__(self, name, value):
        if name == "shutting_down":
            BOT._shutting_down = value
        else:
            setattr(get_ctx().task, name, value)


# =============================================================================
# Bot Configuration Class (backward-compatible wrapper)
# =============================================================================
class BOT:
    """
    Main bot configuration class.
    For multi-user: Use get_ctx() to get per-user state.
    This class provides backward compatibility via proxy objects.
    """

    # Download sources list (legacy — use ctx.task.source)
    SOURCE: list = []

    # Active asyncio task reference (legacy — use ctx.task.task)
    TASK = None

    # Class-level shutdown flag (global, not per-user)
    _shutting_down: bool = False

    # Proxy instances (forward to per-user context)
    Setting = _SettingProxy()
    Options = _OptionsProxy()
    Mode = _ModeProxy()
    State = _StateProxy()


# =============================================================================
# Download Queue (backward-compatible)
# =============================================================================
class DownloadQueue:
    """Thread-safe download queue."""

    def __init__(self):
        self._queue: deque = deque()
        self._current = None

    def add(self, links: list, mode: str = "leech", upload_type: str = "normal"):
        self._queue.append({
            "links": links,
            "mode": mode,
            "type": upload_type,
            "added_at": datetime.now(),
        })

    def next(self):
        if self._queue:
            self._current = self._queue.popleft()
            return self._current
        self._current = None
        return None

    def peek(self):
        return self._queue[0] if self._queue else None

    @property
    def pending(self) -> int:
        return len(self._queue)

    @property
    def current(self):
        return self._current

    def clear(self):
        self._queue.clear()
        self._current = None

    def size(self) -> int:
        return len(self._queue)

    def list_items(self) -> list:
        items = []
        for i, item in enumerate(self._queue, 1):
            link_count = len(item["links"])
            first_link = item["links"][0][:60] if item["links"] else "N/A"
            items.append(f"  {i}. `{first_link}{'...' if len(item['links'][0]) > 60 else ''}` ({link_count} link{'s' if link_count > 1 else ''})")
        return items


Queue = DownloadQueue()


# =============================================================================
# Admin / Multi-User Management
# =============================================================================
class Admin:
    """Multi-user access control with admin priority."""

    _allowed: set = set(config.ALLOWED_USERS)
    _admins: set = set(config.ALLOWED_ADMINS)

    @classmethod
    def is_allowed(cls, user_id: int) -> bool:
        return user_id == config.OWNER_ID or user_id in cls._allowed or user_id in cls._admins

    @classmethod
    def is_admin(cls, user_id: int) -> bool:
        return user_id == config.OWNER_ID or user_id in cls._admins

    @classmethod
    def add_user(cls, user_id: int):
        cls._allowed.add(user_id)

    @classmethod
    def add_admin(cls, user_id: int):
        cls._admins.add(user_id)

    @classmethod
    def remove_user(cls, user_id: int):
        cls._allowed.discard(user_id)

    @classmethod
    def remove_admin(cls, user_id: int):
        cls._admins.discard(user_id)

    @classmethod
    def list_users(cls) -> list:
        return [config.OWNER_ID] + sorted(cls._allowed)

    @classmethod
    def list_admins(cls) -> list:
        return [config.OWNER_ID] + sorted(cls._admins)

    @classmethod
    def is_owner(cls, user_id: int) -> bool:
        return user_id == config.OWNER_ID


# =============================================================================
# YT-DLP Download Status (proxy)
# =============================================================================
class _YTDLProxy:
    """Proxy that forwards YTDL.xxx to get_ctx().ytdl.xxx"""
    def __getattr__(self, name):
        return getattr(get_ctx().ytdl, name)
    def __setattr__(self, name, value):
        setattr(get_ctx().ytdl, name, value)

YTDL = _YTDLProxy()


# =============================================================================
# Transfer Statistics (proxy)
# =============================================================================
class _TransferProxy:
    """Proxy that forwards Transfer.xxx to get_ctx().transfer.xxx"""
    def __getattr__(self, name):
        return getattr(get_ctx().transfer, name)
    def __setattr__(self, name, value):
        setattr(get_ctx().transfer, name, value)

Transfer = _TransferProxy()


# =============================================================================
# Task Error Handling (proxy)
# =============================================================================
class _TaskErrorProxy:
    """Proxy that forwards TaskError.xxx to get_ctx().task.xxx"""
    def __getattr__(self, name):
        if name == "state":
            return get_ctx().task.error_state
        if name == "text":
            return get_ctx().task.error_text
        raise AttributeError(name)
    def __setattr__(self, name, value):
        if name == "state":
            get_ctx().task.error_state = value
        elif name == "text":
            get_ctx().task.error_text = value
        else:
            raise AttributeError(name)

TaskError = _TaskErrorProxy()


# =============================================================================
# Time Tracking (proxy)
# =============================================================================
class _BotTimesProxy:
    """Proxy that forwards BotTimes.xxx to get_ctx().xxx"""
    def __getattr__(self, name):
        return getattr(get_ctx(), name)
    def __setattr__(self, name, value):
        setattr(get_ctx(), name, value)

BotTimes = _BotTimesProxy()


# =============================================================================
# File Paths (proxy)
# =============================================================================
class _PathsProxy:
    """Proxy that forwards Paths.xxx to get_ctx().paths.xxx"""
    def __getattr__(self, name):
        if name == "ASSETS_IMAGES":
            return str(Path(__file__).parent.parent.parent / "assets" / "images")
        if name == "MOUNTED_DRIVE":
            return "/content/drive"
        return getattr(get_ctx().paths, name)
    def __setattr__(self, name, value):
        setattr(get_ctx().paths, name, value)

Paths = _PathsProxy()


# =============================================================================
# Message Templates (proxy)
# =============================================================================
class _MessagesProxy:
    """Proxy that forwards Messages.xxx to get_ctx().messages.xxx"""
    def __getattr__(self, name):
        return getattr(get_ctx().messages, name)
    def __setattr__(self, name, value):
        setattr(get_ctx().messages, name, value)

Messages = _MessagesProxy()


# =============================================================================
# Message Objects (proxy)
# =============================================================================
class _MSGProxy:
    """Proxy that forwards MSG.xxx to get_ctx().messages.xxx"""
    def __getattr__(self, name):
        return getattr(get_ctx().messages, name)
    def __setattr__(self, name, value):
        setattr(get_ctx().messages, name, value)

MSG = _MSGProxy()


# =============================================================================
# Shared (not per-user)
# =============================================================================
class Aria2c:
    link_info: bool = False

class Gdrive:
    service = None

class BotStats:
    total_tasks: int = 0
    total_downloaded: int = 0
    total_uploaded: int = 0
    failed_tasks: int = 0
    start_time: datetime = datetime.now()


# =============================================================================
# Constants
# =============================================================================
MAX_FILE_SIZE = config.MAX_FILE_SIZE
MAX_VIDEO_SPLIT_SIZE = config.MAX_VIDEO_SPLIT_SIZE
VERSION = config.VERSION
BUILD_DATE = config.BUILD_DATE
