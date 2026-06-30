import aiohttp
import logging
import re

logger = logging.getLogger(__name__)


class MiruroAPI:
    """Miruro API client for anime search, episodes, and streaming."""

    def __init__(self, base_url: str = None):
        if base_url is None:
            import config
            base_url = getattr(config, 'ANIME_API_URL', '')
        self.base_url = (base_url or "").rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=30)

    async def _get(self, url: str, params: dict = None) -> dict:
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        return await resp.json(content_type=None)
                    text = await resp.text()
                    logger.warning("HTTP %d from %s: %s", resp.status, url, text[:300])
                    return {"error": f"HTTP {resp.status}", "detail": text[:300]}
        except Exception as e:
            logger.error("Request failed: %s", e)
            return {"error": str(e)}

    async def search(self, query: str) -> dict:
        """Search anime by name."""
        url = f"{self.base_url}/search"
        data = await self._get(url, {"query": query})
        if "error" in data:
            return {"success": False, "message": data["error"], "results": []}

        results_data = data.get("results", {})
        results = results_data.get("results", []) if isinstance(results_data, dict) else results_data
        return {
            "success": True,
            "results": results,
            "query": query,
        }

    async def get_episodes(self, anilist_id: int) -> dict:
        """Get episode list for an anime."""
        url = f"{self.base_url}/episodes/{anilist_id}"
        data = await self._get(url)
        if "error" in data:
            return {"success": False, "message": data["error"], "results": {}}

        results = data.get("results", {})
        return {"success": True, "results": results}

    async def get_stream(self, provider: str, anilist_id: int, category: str, slug: str) -> dict:
        """Get streaming URL for an episode."""
        url = f"{self.base_url}/watch/{provider}/{anilist_id}/{category}/{slug}"
        data = await self._get(url)
        if "error" in data:
            return {"success": False, "message": data["error"], "results": {}}

        results = data.get("results", {})
        streams = results.get("streams", [])

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
                    "referer": best_stream.get("referer", "https://kwik.cx/"),
                }
            }

        return {"success": False, "message": "No M3U8 stream found"}

    def get_episode_stream_info(self, episodes_data: dict, ep_num: int, category: str = "sub") -> dict:
        """Extract stream info for specific episode number."""
        if not episodes_data:
            return None

        providers = episodes_data.get("providers", {})
        if not providers:
            return None

        for provider_name, provider_data in providers.items():
            eps = provider_data.get("episodes", {}).get(category, [])
            for ep in eps:
                if ep.get("number") == ep_num:
                    ep_id = ep.get("id", "")
                    # Parse episode ID: "watch/kiwi/20/sub/animepahe-1"
                    parts = ep_id.split("/")
                    if len(parts) >= 5:
                        prov = parts[1]
                        anilist_id = int(parts[2])
                        cat = parts[3]
                        slug = parts[4]
                    else:
                        prov = provider_name
                        anilist_id = None
                        cat = category
                        slug = ep_id

                    return {
                        "provider": prov,
                        "anilist_id": anilist_id,
                        "category": cat,
                        "slug": slug,
                        "episode_id": ep_id,
                        "number": ep_num,
                        "title": ep.get("title", ""),
                    }

        return None

    def format_search_results(self, results: list) -> list:
        """Format search results for display."""
        formatted = []
        for item in results:
            title = item.get("title", {})
            if isinstance(title, dict):
                title_str = title.get("english") or title.get("romaji") or "Unknown"
            else:
                title_str = str(title) if title else "Unknown"

            episodes = item.get("episodes", "?")
            cover = item.get("coverImage", {})
            if isinstance(cover, dict):
                cover_url = cover.get("extraLarge") or cover.get("large", "")
            else:
                cover_url = cover or ""
            anime_id = item.get("id", "")

            display = f"<b>{title_str}</b>\n📺 {episodes} episodes"

            formatted.append({
                "title": title_str,
                "display": display,
                "episodes": episodes,
                "cover": cover_url,
                "id": anime_id,
                "raw": item,
            })

        return formatted


anime_client = MiruroAPI()
