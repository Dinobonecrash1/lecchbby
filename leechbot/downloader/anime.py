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
Supports MiruroAPI and AniKotoAPI providers.
"""

import logging
import asyncio
from typing import Optional, Dict, List, Any
import aiohttp

logger = logging.getLogger(__name__)

# =============================================================================
# API Configuration
# =============================================================================
MIRURO_API_BASE = "https://miruroapi.vercel.app/api"
ANIKOTO_API_BASE = "https://anikototvapi.vercel.app/api"

# Provider priority - try these in order
PROVIDER_PRIORITY = ["miruro", "anikoto"]


# =============================================================================
# MiruroAPI Client
# =============================================================================
class MiruroAPI:
    """Client for MiruroAPI (miruroapi.vercel.app)."""
    
    def __init__(self):
        self.base_url = MIRURO_API_BASE
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"User-Agent": "LeechBot/3.1.48"}
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
            logger.error(f"MiruroAPI search error: {e}")
            return {"success": False, "message": str(e)}
    
    async def get_info(self, anilist_id: int) -> Dict[str, Any]:
        """Get anime info by AniList ID."""
        session = await self._get_session()
        url = f"{self.base_url}/info/{anilist_id}"
        
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("success"):
                        return {"success": True, "results": data.get("results", {})}
                return {"success": False, "message": f"HTTP {resp.status}"}
        except Exception as e:
            logger.error(f"MiruroAPI info error: {e}")
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
            logger.error(f"MiruroAPI episodes error: {e}")
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
                        # Find best quality M3U8 URL
                        best_stream = None
                        for stream in streams:
                            if stream.get("url", "").endswith(".m3u8"):
                                best_stream = stream
                                # Prefer 1080p
                                if "1080" in stream.get("quality", ""):
                                    break
                        
                        if best_stream:
                            return {
                                "success": True,
                                "results": {
                                    "url": best_stream["url"],
                                    "quality": best_stream.get("quality", "unknown"),
                                    "subtitles": data.get("results", {}).get("subtitles", []),
                                    "skipTimes": data.get("results", {}).get("skipTimes", {})
                                }
                            }
                return {"success": False, "message": "No M3U8 stream found"}
        except Exception as e:
            logger.error(f"MiruroAPI stream error: {e}")
            return {"success": False, "message": str(e)}
    
    def get_episode_stream_info(self, episodes_data: Dict, episode_number: int, category: str = "sub") -> Optional[Dict]:
        """Extract stream info for a specific episode number from episodes data."""
        providers = episodes_data.get("providers", {})
        
        # Try providers in priority order
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
# AniKotoAPI Client
# =============================================================================
class AniKotoAPI:
    """Client for AniKotoAPI (anikototvapi.vercel.app)."""
    
    def __init__(self):
        self.base_url = ANIKOTO_API_BASE
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"User-Agent": "LeechBot/3.1.48"}
            )
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def search(self, keyword: str, page: int = 1) -> Dict[str, Any]:
        """Search for anime."""
        session = await self._get_session()
        url = f"{self.base_url}/search"
        params = {"keyword": keyword, "page": page}
        
        try:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("success"):
                        return {"success": True, "results": data.get("results", {}).get("data", [])}
                return {"success": False, "message": f"HTTP {resp.status}"}
        except Exception as e:
            logger.error(f"AniKotoAPI search error: {e}")
            return {"success": False, "message": str(e)}
    
    async def get_info(self, slug: str) -> Dict[str, Any]:
        """Get anime info by slug."""
        session = await self._get_session()
        url = f"{self.base_url}/info"
        params = {"id": slug}
        
        try:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("success"):
                        return {"success": True, "results": data.get("results", {})}
                return {"success": False, "message": f"HTTP {resp.status}"}
        except Exception as e:
            logger.error(f"AniKotoAPI info error: {e}")
            return {"success": False, "message": str(e)}
    
    async def get_episodes(self, slug: str) -> Dict[str, Any]:
        """Get episode list by slug."""
        session = await self._get_session()
        url = f"{self.base_url}/episodes/{slug}"
        
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("success"):
                        return {"success": True, "results": data.get("results", {})}
                return {"success": False, "message": f"HTTP {resp.status}"}
        except Exception as e:
            logger.error(f"AniKotoAPI episodes error: {e}")
            return {"success": False, "message": str(e)}
    
    async def get_servers(self, episode_ids: str) -> Dict[str, Any]:
        """Get streaming servers for episodes."""
        session = await self._get_session()
        url = f"{self.base_url}/servers"
        params = {"ids": episode_ids}
        
        try:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("success"):
                        return {"success": True, "results": data.get("results", [])}
                return {"success": False, "message": f"HTTP {resp.status}"}
        except Exception as e:
            logger.error(f"AniKotoAPI servers error: {e}")
            return {"success": False, "message": str(e)}
    
    async def get_stream(self, link_id: str) -> Dict[str, Any]:
        """Get streaming URL by link_id."""
        session = await self._get_session()
        url = f"{self.base_url}/stream"
        params = {"id": link_id}
        
        try:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("success"):
                        stream_url = data.get("results", {}).get("url", "")
                        skip_data = data.get("results", {}).get("skipData", {})
                        
                        if stream_url:
                            # Try to extract M3U8 from the embed page
                            m3u8_url = await self._extract_m3u8_from_embed(session, stream_url)
                            if m3u8_url:
                                return {
                                    "success": True,
                                    "results": {
                                        "url": m3u8_url,
                                        "skipTimes": skip_data,
                                        "quality": "adaptive"
                                    }
                                }
                            # Fallback: return embed URL for yt-dlp to handle
                            return {
                                "success": True,
                                "results": {
                                    "url": stream_url,
                                    "skipTimes": skip_data,
                                    "quality": "adaptive"
                                }
                            }
                return {"success": False, "message": "No stream URL found"}
        except Exception as e:
            logger.error(f"AniKotoAPI stream error: {e}")
            return {"success": False, "message": str(e)}
    
    async def _extract_m3u8_from_embed(self, session: aiohttp.ClientSession, embed_url: str) -> Optional[str]:
        """Try to extract M3U8 URL from an embed page."""
        import re
        try:
            async with session.get(embed_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    # Look for M3U8 URLs in the HTML
                    m3u8_patterns = [
                        r'(https?://[^\s"\']+\.m3u8[^\s"\']*)',
                        r'file["\']?\s*[:=]\s*["\']?(https?://[^\s"\']+\.m3u8)',
                        r'source["\']?\s*[:=]\s*["\']?(https?://[^\s"\']+\.m3u8)',
                    ]
                    for pattern in m3u8_patterns:
                        match = re.search(pattern, html, re.IGNORECASE)
                        if match:
                            return match.group(1).rstrip("'\"")
        except Exception as e:
            logger.debug(f"M3U8 extraction failed: {e}")
        return None


# =============================================================================
# Unified Anime Client
# =============================================================================
class AnimeClient:
    """Unified anime client that manages multiple API providers."""
    
    def __init__(self, preferred_provider: str = "miruro"):
        self.miruro = MiruroAPI()
        self.anikoto = AniKotoAPI()
        self.preferred_provider = preferred_provider
    
    async def close(self):
        await self.miruro.close()
        await self.anikoto.close()
    
    async def search(self, query: str) -> Dict[str, Any]:
        """Search for anime across providers."""
        # Try preferred provider first
        if self.preferred_provider == "miruro":
            result = await self.miruro.search(query)
            if result.get("success"):
                return result
            result = await self.anikoto.search(query)
            if result.get("success"):
                return result
        else:
            result = await self.anikoto.search(query)
            if result.get("success"):
                return result
            result = await self.miruro.search(query)
            if result.get("success"):
                return result
        
        return {"success": False, "message": "Search failed on all providers"}
    
    async def get_episodes(self, anime_id: Any, provider: str = "miruro") -> Dict[str, Any]:
        """Get episode list."""
        if provider == "miruro":
            return await self.miruro.get_episodes(anime_id)
        else:
            return await self.anikoto.get_episodes(anime_id)
    
    async def get_stream_url(self, episode_data: Dict, provider: str = "miruro") -> Dict[str, Any]:
        """Get streaming URL for an episode."""
        if provider == "miruro":
            return await self.miruro.get_stream(
                episode_data["provider"],
                episode_data["anilist_id"],
                episode_data["category"],
                episode_data["slug"]
            )
        else:
            # AniKoto flow: get servers then stream
            servers_result = await self.anikoto.get_servers(episode_data.get("episode_ids", ""))
            if not servers_result.get("success"):
                return servers_result
            
            servers = servers_result.get("results", [])
            # Find sub server first, then dub
            target_server = None
            for server in servers:
                if server.get("type") == episode_data.get("category", "sub"):
                    target_server = server
                    break
            
            if not target_server and servers:
                target_server = servers[0]
            
            if target_server:
                return await self.anikoto.get_stream(target_server.get("link_id", ""))
            
            return {"success": False, "message": "No server found"}
    
    def format_search_results(self, results: List[Dict], provider: str = "miruro") -> List[Dict]:
        """Format search results for display."""
        formatted = []
        for item in results[:10]:
            if provider == "miruro":
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
            else:
                title = item.get("title", "Unknown")
                slug = item.get("slug", "")
                anime_id = item.get("animeId", slug)
                total = item.get("total", "?")
                sub = item.get("sub", 0)
                dub = item.get("dub", 0)
                poster = item.get("poster", "")
                
                formatted.append({
                    "id": anime_id,
                    "slug": slug,
                    "title": title,
                    "episodes": total,
                    "cover": poster,
                    "format": item.get("type", ""),
                    "status": "",
                    "score": 0,
                    "display": f"🎬 {title}\n📺 {total} episodes (Sub: {sub}, Dub: {dub})"
                })
        
        return formatted


# =============================================================================
# Singleton instance
# =============================================================================
anime_client = AnimeClient()
