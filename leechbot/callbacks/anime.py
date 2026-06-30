# =============================================================================
# Telegram Leech Bot - Anime Callback Handlers
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Anime episode selection callback handlers.

Handles inline keyboard callbacks for anime search results,
episode selection, category (sub/dub) toggle, and download.
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

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from leechbot import app, OWNER, DUMP_ID
from leechbot.utility.variables import (
    BOT, MSG, Paths, Messages, Transfer, BotTimes, BotStats, config
)
from leechbot.utility.helper import sysINFO, keyboard, sizeUnit
from leechbot.utility.handler import SendLogs

logger = logging.getLogger(__name__)


async def safe_answer(callback_query, text="", show_alert=False):
    """Safely answer callback query."""
    try:
        await callback_query.answer(text=text, show_alert=show_alert)
    except Exception:
        pass


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


async def _handle_anime_select(client, callback_query, data: str):
    """Handle anime selection from search results."""
    from leechbot.downloader.anime import anime_client

    try:
        index = int(data.replace("anime_select_", ""))
        results = BOT.State.anime_search_results
        provider = BOT.State.anime_search_provider

        if index >= len(results):
            await safe_answer(callback_query, "Invalid selection", show_alert=True)
            return

        selected = results[index]
        BOT.State.anime_selected = selected

        anime_id = selected.get("id")
        title_data = selected.get("title", {})
        if isinstance(title_data, dict):
            title = selected.get("display_title") or title_data.get("english") or title_data.get("romaji") or "Unknown"
        else:
            title = selected.get("display_title") or title_data or "Unknown"
        cover_data = selected.get("coverImage", {})
        cover = cover_data.get("large", "") if isinstance(cover_data, dict) else cover_data or ""
        episodes = selected.get("episodes", "?")

        BOT.State.anime_selected["provider"] = provider
        BOT.State.anime_selected["anime_id"] = anime_id
        BOT.State.anime_selected["title"] = title
        BOT.State.anime_selected["cover"] = cover
        BOT.State.anime_selected["total_episodes"] = episodes

        await callback_query.message.edit_text(
            f"<b>🎬 Loading episodes for:</b> <code>{title}</code>...",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="close")]])
        )

        episodes_result = await anime_client.get_episodes(anime_id)

        if not episodes_result.get("success"):
            await callback_query.message.edit_text(
                f"<b>❌ Failed to load episodes:</b> <code>{episodes_result.get('message', 'Unknown error')}</code>"
            )
            return

        episodes_data = episodes_result.get("results", {})
        BOT.State.anime_episodes = episodes_data

        total_episodes = 0
        providers = episodes_data.get("providers", {})
        for prov_data in providers.values():
            for cat in ["sub", "dub"]:
                total_episodes = max(total_episodes, len(prov_data.get("episodes", {}).get(cat, [])))

        if total_episodes == 0:
            await callback_query.message.edit_text(
                f"<b>❌ No episodes found for:</b> <code>{title}</code>"
            )
            return

        buttons = []
        category = BOT.State.anime_selected.get("category", "sub")
        buttons.append([
            InlineKeyboardButton(f"{'✅ ' if category == 'sub' else ''}🇯🇵 Sub", callback_data="anime_cat_sub"),
            InlineKeyboardButton(f"{'✅ ' if category == 'dub' else ''}🇺🇸 Dub", callback_data="anime_cat_dub"),
        ])

        if total_episodes <= 25:
            row = []
            for ep in range(1, total_episodes + 1):
                row.append(InlineKeyboardButton(f"{ep}", callback_data=f"anime_ep_{ep}_{ep}"))
                if len(row) == 5:
                    buttons.append(row)
                    row = []
            if row:
                buttons.append(row)
            buttons.append([InlineKeyboardButton(
                f"⬇️ Download All (1-{total_episodes})",
                callback_data=f"anime_dl_1_{total_episodes}"
            )])
        elif total_episodes <= 100:
            for start in range(1, total_episodes + 1, 12):
                end = min(start + 11, total_episodes)
                buttons.append([
                    InlineKeyboardButton(
                        f"📺 Ep {start}-{end}",
                        callback_data=f"anime_ep_{start}_{end}"
                    )
                ])
        else:
            for start in range(1, min(total_episodes + 1, 600), 24):
                end = min(start + 23, total_episodes)
                buttons.append([
                    InlineKeyboardButton(
                        f"📺 Ep {start}-{end}",
                        callback_data=f"anime_ep_{start}_{end}"
                    )
                ])
            if total_episodes > 600:
                buttons.append([InlineKeyboardButton(
                    f"... and {total_episodes - 600} more episodes",
                    callback_data="close"
                )])

        buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="close")])

        await callback_query.message.edit_text(
            f"<b>🎬 {title}</b>\n\n"
            f"<b>📺 Total Episodes:</b> <code>{total_episodes}</code>\n\n"
            f"<b>Select category and episode range:</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
        )

        await safe_answer(callback_query, f"Selected: {title}")

    except Exception as e:
        logger.error("Anime select error: %s", e)
        await callback_query.message.edit_text(f"<b>❌ Error:</b> <code>{e}</code>")


