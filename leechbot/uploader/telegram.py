# =============================================================================
# Telegram Leech Bot - Telegram Uploader
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================

"""
Telegram uploader module.

Handles uploading files to Telegram with progress tracking.
"""

import os
import logging
from PIL import Image
from asyncio import sleep
from os import path as ospath
from datetime import datetime
from pyrogram.errors import FloodWait
from pyrogram.types import InputMediaPhoto  # <--- Added for batch upload
from leechbot.utility.variables import BOT, Transfer, BotTimes, Messages, MSG, Paths
from leechbot.utility.helper import sizeUnit, fileType, getTime, status_bar, thumbMaintainer, videoExtFix

logger = logging.getLogger(__name__)


# =============================================================================
# Upload Progress Callback
# =============================================================================
async def progress_bar(current: int, total: int):
    """
    Update upload progress.
    
    Args:
        current: bytes uploaded
        total: total bytes
    """
    elapsed = (datetime.now() - BotTimes.task_start).seconds
    
    if current > 0 and elapsed > 0:
        upload_speed = current / elapsed
    else:
        upload_speed = 4 * 1024 * 1024  # Default 4MB/s
    
    remaining = max(Transfer.total_down_size - current - sum(Transfer.up_bytes), 0)
    eta = remaining / upload_speed if upload_speed > 0 else 0
    percentage = (current + sum(Transfer.up_bytes)) / max(Transfer.total_down_size, 1) * 100
    
    await status_bar(
        down_msg=Messages.status_head,
        speed=f"{sizeUnit(upload_speed)}/s",
        percentage=percentage,
        eta=getTime(eta),
        done=sizeUnit(current + sum(Transfer.up_bytes)),
        left=sizeUnit(Transfer.total_down_size),
        engine="Telegram 📤"
    )


# =============================================================================
# Main Upload Function
# =============================================================================
async def upload_file(file_path: str, real_name: str):
    """
    Upload file to Telegram.
    
    Args:
        file_path: path to file
        real_name: original filename
    """
    global Transfer, MSG
    
    BotTimes.task_start = datetime.now()
    
    # Build styled caption
    caption = f"<{BOT.Options.caption}>{BOT.Setting.prefix} {real_name} {BOT.Setting.suffix}</{BOT.Options.caption}>"
    
    # Determine file type
    type_ = fileType(file_path)
    f_type = type_ if BOT.Options.stream_upload else "document"
    
    try:
        if f_type == "video":
            # Video upload
            if not BOT.Options.stream_upload:
                file_path = videoExtFix(file_path)
            
            thmb_path, seconds = thumbMaintainer(file_path)
            
            with Image.open(thmb_path) as img:
                width, height = img.size
            
            MSG.sent_msg = await MSG.sent_msg.reply_video(
                video=file_path,
                supports_streaming=True,
                width=width,
                height=height,
                caption=caption,
                thumb=thmb_path,
                duration=int(seconds),
                progress=progress_bar,
                reply_to_message_id=MSG.sent_msg.id
            )
        
        elif f_type == "audio":
            # Audio upload
            thmb_path = Paths.THMB_PATH if ospath.exists(Paths.THMB_PATH) else None
            
            MSG.sent_msg = await MSG.sent_msg.reply_audio(
                audio=file_path,
                caption=caption,
                thumb=thmb_path,
                progress=progress_bar,
                reply_to_message_id=MSG.sent_msg.id
            )
        
        elif f_type == "photo":
            # Photo upload (single, kept for backward compatibility)
            MSG.sent_msg = await MSG.sent_msg.reply_photo(
                photo=file_path,
                caption=caption,
                progress=progress_bar,
                reply_to_message_id=MSG.sent_msg.id
            )
        
        else:
            # Document upload
            if ospath.exists(Paths.THMB_PATH):
                thmb_path = Paths.THMB_PATH
            elif type_ == "video":
                thmb_path, _ = thumbMaintainer(file_path)
            else:
                thmb_path = None
            
            MSG.sent_msg = await MSG.sent_msg.reply_document(
                document=file_path,
                caption=caption,
                thumb=thmb_path,
                progress=progress_bar,
                reply_to_message_id=MSG.sent_msg.id
            )
        
        # Track sent files
        Transfer.sent_file.append(MSG.sent_msg)
        Transfer.sent_file_names.append(real_name)
    
    except FloodWait as e:
        logger.warning(f"Flood wait: waiting {e.value} seconds")
        await sleep(e.value)
        await upload_file(file_path, real_name)
    
    except Exception as e:
        logger.error(f"Upload error: {e}")


