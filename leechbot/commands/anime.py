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
Anime download commands.

Provides /anime command for searching and downloading anime episodes
from MiruroAPI with optimized UI for large episode counts.

Supports both interactive and quick/batch modes:
- /anime <name> — interactive search with buttons
- /anime <name> ep 1-5 sub — quick download
"""

import re
import logging
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from leechbot import app, OWNER
from leechbot.downloader.anime import anime_client
from leechbot.utility.variables import BOT, MSG, Messages, BotStats

logger = logging.getLogger(__name__)


# =============================================================================
# Anime State (per-user)
# =============================================================================
class AnimeState:
    """Per-user anime session state."""
    search_results: dict = {}      # user_id -> list of search results
    selected_anime: dict = {}      # user_id -> selected anime dict
    episodes_data: dict = {}       # user_id -> episodes data from API
    user_category: dict = {}       # user_id -> "sub" or "dub"
    current_page: dict = {}        # user_id -> current episode page
    episode_range: dict = {}       # user_id -> (start, end) tuple

    EPISODES_PER_PAGE = 20         # Episodes shown per page
    EPISODES_PER_RANGE = 100       # Episodes per range button

    def clear(self, user_id: int):
        """Clear all state for a user."""
        self.search_results.pop(user_id, None)
        self.selected_anime.pop(user_id, None)
        self.episodes_data.pop(user_id, None)
        self.user_category.pop(user_id, None)
        self.current_page.pop(user_id, None)
        self.episode_range.pop(user_id, None)
        anime_client.clear_cache(user_id)


anime_state = AnimeState()


# =============================================================================
# /anime Command
# =============================================================================
@app.on_message(filters.command("anime") & filters.private)
async def anime_command(client, message):
    """
    Search and download anime.
    
    Usage:
        /anime <name> — interactive search
        /anime <name> ep <range> [sub|dub] [quality] — quick download
        
    Examples:
        /anime Solo Leveling
        /anime One Piece ep 1-10 sub
        /anime Naruto ep 5 dub 1080p
    """
    # Check if Anime API is configured
    from leechbot.downloader.anime import is_anime_api_configured
    
    if not is_anime_api_configured():
        await message.reply_text(
            "<b>❌ Anime API Not Configured</b>\n\n"
            "The <code>ANIME_API_URL</code> environment variable is not set.\n\n"
            "<b>📌 To use Anime Downloader:</b>\n"
            "1. Get your Anime API from developer\n"
            "2. Add it to <code>.env</code> file:\n"
            "<code>ANIME_API_URL=your-api-url</code>\n"
            "3. Restart the bot\n\n"
            "<b>🛒 Buy Anime API:</b>\n"
            "<a href=\"https://t.me/Shineii86\">Contact Developer</a>",
            disable_web_page_preview=True
        )
        return

    args = message.text.split(None, 1)
    if len(args) < 2:
        await message.reply_text(
            "<b>🎬 Anime Downloader</b>\n\n"
            "<b>Usage:</b>\n"
            "• <code>/anime &lt;name&gt;</code> — interactive search\n"
            "• <code>/anime &lt;name&gt; ep 1-5 sub</code> — quick download\n\n"
            "<b>Quick Examples:</b>\n"
            "• <code>/anime Solo Leveling ep 1-5 sub</code>\n"
            "• <code>/anime One Piece ep 1-10 dub 1080p</code>\n"
            "• <code>/anime Naruto ep 5 sub</code>\n\n"
            "<b>Parameters:</b>\n"
            "• <code>ep &lt;range&gt;</code> — episode(s): 5 or 1-13\n"
            "• <code>sub</code> / <code>dub</code> — audio type\n"
            "• <code>480p</code> / <code>720p</code> / <code>1080p</code> — quality"
        )
        return

    # Parse input
    input_text = args[1].strip()
    
    # Check for quick mode: "ep" keyword
    ep_match = re.search(r'\bep\s+(\d+(?:-\d+)?)\b', input_text, re.IGNORECASE)
    
    # Check for sub/dub
    category = "sub"
    if re.search(r'\b(dub)\b', input_text, re.IGNORECASE):
        category = "dub"
    elif re.search(r'\b(sub)\b', input_text, re.IGNORECASE):
        category = "sub"
    
    # Check for quality
    quality = None
    quality_match = re.search(r'\b(480p|720p|1080p)\b', input_text, re.IGNORECASE)
    if quality_match:
        quality = quality_match.group(1)
    
    # Extract query (remove ep, sub/dub, quality keywords)
    query = re.sub(r'\bep\s+\d+(?:-\d+)?\b', '', input_text, flags=re.IGNORECASE)
    query = re.sub(r'\b(sub|dub)\b', '', query, flags=re.IGNORECASE)
    query = re.sub(r'\b(480p|720p|1080p)\b', '', query, flags=re.IGNORECASE)
    query = query.strip()
    
    if not query:
        await message.reply_text("<b>❌ Please provide an anime name.</b>")
        return

    # Interactive mode (no "ep" keyword)
    if not ep_match:
        status_msg = await message.reply_text(f"<b>🔍 Searching:</b> <code>{query}</code>...")

        try:
            results = await anime_client.search(query)
        except Exception as e:
            await status_msg.edit_text(f"<b>❌ Search failed:</b>\n<code>{str(e)}</code>")
            return

        if not results:
            await status_msg.edit_text("<b>❌ No results found.</b>")
            return

        user_id = message.from_user.id
        anime_state.search_results[user_id] = results

        # Build search results message
        text = f"<b>🔍 Search Results for:</b> <code>{query}</code>\n\n"
        buttons = []
        
        for i, item in enumerate(results[:5]):
            score_text = f" | ⭐ {item['score']}%" if item.get("score") else ""
            eps_text = f"{item['episodes']} eps" if item.get("episodes") else "Ongoing"
            status_emoji = "🟢" if item.get("status") == "RELEASING" else "🔵" if item.get("status") == "FINISHED" else "⚪"
            
            text += f"{i+1}. {status_emoji} <b>{item['title']}</b>\n"
            text += f"   {item['format']} | {eps_text}{score_text}\n\n"
            
            buttons.append([InlineKeyboardButton(
                f"{i+1}. {item['title'][:40]}",
                callback_data=f"anime_select_{user_id}_{i}"
            )])
        
        buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="anime_cancel")])

        await status_msg.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
        return

    # Quick mode: search + auto-download
    ep_range = ep_match.group(1)
    status_msg = await message.reply_text(f"<b>🔍 Searching:</b> <code>{query}</code>...")

    try:
        results = await anime_client.search(query)
    except Exception as e:
        await status_msg.edit_text(f"<b>❌ Search failed:</b>\n<code>{str(e)}</code>")
        return

    if not results:
        await status_msg.edit_text("<b>❌ No results found.</b>")
        return

    # Use first result
    anime = results[0]
    user_id = message.from_user.id

    await status_msg.edit_text(f"<b>⏳ Loading episodes for:</b>\n<code>{anime['title']}</code>...")

    try:
        episodes_data = await anime_client.get_episodes(anime["id"], user_id)
    except Exception as e:
        await status_msg.edit_text(f"<b>❌ Failed to load episodes:</b>\n<code>{str(e)}</code>")
        return

    if not episodes_data:
        await status_msg.edit_text("<b>❌ No episodes found.</b>")
        return

    # Parse episode range
    if "-" in ep_range:
        start, end = map(int, ep_range.split("-"))
        episode_numbers = list(range(start, end + 1))
    else:
        episode_numbers = [int(ep_range)]

    # Filter to available episodes
    available = anime_client.get_available_episodes(episodes_data, category)
    valid_episodes = [ep for ep in episode_numbers if ep in available]

    if not valid_episodes:
        await status_msg.edit_text(
            f"<b>❌ No {category.upper()} episodes found in range {ep_range}.</b>"
        )
        return

    # Store state and start download
    anime_state.selected_anime[user_id] = anime
    anime_state.episodes_data[user_id] = episodes_data
    anime_state.user_category[user_id] = category

    # Start batch download
    await status_msg.edit_text(
        f"<b>📥 Starting Quick Download</b>\n\n"
        f"🎬 <b>{anime['title']}</b>\n"
        f"📺 <b>Episodes:</b> {len(valid_episodes)}\n"
        f"🔊 <b>Audio:</b> {category.upper()}\n"
        f"📊 <b>Range:</b> {ep_range}\n\n"
        f"<b>Downloading...</b>"
    )

    # Download episodes
    for ep_num in valid_episodes:
        stream_info = anime_client.get_episode_stream_info(episodes_data, ep_num, category)
        if stream_info:
            await _start_quick_download(status_msg, anime, stream_info, ep_num, category, quality)
            import asyncio
            await asyncio.sleep(1)


# =============================================================================
# Internal: Quick Download Handler
# =============================================================================
async def _start_quick_download(status_msg, anime: dict, stream_info: dict, ep_num: int, category: str, quality: str = None):
    """Handle quick mode anime download."""
    from leechbot.commands.autorename import parse_autorename_template
    
    provider = stream_info["provider"]
    slug = stream_info["slug"]
    anime_id = anime["id"]

    # Get stream data
    try:
        stream_data = await anime_client.get_stream(provider, anime_id, category, slug)
    except Exception as e:
        await status_msg.edit_text(f"<b>❌ Failed to get stream for Ep {ep_num}:</b>\n<code>{str(e)}</code>")
        return

    # Extract stream URL
    stream_url = None

    if stream_data and "bestStream" in stream_data:
        best = stream_data["bestStream"]
        if best and best.get("url"):
            stream_url = best["url"]

    if not stream_url and stream_data and "streams" in stream_data:
        for s in stream_data["streams"]:
            if s.get("type") == "hls" and s.get("isActive"):
                stream_url = s["url"]
                break

    if not stream_url and stream_data and "download" in stream_data:
        stream_url = stream_data["download"]

    if not stream_url:
        return

    # Set up download
    BOT.SOURCE = [stream_url]
    BOT.Mode.mode = "leech"
    BOT.Mode.ytdl = True
    BOT.Mode.gallery = False
    BOT.Mode.type = "normal"

    # Apply autorename template if set
    if BOT.Options.custom_name:
        parsed_name = parse_autorename_template(
            BOT.Options.custom_name,
            season="1",
            episode=f"{ep_num:02d}",
            quality=quality or "Unknown",
            audio=category.upper(),
            title=anime['title']
        )
        Messages.download_name = parsed_name
    else:
        Messages.download_name = f"[S1 E{ep_num:02d}] {anime['title']} [{category.upper()}]"

    # Start download via task scheduler
    try:
        from leechbot.utility.task_manager import taskScheduler
        await taskScheduler()
        BotStats.total_tasks += 1
    except Exception as e:
        logger.error(f"Quick download failed for Ep {ep_num}: {e}")
        BotStats.failed_tasks += 1


# =============================================================================
# Helper: Build Episode Keyboard (Optimized for 1000+ episodes)
# =============================================================================
def build_episode_keyboard(user_id: int, total_episodes: int, category: str = "sub", page: int = 0) -> InlineKeyboardMarkup:
    """
    Build episode selection keyboard with pagination.
    
    For 1000+ episodes, uses range-based navigation:
    - Range buttons: 1-100, 101-200, etc.
    - Page buttons within range: 1-20, 21-40, etc.
    - Individual episode buttons within current page
    """
    buttons = []
    
    # Calculate range boundaries
    total_ranges = (total_episodes + anime_state.EPISODES_PER_RANGE - 1) // anime_state.EPISODES_PER_RANGE
    current_range_start = (page * anime_state.EPISODES_PER_PAGE) + 1
    current_range_end = min(current_range_start + anime_state.EPISODES_PER_PAGE - 1, total_episodes)
    
    # Episode buttons (grid of 5 columns)
    row = []
    for i in range(current_range_start, current_range_end + 1):
        row.append(InlineKeyboardButton(str(i), callback_data=f"anime_dl_{user_id}_{i}_{category}"))
        if len(row) == 5:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    # Navigation row
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"anime_page_{user_id}_{page-1}_{category}"))
    if current_range_end < total_episodes:
        nav_row.append(InlineKeyboardButton("➡️ Next", callback_data=f"anime_page_{user_id}_{page+1}_{category}"))
    if nav_row:
        buttons.append(nav_row)
    
    # Range quick-jump (for 100+ episodes)
    if total_episodes > anime_state.EPISODES_PER_RANGE:
        range_row = []
        for r in range(total_ranges):
            r_start = r * anime_state.EPISODES_PER_RANGE + 1
            r_end = min(r_start + anime_state.EPISODES_PER_RANGE - 1, total_episodes)
            range_row.append(InlineKeyboardButton(
                f"{r_start}-{r_end}",
                callback_data=f"anime_range_{user_id}_{r}_{category}"
            ))
            if len(range_row) == 3:
                buttons.append(range_row)
                range_row = []
        if range_row:
            buttons.append(range_row)
    
    # Category toggle
    sub_emoji = "✅" if category == "sub" else "❌"
    dub_emoji = "✅" if category == "dub" else "❌"
    buttons.append([
        InlineKeyboardButton(f"{sub_emoji} 🇯🇵 Sub", callback_data=f"anime_cat_{user_id}_sub"),
        InlineKeyboardButton(f"{dub_emoji} 🇺🇸 Dub", callback_data=f"anime_cat_{user_id}_dub"),
    ])
    
    # Quick actions
    buttons.append([
        InlineKeyboardButton(f"📥 Download All (1-{total_episodes})", callback_data=f"anime_dlall_{user_id}_{category}")
    ])
    buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="anime_cancel")])
    
    return InlineKeyboardMarkup(buttons)


# =============================================================================
# Helper: Send Anime Info
# =============================================================================
async def send_anime_info(message, anime: dict, episodes_data: list, user_id: int, category: str = "sub", page: int = 0):
    """Send anime info with episode selection keyboard."""
    available = anime_client.get_available_episodes(episodes_data, category)
    total = len(available) if available else 0
    
    if total == 0:
        await message.edit_text(
            f"<b>🎬 {anime['title']}</b>\n\n"
            f"<i>❌ No {category.upper()} episodes available.</i>"
        )
        return
    
    max_ep = max(available.keys())
    min_ep = min(available.keys())
    
    # Build info text
    text = (
        f"🎬 <b>{anime['title']}</b>\n"
        f"📺 <b>Episodes:</b> {min_ep}-{max_ep} ({total} total)\n"
        f"🔊 <b>Audio:</b> {category.upper()}\n"
        f"📊 <b>Page:</b> {page + 1}/{(total + anime_state.EPISODES_PER_PAGE - 1) // anime_state.EPISODES_PER_PAGE}\n\n"
        f"<b>Select episodes to download:</b>"
    )
    
    keyboard = build_episode_keyboard(user_id, max_ep, category, page)
    await message.edit_text(text, reply_markup=keyboard)


# =============================================================================
# Export for callbacks module
# =============================================================================
__all__ = ["anime_state", "anime_client", "send_anime_info", "build_episode_keyboard"]
