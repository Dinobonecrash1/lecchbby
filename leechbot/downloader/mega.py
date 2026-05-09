# =============================================================================
# Telegram Leech Bot - Mega.nz Downloader
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================

"""
Mega.nz downloader module.

Handles downloads from Mega.nz using megatools CLI.
"""

import os
import re
import asyncio
import logging
from datetime import datetime

from leechbot.utility.helper import sizeUnit, status_bar
from leechbot.utility.variables import BotTimes, Messages, Paths, Transfer

logger = logging.getLogger(__name__)


# =============================================================================
# Check megatools availability
# =============================================================================
def _check_megadl():
    """Raise a clear error if megatools is not installed."""
    import shutil
    if shutil.which("megadl") is None:
        raise ImportError(
            "megatools is not installed. Install it via:\n"
            "  • Debian/Ubuntu: sudo apt install megatools\n"
            "  • Arch:          sudo pacman -S megatools\n"
            "  • macOS:         brew install megatools"
        )


# =============================================================================
# Parse megadl progress output
# =============================================================================
_PROGRESS_RE = re.compile(
    r"([\d.]+)\s*%\s+"           # percentage
    r"([\d.]+\s*[KMG]?i?B)\s+"  # downloaded size
    r"([\d.]+\s*[KMG]?i?B)\s+"  # total size
    r"([\d.]+\s*[KMG]?i?B/s)"   # speed
)

FILENAME_RE = re.compile(r"^(.+?):\s+")

def _parse_progress(line: str):
    """Parse megadl output line into (name, percent, downloaded, total, speed) or None."""
    line = line.strip()
    if not line:
        return None

    m = _PROGRESS_RE.search(line)
    if not m:
        return None

    name_match = _FILENAME_RE.match(line)
    name = name_match.group(1).strip() if name_match else "Mega Download"

    return {
        "name": name,
        "percent": round(float(m.group(1))),
        "downloaded": m.group(2),
        "total": m.group(3),
        "speed": m.group(4),
    }


# =============================================================================
# Main Download Function
# =============================================================================
async def megadl(link: str, num: int):
    """
    Download file from Mega.nz via megatools CLI.

    Args:
        link: Mega.nz share link
        num: link number for display
    """
    _check_megadl()
    BotTimes.task_start = datetime.now()

    save_path = str(Paths.down_path)

    # Build megadl command
    command = [
        "megadl",
        "--no-ask-password",
        "--path", save_path,
        link,
    ]

    logger.info(f"Starting Mega download: {link[:80]}")

    # Launch as async subprocess — does NOT block the event loop
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    downloaded_files = []
    last_update = 0.0

    try:
        while True:
            raw = await asyncio.wait_for(process.stdout.readline(), timeout=600)
            if not raw:
                break

            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue

            info = _parse_progress(line)
            if info:
                Messages.download_name = info["name"]
                Messages.status_head = (
                    f"**📥 Downloading** `Link {str(num).zfill(2)}`\n\n"
                    f"**🏷️ Name:** `{info['name']}`\n"
                )

                now = asyncio.get_event_loop().time()
                if now - last_update >= 2:  # throttle UI updates
                    await status_bar(
                        Messages.status_head,
                        info["speed"],
                        info["percent"],
                        "Calculating...",
                        info["downloaded"],
                        info["total"],
                        "Mega 💾",
                    )
                    last_update = now

            # Collect file paths from output
            if "downloaded successfully" in line.lower() or "saved to" in line.lower():
                logger.info(f"Mega: {line}")

        await process.wait()

    except asyncio.TimeoutError:
        process.kill()
        raise TimeoutError("Mega download timed out (no output for 10 minutes)")

    if process.returncode != 0:
        raise RuntimeError(f"megadl exited with code {process.returncode}")

    # Find downloaded files in save_path
    for f in os.listdir(save_path):
        full = os.path.join(save_path, f)
        if os.path.isfile(full):
            mtime = os.path.getmtime(full)
            if mtime >= BotTimes.task_start.timestamp():
                downloaded_files.append(full)

    if not downloaded_files:
        # Fallback: list all files
        downloaded_files = [
            os.path.join(save_path, f)
            for f in os.listdir(save_path)
            if os.path.isfile(os.path.join(save_path, f))
        ]

    if downloaded_files:
        Transfer.download_path = save_path
        logger.info(f"Mega download complete: {len(downloaded_files)} file(s)")
    else:
        logger.warning("Mega: no downloaded files found in save path")

    return downloaded_files
