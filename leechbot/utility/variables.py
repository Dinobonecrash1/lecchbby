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
# Bot Configuration Class (backward-compatible wrapper)
# =============================================================================
class BOT:
    """
    Main bot configuration class.
    For multi-user: Use get_ctx() to get per-user state.
    This class provides backward compatibility.
    """

    # Download sources list (legacy — use ctx.task.source)
    SOURCE: list = []

    # Active asyncio task reference (legacy — use ctx.task.task)
    TASK = None

    class Setting:
        """
        Persistent user preference settings.
        For multi-user: These are now per-user via UserContext.settings.
        This class provides backward compatibility by delegating to current context.
        """
        @property
        def stream_upload(self): return get_ctx().settings.stream_upload
        @stream_upload.setter
        def stream_upload(self, v): get_ctx().settings.stream_upload = v

        @property
        def convert_video(self): return get_ctx().settings.convert_video
        @convert_video.setter
        def convert_video(self, v): get_ctx().settings.convert_video = v

        @property
        def convert_quality(self): return get_ctx().settings.convert_quality
        @convert_quality.setter
        def convert_quality(self, v): get_ctx().settings.convert_quality = v

        @property
        def caption(self): return get_ctx().settings.caption
        @caption.setter
        def caption(self, v): get_ctx().settings.caption = v

        @property
        def split_video(self): return get_ctx().settings.split_video
        @split_video.setter
        def split_video(self, v): get_ctx().settings.split_video = v

        @property
        def prefix(self): return get_ctx().settings.prefix
        @prefix.setter
        def prefix(self, v): get_ctx().settings.prefix = v

        @property
        def suffix(self): return get_ctx().settings.suffix
        @suffix.setter
        def suffix(self, v): get_ctx().settings.suffix = v

        @property
        def thumbnail(self): return get_ctx().settings.thumbnail
        @thumbnail.setter
        def thumbnail(self, v): get_ctx().settings.thumbnail = v

        @property
        def photo_mode(self): return get_ctx().settings.photo_mode
        @photo_mode.setter
        def photo_mode(self, v): get_ctx().settings.photo_mode = v

        @property
        def auto_delete(self): return get_ctx().settings.auto_delete
        @auto_delete.setter
        def auto_delete(self, v): get_ctx().settings.auto_delete = v

        @property
        def auto_delete_delay(self): return get_ctx().settings.auto_delete_delay
        @auto_delete_delay.setter
        def auto_delete_delay(self, v): get_ctx().settings.auto_delete_delay = v

        @property
        def autorename_template(self): return get_ctx().settings.autorename_template
        @autorename_template.setter
        def autorename_template(self, v): get_ctx().settings.autorename_template = v

    class Options:
        """Runtime options for current task (per-user via context)."""
        @property
        def stream_upload(self): return get_ctx().task.stream_upload
        @stream_upload.setter
        def stream_upload(self, v): get_ctx().task.stream_upload = v

        @property
        def convert_video(self): return get_ctx().task.convert_video
        @convert_video.setter
        def convert_video(self, v): get_ctx().task.convert_video = v

        @property
        def convert_quality(self): return get_ctx().task.convert_quality
        @convert_quality.setter
        def convert_quality(self, v): get_ctx().task.convert_quality = v

        @property
        def is_split(self): return get_ctx().task.is_split
        @is_split.setter
        def is_split(self, v): get_ctx().task.is_split = v

        @property
        def caption(self): return get_ctx().task.caption
        @caption.setter
        def caption(self, v): get_ctx().task.caption = v

        @property
        def video_out(self): return get_ctx().task.video_out
        @video_out.setter
        def video_out(self, v): get_ctx().task.video_out = v

        @property
        def custom_name(self): return get_ctx().task.custom_name
        @custom_name.setter
        def custom_name(self, v): get_ctx().task.custom_name = v

        @property
        def file_name(self): return get_ctx().task.file_name
        @file_name.setter
        def file_name(self, v): get_ctx().task.file_name = v

        @property
        def zip_pswd(self): return get_ctx().task.zip_pswd
        @zip_pswd.setter
        def zip_pswd(self, v): get_ctx().task.zip_pswd = v

        @property
        def unzip_pswd(self): return get_ctx().task.unzip_pswd
        @unzip_pswd.setter
        def unzip_pswd(self, v): get_ctx().task.unzip_pswd = v

        @property
        def ytdl_format(self): return get_ctx().task.ytdl_format
        @ytdl_format.setter
        def ytdl_format(self, v): get_ctx().task.ytdl_format = v

        @property
        def bandwidth_limit(self): return get_ctx().task.bandwidth_limit
        @bandwidth_limit.setter
        def bandwidth_limit(self, v): get_ctx().task.bandwidth_limit = v

        @property
        def http_headers(self): return get_ctx().task.http_headers
        @http_headers.setter
        def http_headers(self, v): get_ctx().task.http_headers = v

    class Mode:
        """Current task mode (per-user via context)."""
        @property
        def mode(self): return get_ctx().task.mode
        @mode.setter
        def mode(self, v): get_ctx().task.mode = v

        @property
        def type(self): return get_ctx().task.type
        @type.setter
        def type(self, v): get_ctx().task.type = v

        @property
        def ytdl(self): return get_ctx().task.ytdl
        @ytdl.setter
        def ytdl(self, v): get_ctx().task.ytdl = v

        @property
        def gallery(self): return get_ctx().task.gallery
        @gallery.setter
        def gallery(self, v): get_ctx().task.gallery = v

    class State:
        """Bot state tracking flags (per-user via context)."""
        @property
        def started(self): return False  # Legacy — not used per-user
        @started.setter
        def started(self, v): pass

        @property
        def task_going(self): return get_ctx().task.task_going
        @task_going.setter
        def task_going(self, v): get_ctx().task.task_going = v

        @property
        def prefix(self): return get_ctx().task.prefix
        @prefix.setter
        def prefix(self, v): get_ctx().task.prefix = v

        @property
        def suffix(self): return get_ctx().task.suffix
        @suffix.setter
        def suffix(self, v): get_ctx().task.suffix = v

        @property
        def setting_autodelete_delay(self): return get_ctx().task.setting_autodelete_delay
        @setting_autodelete_delay.setter
        def setting_autodelete_delay(self, v): get_ctx().task.setting_autodelete_delay = v

        @property
        def setting_autorename(self): return get_ctx().task.setting_autorename
        @setting_autorename.setter
        def setting_autorename(self, v): get_ctx().task.setting_autorename = v

        @property
        def anime_search_results(self): return get_ctx().task.anime_search_results
        @anime_search_results.setter
        def anime_search_results(self, v): get_ctx().task.anime_search_results = v

        @property
        def anime_search_query(self): return get_ctx().task.anime_search_query
        @anime_search_query.setter
        def anime_search_query(self, v): get_ctx().task.anime_search_query = v

        @property
        def anime_search_provider(self): return get_ctx().task.anime_search_provider
        @anime_search_provider.setter
        def anime_search_provider(self, v): get_ctx().task.anime_search_provider = v

        @property
        def anime_selected(self): return get_ctx().task.anime_selected
        @anime_selected.setter
        def anime_selected(self, v): get_ctx().task.anime_selected = v

        @property
        def anime_episodes(self): return get_ctx().task.anime_episodes
        @anime_episodes.setter
        def anime_episodes(self, v): get_ctx().task.anime_episodes = v

        @property
        def anime_episode_meta(self): return get_ctx().task.anime_episode_meta
        @anime_episode_meta.setter
        def anime_episode_meta(self, v): get_ctx().task.anime_episode_meta = v

        @property
        def anime_poster_path(self): return get_ctx().task.anime_poster_path
        @anime_poster_path.setter
        def anime_poster_path(self, v): get_ctx().task.anime_poster_path = v

        @property
        def shutting_down(self):
            # Global — shared across all users
            return BOT._shutting_down
        @shutting_down.setter
        def shutting_down(self, v):
            BOT._shutting_down = v

    # Class-level shutdown flag (global, not per-user)
    _shutting_down: bool = False