async def _handle_anime_episode(client, callback_query, data: str):
    """Handle episode selection."""
    try:
        parts = data.replace("anime_ep_", "").split("_")
        start_ep = int(parts[0])
        end_ep = int(parts[1])

        BOT.State.anime_selected["episode_range"] = (start_ep, end_ep)

        title = BOT.State.anime_selected.get("title", "Unknown")
        category = BOT.State.anime_selected.get("category", "sub")
        category_label = "🇯🇵 Sub" if category == "sub" else "🇺🇸 Dub"

        ep_label = f"Ep {start_ep}" if start_ep == end_ep else f"Ep {start_ep}-{end_ep}"
        buttons = [
            [InlineKeyboardButton(
                f"⬇️ Download {ep_label}",
                callback_data=f"anime_dl_{start_ep}_{end_ep}"
            )],
            [
                InlineKeyboardButton(
                    f"{'✅ ' if category == 'sub' else ''}🇯🇵 Sub",
                    callback_data="anime_cat_sub"
                ),
                InlineKeyboardButton(
                    f"{'✅ ' if category == 'dub' else ''}🇺🇸 Dub",
                    callback_data="anime_cat_dub"
                ),
            ],
            [InlineKeyboardButton("❌ Cancel", callback_data="close")],
        ]

        await callback_query.message.edit_text(
            f"<b>🎬 {title}</b>\n\n"
            f"<b>🔊 Audio:</b> <code>{category_label}</code>\n"
            f"<b>📺 Selected:</b> <code>{ep_label}</code>\n\n"
            f"<b>Ready to download:</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
        )

        await safe_answer(callback_query, f"{ep_label} selected")

    except Exception as e:
        logger.error("Anime episode error: %s", e)
        await callback_query.message.edit_text(f"<b>❌ Error:</b> <code>{e}</code>")


async def _handle_anime_category(client, callback_query, data: str):
    """Handle category (sub/dub) selection."""
    try:
        category = data.replace("anime_cat_", "")
        BOT.State.anime_selected["category"] = category

        title = BOT.State.anime_selected.get("title", "Unknown")
        total_episodes = BOT.State.anime_selected.get("total_episodes", 0)
        if isinstance(total_episodes, str):
            total_episodes = int(total_episodes) if total_episodes.isdigit() else 0

        buttons = [
            [
                InlineKeyboardButton(f"{'✅ ' if category == 'sub' else ''}🇯🇵 Sub", callback_data="anime_cat_sub"),
                InlineKeyboardButton(f"{'✅ ' if category == 'dub' else ''}🇺🇸 Dub", callback_data="anime_cat_dub"),
            ],
        ]

        if total_episodes <= 25:
            row = []
            for ep in range(1, total_episodes + 1):
                row.append(InlineKeyboardButton(f"{ep}", callback_data=f"anime_ep_{ep}_{ep}"))
                if len(row) == 5:
                    buttons.append(row)
                    row = []
            if row:
                buttons.append(row)
            buttons.append([InlineKeyboardButton(
                f"⬇️ Download All (1-{total_episodes})",
                callback_data=f"anime_dl_1_{total_episodes}"
            )])
        elif total_episodes <= 100:
            for start in range(1, total_episodes + 1, 12):
                end = min(start + 11, total_episodes)
                buttons.append([
                    InlineKeyboardButton(
                        f"📺 Ep {start}-{end}",
                        callback_data=f"anime_ep_{start}_{end}"
                    )
                ])
        else:
            for start in range(1, min(total_episodes + 1, 600), 24):
                end = min(start + 23, total_episodes)
                buttons.append([
                    InlineKeyboardButton(
                        f"📺 Ep {start}-{end}",
                        callback_data=f"anime_ep_{start}_{end}"
                    )
                ])
            if total_episodes > 600:
                buttons.append([InlineKeyboardButton(
                    f"... and {total_episodes - 600} more episodes",
                    callback_data="close"
                )])

        buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="close")])

        category_label = "🇯🇵 Sub" if category == "sub" else "🇺🇸 Dub"
        await callback_query.message.edit_text(
            f"<b>🎬 {title}</b>\n\n"
            f"<b>🔊 Audio:</b> <code>{category_label}</code>\n"
            f"<b>📺 Episodes:</b> <code>{total_episodes}</code>\n\n"
            f"<b>Select episodes to download:</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
        )

        await safe_answer(callback_query, f"Audio: {category_label}")

    except Exception as e:
        logger.error("Anime category error: %s", e)
        await safe_answer(callback_query, "Error setting category", show_alert=True)


