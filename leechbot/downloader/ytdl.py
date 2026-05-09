# =============================================================================
# Telegram Leech Bot - YT-DLP Downloader
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
YT-DLP downloader module.

Handles downloads from YouTube and 2000+ other sites via yt-dlp.
Supports format selection (best, 720p, 480p, audio-only).
"""

import logging
import yt_dlp
from asyncio import sleep
from threading import Thread
from os import makedirs, path as ospath

import config
from leechbot.utility.variables import YTDL, MSG, Messages, Paths, BOT
from leechbot.utility.helper import getTime, keyboard, sizeUnit, status_bar, sysINFO

logger = logging.getLogger(__name__)

# =============================================================================
# Format Presets
# =============================================================================
FORMAT_PRESETS = {
    "best": "bestvideo+bestaudio/best",
    "bestvideo": "bestvideo+bestaudio/best",
    "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
    "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
    "audio": "bestaudio/best",
    "worst": "worstvideo+worstaudio/worst",
}


def get_format_string(preset: str = None) -> str:
    """Resolve a format preset name to a yt-dlp format string."""
    if preset is None:
        preset = BOT.Options.ytdl_format

    # If it's a known preset name, use it; otherwise treat as raw format string
    return FORMAT_PRESETS.get(preset.lower(), preset)


def _get_cookie_opts() -> dict:
    """
    Return yt-dlp options dict for cookie authentication.

    Resolution order:
      1. YTDL_COOKIES_FILE env var — explicit path to cookies.txt
      2. Default save path (Paths.COOKIE_FILE) — uploaded via /setcookies
      3. YTDL_BROWSER_COOKIES env var — extract from installed browser

    Returns:
        dict: yt-dlp options with cookie settings, or empty dict if unconfigured.
    """
    cookies_file = getattr(config, "YTDL_COOKIES_FILE", "")
    browser_cookies = getattr(config, "YTDL_BROWSER_COOKIES", "")
    default_path = getattr(Paths, "COOKIE_FILE", "")

    # Priority 1: explicit env var
    if cookies_file and ospath.isfile(cookies_file):
        logger.info("Using cookies file (env): %s", cookies_file)
        return {"cookiefile": cookies_file}

    # Priority 2: uploaded via /setcookies command
    if default_path and ospath.isfile(default_path):
        logger.info("Using cookies file (uploaded): %s", default_path)
        return {"cookiefile": default_path}

    # Priority 3: browser extraction (requires browser on same machine)
    if browser_cookies:
        logger.info("Extracting cookies from browser: %s", browser_cookies)
        return {"cookiesfrombrowser": (browser_cookies,)}

    return {}


# =============================================================================
# YT-DLP Status Monitor
# =============================================================================
async def YTDL_Status(link: str, num: int):
    """
    Monitor YT-DLP download progress in a background thread.

    Args:
        link: video URL
        num: link number for display
    """
    name = await get_YT_Name(link)
    Messages.status_head = (
        f"**📥 Downloading** `Link {str(num).zfill(2)}`\n\n`{name}`\n"
    )

    ytdl_thread = Thread(target=YouTubeDL, name="YT-DLP", args=(link,), daemon=True)
    ytdl_thread.start()

    while ytdl_thread.is_alive():
        if YTDL.header:
            try:
                await MSG.status_msg.edit_text(
                    text=Messages.task_msg + Messages.status_head + YTDL.header + sysINFO(),
                    reply_markup=keyboard()
                )
            except Exception:
                pass
        else:
            try:
                await status_bar(
                    down_msg=Messages.status_head,
                    speed=YTDL.speed,
                    percentage=float(YTDL.percentage),
                    eta=YTDL.eta,
                    done=YTDL.done,
                    left=YTDL.left,
                    engine="YT-DLP 🏮"
                )
            except Exception:
                pass

        await sleep(2.5)


# =============================================================================
# YT-DLP Logger
# =============================================================================
class MyLogger:
    """Custom logger for yt-dlp that updates the YTDL status object."""

    @staticmethod
    def debug(msg):
        if "item" in str(msg):
            msgs = msg.split(" ")
            YTDL.header = f"\n⏳ `Getting Info {msgs[-3]} of {msgs[-1]}`"

    @staticmethod
    def warning(msg):
        pass

    @staticmethod
    def error(msg):
        logger.error(f"YT-DLP: {msg}")


# =============================================================================
# Progress Hook
# =============================================================================
def _progress_hook(d):
    """Progress hook for yt-dlp that updates global YTDL status."""
    if d["status"] == "downloading":
        total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
        dl_bytes = d.get("downloaded_bytes", 0)
        speed = d.get("speed")
        eta = d.get("eta")

        percent = round((float(dl_bytes) * 100 / float(total_bytes)), 2) if total_bytes else 0

        YTDL.header = ""
        YTDL.speed = sizeUnit(speed) if speed else "N/A"
        YTDL.percentage = min(percent, 100)
        YTDL.eta = getTime(eta) if eta else "N/A"
        YTDL.done = sizeUnit(dl_bytes) if dl_bytes else "N/A"
        YTDL.left = sizeUnit(total_bytes) if total_bytes else "N/A"

    elif d["status"] == "finished":
        YTDL.header = "\n⏳ `Download finished, processing...`"


# =============================================================================
# YT-DLP Download Function
# =============================================================================
def YouTubeDL(url: str):
    """
    Download video/audio using yt-dlp.

    Args:
        url: video URL
    """
    format_str = get_format_string()
    is_audio_only = format_str == FORMAT_PRESETS.get("audio")

    ydl_opts = {
        "format": format_str,
        "merge_output_format": "mp4" if not is_audio_only else None,
        "writethumbnail": True,
        "concurrent_fragment_downloads": 5,
        "overwrites": True,
        "progress_hooks": [_progress_hook],
        "writesubtitles": True,
        "subtitleslangs": ["en", "en-US", "en-GB"],
        "extractor_args": {
            "subtitlesformat": "srt",
        },
        "logger": MyLogger(),
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "outtmpl": {
            "default": f"{Paths.down_path}/%(title)s.%(ext)s",
            "thumbnail": f"{Paths.thumbnail_ytdl}/%(title)s.%(ext)s",
        },
    }

    # Merge cookie authentication options (fixes YouTube bot detection)
    ydl_opts.update(_get_cookie_opts())

    # Audio-only options
    if is_audio_only:
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        }]

    if not ospath.exists(Paths.thumbnail_ytdl):
        makedirs(Paths.thumbnail_ytdl)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            YTDL.header = "⏳ `Preparing...`"

            if info.get("_type") == "playlist":
                # Playlist download
                playlist_name = info["title"]
                playlist_path = ospath.join(Paths.down_path, playlist_name)

                if not ospath.exists(playlist_path):
                    makedirs(playlist_path)

                ydl_opts["outtmpl"]["default"] = f"{playlist_path}/%(title)s.%(ext)s"

                with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                    for entry in info.get("entries", []):
                        if entry:
                            try:
                                ydl2.download([entry["webpage_url"]])
                            except Exception as e:
                                logger.error(f"Playlist item error: {e}")
            else:
                ydl.download([url])

        except Exception as e:
            logger.error(f"YT-DLP error: {e}")
            raise


# =============================================================================
# Get Video Name
# =============================================================================
async def get_YT_Name(link: str) -> str:
    """Get video title from link without downloading."""
    try:
        opts = {"logger": MyLogger(), "quiet": True}
        opts.update(_get_cookie_opts())
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(link, download=False)
            return info.get("title", "Unknown")
    except Exception as e:
        logger.error(f"Cannot get YT name: {e}")
        return "Unknown"


# =============================================================================
# List Available Formats
# =============================================================================
async def list_formats(link: str) -> str:
    """
    List available formats for a link.

    Returns:
        str: formatted list of available formats
    """
    try:
        opts = {"quiet": True, "no_warnings": True}
        opts.update(_get_cookie_opts())
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(link, download=False)
            formats = info.get("formats", [])

            if not formats:
                return "**⚠️ No formats found**"

            text = f"**🎬 Available Formats for:**\n`{info.get('title', 'Unknown')}`\n\n"

            seen = set()
            for f in formats:
                fmt_id = f.get("format_id", "?")
                ext = f.get("ext", "?")
                res = f.get("resolution", "audio only")
                height = f.get("height")
                filesize = f.get("filesize") or f.get("filesize_approx", 0)

                key = f"{height}_{ext}"
                if key in seen:
                    continue
                seen.add(key)

                size_str = sizeUnit(filesize) if filesize else "N/A"
                height_str = f"{height}p" if height else "audio"

                text += f"• `{fmt_id}` — {height_str} ({ext}) — {size_str}\n"

                if len(text) > 3500:
                    text += "\n... (truncated)"
                    break

            return text

    except Exception as e:
        return f"**❌ Error:** `{e}`"