# =============================================================================
# Download Queue (backward-compatible)
# =============================================================================
class DownloadQueue:
    """
    Thread-safe download queue.
    For multi-user: Use TaskQueue from user_state.py.
    This class provides backward compatibility.
    """

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


# Global queue instance (backward-compatible)
Queue = DownloadQueue()


# =============================================================================
# Admin / Multi-User Management (enhanced with multi-admin)
# =============================================================================
class Admin:
    """
    Multi-user access control with admin priority.
    OWNER and ADMINS always have full access and queue priority.
    """

    _allowed: set = set(config.ALLOWED_USERS)
    _admins: set = set(config.ALLOWED_ADMINS)

    @classmethod
    def is_allowed(cls, user_id: int) -> bool:
        """Check if a user is allowed to use the bot."""
        return user_id == config.OWNER_ID or user_id in cls._allowed or user_id in cls._admins

    @classmethod
    def is_admin(cls, user_id: int) -> bool:
        """Check if user is admin (gets queue priority)."""
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
        users = [config.OWNER_ID] + sorted(cls._allowed)
        return users

    @classmethod
    def list_admins(cls) -> list:
        return [config.OWNER_ID] + sorted(cls._admins)

    @classmethod
    def is_owner(cls, user_id: int) -> bool:
        return user_id == config.OWNER_ID


