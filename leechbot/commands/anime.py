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
"""

import logging
import os
import re
import shutil
import random
import time as time_mod
from asyncio import sleep as async_sleep
from datetime import datetime
from os import makedirs, listdir
from os import path as ospath

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from leechbot import app, OWNER, DUMP_ID
from leechbot.utility.variables import (
    BOT, MSG, Paths, Messages, Transfer, BotTimes, BotStats, config
)
from leechbot.utility.helper import sysINFO, keyboard, sizeUnit, message_deleter
from leechbot.utility.handler import SendLogs

logger = logging.getLogger(__name__)


@app.on_message(filters.command("anime") & filters.private)
async def anime_command(client, message):
    """Search and download anime episodes.

    Quick mode: /anime <query> [ep/start-end] [sub/dub] [quality] [provider]
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
            "• <code>/anime Naruto ep 5 sub animex</code>\n\n"
            "<b>📋 Parameters (optional):</b>\n"
            "• <code>ep &lt;range&gt;</code> — episode(s): <code>5</code> or <code>1-13</code>\n"
            "• <code>sub</code> / <code>dub</code> — audio type\n"
            "• <code>480p</code> / <code>720p</code> / <code>1080p</code> — quality\n"
            "• <code>animex</code> / <code>miruro</code> — provider\n",
            quote=True,
        )
        return

    # Parse arguments
    raw_args = " ".join(message.command[1:])
    ep_start = ep_end = None
    category = "sub"
    quality = None
    provider = None
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
        elif tok in ("animex", "miruro"):
            provider = tok
            i += 1
        else:
            query_parts.append(tokens[i])
            i += 1

    query = " ".join(query_parts)

    if not query:
        await message.reply_text("<b>❌ Please provide an anime name.</b>", quote=True)
        return

    # Quick mode: episodes specified
    if ep_start is not None:
        await _quick_download(message, query, ep_start, ep_end, category, quality)
        return

    # Interactive mode
    await _interactive_search(message, query)


async def _quick_download(message, query, ep_start, ep_end, category, quality):
    """Quick download mode - download 1, upload 1, repeat."""
    from leechbot.uploader.telegram import upload_file
    from leechbot.downloader.anime import anime_client

    status = await message.reply_text(
        f"<b>🔍 Searching:</b> <code>{query}</code>...\n"
        f"<b>📺 Episodes:</b> <code>{ep_start}-{ep_end}</code>\n"
        f"<b>🔊 Audio:</b> <code>{category}</code>",
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
        dump_msg = await app.send_message(chat_id=DUMP_ID, text=Messages.dump_task, disable_web_page_preview=True)
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
                    disable_web_page_preview=True
                )
        else:
            MSG.status_msg = await app.send_message(
                chat_id=OWNER,
                text=caption,
                reply_markup=keyboard(),
                disable_web_page_preview=True
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

        uploaded = 0
        failed = 0

        for ep_num in range(ep_start, ep_end + 1):
            if BOT.State.shutting_down:
                break

            ep_label = f"Ep {ep_num:02d}"
            file_name = f"{display_title} - {ep_label}"

            Messages.status_head = (
                f"<b>📥 Downloading</b> <code>{ep_label}</code>\n\n"
                f"<code>{display_title}</code>\n"
            )

            try:
                await MSG.status_msg.edit_text(
                    text=Messages.task_msg + Messages.status_head + sysINFO(),
                    reply_markup=keyboard()
                )
            except Exception:
                pass

            # Fetch stream URL
            ep_info = anime_client.miruro.get_episode_stream_info(episodes_list, ep_num, category)
            if not ep_info:
                logger.warning("Ep %d: no episode info found, skipping", ep_num)
                failed += 1
                continue

            # Use the provider/slug from episode info
            prov = ep_info.get("provider", "kiwi")
            anilist_id = ep_info.get("anilist_id") or anime_id
            cat = ep_info.get("category", category)
            slug = ep_info.get("slug", "")

            stream_result = None
            stream_url = None
            try:
                result = await anime_client.get_stream(prov, anilist_id, cat, slug)
                if result.get("success") and result.get("results", {}).get("url"):
                    stream_result = result
                    stream_url = result["results"]["url"]
                    logger.info("Ep %d: stream found via %s", ep_num, prov)
                else:
                    logger.warning("Ep %d: provider %s failed — %s", ep_num, prov, result.get("message", "no stream"))
            except Exception as e:
                logger.warning("Ep %d: provider %s error — %s", ep_num, prov, e)

            if not stream_result or not stream_url:
                logger.error("Ep %d: provider %s failed, skipping", ep_num, prov)
                failed += 1
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
                if ospath.exists(ep_dir):
                    shutil.rmtree(ep_dir)
                continue

            # Find downloaded file
            files = [f for f in listdir(ep_dir) if ospath.isfile(ep_dir + "/" + f)]
            if not files:
                failed += 1
                shutil.rmtree(ep_dir)
                continue

            file_size = ospath.getsize(ep_dir + "/" + files[0])
            if file_size == 0:
                logger.warning("Episode %d: downloaded file is 0 bytes, skipping", ep_num)
                failed += 1
                shutil.rmtree(ep_dir)
                continue
            Transfer.total_down_size = file_size

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
                    'audio': category.upper(),
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

            # Update status to show uploading
            Messages.status_head = (
                f"<b>📤 Uploading</b> <code>{ep_label}</code>\n\n"
                f"<code>{display_title}</code>\n"
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
            except Exception as e:
                logger.error("Episode %d upload failed: %s", ep_num, e)
                failed += 1

            if ospath.exists(ep_dir):
                shutil.rmtree(ep_dir)

            if ep_num < ep_end:
                await async_sleep(3)

        # Add date and final update
        cdt = datetime.now()
        dt = cdt.strftime(" %d-%m-%Y")
        Messages.dump_task += f"\n\n<b>📅 Date:</b> <code>{dt}</code>"
        try:
            await dump_msg.edit_text(
                text=Messages.dump_task,
                disable_web_page_preview=True
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
        logger.error(f"Anime quick download error: {e}")
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
            buttons.append([InlineKeyboardButton(
                f"{'🎬' if i == 0 else '📺'} {title}",
                callback_data=f"anime_select_{i}"
            )])

        buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="close")])

        result_text = f"<b>🔍 Search Results for:</b> <code>{query}</code>\n\n"
        for i, item in enumerate(formatted):
            result_text += f"<b>{i+1}.</b> {item['display']}\n\n"

        await status.edit_text(
            result_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
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
