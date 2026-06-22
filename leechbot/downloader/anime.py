# =============================================================================
# Telegram Leech Bot - Anime API Client
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Anime API client for searching anime, fetching episodes, and streaming URLs.
Supports MiruroAPI and AnimexAPI providers.
"""

import logging
from typing import Optional, Dict, List, Any
import aiohttp

logger = logging.getLogger(__name__)

# =============================================================================
# API Configuration
# =============================================================================
MIRURO_API_BASE = "https://mirurotvapi.vercel.app/api"
ANIMEX_API_BASE = "https://animexoneapi.vercel.app/api"

# Provider priority - try these in order
PROVIDER_PRIORITY = ["animex", "miruro"]


# =============================================================================
# MiruroAPI Client
# =============================================================================
class MiruroAPI:
    """Client for MiruroAPI (mirurotvapi.vercel.app)."""

    def __init__(self):
        self.base_url = MIRURO_API_BASE
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"User-Agent": "LeechBot/3.1.49"}
            )
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def search(self, query: str, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Search for anime."""
        session = await self._get_session()
        url = f"{self.base_url}/search"
        params = {"query": query, "page": page, "per_page": per_page}

        try:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("success"):
                        return {"success": True, "results": data.get("results", {}).get("results", [])}
                return {"success": False, "message": f"HTTP {resp.status}"}
        except Exception as e:
            logger.error("MiruroAPI search error: %s", e)
            return {"success": False, "message": str(e)}

    async def get_episodes(self, anilist_id: int) -> Dict[str, Any]:
        """Get episode list by AniList ID."""
        session = await self._get_session()
        url = f"{self.base_url}/episodes/{anilist_id}"

        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("success"):
                        return {"success": True, "results": data.get("results", {})}
                return {"success": False, "message": f"HTTP {resp.status}"}
        except Exception as e:
            logger.error("MiruroAPI episodes error: %s", e)
            return {"success": False, "message": str(e)}

    async def get_stream(self, provider: str, anilist_id: int, category: str, slug: str) -> Dict[str, Any]:
        """Get streaming URL for an episode."""
        session = await self._get_session()
        url = f"{self.base_url}/watch/{provider}/{anilist_id}/{category}/{slug}"

        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("success"):
                        streams = data.get("results", {}).get("streams", [])
                        download_url = data.get("results", {}).get("download", "")
                        best_stream = None
                        for stream in streams:
                            if stream.get("url", "").endswith(".m3u8"):
                                best_stream = stream
                                if "1080" in stream.get("quality", ""):
                                    break

                        if best_stream:
                            return {
                                "success": True,
                                "results": {
                                    "url": best_stream["url"],
                                    "quality": best_stream.get("quality", "unknown"),
                                    "codec": best_stream.get("codec", ""),
                                    "fansub": best_stream.get("fansub", ""),
                                    "audio": best_stream.get("audio", "sub"),
                                    "download": download_url,
                                    "subtitles": data.get("results", {}).get("subtitles", []),
                                    "skipTimes": data.get("results", {}).get("skipTimes", {})
                                }
                            }
                return {"success": False, "message": "No M3U8 stream found"}
        except Exception as e:
            logger.error("MiruroAPI stream error: %s", e)
            return {"success": False, "message": str(e)}

    def get_episode_stream_info(self, episodes_data: Dict, episode_number: int, category: str = "sub") -> Optional[Dict]:
        """Extract stream info for a specific episode number from episodes data."""
        providers = episodes_data.get("providers", {})

        for provider_name in ["kiwi", "bee", "bonk", "bun", "ally", "nun", "twin"]:
            provider_data = providers.get(provider_name, {})
            episodes = provider_data.get("episodes", {})
            category_episodes = episodes.get(category, [])

            for ep in category_episodes:
                if ep.get("number") == episode_number:
                    return {
                        "provider": provider_name,
                        "category": category,
                        "slug": ep.get("id", "").split("/")[-1],
                        "number": episode_number,
                        "title": ep.get("title", "")
                    }

        return None


