# =============================================================================
# Telegram Leech Bot - Bunkr Downloader
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Bunkr.la / Bunkr.ru / Bunkr.si downloader.

Handles album and single file downloads from Bunkr image/video hosting.
"""

import re
import os
import logging
import aiohttp
from os import path as ospath
from leechbot.utility.variables import MSG, Messages, BotTimes, Paths
from leechbot.utility.helper import sizeUnit, getTime, status_bar, sysINFO, keyboard

logger = logging.getLogger(__name__)

BUNKR_DOMAINS = ["bunkr.la", "bunkr.ru", "bunkr.si", "bunkr.is", "bunkr.black"]


async def _get_page(session, url: str) -> str:
    """Fetch a page and return HTML."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    async with session.get(url, headers=headers) as resp:
        return await resp.text()


async def _extract_album_files(html: str) -> list:
    """Extract file URLs from a Bunkr album page."""
    # Bunkr album pages have file cards with links
    # Pattern: href="/f/xxxxx" or href="https://bunkr.xx/f/xxxxx"
    file_links = re.findall(r'href=["\']([^"\']*(?:/f/|/v/)[^"\']*)["\']', html)

    # Deduplicate and make absolute
    seen = set()
    result = []
    for link in file_links:
        if link.startswith("/"):
            # Will be resolved later with domain
            if link not in seen:
                seen.add(link)
                result.append(link)
        elif any(d in link for d in BUNKR_DOMAINS):
            if link not in seen:
                seen.add(link)
                result.append(link)

    return result


async def _get_direct_url(session, page_url: str) -> tuple:
    """Get direct download URL from a Bunkr file page."""
    html = await _get_page(session, page_url)

    # Look for direct download link
    # Bunkr uses CDN URLs like cdn.bunkr.xx/filename.ext
    cdn_match = re.findall(r'href=["\']([^"\']*cdn[^"\']*\.\w{2,4})["\']', html)
    if cdn_match:
        url = cdn_match[0]
        filename = url.split("/")[-1].split("?")[0]
        return url, filename

    # Alternative: look for download button
    dl_match = re.findall(r'href=["\']([^"\']*download[^"\']*)["\']', html)
    if dl_match:
        url = dl_match[0]
        filename = url.split("/")[-1].split("?")[0]
        return url, filename

    # Fallback: look for any direct media link
    media_match = re.findall(r'(https?://[^"\'\s]*\.(?:mp4|mkv|avi|webm|jpg|jpeg|png|gif|webp))', html, re.IGNORECASE)
    if media_match:
        url = media_match[0]
        filename = url.split("/")[-1].split("?")[0]
        return url, filename

    raise Exception("Could not extract direct URL from Bunkr page")


async def _download_file(session, url: str, dest: str, filename: str, file_num: int, total: int):
    """Download a single file with progress."""
    BotTimes.task_start = __import__('datetime').datetime.now()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    async with session.get(url, headers=headers) as resp:
        if resp.status != 200:
            raise Exception(f"HTTP {resp.status}")

        total_size = int(resp.headers.get('content-length', 0))
        downloaded = 0

        Messages.status_head = (
            f"**📥 Bunkr** `{file_num}/{total}`\n\n"
            f"`{filename}`\n"
        )

        with open(dest, 'wb') as f:
            async for chunk in resp.content.iter_chunked(1024 * 1024):
                f.write(chunk)
                downloaded += len(chunk)

                if total_size > 0:
                    pct = (downloaded / total_size) * 100
                    elapsed = max((__import__('datetime').datetime.now() - BotTimes.task_start).total_seconds(), 0.01)
                    speed = downloaded / elapsed
                    remaining = total_size - downloaded
                    eta = remaining / speed if speed > 0 else 0

                    await status_bar(
                        down_msg=Messages.status_head,
                        speed=f"{sizeUnit(speed)}/s",
                        percentage=pct,
                        eta=getTime(eta),
                        done=sizeUnit(downloaded),
                        left=sizeUnit(total_size),
                        engine="Bunkr 🖼️"
                    )


async def bunkr_download(link: str, num: int):
    """
    Download files from Bunkr.

    Supports:
    - Album links: https://bunkr.la/a/xxxxx
    - Single file links: https://bunkr.la/f/xxxxx
    - Direct CDN links

    Args:
        link: Bunkr URL
        num: link number in batch
    """
    os.makedirs(Paths.down_path, exist_ok=True)

    # Detect domain
    domain = None
    for d in BUNKR_DOMAINS:
        if d in link.lower():
            domain = d
            break

    if not domain:
        domain = "bunkr.la"

    async with aiohttp.ClientSession() as session:
        if "/a/" in link:
            # Album page — get all file links
            logger.info(f"Bunkr: downloading album {link[:60]}")
            html = await _get_page(session, link)
            file_paths = await _extract_album_files(html)

            if not file_paths:
                raise Exception("No files found in Bunkr album")

            for idx, file_path in enumerate(file_paths, 1):
                if file_path.startswith("/"):
                    file_url = f"https://{domain}{file_path}"
                else:
                    file_url = file_path

                try:
                    direct_url, filename = await _get_direct_url(session, file_url)
                    dest = ospath.join(Paths.down_path, filename)
                    await _download_file(session, direct_url, dest, filename, idx, len(file_paths))
                except Exception as e:
                    logger.warning(f"Bunkr: failed to download {file_url}: {e}")
                    continue

        elif "/f/" in link or "/v/" in link:
            # Single file page
            logger.info(f"Bunkr: downloading single file {link[:60]}")
            direct_url, filename = await _get_direct_url(session, link)
            dest = ospath.join(Paths.down_path, filename)
            await _download_file(session, direct_url, dest, filename, 1, 1)

        else:
            # Might be a direct CDN link
            filename = link.split("/")[-1].split("?")[0]
            dest = ospath.join(Paths.down_path, filename)
            await _download_file(session, link, dest, filename, 1, 1)

    logger.info(f"Bunkr: download complete")


def is_bunkr(link: str) -> bool:
    """Check if link is a Bunkr URL."""
    lower = link.lower()
    return any(d in lower for d in BUNKR_DOMAINS)
