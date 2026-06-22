# =============================================================================
# Telegram Leech Bot - Per-User State Management
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Per-user state isolation for multi-user support.

Each user gets their own UserContext with isolated:
  - Settings (persistent preferences)
  - Task state (current download/upload)
  - Transfer stats (bytes, files)
  - Messages (status, dump, source)
  - Paths (per-user temp directories)
"""

import os
import config
from time import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Optional
from asyncio import Task


# =============================================================================
# User Settings (persistent across tasks)
# =============================================================================
@dataclass
class UserSettings:
    """Persistent user preferences — survive across tasks."""
    stream_upload: str = config.DEFAULT_UPLOAD_MODE
    convert_video: str = "Yes"
    convert_quality: str = "Low"
    caption: str = "Regular"
    split_video: str = "Split"
    prefix: str = ""
    suffix: str = ""
    thumbnail: bool = False
    photo_mode: str = "Group"
    auto_delete: bool = False
    auto_delete_delay: int = 30
    autorename_template: str = ""
    ytdl_format: str = "bestvideo+bestaudio/best"


# =============================================================================
# User Paths (per-user isolated directories)
# =============================================================================
@dataclass
class UserPaths:
    """Per-user file system paths."""
    base: Path = field(default_factory=Path)
    work: Path = field(default_factory=Path)
    downloads: Path = field(default_factory=Path)
    temp: Path = field(default_factory=Path)
    thumbnails: Path = field(default_factory=Path)

    # Derived paths used by code
    WORK_PATH: str = ""
    temp_zpath: str = ""
    temp_unzip_path: str = ""
    temp_files_dir: str = ""
    temp_dirleech_path: str = ""
    thumbnail_ytdl: str = ""
    down_path: str = ""
    THMB_PATH: str = ""
    VIDEO_FRAME: str = ""
    HERO_IMAGE: str = ""
    DEFAULT_HERO: str = ""
    FONT_FILE: str = ""
    MOUNTED_DRIVE: str = "/content/drive"
    mirror_dir: str = ""
    access_token: str = ""
    ytdl_cookies: str = ""
    COOKIE_FILE: str = ""

    @classmethod
    def create(cls, user_id: int) -> "UserPaths":
        """Create isolated directories for a user."""
        base = config.BASE_DIR / "users" / str(user_id)
        work = base / "work"
        downloads = work / "downloads"
        temp = base / "temp"
        thumbs = base / "thumbnails"

        for p in [work, downloads, temp, thumbs]:
            p.mkdir(parents=True, exist_ok=True)

        paths = cls(
            base=base,
            work=work,
            downloads=downloads,
            temp=temp,
            thumbnails=thumbs,
        )

        # Set derived paths
        paths.WORK_PATH = str(work)
        paths.temp_zpath = str(temp / "zipped")
        paths.temp_unzip_path = str(temp / "unzipped")
        paths.temp_files_dir = str(temp / "leech_temp")
        paths.temp_dirleech_path = str(work / "dir_leech_temp")
        paths.thumbnail_ytdl = str(temp / "ytdl_thumbnails")
        paths.down_path = str(downloads)
        paths.THMB_PATH = str(thumbs / "Thumbnail.jpg")
        paths.VIDEO_FRAME = str(temp / "video_frame.jpg")
        paths.mirror_dir = str(downloads / "mirror")
        paths.access_token = config.TOKEN_PICKLE_PATH
        paths.ytdl_cookies = config.YTDL_COOKIES_FILE
        paths.COOKIE_FILE = str(config.SESSIONS_PATH / f"cookies_{user_id}.txt")

        # Create subdirs
        for d in [paths.temp_zpath, paths.temp_unzip_path, paths.temp_files_dir,
                  paths.temp_dirleech_path, paths.thumbnail_ytdl, paths.mirror_dir]:
            os.makedirs(d, exist_ok=True)

        return paths

    def cleanup(self):
        """Remove user's temp files after task completes."""
        import shutil
        for d in [self.temp_zpath, self.temp_unzip_path, self.temp_files_dir,
                  self.temp_dirleech_path, self.thumbnail_ytdl]:
            if os.path.exists(d):
                shutil.rmtree(d, ignore_errors=True)