# =============================================================================
# AnimexAPI Client
# =============================================================================
class AnimexAPI:
    """Client for AnimexAPI (animexoneapi.vercel.app)."""

    def __init__(self):
        self.base_url = ANIMEX_API_BASE
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=45),
                headers={"User-Agent": "LeechBot/3.1.49"}
            )
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search for anime."""
        session = await self._get_session()
        url = f"{self.base_url}/search"
        params = {"q": query, "limit": limit}

        try:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {"success": True, "results": data.get("results", [])}
                return {"success": False, "message": f"HTTP {resp.status}"}
        except Exception as e:
            logger.error("AnimexAPI search error: %s", e)
            return {"success": False, "message": str(e)}

    async def get_anime_info(self, anime_id: str) -> Dict[str, Any]:
        """Get anime info by slug or AniList ID."""
        session = await self._get_session()
        # Try as AniList ID first (numeric)
        if anime_id.isdigit():
            url = f"{self.base_url}/anime/anilist/{anime_id}"
        else:
            url = f"{self.base_url}/anime/{anime_id}"

        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {"success": True, "results": data.get("results", {})}
                return {"success": False, "message": f"HTTP {resp.status}"}
        except Exception as e:
            logger.error("AnimexAPI info error: %s", e)
            return {"success": False, "message": str(e)}

    async def get_episodes(self, anime_id: str) -> Dict[str, Any]:
        """Get episode list by slug or AniList ID."""
        session = await self._get_session()
        if anime_id.isdigit():
            url = f"{self.base_url}/episodes/{anime_id}"
        else:
            # For slug, need to resolve AniList ID first
            info_result = await self.get_anime_info(anime_id)
            if info_result.get("success"):
                anilist_id = info_result["results"].get("anilistId")
                if anilist_id:
                    url = f"{self.base_url}/episodes/{anilist_id}"
                else:
                    return {"success": False, "message": "Could not resolve AniList ID"}
            else:
                return info_result

        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {"success": True, "results": data.get("results", [])}
                return {"success": False, "message": f"HTTP {resp.status}"}
        except Exception as e:
            logger.error("AnimexAPI episodes error: %s", e)
            return {"success": False, "message": str(e)}

    async def get_stream(self, anilist_id: int, episode_number: int) -> Dict[str, Any]:
        """Get streaming URL via /watch endpoint (all-in-one)."""
        session = await self._get_session()
        url = f"{self.base_url}/watch/{anilist_id}/{episode_number}"

        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("success"):
                        results = data.get("results", {})
                        return {
                            "success": True,
                            "results": {
                                "streams": results.get("streams", []),
                                "episode": results.get("episode", {}),
                                "anilistId": results.get("anilistId", anilist_id),
                            }
                        }
                return {"success": False, "message": f"HTTP {resp.status}"}
        except Exception as e:
            logger.error("AnimexAPI watch error: %s", e)
            return {"success": False, "message": str(e)}

    async def get_sources(self, episode_id: int) -> Dict[str, Any]:
        """Get streaming sources directly by episode ID."""
        session = await self._get_session()
        url = f"{self.base_url}/sources/{episode_id}"

        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {"success": True, "results": data.get("results", [])}
                return {"success": False, "message": f"HTTP {resp.status}"}
        except Exception as e:
            logger.error("AnimexAPI sources error: %s", e)
            return {"success": False, "message": str(e)}

    def find_best_stream(self, streams: List[Dict], preferred_audio: str = "sub") -> Optional[Dict]:
        """Find the best M3U8 stream from a list, preferring audio type and highest quality."""
        if not streams:
            return None

        # Filter for active M3U8 streams
        active_streams = [
            s for s in streams
            if s.get("url", "").endswith(".m3u8")
            and s.get("isActive", True)
        ]

        if not active_streams:
            # Fallback to any M3U8 stream
            active_streams = [s for s in streams if s.get("url", "").endswith(".m3u8")]

        if not active_streams:
            return None

        # Sort by: preferred audio type first, then quality (1080p > 720p > 480p)
        quality_order = {"1080p": 3, "720p": 2, "480p": 1, "360p": 0}
        active_streams.sort(
            key=lambda s: (
                1 if s.get("audio") == preferred_audio else 0,
                quality_order.get(s.get("quality", ""), 0)
            ),
            reverse=True
        )

        return active_streams[0]

    def format_search_results(self, results: List[Dict]) -> List[Dict]:
        """Format search results for display."""
        formatted = []
        for item in results[:10]:
            title_en = item.get("titleEnglish") or ""
            title_jp = item.get("titleRomaji") or ""
            title = title_en or title_jp or "Unknown"
            anime_id = item.get("anilistId") or item.get("id", "")
            slug = item.get("id", "")
            episodes = item.get("episodeCount", "?")
            cover = item.get("coverImage", {}).get("extraLarge") or item.get("coverImage", {}).get("large", "")
            format_type = item.get("format", "")
            status = item.get("status", "")
            score = item.get("averageScore", 0)
            genres = item.get("genres", [])
            banner = item.get("bannerImage", "")

            # Show English title, with Japanese subtitle if different
            display_title = title_en if title_en else title_jp
            subtitle = f"\n<i>{title_jp}</i>" if title_en and title_jp and title_en != title_jp else ""

            formatted.append({
                "id": anime_id,
                "slug": slug,
                "title": title,
                "episodes": episodes,
                "cover": cover,
                "banner": banner,
                "format": format_type,
                "status": status,
                "score": score,
                "genres": genres,
                "display": f"🎬 {display_title}{subtitle}\n({format_type}) 📺 {episodes} eps | ⭐ {score}%"
            })

        return formatted


# =============================================================================
# Unified Anime Client
# =============================================================================
class AnimeClient:
    """Unified anime client that manages multiple API providers.

    Strategy: AnimexAPI for search (richer data), MiruroAPI for episodes + streaming (reliable).
    """

    def __init__(self):
        self.miruro = MiruroAPI()
        self.animex = AnimexAPI()

    async def close(self):
        await self.miruro.close()
        await self.animex.close()

    async def search(self, query: str) -> Dict[str, Any]:
        """Search for anime. Try AnimexAPI first (richer results), fallback to MiruroAPI."""
        for provider in PROVIDER_PRIORITY:
            if provider == "animex":
                result = await self.animex.search(query)
            else:
                result = await self.miruro.search(query)
            if result.get("success") and result.get("results"):
                result["provider"] = provider
                return result

        return {"success": False, "message": "Search failed on all providers"}

    async def get_episodes(self, anilist_id: Any, provider: str = "animex") -> Dict[str, Any]:
        """Get episode list. Always uses MiruroAPI (AnimexAPI episodes returns 403)."""
        return await self.miruro.get_episodes(anilist_id)

    async def get_stream_url(self, anilist_id: int, episode_number: int, provider: str = "animex", preferred_audio: str = "sub") -> Dict[str, Any]:
        """Get streaming URL. Always uses MiruroAPI (AnimexAPI watch returns 403)."""
        # MiruroAPI needs episode stream info from episodes data
        # This method is called from callbacks.py which passes episode info
        return {"success": False, "message": "Use get_stream_from_miruro() directly"}

    async def get_stream_from_miruro(self, provider: str, anilist_id: int, category: str, slug: str) -> Dict[str, Any]:
        """Get stream URL from MiruroAPI directly."""
        return await self.miruro.get_stream(provider, anilist_id, category, slug)

    def format_search_results(self, results: List[Dict], provider: str = "animex") -> List[Dict]:
        """Format search results for display."""
        if provider == "animex":
            return self.animex.format_search_results(results)
        else:
            return self._format_miruro_results(results)

    def _format_miruro_results(self, results: List[Dict]) -> List[Dict]:
        """Format MiruroAPI search results."""
        formatted = []
        for item in results[:10]:
            title_data = item.get("title", {})
            title = title_data.get("english") or title_data.get("romaji") or "Unknown"
            anime_id = item.get("id")
            episodes = item.get("episodes", "?")
            cover = item.get("coverImage", {}).get("large") or item.get("coverImage", {}).get("medium", "")
            format_type = item.get("format", "")
            status = item.get("status", "")
            score = item.get("averageScore", 0)

            formatted.append({
                "id": anime_id,
                "title": title,
                "episodes": episodes,
                "cover": cover,
                "format": format_type,
                "status": status,
                "score": score,
                "display": f"🎬 {title} ({format_type})\n📺 {episodes} episodes | ⭐ {score}%"
            })

        return formatted


# =============================================================================
# Singleton instance
# =============================================================================
anime_client = AnimeClient()