# =============================================================================
# Batch Photo Upload (New) 29-04-2026
# =============================================================================
async def _batch_progress(current: int, total: int):
    """Progress callback for batch photo uploads — updates status bar."""
    elapsed = max((datetime.now() - BotTimes.task_start).total_seconds(), 0.01)
    speed = current / elapsed if current > 0 else 0
    percentage = (current + sum(Transfer.up_bytes)) / max(Transfer.total_down_size, 1) * 100
    remaining = max(Transfer.total_down_size - current - sum(Transfer.up_bytes), 0)
    eta = remaining / speed if speed > 0 else 0

    await status_bar(
        down_msg=Messages.status_head,
        speed=f"{sizeUnit(speed)}/s",
        percentage=min(percentage, 100),
        eta=getTime(eta),
        done=sizeUnit(current + sum(Transfer.up_bytes)),
        left=sizeUnit(Transfer.total_down_size),
        engine="Telegram 📤",
    )


async def upload_photos_batch(photo_paths: list, remove: bool = False):
    """
    Upload multiple photos in batches of 10 using media groups.

    Each batch upload shows a live progress bar with speed, ETA,
    and percentage via the Pyrogram progress callback.

    Args:
        photo_paths: list of absolute paths to photo files
        remove: whether to remove files after successful upload
    """
    if not photo_paths:
        return

    total_photos = len(photo_paths)
    batch_size = 10
    processed = 0
    i = 0

    while i < total_photos:
        batch = photo_paths[i:i + batch_size]
        media_group = []
        batch_names = []

        for idx, file_path in enumerate(batch):
            real_name = ospath.basename(file_path)
            batch_names.append(real_name)

            # Caption only on first photo of each group
            if idx == 0:
                caption = f"<{BOT.Options.caption}>{BOT.Setting.prefix} {real_name} {BOT.Setting.suffix}</{BOT.Options.caption}>"
            else:
                caption = None  # No caption for subsequent photos per Telegram API

            media_group.append(
                InputMediaPhoto(
                    media=file_path,
                    caption=caption
                )
            )

        try:
            # Calculate batch size for progress tracking
            batch_bytes = 0
            for file_path in batch:
                try:
                    batch_bytes += os.stat(file_path).st_size
                except OSError:
                    pass

            # Update status head for this batch
            batch_label = f"{processed + 1}–{min(processed + batch_size, total_photos)}"
            Messages.status_head = (
                f"**📤 Uploading Photos** `{batch_label}/{total_photos}`\n\n"
            )

            # Send the media group with progress callback
            messages = await MSG.sent_msg.reply_media_group(
                media=media_group,
                progress=_batch_progress,
                reply_to_message_id=MSG.sent_msg.id
            )

            # Update the chaining message to the first of this group
            MSG.sent_msg = messages[0]

            # Track sent files
            Transfer.sent_file.extend(messages)
            Transfer.sent_file_names.extend(batch_names)

            # Track upload bytes for progress
            for file_path in batch:
                try:
                    Transfer.up_bytes.append(os.stat(file_path).st_size)
                except OSError:
                    pass

            # Clean up uploaded files if requested
            if remove:
                for file_path in batch:
                    try:
                        if ospath.exists(file_path):
                            os.remove(file_path)
                    except OSError as e:
                        logger.warning(f"Failed to remove {file_path}: {e}")

            processed += len(batch)
            logger.info(f"Uploaded photo batch {processed}/{total_photos}")
            i += batch_size  # Advance to next batch only on success

        except FloodWait as e:
            logger.warning(f"Flood wait: waiting {e.value} seconds")
            await sleep(e.value)
            # Do NOT advance i — retry the same batch

        except Exception as e:
            logger.error(f"Batch photo upload error: {e}")
            i += batch_size  # Skip failed batch to avoid infinite loop