# =============================================================================
# User Transfer Stats
# =============================================================================
@dataclass
class UserTransfer:
    """Per-user file transfer statistics."""
    down_bytes: list = field(default_factory=lambda: [0, 0])
    up_bytes: list = field(default_factory=lambda: [0, 0])
    total_down_size: int = 0
    sent_file: list = field(default_factory=list)
    sent_file_names: list = field(default_factory=list)
    download_path: str = ""

    def reset(self):
        self.down_bytes = [0, 0]
        self.up_bytes = [0, 0]
        self.total_down_size = 0
        self.sent_file = []
        self.sent_file_names = []
        self.download_path = ""


# =============================================================================
# User Messages
# =============================================================================
@dataclass
class UserMessages:
    """Per-user message content and references."""
    download_name: str = ""
    task_msg: str = ""
    status_head: str = ""
    dump_task: str = ""
    src_link: str = ""
    link_p: str = ""
    caution_msg: str = ""

    # Pyrogram message objects
    sent_msg = None  # Message object for uploads
    status_msg = None  # Message object for status updates
    src_request_msg = None  # "Please send links" request message


# =============================================================================
# User YTDL Status
# =============================================================================
@dataclass
class UserYTDL:
    """Per-user YT-DLP download status."""
    header: str = ""
    speed: str = ""
    percentage: float = 0.0
    eta: str = ""
    done: str = ""
    left: str = ""
    complete: bool = False


# =============================================================================
# User Task State
# =============================================================================
@dataclass
class UserTaskState:
    """Per-user, per-task runtime state."""
    task_going: bool = False
    task: Optional[Task] = None
    source: list = field(default_factory=list)
    mode: str = "leech"
    type: str = "normal"
    ytdl: bool = False
    gallery: bool = False
    started: bool = False
    is_leech: bool = False
    stream: bool = False
    link_info: bool = False

    # Anime state
    anime_search_results: list = field(default_factory=list)
    anime_search_query: str = ""
    anime_search_provider: str = "animex"
    anime_selected: dict = field(default_factory=dict)
    anime_episodes: list = field(default_factory=list)
    anime_episode_meta: list = field(default_factory=list)
    anime_poster_path: str = ""

    # Options (per-task)
    stream_upload: bool = True
    convert_video: bool = True
    convert_quality: bool = False
    is_split: bool = True
    caption: str = "code"
    video_out: str = "mp4"
    custom_name: str = ""
    file_name: str = ""
    zip_pswd: str = ""
    unzip_pswd: str = ""
    ytdl_format: str = "bestvideo+bestaudio/best"
    bandwidth_limit: str = config.BANDWIDTH_LIMIT
    http_headers: dict = None

    # Input state flags
    prefix: bool = False
    suffix: bool = False
    setting_autodelete_delay: bool = False
    setting_autorename: bool = False

    # Error state
    error_state: bool = False
    error_text: str = ""

    def reset_task(self):
        """Reset per-task state (keep persistent settings)."""
        self.task_going = False
        self.task = None
        self.source = []
        self.mode = "leech"
        self.type = "normal"
        self.ytdl = False
        self.gallery = False
        self.started = False
        self.is_leech = False
        self.stream = False
        self.link_info = False

        # Anime state
        self.anime_search_results = []
        self.anime_search_query = ""
        self.anime_search_provider = "animex"
        self.anime_selected = {}
        self.anime_episodes = []
        self.anime_episode_meta = []
        self.anime_poster_path = ""

        # Options (per-task)
        self.stream_upload = True
        self.convert_video = True
        self.convert_quality = False
        self.is_split = True
        self.caption = "code"
        self.video_out = "mp4"
        self.custom_name = ""
        self.file_name = ""
        self.zip_pswd = ""
        self.unzip_pswd = ""
        self.ytdl_format = "bestvideo+bestaudio/best"
        self.bandwidth_limit = config.BANDWIDTH_LIMIT
        self.http_headers = None
        self.error_state = False
        self.error_text = ""