# =============================================================================
# YT-DLP Download Status (backward-compatible — delegates to context)
# =============================================================================
class YTDL:
    """Real-time YT-DLP download status (per-user via context)."""
    @property
    def header(self): return get_ctx().ytdl.header
    @header.setter
    def header(self, v): get_ctx().ytdl.header = v

    @property
    def speed(self): return get_ctx().ytdl.speed
    @speed.setter
    def speed(self, v): get_ctx().ytdl.speed = v

    @property
    def percentage(self): return get_ctx().ytdl.percentage
    @percentage.setter
    def percentage(self, v): get_ctx().ytdl.percentage = v

    @property
    def eta(self): return get_ctx().ytdl.eta
    @eta.setter
    def eta(self, v): get_ctx().ytdl.eta = v

    @property
    def done(self): return get_ctx().ytdl.done
    @done.setter
    def done(self, v): get_ctx().ytdl.done = v

    @property
    def left(self): return get_ctx().ytdl.left
    @left.setter
    def left(self, v): get_ctx().ytdl.left = v

    @property
    def complete(self): return get_ctx().ytdl.complete
    @complete.setter
    def complete(self, v): get_ctx().ytdl.complete = v


# =============================================================================
# Transfer Statistics (backward-compatible — delegates to context)
# =============================================================================
class Transfer:
    """File transfer statistics tracker (per-user via context)."""
    @property
    def down_bytes(self): return get_ctx().transfer.down_bytes
    @down_bytes.setter
    def down_bytes(self, v): get_ctx().transfer.down_bytes = v

    @property
    def up_bytes(self): return get_ctx().transfer.up_bytes
    @up_bytes.setter
    def up_bytes(self, v): get_ctx().transfer.up_bytes = v

    @property
    def total_down_size(self): return get_ctx().transfer.total_down_size
    @total_down_size.setter
    def total_down_size(self, v): get_ctx().transfer.total_down_size = v

    @property
    def sent_file(self): return get_ctx().transfer.sent_file
    @sent_file.setter
    def sent_file(self, v): get_ctx().transfer.sent_file = v

    @property
    def sent_file_names(self): return get_ctx().transfer.sent_file_names
    @sent_file_names.setter
    def sent_file_names(self, v): get_ctx().transfer.sent_file_names = v

    @property
    def download_path(self): return get_ctx().transfer.download_path
    @download_path.setter
    def download_path(self, v): get_ctx().transfer.download_path = v


# =============================================================================
# Task Error Handling (backward-compatible — delegates to context)
# =============================================================================
class TaskError:
    """Task error tracker (per-user via context)."""
    @property
    def state(self): return get_ctx().task.error_state
    @state.setter
    def state(self, v): get_ctx().task.error_state = v

    @property
    def text(self): return get_ctx().task.error_text
    @text.setter
    def text(self, v): get_ctx().task.error_text = v


# =============================================================================
# Time Tracking (backward-compatible — delegates to context)
# =============================================================================
class BotTimes:
    """Bot timing tracker for progress calculations (per-user via context)."""
    @property
    def current_time(self): return get_ctx().current_time
    @current_time.setter
    def current_time(self, v): get_ctx().current_time = v

    @property
    def start_time(self): return get_ctx().start_time
    @start_time.setter
    def start_time(self, v): get_ctx().start_time = v

    @property
    def task_start(self): return get_ctx().task_start
    @task_start.setter
    def task_start(self, v): get_ctx().task_start = v


