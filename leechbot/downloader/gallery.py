# =============================================================================
# Telegram Leech Bot - Gallery-DL Downloader
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
gallery-dl downloader module.

Handles photo/image gallery downloads from Instagram, Twitter, Pinterest,
Pixiv, DeviantArt, ArtStation, Flickr, Reddit, Tumblr, and 100+ other sites.
"""

import os
import json
import glob
import logging
import asyncio
import subprocess
from asyncio import sleep
from os import makedirs, path as ospath

from leechbot.utility.variables import Paths, Messages, MSG, BotTimes
from leechbot.utility.helper import keyboard, sysINFO, sizeUnit, getSize

logger = logging.getLogger(__name__)


# =============================================================================
# Supported Sites (for detection)
# =============================================================================
GALLERY_SITES = [
    "instagram.com",
    "twitter.com",
    "x.com",
    "pinterest.com",
    "pixiv.net",
    "deviantart.com",
    "artstation.com",
    "flickr.com",
    "tumblr.com",
    "reddit.com",
    "imgur.com",
    "danbooru.donmai.us",
    "gelbooru.com",
    "konachan.com",
    "yande.re",
    "safebooru.org",
    "zerochan.net",
    "baraag.net",
    "pawoo.net",
    "newgrounds.com",
    "webtoons.com",
    "tapas.io",
    "hentaihaven.xxx",
    "nhentai.net",
    "ehentai.org",
    "exhentai.org",
    "furaffinity.net",
    "weasyl.com",
    "inkbunny.net",
    "tiktok.com",
    "bsky.app",
]


def is_gallery_link(link: str) -> bool:
    """Check if a link is supported by gallery-dl."""
    link_lower = link.lower()
    return any(site in link_lower for site in GALLERY_SITES)


# =============================================================================
# Gallery-DL Download Function
# =============================================================================
async def gallery_download(url: str, num: int):
    """
    Download images/media from a gallery URL using gallery-dl.

    Args:
        url: gallery URL
        num: link number for display
    """
    # Create output directory
    gallery_dir = ospath.join(Paths.down_path, f"gallery_{str(num).zfill(2)}")
    if not ospath.exists(gallery_dir):
        makedirs(gallery_dir)

    Messages.status_head = (
        f"**📸 Downloading Gallery** `Link {str(num).zfill(2)}`\n\n"
        f"`{url[:80]}`\n"
    )

    try:
        await MSG.status_msg.edit_text(
            text=Messages.task_msg + Messages.status_head + "\n⏳ Starting..." + sysINFO(),
            reply_markup=keyboard()
        )
    except Exception:
        pass

    # Build gallery-dl command
    cmd = [
        "gallery-dl",
        "--directory", gallery_dir,
        "--no-skip",          # Don't skip existing files
        "--no-mtime",         # Don't set file modification time
        "-q",                 # Quiet mode (less output)
        url
    ]

    try:
        # Run gallery-dl as subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # Monitor progress
        file_count = 0
        while process.returncode is None:
            await sleep(2)

            # Count downloaded files
            current_count = len(_get_files(gallery_dir))
            if current_count > file_count:
                file_count = current_count
                total_size = sizeUnit(getSize(gallery_dir))

                try:
                    await MSG.status_msg.edit_text(
                        text=Messages.task_msg + Messages.status_head +
                        f"\n📸 **Downloaded:** `{file_count} files` ({total_size})" + sysINFO(),
                        reply_markup=keyboard()
                    )
                except Exception:
                    pass

            await sleep(1)

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode().strip()[:200] if stderr else "Unknown error"
            logger.error(f"gallery-dl error: {error_msg}")
            raise Exception(f"gallery-dl failed (code {process.returncode}): {error_msg}")

        # Final count
        files = _get_files(gallery_dir)
        total_size = sizeUnit(getSize(gallery_dir))

        try:
            await MSG.status_msg.edit_text(
                text=Messages.task_msg + Messages.status_head +
                f"\n✅ **Complete:** `{len(files)} files` ({total_size})" + sysINFO(),
                reply_markup=keyboard()
            )
        except Exception:
            pass

        logger.info(f"gallery-dl downloaded {len(files)} files to {gallery_dir}")

    except FileNotFoundError:
        logger.error("gallery-dl not installed. Run: pip install gallery-dl")
        raise Exception("gallery-dl not installed")
    except Exception as e:
        logger.error(f"gallery-dl error: {e}")
        raise


# =============================================================================
# Get Downloaded Files
# =============================================================================
def _get_files(directory: str) -> list:
    """Get all downloaded files from gallery directory."""
    extensions = ('*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp', '*.bmp',
                  '*.tiff', '*.mp4', '*.webm', '*.mkv', '*.mov', '*.avi')
    files = []
    for ext in extensions:
        files.extend(glob.glob(os.path.join(directory, '**', ext), recursive=True))
    return sorted(files)


# =============================================================================
# Get Gallery Name (for display)
# =============================================================================
async def get_gallery_name(url: str) -> str:
    """Get a human-readable name for a gallery URL."""
    # Extract username/post from URL
    parts = url.rstrip('/').split('/')
    if 'instagram.com' in url:
        if 'p/' in url:
            return f"Instagram Post: {parts[-1]}"
        return f"Instagram: @{parts[-1] if parts[-1] else parts[-2]}"
    elif 'twitter.com' in url or 'x.com' in url:
        return f"Twitter: @{parts[-1] if parts[-1] else parts[-2]}"
    elif 'pinterest.com' in url:
        return f"Pinterest: {parts[-1] if parts[-1] else parts[-2]}"
    elif 'reddit.com' in url:
        return f"Reddit: r/{parts[-1] if parts[-1] else parts[-2]}"
    elif 'pixiv.net' in url:
        return f"Pixiv: {parts[-1] if parts[-1] else parts[-2]}"
    else:
        return f"Gallery: {parts[-1][:30] if parts[-1] else parts[-2][:30]}"


# =============================================================================
# List Available Content (dry run)
# =============================================================================
async def list_gallery_content(url: str) -> str:
    """List what would be downloaded from a gallery URL."""
    cmd = ["gallery-dl", "-K", url]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            output = stdout.decode().strip()
            # Truncate for Telegram
            if len(output) > 3000:
                output = output[:3000] + "\n... (truncated)"
            return f"```\n{output}\n```"
        else:
            return f"**❌ Error:** `{stderr.decode().strip()[:200]}`"

    except Exception as e:
        return f"**❌ Error:** `{e}`"