# =============================================================================
# User Context — Complete state bundle for one user
# =============================================================================
@dataclass
class UserContext:
    """Complete per-user state bundle."""
    user_id: int
    is_admin: bool = False
    settings: UserSettings = field(default_factory=UserSettings)
    task: UserTaskState = field(default_factory=UserTaskState)
    transfer: UserTransfer = field(default_factory=UserTransfer)
    messages: UserMessages = field(default_factory=UserMessages)
    ytdl: UserYTDL = field(default_factory=UserYTDL)
    paths: UserPaths = field(default_factory=UserPaths)
    queue: deque = field(default_factory=deque)

    # Timing
    current_time: float = field(default_factory=time)
    start_time: datetime = field(default_factory=datetime.now)
    task_start: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.paths.WORK_PATH:
            self.paths = UserPaths.create(self.user_id)

    def reset_task(self):
        """Reset per-task state for new task."""
        self.task.reset_task()
        self.transfer.reset()
        self.ytdl = UserYTDL()
        self.messages = UserMessages()
        self.current_time = time()
        self.start_time = datetime.now()
        self.task_start = datetime.now()
        # Persist ytdl format from user settings
        self.task.ytdl_format = self.settings.ytdl_format


# =============================================================================
# User Registry — Global dictionary of all user contexts
# =============================================================================
class UserRegistry:
    """Global registry of per-user state contexts."""

    _users: dict = {}

    @classmethod
    def get(cls, user_id: int) -> UserContext:
        """Get or create a UserContext for a user."""
        if user_id not in cls._users:
            is_admin = user_id == config.OWNER_ID or user_id in config.ALLOWED_ADMINS
            cls._users[user_id] = UserContext(user_id=user_id, is_admin=is_admin)
        return cls._users[user_id]

    @classmethod
    def get_or_none(cls, user_id: int) -> Optional[UserContext]:
        """Get UserContext without creating."""
        return cls._users.get(user_id)

    @classmethod
    def all_users(cls) -> list:
        """Return list of all user contexts."""
        return list(cls._users.values())

    @classmethod
    def active_tasks(cls) -> int:
        """Count currently running tasks."""
        return sum(1 for u in cls._users.values() if u.task.task_going)

    @classmethod
    def queue_position(cls, user_id: int) -> int:
        """Get user's position in the global queue (1-based, 0 if not queued)."""
        pos = 1
        for uid, ctx in cls._users.items():
            if uid == user_id:
                return pos
            if ctx.task.task_going or ctx.queue:
                pos += 1
        return 0


# =============================================================================
# Global Task Queue with Priority (admin > user)
# =============================================================================
class PriorityQueue:
    """
    Task queue with priority: admin tasks go first.
    """

    def __init__(self):
        self._queue: deque = deque()

    def add(self, user_id: int, task_data: dict):
        """Add task to queue. Admin tasks are inserted at the front."""
        entry = {"user_id": user_id, **task_data, "added_at": datetime.now()}

        is_admin = user_id == config.OWNER_ID or user_id in config.ALLOWED_ADMINS

        if is_admin:
            # Admin tasks go to the front (after any currently running admin task)
            insert_pos = 0
            for i, item in enumerate(self._queue):
                if not (item["user_id"] == config.OWNER_ID or
                        item["user_id"] in config.ALLOWED_ADMINS):
                    break
                insert_pos = i + 1
            self._queue.insert(insert_pos, entry)
        else:
            self._queue.append(entry)

    def next(self) -> Optional[dict]:
        """Get next task from queue."""
        if self._queue:
            return self._queue.popleft()
        return None

    def peek(self) -> Optional[dict]:
        """Look at next task without removing."""
        return self._queue[0] if self._queue else None

    def remove_user(self, user_id: int):
        """Remove all tasks for a specific user."""
        self._queue = deque(item for item in self._queue if item["user_id"] != user_id)

    def position(self, user_id: int) -> int:
        """Get user's position in queue (1-based, 0 if not queued)."""
        for i, item in enumerate(self._queue, 1):
            if item["user_id"] == user_id:
                return i
        return 0

    @property
    def pending(self) -> int:
        return len(self._queue)

    def clear(self):
        self._queue.clear()

    def list_items(self) -> list:
        """Return summary of queued items."""
        items = []
        for i, item in enumerate(self._queue, 1):
            uid = item["user_id"]
            is_admin = uid == config.OWNER_ID or uid in config.ALLOWED_ADMINS
            label = "👑 Admin" if is_admin else f"User {uid}"
            items.append(f"  {i}. {label}")
        return items


# Global priority queue instance
TaskQueue = PriorityQueue()
