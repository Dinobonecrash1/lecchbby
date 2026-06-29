# =============================================================================
# Telegram Leech Bot - Anime Callbacks
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Anime callback query handlers.

Handles inline keyboard callbacks for anime search results,
episode selection, pagination, sub/dub toggle, and download initiation.
"""

import asyncio
import logging
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from leechbot import app, OWNER
from leechbot.downloader.anime import anime_client
from leechbot.commands.anime import anime_state, send_anime_info
from leechbot.utility.variables import BOT, MSG, Messages, BotStats
from leechbot.utility.helper import keyboard, sysINFO
from leechbot.utility.handler import cancelTask

logger = logging.getLogger(__name__)


# =============================================================================
# Search Result Selection
# =============================================================================
@app.on_callback_query(filters.regex(r"^anime_select_(\d+)_(\d+)$"))
async def anime_select_callback(client, callback_query):
    """Handle anime search result selection."""
    user_id = callback_query.from_user.id
    data = callback_query.data
    parts = data.split("_")
    idx = int(parts[3])

    if user_id not in anime_state.search_results:
        await callback_query.answer("⚠️ Session expired. Search again.", show_alert=True)
        return

    results = anime_state.search_results[user_id]
    if idx >= len(results):
        await callback_query.answer("⚠️ Invalid selection.", show_alert=True)
        return

    anime = results[idx]
    anime_state.selected_anime[user_id] = anime

    await callback_query.answer(f"⏳ Loading episodes for {anime['title'][:30]}...")
    await callback_query.message.edit_text(
        f"<b>⏳ Loading episodes for:</b>\n"
        f"<code>{anime['title']}</code>..."
    )

    try:
        episodes_data = await anime_client.get_episodes(anime["id"], user_id)
    except Exception as e:
        await callback_query.message.edit_text(
            f"<b>❌ Failed to load episodes:</b>\n<code>{str(e)}</code>"
        )
        return

    if not episodes_data:
        await callback_query.message.edit_text("<b>❌ No episodes found.</b>")
        return

    anime_state.episodes_data[user_id] = episodes_data
    anime_state.user_category[user_id] = "sub"
    anime_state.current_page[user_id] = 0

    await send_anime_info(callback_query.message, anime, episodes_data, user_id, "sub", 0)


# =============================================================================
# Category Toggle (Sub/Dub)
# =============================================================================
@app.on_callback_query(filters.regex(r"^anime_cat_(\d+)_(sub|dub)$"))
async def anime_category_callback(client, callback_query):
    """Handle sub/dub category toggle."""
    user_id = callback_query.from_user.id
    data = callback_query.data
    category = data.split("_")[-1]

    if user_id not in anime_state.selected_anime:
        await callback_query.answer("⚠️ Session expired.", show_alert=True)
        return

    anime = anime_state.selected_anime[user_id]
    episodes_data = anime_state.episodes_data.get(user_id, [])
    anime_state.user_category[user_id] = category
    anime_state.current_page[user_id] = 0

    await callback_query.answer(f"🔄 Switched to {category.upper()}")
    await send_anime_info(callback_query.message, anime, episodes_data, user_id, category, 0)


# =============================================================================
# Episode Pagination
# =============================================================================
@app.on_callback_query(filters.regex(r"^anime_page_(\d+)_(\d+)_(sub|dub)$"))
async def anime_page_callback(client, callback_query):
    """Handle episode page navigation."""
    user_id = callback_query.from_user.id
    data = callback_query.data
    parts = data.split("_")
    page = int(parts[3])
    category = parts[4]

    if user_id not in anime_state.selected_anime:
        await callback_query.answer("⚠️ Session expired.", show_alert=True)
        return

    anime = anime_state.selected_anime[user_id]
    episodes_data = anime_state.episodes_data.get(user_id, [])
    anime_state.current_page[user_id] = page

    await callback_query.answer(f"📄 Page {page + 1}")
    await send_anime_info(callback_query.message, anime, episodes_data, user_id, category, page)


# =============================================================================
# Episode Range Jump (for 100+ episodes)
# =============================================================================
@app.on_callback_query(filters.regex(r"^anime_range_(\d+)_(\d+)_(sub|dub)$"))
async def anime_range_callback(client, callback_query):
    """Handle episode range jump for large episode counts."""
    user_id = callback_query.from_user.id
    data = callback_query.data
    parts = data.split("_")
    range_idx = int(parts[3])
    category = parts[4]

    if user_id not in anime_state.selected_anime:
        await callback_query.answer("⚠️ Session expired.", show_alert=True)
        return

    anime = anime_state.selected_anime[user_id]
    episodes_data = anime_state.episodes_data.get(user_id, [])
    
    # Calculate page from range index
    page = (range_idx * anime_state.EPISODES_PER_RANGE) // anime_state.EPISODES_PER_PAGE
    anime_state.current_page[user_id] = page

    range_start = range_idx * anime_state.EPISODES_PER_RANGE + 1
    range_end = range_start + anime_state.EPISODES_PER_RANGE - 1
    
    await callback_query.answer(f"📖 Episodes {range_start}-{range_end}")
    await send_anime_info(callback_query.message, anime, episodes_data, user_id, category, page)


# =============================================================================
# Single Episode Download
# =============================================================================
@app.on_callback_query(filters.regex(r"^anime_dl_(\d+)_(\d+)_(sub|dub)$"))
async def anime_download_callback(client, callback_query):
    """Handle single episode download."""
    user_id = callback_query.from_user.id
    data = callback_query.data
    parts = data.split("_")
    ep_num = int(parts[3])
    category = parts[4]

    if user_id not in anime_state.selected_anime:
        await callback_query.answer("⚠️ Session expired.", show_alert=True)
        return

    anime = anime_state.selected_anime[user_id]
    episodes_data = anime_state.episodes_data.get(user_id, [])

    stream_info = anime_client.get_episode_stream_info(episodes_data, ep_num, category)
    if not stream_info:
        await callback_query.answer(
            f"❌ No {category.upper()} stream found for Episode {ep_num}",
            show_alert=True
        )
        return

    await callback_query.answer(f"📥 Starting download: Episode {ep_num} ({category.upper()})...")
    await _start_anime_download(callback_query, anime, stream_info, ep_num, category)


# =============================================================================
# Download All Episodes
# =============================================================================
@app.on_callback_query(filters.regex(r"^anime_dlall_(\d+)_(sub|dub)$"))
async def anime_download_all_callback(client, callback_query):
    """Handle batch download of all episodes."""
    user_id = callback_query.from_user.id
    data = callback_query.data
    category = data.split("_")[-1]

    if user_id not in anime_state.selected_anime:
        await callback_query.answer("⚠️ Session expired.", show_alert=True)
        return

    anime = anime_state.selected_anime[user_id]
    episodes_data = anime_state.episodes_data.get(user_id, [])
    available = anime_client.get_available_episodes(episodes_data, category)

    if not available:
        await callback_query.answer("❌ No episodes available.", show_alert=True)
        return

    ep_count = len(available)
    await callback_query.answer(f"📥 Starting batch download ({ep_count} episodes)...")

    # Show batch download info
    await callback_query.message.edit_text(
        f"<b>📥 Batch Download Started</b>\n\n"
        f"🎬 <b>{anime['title']}</b>\n"
        f"📺 <b>Episodes:</b> {ep_count}\n"
        f"🔊 <b>Audio:</b> {category.upper()}\n\n"
        f"<b>Downloading episodes...</b>"
    )

    # Download episodes sequentially
    for ep_num in sorted(available.keys()):
        stream_info = anime_client.get_episode_stream_info(episodes_data, ep_num, category)
        if stream_info:
            await _start_anime_download(callback_query, anime, stream_info, ep_num, category)
            await asyncio.sleep(1)


# =============================================================================
# Internal: Start Anime Download
# =============================================================================
async def _start_anime_download(callback_query, anime: dict, stream_info: dict, ep_num: int, category: str):
    """Internal function to start anime episode download."""
    user_id = callback_query.from_user.id
    provider = stream_info["provider"]
    slug = stream_info["slug"]
    anime_id = anime["id"]

    # Build status message
    status_text = (
        f"⬇️ <b>Downloading Ep {ep_num:02d}</b>\n\n"
        f"🎬 <b>{anime['title']}</b>\n"
        f"🔊 <b>Audio:</b> {category.upper()}\n"
        f"📡 <b>Provider:</b> {provider}\n"
    )

    status_msg = await callback_query.message.edit_text(status_text)

    # Get stream data
    try:
        stream_data = await anime_client.get_stream(provider, anime_id, category, slug)
    except Exception as e:
        await status_msg.edit_text(f"<b>❌ Failed to get stream:</b>\n<code>{str(e)}</code>")
        return

    # Extract stream URL
    stream_url = None
    referer = None

    if stream_data and "bestStream" in stream_data:
        best = stream_data["bestStream"]
        if best and best.get("url"):
            stream_url = best["url"]
            referer = best.get("referer")

    if not stream_url and stream_data and "streams" in stream_data:
        for s in stream_data["streams"]:
            if s.get("type") == "hls" and s.get("isActive"):
                stream_url = s["url"]
                referer = s.get("referer")
                break

    if not stream_url and stream_data and "download" in stream_data:
        stream_url = stream_data["download"]

    if not stream_url:
        await status_msg.edit_text("<b>❌ No valid stream found.</b>")
        return

    # Set up download
    BOT.SOURCE = [stream_url]
    BOT.Mode.mode = "leech"
    BOT.Mode.ytdl = True
    BOT.Mode.gallery = False
    BOT.Mode.type = "normal"

    # Set download name with autorename template support
    ep_title = stream_info.get("title", f"Episode {ep_num}")
    Messages.download_name = f"[S1 E{ep_num:02d}] {anime['title']} [{category.upper()}]"

    # Update status
    stream_type = "M3U8" if ".m3u8" in (stream_url or "") else "Direct"
    await status_msg.edit_text(
        f"✅ <b>Stream found!</b>\n\n"
        f"🎬 <b>{anime['title']}</b>\n"
        f"📺 <b>Episode:</b> {ep_num} - {ep_title}\n"
        f"🔊 <b>Audio:</b> {category.upper()}\n"
        f"📡 <b>Provider:</b> {provider}\n"
        f"🔗 <b>Type:</b> {stream_type}\n\n"
        f"<b>Starting download...</b>"
    )

    # Start download via task scheduler
    try:
        from leechbot.utility.task_manager import taskScheduler
        await taskScheduler()
        BotStats.total_tasks += 1
    except Exception as e:
        await status_msg.edit_text(f"<b>❌ Download failed:</b>\n<code>{str(e)}</code>")
        BotStats.failed_tasks += 1


# =============================================================================
# Cancel
# =============================================================================
@app.on_callback_query(filters.regex(r"^anime_cancel$"))
async def anime_cancel_callback(client, callback_query):
    """Handle anime session cancellation."""
    user_id = callback_query.from_user.id
    anime_state.clear(user_id)
    await callback_query.answer("❌ Cancelled")
    await callback_query.message.edit_text("<b>❌ Cancelled.</b>")
