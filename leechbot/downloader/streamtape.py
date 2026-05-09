# =============================================================================
# Telegram Leech Bot - StreamTape Downloader
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
StreamTape.com video downloader.

Extracts direct download links from StreamTape embed pages.
"""

import re
import logging
import aiohttp
from os import path as ospath
from leechbot.utility.variables import Paths

logger = logging.getLogger(__name__)


async def _extract_download_url(page_url: str) -> tuple:
    """
    Extract direct download URL from StreamTape page.

    Returns: (download_url, filename)
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(page_url) as resp:
            html = await resp.text()

    # StreamTape uses JavaScript to construct the download URL
    # Pattern: ('robotlink') + '/<hash>' or similar obfuscated patterns
    # Try multiple extraction methods

    # Method 1: Direct link pattern in page source
    dl_match = re.search(r"getElementById\('norobotlink'\)\.href\s*=\s*['\"]([^'\"]+)", html)
    if dl_match:
        url = dl_match.group(1)
        if url.startswith("//"):
            url = "https:" + url

    # Method 2: Token-based extraction
    if not dl_match:
        token_match = re.search(r"token=([a-zA-Z0-9_]+)", html)
        if token_match:
            token = token_match.group(1)
            url = f"https://streamtape.com/get_video?id={token}"

    # Method 3: Obfuscated link construction
    if not dl_match:
        parts = re.findall(r"(/\d+/[^'\"]+)", html)
        if parts:
            url = "https://streamtape.com" + parts[-1]

    # Extract filename from page
    title_match = re.search(r'<title>([^<]+)</title>', html)
    filename = title_match.group(1).strip() if title_match else "streamtape_video"
    filename = re.sub(r'[^\w\s\-.]', '', filename).strip()
    if not filename.endswith(('.mp4', '.mkv', '.avi', '.webm')):
        filename += '.mp4'

    return url, filename


async def streamtape_download(link: str, num: int):
    """
    Download video from StreamTape.

    Args:
        link: StreamTape URL
        num: link number in batch
    """
    from leechbot.downloader.aria2 import aria2_Download

    logger.info(f"StreamTape: extracting from {link[:60]}")

    try:
        url, filename = await _extract_download_url(link)
        logger.info(f"StreamTape: direct URL extracted, downloading via aria2c")

        # Use aria2c for the actual download (resumable, multi-connection)
        # We pass the direct URL to aria2c
        import subprocess
        from leechbot.utility.variables import Messages, BotTimes
        from leechbot.utility.helper import sizeUnit, getTime, status_bar, sysINFO, keyboard

        dest = ospath.join(Paths.down_path, filename)
        Messages.status_head = f"**📥 StreamTape** `{num}`\n\n`{filename}`\n"

        # Use aria2c for reliable download
        cmd = [
            "aria2c", "--dir=" + Paths.down_path,
            "--out=" + filename,
            "--max-connection-per-server=16",
            "--split=16",
            "--continue=true",
            "--summary-interval=0",
            "--console-log-level=error",
            url
        ]

        proc = await __import__('asyncio').create_subprocess_exec(
            *cmd,
            stdout=__import__('asyncio').subprocess.PIPE,
            stderr=__import__('asyncio').subprocess.PIPE
        )
        await proc.communicate()

        if proc.returncode != 0:
            raise Exception(f"aria2c failed with code {proc.returncode}")

        logger.info(f"StreamTape: downloaded {filename}")

    except Exception as e:
        logger.error(f"StreamTape download failed: {e}")
        raise


def is_streamtape_link(link: str) -> bool:
    """Check if link is a StreamTape URL."""
    lower = link.lower()
    return "streamtape" in lower or "stape." in lower