async def _handle_anime_download(client, callback_query, data: str):
    """Handle anime episode download."""
    from leechbot.uploader.telegram import upload_file
    from leechbot.downloader.anime import anime_client

    try:
        if BOT.State.shutting_down:
            await safe_answer(callback_query, "⏳ Bot is shutting down, try again later.", show_alert=True)
            return

        BOT.State.task_going = True

        parts = data.replace("anime_dl_", "").split("_")
        start_ep = int(parts[0])
        end_ep = int(parts[1])

        selected = BOT.State.anime_selected
        title = selected.get("title", "Unknown")
        provider = selected.get("provider", "miruro")
        anime_id = selected.get("anime_id", "")
        category = selected.get("category", "sub")
        cover = selected.get("cover", "")

        ep_label_range = f"Ep {start_ep}" if start_ep == end_ep else f"Ep {start_ep}-{end_ep}"
        total = end_ep - start_ep + 1

        BOT.Mode.type = "normal"
        BOT.Mode.stream = True
        BOT.Mode.ytdl = True
        BOT.Mode.mode = "leech"
        BOT.Mode.is_leech = True
        BOT.Options.http_headers = {"Referer": "https://kwik.cx/", "Origin": "https://kwik.cx/"}

        Messages.download_name = title
        Messages.task_msg = "<b>🎯 Task Mode:</b> "
        mode_label = "Leech"
        Messages.dump_task = Messages.task_msg + f"<code>{BOT.Mode.type.capitalize()} {mode_label} as {BOT.Setting.stream_upload}</code>\n\n<b>🔗 Sources:</b>"
        Messages.link_p = str(DUMP_ID)[4:]

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

        if cover:
            await _download_anime_poster(cover)

        dump_msg = await app.send_message(chat_id=DUMP_ID, text=Messages.dump_task, link_preview_options={"is_disabled": True})
        Messages.src_link = f"https://t.me/c/{Messages.link_p}/{dump_msg.id}"
        Messages.task_msg += f"[{BOT.Mode.type.capitalize()} {mode_label} as {BOT.Setting.stream_upload}]({Messages.src_link})\n\n"

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
            await callback_query.message.delete()
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
                    link_preview_options={"is_disabled": True}
                )
        else:
            MSG.status_msg = await app.send_message(
                chat_id=OWNER,
                text=caption,
                reply_markup=keyboard(),
                link_preview_options={"is_disabled": True}
            )

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

        for ep_num in range(start_ep, end_ep + 1):
            if BOT.State.shutting_down:
                break

            ep_label = f"Ep {ep_num:02d}"
            file_name = f"{title} - {ep_label}"

            Messages.status_head = (
                f"<b>📥 Downloading</b> <code>{ep_label}</code>\n\n"
                f"<code>{title}</code>\n"
            )

            try:
                await MSG.status_msg.edit_text(
                    text=Messages.task_msg + Messages.status_head + sysINFO(),
                    reply_markup=keyboard()
                )
            except Exception:
                pass

            episodes_data = BOT.State.anime_episodes
            ep_info = anime_client.get_episode_stream_info(episodes_data, ep_num, category)
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

            ep_dir = ospath.join(str(config.DOWNLOADS_PATH), f"ep_{ep_num}")
            if ospath.exists(ep_dir):
                shutil.rmtree(ep_dir)
            makedirs(ep_dir, exist_ok=True)
            Paths.down_path = ep_dir

            download_ok = False
            for attempt in range(2):
                try:
                    Messages.download_name = file_name
                    from leechbot.downloader.ytdl import YTDL_Status, YTDL
                    YTDL.complete = False
                    await YTDL_Status(stream_url, ep_num - start_ep + 1)
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

            if BOT.Setting.autorename_template:
                from leechbot.utility.handler import _apply_autorename_template
                q = stream_result["results"].get("quality", "")
                if not q:
                    q_match = re.search(r'(\d{3,4}p)', stream_url, re.IGNORECASE)
                    if q_match:
                        q = q_match.group(1).upper()
                file_metadata = {
                    'title': title,
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

            Messages.status_head = (
                f"<b>📤 Uploading</b> <code>{ep_label}</code>\n\n"
                f"<code>{title}</code>\n"
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

            if ep_num < end_ep:
                await async_sleep(3)

        cdt = datetime.now()
        dt = cdt.strftime(" %d-%m-%Y")
        Messages.dump_task += f"\n\n<b>📅 Date:</b> <code>{dt}</code>"
        try:
            await dump_msg.edit_text(
                text=Messages.dump_task,
                link_preview_options={"is_disabled": True}
            )
        except Exception:
            pass

        BOT.Options.custom_name = ""
        BOT.Options.http_headers = None
        Messages.download_name = title
        await SendLogs(is_leech=True)

    except Exception as e:
        logger.error("Anime download error: %s", e)
        try:
            await callback_query.message.edit_text(f"<b>❌ Error:</b> <code>{e}</code>")
        except Exception:
            pass
