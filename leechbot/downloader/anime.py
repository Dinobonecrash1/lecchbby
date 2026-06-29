# =============================================================================
# Telegram Leech Bot - Anime Downloader (MiruroAPI)
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Anime downloader module using MiruroAPI.

Provides search, episode listing, and stream resolution for anime content.
Optimized for large episode counts (1000+ episodes like One Piece).

API URL is configured via ANIME_API_URL environment variable (REQUIRED).
Get your API from: https://t.me/Shineii86
"""

import logging
import aiohttp
import asyncio
import config
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)


def get_anime_api_url() -> str:
    """Get anime API URL from config. Returns empty string if not set."""
    return config.ANIME_API_URL if config.ANIME_API_URL else ""


def is_anime_api_configured() -> bool:
    """Check if anime API URL is configured."""
    return bool(config.ANIME_API_URL)


# =============================================================================
# MiruroAPI Client
# =============================================================================
class MiruroAPI:
    """Async client for MiruroAPI anime streaming service."""

    BASE_URL = get_anime_api_url()
    
    # Provider priority order (tried in sequence for fallback)
    PROVIDERS = ["kiwi", "pewe", "bonk", "bee", "ally", "moo", "hop", "nun", "bun", "twin", "cog", "telli"]
    
    # Cache for episode data (user_id -> {anime_id: episodes_data})
    _episode_cache: Dict[int, Dict[int, list]] = {}
    
    # Cache TTL in seconds (5 minutes)
    CACHE_TTL = 300

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self._cache_timestamps: Dict[int, float] = {}

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers={"User-Agent": "LeechBot/3.2.6"}
            )
        return self._session

    async def close(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(self, endpoint: str, params: dict = None) -> dict:
        """Make API request with error handling."""
        if not self.BASE_URL:
            return {"success": False, "message": "API not configured"}
        
        session = await self._get_session()
        url = f"{self.BASE_URL}{endpoint}"
        try:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                logger.warning("MiruroAPI HTTP %d for %s", resp.status, endpoint)
                return {"success": False, "message": f"HTTP {resp.status}"}
        except asyncio.TimeoutError:
            logger.error("MiruroAPI timeout for %s", endpoint)
            return {"success": False, "message": "Request timeout"}
        except Exception as e:
            logger.error("MiruroAPI error for %s: %s", endpoint, e)
            return {"success": False, "message": str(e)}

    # =========================================================================
    # Search
    # =========================================================================
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for anime by name.
        
        Args:
            query: Search query string
            
        Returns:
            List of formatted search results
        """
        data = await self._request("/search", {"query": query, "per_page": 10})
        if not data.get("success"):
            return []
        results = data.get("results", [])
        return self._format_search_results(results)

    def _format_search_results(self, results: list) -> list:
        """Format raw API results for display."""
        formatted = []
        for item in results[:10]:
            title = item.get("title", {})
            formatted.append({
                "id": item.get("id"),
                "title": title.get("english") or title.get("romaji") or "Unknown",
                "romaji": title.get("romaji", ""),
                "native": title.get("native", ""),
                "format": item.get("format", "TV"),
                "episodes": item.get("episodes", 0),
                "status": item.get("status", "UNKNOWN"),
                "score": item.get("averageScore", 0),
                "cover": item.get("coverImage", {}).get("large", ""),
                "genres": item.get("genres", []),
                "description": (item.get("description", "") or "")[:200]
            })
        return formatted

    # =========================================================================
    # Episodes
    # =========================================================================
    async def get_episodes(self, anilist_id: int, user_id: int = 0) -> list:
        """
        Get episode list for an anime.
        
        Args:
            anilist_id: AniList anime ID
            user_id: User ID for caching
            
        Returns:
            List of episode objects
        """
        # Check cache
        if user_id and user_id in self._episode_cache:
            if anilist_id in self._episode_cache[user_id]:
                import time
                cache_time = self._cache_timestamps.get(f"{user_id}_{anilist_id}", 0)
                if time.time() - cache_time < self.CACHE_TTL:
                    logger.debug("Using cached episodes for anime %d", anilist_id)
                    return self._episode_cache[user_id][anilist_id]

        data = await self._request(f"/episodes/{anilist_id}")
        if not data.get("success"):
            return []
        
        episodes = data.get("results", [])
        
        # Cache the result
        if user_id:
            if user_id not in self._episode_cache:
                self._episode_cache[user_id] = {}
            self._episode_cache[user_id][anilist_id] = episodes
            import time
            self._cache_timestamps[f"{user_id}_{anilist_id}"] = time.time()
        
        return episodes

    def clear_cache(self, user_id: int):
        """Clear episode cache for a user."""
        self._episode_cache.pop(user_id, None)
        keys_to_remove = [k for k in self._cache_timestamps if k.startswith(f"{user_id}_")]
        for k in keys_to_remove:
            del self._cache_timestamps[k]

    # =========================================================================
    # Stream Resolution
    # =========================================================================
    async def get_stream(self, provider: str, anilist_id: int, category: str, slug: str) -> Optional[dict]:
        """
        Get streaming URL for an episode.
        
        Args:
            provider: Provider name (kiwi, pewe, bonk, etc.)
            anilist_id: AniList anime ID
            category: Audio category (sub/dub)
            slug: Episode slug
            
        Returns:
            Stream data dict or None
        """
        data = await self._request(f"/watch/{provider}/{anilist_id}/{category}/{slug}")
        if not data.get("success"):
            return None
        return data.get("results", {})

    async def get_download(self, provider: str, anilist_id: int, category: str, slug: str) -> Optional[dict]:
        """
        Get download URL for an episode.
        
        Args:
            provider: Provider name
            anilist_id: AniList anime ID
            category: Audio category (sub/dub)
            slug: Episode slug
            
        Returns:
            Download data dict or None
        """
        data = await self._request("/download", {
            "provider": provider,
            "anilistId": anilist_id,
            "category": category,
            "slug": slug
        })
        if not data.get("success"):
            return None
        return data.get("results", {})

    # =========================================================================
    # Episode Info Helpers
    # =========================================================================
    def get_available_episodes(self, episodes_data: list, category: str = "sub") -> Dict[int, dict]:
        """
        Get available episodes for a category.
        
        Args:
            episodes_data: Raw episodes data from API
            category: Audio category (sub/dub)
            
        Returns:
            Dict of episode_number -> episode_info
        """
        eps = {}
        for ep in episodes_data:
            if ep.get("audio") == category:
                num = ep.get("number", 0)
                if num not in eps:
                    eps[num] = {
                        "number": num,
                        "title": ep.get("title", f"Episode {num}"),
                        "image": ep.get("image", ""),
                        "air_date": ep.get("airDate", ""),
                        "filler": ep.get("filler", False)
                    }
        return eps

    def get_episode_stream_info(self, episodes_data: list, episode_number: int, category: str = "sub") -> Optional[dict]:
        """
        Get stream info for a specific episode.
        
        Args:
            episodes_data: Raw episodes data from API
            episode_number: Episode number to find
            category: Audio category (sub/dub)
            
        Returns:
            Stream info dict or None
        """
        # First try: exact match with provider priority
        for provider in self.PROVIDERS:
            for ep in episodes_data:
                ep_id = ep.get("id", "")
                ep_num = ep.get("number", 0)
                ep_audio = ep.get("audio", "")
                if ep_num == episode_number and ep_audio == category and provider in ep_id:
                    slug = ep_id.split(f"/{category}/")[-1] if f"/{category}/" in ep_id else ep_id.split("/")[-1]
                    return {
                        "provider": provider,
                        "slug": slug,
                        "category": category,
                        "episode_number": episode_number,
                        "title": ep.get("title", f"Episode {episode_number}"),
                        "image": ep.get("image", ""),
                        "air_date": ep.get("airDate", "")
                    }
        
        # Fallback: any provider with matching audio
        for ep in episodes_data:
            ep_num = ep.get("number", 0)
            ep_audio = ep.get("audio", "")
            if ep_num == episode_number and ep_audio == category:
                ep_id = ep.get("id", "")
                slug = ep_id.split(f"/{category}/")[-1] if f"/{category}/" in ep_id else ep_id.split("/")[-1]
                for provider in self.PROVIDERS:
                    if provider in ep_id:
                        return {
                            "provider": provider,
                            "slug": slug,
                            "category": category,
                            "episode_number": episode_number,
                            "title": ep.get("title", f"Episode {episode_number}"),
                            "image": ep.get("image", ""),
                            "air_date": ep.get("airDate", "")
                        }
        
        return None

    async def resolve_stream_url(self, episodes_data: list, episode_number: int, category: str = "sub") -> Optional[str]:
        """
        Resolve the best stream URL for an episode.
        
        Args:
            episodes_data: Raw episodes data from API
            episode_number: Episode number
            category: Audio category (sub/dub)
            
        Returns:
            Stream URL (M3U8 or direct) or None
        """
        stream_info = self.get_episode_stream_info(episodes_data, episode_number, category)
        if not stream_info:
            return None
        
        provider = stream_info["provider"]
        slug = stream_info["slug"]
        anime_id = episodes_data[0].get("id", "").split("/")[2] if episodes_data else None
        
        if not anime_id:
            return None
        
        # Try to get stream data
        stream_data = await self.get_stream(provider, int(anime_id), category, slug)
        if not stream_data:
            # Fallback to download endpoint
            download_data = await self.get_download(provider, int(anime_id), category, slug)
            if download_data and download_data.get("download"):
                return download_data["download"]
            return None
        
        # Priority: bestStream -> active HLS -> download link
        if "bestStream" in stream_data and stream_data["bestStream"]:
            best = stream_data["bestStream"]
            if best.get("url"):
                return best["url"]
        
        if "streams" in stream_data:
            for s in stream_data["streams"]:
                if s.get("type") == "hls" and s.get("isActive"):
                    return s["url"]
        
        if "download" in stream_data:
            return stream_data["download"]
        
        return None

    # =========================================================================
    # Batch Operations
    # =========================================================================
    async def batch_resolve_streams(self, episodes_data: list, episode_numbers: list, category: str = "sub", concurrency: int = 3) -> Dict[int, Optional[str]]:
        """
        Resolve stream URLs for multiple episodes concurrently.
        
        Args:
            episodes_data: Raw episodes data from API
            episode_numbers: List of episode numbers to resolve
            category: Audio category (sub/dub)
            concurrency: Max concurrent requests
            
        Returns:
            Dict of episode_number -> stream_url
        """
        semaphore = asyncio.Semaphore(concurrency)
        results = {}

        async def resolve_one(ep_num: int):
            async with semaphore:
                url = await self.resolve_stream_url(episodes_data, ep_num, category)
                results[ep_num] = url

        tasks = [resolve_one(ep_num) for ep_num in episode_numbers]
        await asyncio.gather(*tasks, return_exceptions=True)
        return results


# =============================================================================
# Global Instance
# =============================================================================
anime_client = MiruroAPI()