# =============================================================================
# File Paths (backward-compatible — delegates to context)
# =============================================================================
class Paths:
    """File system paths (per-user via context)."""
    @property
    def WORK_PATH(self): return str(get_ctx().paths.work)
    @WORK_PATH.setter
    def WORK_PATH(self, v): pass  # Read-only, set per-user

    @property
    def down_path(self): return get_ctx().paths.down_path
    @down_path.setter
    def down_path(self, v): get_ctx().paths.down_path = v

    @property
    def THMB_PATH(self): return get_ctx().paths.THMB_PATH
    @THMB_PATH.setter
    def THMB_PATH(self, v): get_ctx().paths.THMB_PATH = v

    @property
    def VIDEO_FRAME(self): return get_ctx().paths.VIDEO_FRAME
    @VIDEO_FRAME.setter
    def VIDEO_FRAME(self, v): get_ctx().paths.VIDEO_FRAME = v

    @property
    def ASSETS_IMAGES(self): return str(Path(__file__).parent.parent.parent / "assets" / "images")

    @property
    def HERO_IMAGE(self): return get_ctx().paths.HERO_IMAGE
    @HERO_IMAGE.setter
    def HERO_IMAGE(self, v): get_ctx().paths.HERO_IMAGE = v

    @property
    def DEFAULT_HERO(self): return get_ctx().paths.DEFAULT_HERO
    @DEFAULT_HERO.setter
    def DEFAULT_HERO(self, v): get_ctx().paths.DEFAULT_HERO = v

    @property
    def MOUNTED_DRIVE(self): return "/content/drive"

    @property
    def temp_dirleech_path(self): return get_ctx().paths.temp_dirleech_path
    @temp_dirleech_path.setter
    def temp_dirleech_path(self, v): get_ctx().paths.temp_dirleech_path = v

    @property
    def mirror_dir(self): return get_ctx().paths.mirror_dir
    @mirror_dir.setter
    def mirror_dir(self, v): get_ctx().paths.mirror_dir = v

    @property
    def temp_zpath(self): return get_ctx().paths.temp_zpath
    @temp_zpath.setter
    def temp_zpath(self, v): get_ctx().paths.temp_zpath = v

    @property
    def temp_unzip_path(self): return get_ctx().paths.temp_unzip_path
    @temp_unzip_path.setter
    def temp_unzip_path(self, v): get_ctx().paths.temp_unzip_path = v

    @property
    def temp_files_dir(self): return get_ctx().paths.temp_files_dir
    @temp_files_dir.setter
    def temp_files_dir(self, v): get_ctx().paths.temp_files_dir = v

    @property
    def thumbnail_ytdl(self): return get_ctx().paths.thumbnail_ytdl
    @thumbnail_ytdl.setter
    def thumbnail_ytdl(self, v): get_ctx().paths.thumbnail_ytdl = v

    @property
    def access_token(self): return get_ctx().paths.access_token
    @access_token.setter
    def access_token(self, v): get_ctx().paths.access_token = v

    @property
    def ytdl_cookies(self): return get_ctx().paths.ytdl_cookies
    @ytdl_cookies.setter
    def ytdl_cookies(self, v): get_ctx().paths.ytdl_cookies = v

    @property
    def COOKIE_FILE(self): return get_ctx().paths.COOKIE_FILE
    @COOKIE_FILE.setter
    def COOKIE_FILE(self, v): get_ctx().paths.COOKIE_FILE = v


# =============================================================================
# Message Templates (backward-compatible — delegates to context)
# =============================================================================
class Messages:
    """Dynamic message content storage (per-user via context)."""
    @property
    def caution_msg(self): return get_ctx().messages.caution_msg
    @caution_msg.setter
    def caution_msg(self, v): get_ctx().messages.caution_msg = v

    @property
    def download_name(self): return get_ctx().messages.download_name
    @download_name.setter
    def download_name(self, v): get_ctx().messages.download_name = v

    @property
    def task_msg(self): return get_ctx().messages.task_msg
    @task_msg.setter
    def task_msg(self, v): get_ctx().messages.task_msg = v

    @property
    def status_head(self): return get_ctx().messages.status_head
    @status_head.setter
    def status_head(self, v): get_ctx().messages.status_head = v

    @property
    def dump_task(self): return get_ctx().messages.dump_task
    @dump_task.setter
    def dump_task(self, v): get_ctx().messages.dump_task = v

    @property
    def src_link(self): return get_ctx().messages.src_link
    @src_link.setter
    def src_link(self, v): get_ctx().messages.src_link = v

    @property
    def link_p(self): return get_ctx().messages.link_p
    @link_p.setter
    def link_p(self, v): get_ctx().messages.link_p = v


# =============================================================================
# Message Objects (backward-compatible — delegates to context)
# =============================================================================
class MSG:
    """Telegram message object references (per-user via context)."""
    @property
    def sent_msg(self): return get_ctx().messages.sent_msg
    @sent_msg.setter
    def sent_msg(self, v): get_ctx().messages.sent_msg = v

    @property
    def status_msg(self): return get_ctx().messages.status_msg
    @status_msg.setter
    def status_msg(self, v): get_ctx().messages.status_msg = v


# =============================================================================
# Aria2c Configuration (shared — not per-user)
# =============================================================================
class Aria2c:
    """Aria2c downloader state."""
    link_info: bool = False


# =============================================================================
# Google Drive Service (shared — connection pool)
# =============================================================================
class Gdrive:
    """Google Drive API service holder."""
    service = None


# =============================================================================
# Bot Statistics (shared — aggregate across all users)
# =============================================================================
class BotStats:
    """Cumulative bot usage statistics."""
    total_tasks: int = 0
    total_downloaded: int = 0
    total_uploaded: int = 0
    failed_tasks: int = 0
    start_time: datetime = datetime.now()


# =============================================================================
# Constants (re-exported from config for convenience)
# =============================================================================
MAX_FILE_SIZE = config.MAX_FILE_SIZE
MAX_VIDEO_SPLIT_SIZE = config.MAX_VIDEO_SPLIT_SIZE
VERSION = config.VERSION
BUILD_DATE = config.BUILD_DATE
