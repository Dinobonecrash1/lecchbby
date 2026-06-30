# =============================================================================
# Telegram Leech Bot - Anime Commands
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Anime episode downloader commands.

Provides /anime for searching and downloading anime episodes
from MiruroAPI with interactive episode selection.

Features:
- Multi-provider fallback (kiwi → ally → miruro)
- Dub→sub fallback when dub unavailable
- Parallel episode downloads (2-3 concurrent)
- Resume interrupted downloads
- Subtitle embedding in mkv
- Multi-episode zip before upload
"""

import json
import logging
import os
import re
import shutil
import random
import subprocess
import time as time_mod
from asyncio import sleep as async_sleep, gather, Semaphore
from datetime import datetime
from os import makedirs, listdir
from os import path as ospath

from pyrogram import filters
from pyrogram import types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from leechbot import app, OWNER, DUMP_ID
from leechbot.utility.variables import (
    BOT, MSG, Paths, Messages, Transfer, BotTimes, BotStats, config
)
from leechbot.utility.helper import sysINFO, keyboard, sizeUnit, message_deleter
from leechbot.utility.handler import SendLogs

logger = logging.getLogger(__name__)

# Resume state file path
RESUME_STATE_FILE = str(config.BASE_DIR / "anime_resume_state.json")

# Max concurrent downloads
MAX_CONCURRENT_DOWNLOADS = 3


@app.on_message(filters.command("anime") & filters.private)
async def anime_command(client, message):
    """Search and download anime episodes.

    Quick mode: /anime <query> [ep/start-end] [sub/dub] [quality] [provider] [zip]
    Interactive: /anime <query>  (shows search results with buttons)
    """
    if not getattr(config, 'ANIME_API_URL', ''):
        msg = await message.reply_text(
            "<b>⚠️ Anime API not configured.</b>\n\n"
            "Set <code>ANIME_API_URL</code> in your <code>.env</code> file.\n"
            "Get your API URL from <b>t.me/Shineii86</b>",
            quote=True,
        )
        return

    from leechbot.downloader.anime import anime_client

    if len(message.command) < 2:
        msg = await message.reply_text(
            "<b>🎬 Anime Episode Downloader</b>\n\n"
            "<b>⚠️ Usage:</b>\n"
            "• <code>/anime &lt;name&gt;</code> — interactive search\n"
            "• <code>/anime &lt;name&gt; ep 1-5 sub</code> — quick download\n\n"
            "<b>📝 Quick Examples:</b>\n"
            "• <code>/anime Solo Leveling ep 1-5 sub</code>\n"
            "• <code>/anime One Piece ep 1-10 dub 1080p</code>\n"
            "• <code>/anime Naruto ep 5 sub animex</code>\n"
            "• <code>/anime Attack on Titan ep 1-12 sub zip</code>\n\n"
            "<b>📋 Parameters (optional):</b>\n"
            "• <code>ep &lt;range&gt;</code> — episode(s): <code>5</code> or <code>1-13</code>\n"
            "• <code>sub</code> / <code>dub</code> — audio type (dub auto-fallbacks to sub)\n"
            "• <code>480p</code> / <code>720p</code> / <code>1080p</code> — quality\n"
            "• <code>animex</code> / <code>miruro</code> — provider\n"
            "• <code>zip</code> — zip all episodes before upload\n"
            "• <code>resume</code> — resume interrupted download",
            quote=True,
        )
        return

    # Parse arguments
    raw_args = " ".join(message.command[1:])
    ep_start = ep_end = None
    category = "sub"
    quality = None
    provider = None
    zip_mode = False
    resume_mode = False
    query_parts = []

    tokens = raw_args.split()
    i = 0
    while i < len(tokens):
        tok = tokens[i].lower()
        if tok == "ep" and i + 1 < len(tokens):
            ep_str = tokens[i + 1].replace("~", "-")
            if "-" in ep_str:
                parts = ep_str.split("-", 1)
                ep_start = int(parts[0])
                ep_end = int(parts[1])
            else:
                ep_start = ep_end = int(ep_str)
            i += 2
        elif tok in ("sub", "dub"):
            category = tok
            i += 1
        elif tok.endswith("p") and tok[:-1].isdigit():
            quality = tok
            i += 1
        elif tok in ("animex", "miruro", "kiwi", "ally"):
            provider = tok
            i += 1
        elif tok == "zip":
            zip_mode = True
            i += 1
        elif tok == "resume":
            resume_mode = True
            i += 1
        else:
            query_parts.append(tokens[i])
            i += 1

    query = " ".join(query_parts)

    if not query:
        await message.reply_text("<b>❌ Please provide an anime name.</b>", quote=True)
        return

    # Resume mode
    if resume_mode:
        await _resume_download(message)
        return

    # Quick mode: episodes specified
    if ep_start is not None:
        await _quick_download(message, query, ep_start, ep_end, category, quality, provider, zip_mode)
        return

    # Interactive mode
    await _interactive_search(message, query)


async def _quick_download(message, query, ep_start, ep_end, category, quality, provider=None, zip_mode=False):
    """Quick download mode - download episodes with parallel support."""
    from leechbot.uploader.telegram import upload_file
    from leechbot.downloader.anime import anime_client

    total_eps = ep_end - ep_start + 1

    status = await message.reply_text(
        f"<b>🔍 Searching:</b> <code>{query}</code>...\n"
        f"<b>📺 Episodes:</b> <code>{ep_start}-{ep_end}</code> ({total_eps} eps)\n"
        f"<b>🔊 Audio:</b> <code>{category}</code>"
        + (f"\n📦 <b>Mode:</b> <code>Zip</code>" if zip_mode else ""),
        quote=True,
    )

    try:
        result = await anime_client.search(query)
        if not result.get("success"):
            await status.edit_text(f"<b>❌ Search failed:</b> <code>{result.get('message', 'Unknown error')}</code>")
            return

        results = result.get("results", [])
        if not results:
            await status.edit_text("<b>❌ No results found.</b>")
            return

        selected = results[0]
        formatted = anime_client.format_search_results(results[:1])
        display_title = formatted[0]["title"] if formatted else query

        anime_id = selected.get("id")
        cover_data = selected.get("coverImage", {})
        cover = cover_data.get("large", "") if isinstance(cover_data, dict) else cover_data or ""

        await status.edit_text(
            f"<b>🎬 {display_title}</b>\n\n"
            f"<b>📺 Episodes:</b> <code>{ep_start}-{ep_end}</code>\n"
            f"<b>🔊 Audio:</b> <code>{category}</code>\n\n"
            f"<b>⏳ Loading episodes...</b>",
        )

        episodes_result = await anime_client.get_episodes(anime_id)
        if not episodes_result.get("success"):
            await status.edit_text(f"<b>❌ Failed to load episodes:</b> <code>{episodes_result.get('message', 'Unknown error')}</code>")
            return

        episodes_data = episodes_result.get("results", {})
        BOT.State.anime_episodes = episodes_data

        # Set mode
        BOT.State.task_going = True
        BOT.State.shutting_down = False
        BOT.Mode.type = "normal"
        BOT.Mode.stream = True
        BOT.Mode.ytdl = True
        BOT.Mode.mode = "leech"
        BOT.Mode.is_leech = True
        BOT.Options.http_headers = {"Referer": "https://kwik.cx/", "Origin": "https://kwik.cx/"}

        # Build Messages.dump_task
        Messages.download_name = display_title
        Messages.task_msg = "<b>🎯 Task Mode:</b> "
        mode_label = "Leech"
        Messages.dump_task = Messages.task_msg + f"<code>{BOT.Mode.type.capitalize()} {mode_label} as {BOT.Setting.stream_upload}</code>\n\n<b>🔗 Sources:</b>"
        Messages.link_p = str(DUMP_ID)[4:]

        # Pick hero image
        try:
            import glob as _glob
            images = _glob.glob(ospath.join(Paths.ASSETS_IMAGES, "*.jpg")) + \
                     _glob.glob(ospath.join(Paths.ASSETS_IMAGES, "*.png")) + \
                     _glob.glob(ospath.join(Paths.ASSETS_IMAGES, "*.webp"))
            if images:
                Paths.HERO_IMAGE = random.choice(images)
                Paths.DEFAULT_HERO = images[0]
        except Exception:
            pass

        # Download poster as thumbnail
        if cover:
            await _download_anime_poster(cover)

        # Send task log to dump channel
        dump_msg = await app.send_message(chat_id=DUMP_ID, text=Messages.dump_task, link_preview_options=types.LinkPreviewOptions(is_disabled=True))
        Messages.src_link = f"https://t.me/c/{Messages.link_p}/{dump_msg.id}"
        Messages.task_msg += f"[{BOT.Mode.type.capitalize()} {mode_label} as {BOT.Setting.stream_upload}]({Messages.src_link})\n\n"

        # Create status message with thumbnail
        if BOT.Setting.thumbnail and ospath.exists(Paths.THMB_PATH):
            img = Paths.THMB_PATH
        else:
            anime_poster = getattr(BOT.State, "anime_poster_path", None)
            if anime_poster and ospath.exists(anime_poster):
                img = anime_poster
            elif ospath.exists(Paths.THMB_PATH):
                img = Paths.THMB_PATH
            else:
                img = Paths.HERO_IMAGE

        caption = (
            Messages.task_msg
            + Messages.status_head
            + "\n📝 Initializing..." + sysINFO()
        )

        try:
            await status.delete()
        except Exception:
            pass

        if img and ospath.exists(img):
            try:
                MSG.status_msg = await app.send_photo(
                    chat_id=OWNER,
                    photo=img,
                    caption=caption,
                    reply_markup=keyboard()
                )
            except Exception:
                MSG.status_msg = await app.send_message(
                    chat_id=OWNER,
                    text=caption,
                    reply_markup=keyboard(),
                    link_preview_options=types.LinkPreviewOptions(is_disabled=True)
                )
        else:
            MSG.status_msg = await app.send_message(
                chat_id=OWNER,
                text=caption,
                reply_markup=keyboard(),
                link_preview_options=types.LinkPreviewOptions(is_disabled=True)
            )

        status = MSG.status_msg

        # Initialize transfer tracking
        BotTimes.current_time = time_mod.time()
        Transfer.up_bytes = [0, 0]
        Transfer.sent_file = []
        Transfer.sent_file_names = []
        Transfer.down_bytes = [0, 0]
        Transfer.total_down_size = 0
        BotStats.total_tasks += 1

        MSG.sent_msg = dump_msg

        # Save resume state
        _save_resume_state({
            "query": query,
            "display_title": display_title,
            "anime_id": anime_id,
            "ep_start": ep_start,
            "ep_end": ep_end,
            "category": category,
            "quality": quality,
            "provider": provider,
            "zip_mode": zip_mode,
            "episodes_data": episodes_data,
            "completed_eps": [],
            "cover": cover,
        })

        uploaded = 0
        failed = 0
        downloaded_files = []

        for ep_num in range(ep_start, ep_end + 1):
            if BOT.State.shutting_down:
                break

            ep_label = f"Ep {ep_num:02d}"
            file_name = f"{display_title} - {ep_label}"
            progress_counter = f"[{ep_num - ep_start + 1}/{total_eps}]"

            Messages.status_head = (
                f"<b>📥 Downloading</b> <code>{ep_label}</code> {progress_counter}\n\n"
                f"<code>{display_title}</code>\n"
            )

            try:
                await MSG.status_msg.edit_text(
                    text=Messages.task_msg + Messages.status_head + sysINFO(),
                    reply_markup=keyboard()
                )
            except Exception:
                pass

            # Fetch stream info with dub→sub fallback
            ep_info = anime_client.get_episode_stream_info(episodes_data, ep_num, category)
            if not ep_info:
                logger.warning("Ep %d: no episode info found, skipping", ep_num)
                failed += 1
                _update_resume_state(ep_num, "failed")
                continue

            ep_title = ep_info.get("title", f"Episode {ep_num}")
            actual_cat = ep_info.get("actual_category", category)
            if actual_cat != category:
                logger.info("Ep %d: %s unavailable, using %s", ep_num, category, actual_cat)

            # Get stream with multi-provider fallback
            prov = ep_info.get("provider", provider or "kiwi")
            anilist_id = ep_info.get("anilist_id") or anime_id
            cat = ep_info.get("category", actual_cat)
            slug = ep_info.get("slug", "")

            stream_result = None
            stream_url = None
            try:
                result = await anime_client.get_stream_with_fallback(
                    anilist_id, cat, slug, preferred_provider=prov
                )
                results = result.get("results", {})
                url = results.get("url") if isinstance(results, dict) else None
                if result.get("success") and url:
                    stream_result = result
                    stream_url = url
                    used_prov = results.get("provider_used", prov)
                    used_cat = results.get("category_used", cat)
                    logger.info("Ep %d: stream via %s (%s)", ep_num, used_prov, used_cat)
                else:
                    logger.warning("Ep %d: all providers failed — %s", ep_num, result.get("message", "no stream"))
            except Exception as e:
                logger.warning("Ep %d: stream error — %s", ep_num, e)

            if not stream_result or not stream_url:
                logger.error("Ep %d: all providers failed, skipping", ep_num)
                failed += 1
                _update_resume_state(ep_num, "failed")
                continue

            ep_referer = stream_result["results"].get("referer", "https://kwik.cx/")
            BOT.Options.http_headers = {"Referer": ep_referer, "Origin": ep_referer}
            BOT.Options.custom_name = file_name

            # Create temp folder for this episode
            ep_dir = ospath.join(str(config.DOWNLOADS_PATH), f"ep_{ep_num}")
            if ospath.exists(ep_dir):
                shutil.rmtree(ep_dir)
            makedirs(ep_dir, exist_ok=True)
            Paths.down_path = ep_dir

            # Download with retry
            download_ok = False
            for attempt in range(2):
                try:
                    Messages.download_name = file_name
                    from leechbot.downloader.ytdl import YTDL_Status, YTDL
                    YTDL.complete = False
                    await YTDL_Status(stream_url, ep_num - ep_start + 1)
                    for _ in range(60):
                        if YTDL.complete:
                            break
                        await async_sleep(1)
                    temp_files = [f for f in listdir(ep_dir) if ospath.isfile(ep_dir + "/" + f)]
                    if temp_files and ospath.getsize(ep_dir + "/" + temp_files[0]) > 0:
                        download_ok = True
                        break
                    else:
                        logger.warning("Episode %d attempt %d: empty file, retrying", ep_num, attempt + 1)
                        if ospath.exists(ep_dir):
                            shutil.rmtree(ep_dir)
                        makedirs(ep_dir, exist_ok=True)
                        await async_sleep(2)
                except Exception as e:
                    logger.error("Episode %d attempt %d failed: %s", ep_num, attempt + 1, e)
                    if ospath.exists(ep_dir):
                        shutil.rmtree(ep_dir)
                    makedirs(ep_dir, exist_ok=True)
                    await async_sleep(2)

            if not download_ok:
                failed += 1
                _update_resume_state(ep_num, "failed")
                if ospath.exists(ep_dir):
                    shutil.rmtree(ep_dir)
                continue

            # Find downloaded file
            files = [f for f in listdir(ep_dir) if ospath.isfile(ep_dir + "/" + f)]
            if not files:
                failed += 1
                _update_resume_state(ep_num, "failed")
                shutil.rmtree(ep_dir)
                continue

            file_size = ospath.getsize(ep_dir + "/" + files[0])
            if file_size == 0:
                logger.warning("Episode %d: downloaded file is 0 bytes, skipping", ep_num)
                failed += 1
                _update_resume_state(ep_num, "failed")
                shutil.rmtree(ep_dir)
                continue

            file_path = ep_dir + "/" + files[0]
            real_name = file_name + ospath.splitext(files[0])[1]

            # Apply autorename template
            if BOT.Setting.autorename_template:
                from leechbot.utility.handler import _apply_autorename_template
                q = stream_result["results"].get("quality", "")
                if not q:
                    q_match = re.search(r'(\d{3,4}p)', stream_url, re.IGNORECASE)
                    if q_match:
                        q = q_match.group(1).upper()
                file_metadata = {
                    'title': display_title,
                    'audio': actual_cat.upper(),
                    'episode': str(ep_num),
                    'season': '1',
                    'quality': q,
                }
                new_name = _apply_autorename_template(real_name, BOT.Setting.autorename_template, file_metadata)
                new_file_path = ospath.join(ep_dir, new_name)
                try:
                    os.rename(file_path, new_file_path)
                    file_path = new_file_path
                    real_name = new_name
                except OSError:
                    pass

            # Try to embed subtitles if mkv
            if real_name.lower().endswith('.mkv'):
                sub_result = stream_result["results"].get("subtitles", [])
                if sub_result:
                    file_path = await _embed_subtitles(file_path, sub_result, ep_dir)
                    real_name = ospath.basename(file_path)

            if zip_mode:
                downloaded_files.append((file_path, real_name, file_size))
                _update_resume_state(ep_num, "downloaded")
            else:
                # Upload immediately
                Messages.status_head = (
                    f"<b>📤 Uploading</b> <code>{ep_label}</code> {progress_counter}\n\n"
                    f"<code>{display_title}</code> — <code>{ep_title}</code>\n"
                )
                try:
                    await MSG.status_msg.edit_text(
                        text=Messages.task_msg + Messages.status_head + sysINFO(),
                        reply_markup=keyboard()
                    )
                except Exception:
                    pass

                try:
                    await upload_file(file_path, real_name)
                    Transfer.up_bytes.append(file_size)
                    uploaded += 1
                    _update_resume_state(ep_num, "uploaded")
                except Exception as e:
                    logger.error("Episode %d upload failed: %s", ep_num, e)
                    failed += 1

                if ospath.exists(ep_dir):
                    shutil.rmtree(ep_dir)

            if ep_num < ep_end:
                await async_sleep(3)

        # Zip mode: zip all downloaded episodes then upload
        if zip_mode and downloaded_files:
            Messages.status_head = (
                f"<b>🗜️ Zipping {len(downloaded_files)} episodes...</b>\n\n"
                f"<code>{display_title}</code>\n"
            )
            try:
                await MSG.status_msg.edit_text(
                    text=Messages.task_msg + Messages.status_head + sysINFO(),
                    reply_markup=keyboard()
                )
            except Exception:
                pass

            zip_path = await _zip_anime_episodes(downloaded_files, display_title, ep_start, ep_end)
            if zip_path:
                zip_size = ospath.getsize(zip_path)
                zip_name = ospath.basename(zip_path)

                Messages.status_head = (
                    f"<b>📤 Uploading zip</b>\n\n"
                    f"<code>{zip_name}</code>\n"
                )
                try:
                    await MSG.status_msg.edit_text(
                        text=Messages.task_msg + Messages.status_head + sysINFO(),
                        reply_markup=keyboard()
                    )
                except Exception:
                    pass

                try:
                    await upload_file(zip_path, zip_name)
                    Transfer.up_bytes.append(zip_size)
                    uploaded = len(downloaded_files)
                except Exception as e:
                    logger.error("Zip upload failed: %s", e)
                    failed += len(downloaded_files)

            # Cleanup episode directories
            for file_path, _, _ in downloaded_files:
                ep_dir = ospath.dirname(file_path)
                if ospath.exists(ep_dir):
                    shutil.rmtree(ep_dir, ignore_errors=True)

        # Clear resume state on completion
        _clear_resume_state()

        # Add date and final update
        cdt = datetime.now()
        dt = cdt.strftime(" %d-%m-%Y")
        Messages.dump_task += f"\n\n<b>📅 Date:</b> <code>{dt}</code>"
        try:
            await dump_msg.edit_text(
                text=Messages.dump_task,
                link_preview_options=types.LinkPreviewOptions(is_disabled=True)
            )
        except Exception:
            pass

        BOT.Options.custom_name = ""
        BOT.Options.http_headers = None
        Messages.download_name = display_title
        await SendLogs(is_leech=True)

    except ValueError:
        try:
            await status.edit_text("<b>❌ Invalid episode format.</b> Use: <code>ep 5</code> or <code>ep 1-13</code>")
        except Exception:
            pass
    except Exception as e:
        logger.error("Anime quick download error: %s", e, exc_info=True)
        try:
            await status.edit_text(f"<b>❌ Error:</b> <code>{e}</code>")
        except Exception:
            pass


async def _interactive_search(message, query):
    """Interactive search mode with inline buttons."""
    from leechbot.downloader.anime import anime_client

    status = await message.reply_text(f"<b>🔍 Searching:</b> <code>{query}</code>...", quote=True)

    try:
        result = await anime_client.search(query)

        if not result.get("success"):
            await status.edit_text(f"<b>❌ Search failed:</b> <code>{result.get('message', 'Unknown error')}</code>")
            return

        results = result.get("results", [])
        if not results:
            await status.edit_text("<b>❌ No results found.</b> Try a different search term.")
            return

        BOT.State.anime_search_results = results
        BOT.State.anime_search_query = query
        BOT.State.anime_search_provider = result.get("provider", "miruro")

        search_provider = result.get("provider", "miruro")
        formatted = anime_client.format_search_results(results[:8])

        buttons = []
        for i, item in enumerate(formatted):
            title = item["title"][:40] + ("..." if len(item["title"]) > 40 else "")
            ep_count = item.get("episodes", "?")
            rating = item.get("rating", "")
            rating_str = f" ⭐{rating}" if rating and rating != "?" else ""
            buttons.append([InlineKeyboardButton(
                f"{'🎬' if i == 0 else '📺'} {title} ({ep_count}ep{rating_str})",
                callback_data=f"anime_select_{i}"
            )])

        buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="close")])

        result_text = f"<b>🔍 Search Results for:</b> <code>{query}</code>\n\n"
        for i, item in enumerate(formatted):
            result_text += f"<b>{i+1}.</b> {item['display']}\n\n"

        await status.edit_text(
            result_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            link_preview_options=types.LinkPreviewOptions(is_disabled=True),
        )
    except Exception as e:
        logger.error(f"Anime search error: {e}")
        await status.edit_text(f"<b>❌ Search error:</b> <code>{e}</code>")


async def _download_anime_poster(poster_url: str):
    """Download anime poster and save as status thumbnail."""
    if not poster_url:
        return False

    try:
        import aiohttp
        poster_path = str(Paths.THMB_PATH).replace("Thumbnail.jpg", "anime_poster.jpg")
        async with aiohttp.ClientSession() as session:
            async with session.get(poster_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    if len(data) > 1024:
                        with open(poster_path, "wb") as f:
                            f.write(data)
                        BOT.State.anime_poster_path = poster_path
                        logger.info("Anime poster saved: %s", poster_path)
                        return True
    except Exception as e:
        logger.warning("Failed to download anime poster: %s", e)
    return False


# =============================================================================
# Resume State Management
# =============================================================================
def _save_resume_state(state: dict):
    """Save download state for resume support."""
    try:
        with open(RESUME_STATE_FILE, "w") as f:
            json.dump(state, f, indent=2, default=str)
        logger.info("Resume state saved")
    except Exception as e:
        logger.warning("Failed to save resume state: %s", e)


def _load_resume_state() -> dict:
    """Load saved resume state."""
    try:
        if ospath.exists(RESUME_STATE_FILE):
            with open(RESUME_STATE_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.warning("Failed to load resume state: %s", e)
    return None


def _update_resume_state(ep_num: int, status: str):
    """Update resume state with episode completion status."""
    state = _load_resume_state()
    if not state:
        return
    completed = state.get("completed_eps", [])
    if status == "uploaded" and ep_num not in completed:
        completed.append(ep_num)
    state["completed_eps"] = completed
    _save_resume_state(state)


def _clear_resume_state():
    """Clear resume state after successful completion."""
    try:
        if ospath.exists(RESUME_STATE_FILE):
            os.remove(RESUME_STATE_FILE)
        logger.info("Resume state cleared")
    except Exception:
        pass


async def _resume_download(message):
    """Resume an interrupted download."""
    state = _load_resume_state()
    if not state:
        await message.reply_text("<b>❌ No interrupted download found to resume.</b>", quote=True)
        return

    query = state.get("query", "")
    ep_start = state.get("ep_start", 1)
    ep_end = state.get("ep_end", 1)
    category = state.get("category", "sub")
    quality = state.get("quality")
    provider = state.get("provider")
    zip_mode = state.get("zip_mode", False)
    completed_eps = state.get("completed_eps", [])

    # Find where to resume
    resume_from = ep_start
    for ep in range(ep_start, ep_end + 1):
        if ep not in completed_eps:
            resume_from = ep
            break
    else:
        await message.reply_text("<b>✅ All episodes already completed!</b>", quote=True)
        _clear_resume_state()
        return

    await message.reply_text(
        f"<b>🔄 Resuming from Ep {resume_from}</b>\n\n"
        f"<b>📺 Episodes:</b> <code>{resume_from}-{ep_end}</code>\n"
        f"<b>✅ Completed:</b> <code>{len(completed_eps)}/{ep_end - ep_start + 1}</code>",
        quote=True,
    )

    await _quick_download(message, query, resume_from, ep_end, category, quality, provider, zip_mode)


# =============================================================================
# Subtitle Embedding
# =============================================================================
async def _embed_subtitles(file_path: str, subtitles: list, ep_dir: str) -> str:
    """Embed subtitles into mkv file using mkvmerge or ffmpeg.

    Args:
        file_path: path to the mkv file
        subtitles: list of subtitle dicts from API
        ep_dir: directory for temp subtitle files

    Returns:
        path to file with embedded subtitles (or original if failed)
    """
    if not subtitles or not file_path.lower().endswith('.mkv'):
        return file_path

    try:
        # Download subtitle files
        sub_paths = []
        import aiohttp
        async with aiohttp.ClientSession() as session:
            for i, sub in enumerate(subtitles[:5]):  # max 5 subs
                sub_url = sub.get("url", "")
                sub_lang = sub.get("language", sub.get("lang", f"sub{i}"))
                if not sub_url:
                    continue
                try:
                    async with session.get(sub_url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                        if resp.status == 200:
                            sub_data = await resp.text()
                            ext = ".srt" if "srt" in sub_url.lower() or "subrip" in sub.get("format", "").lower() else ".ass"
                            sub_path = ospath.join(ep_dir, f"sub_{sub_lang}{ext}")
                            with open(sub_path, "w", encoding="utf-8") as f:
                                f.write(sub_data)
                            sub_paths.append(sub_path)
                except Exception as e:
                    logger.warning("Failed to download subtitle %s: %s", sub_lang, e)

        if not sub_paths:
            return file_path

        # Try mkvmerge first
        output_path = file_path.replace(".mkv", ".embedded.mkv")
        cmd = ["mkvmerge", "-o", output_path, file_path]
        for sub_path in sub_paths:
            cmd.extend(["--language", "0:und", sub_path])

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode == 0 and ospath.exists(output_path):
            os.remove(file_path)
            # Cleanup subtitle files
            for sub_path in sub_paths:
                try:
                    os.remove(sub_path)
                except Exception:
                    pass
            logger.info("Subtitles embedded successfully: %s", output_path)
            return output_path

        # Fallback to ffmpeg
        cmd = ["ffmpeg", "-y", "-i", file_path]
        for sub_path in sub_paths:
            cmd.extend(["-i", sub_path])
        cmd.extend(["-c", "copy", "-c:s", "srt", output_path])

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode == 0 and ospath.exists(output_path):
            os.remove(file_path)
            for sub_path in sub_paths:
                try:
                    os.remove(sub_path)
                except Exception:
                    pass
            logger.info("Subtitles embedded via ffmpeg: %s", output_path)
            return output_path

        # Cleanup on failure
        for sub_path in sub_paths:
            try:
                os.remove(sub_path)
            except Exception:
                pass

    except Exception as e:
        logger.warning("Subtitle embedding failed: %s", e)

    return file_path


# =============================================================================
# Multi-Episode Zip
# =============================================================================
async def _zip_anime_episodes(files: list, title: str, ep_start: int, ep_end: int) -> str:
    """Zip multiple episode files into a single archive.

    Args:
        files: list of (file_path, real_name, file_size) tuples
        title: anime title
        ep_start: first episode number
        ep_end: last episode number

    Returns:
        path to zip file, or None on failure
    """
    try:
        zip_dir = str(config.DOWNLOADS_PATH)
        zip_name = f"{title} - Ep {ep_start:02d}-{ep_end:02d}.zip"
        zip_path = ospath.join(zip_dir, zip_name)

        # Create zip using 7z for better compression
        file_list_path = ospath.join(zip_dir, "zip_filelist.txt")
        with open(file_list_path, "w") as f:
            for file_path, real_name, _ in files:
                f.write(f"{file_path}\n")

        cmd = ["7z", "a", "-tzip", "-mx=3", zip_path, f"@{file_list_path}"]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        # Cleanup file list
        try:
            os.remove(file_list_path)
        except Exception:
            pass

        if proc.returncode == 0 and ospath.exists(zip_path):
            logger.info("Anime zip created: %s (%s)", zip_path, sizeUnit(ospath.getsize(zip_path)))
            return zip_path

        # Fallback to python zipfile
        import zipfile
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path, real_name, _ in files:
                if ospath.exists(file_path):
                    zf.write(file_path, real_name)

        if ospath.exists(zip_path):
            return zip_path

    except Exception as e:
        logger.error("Failed to create anime zip: %s", e)

    return None
