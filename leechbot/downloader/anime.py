import aiohttp
import logging
import re

logger = logging.getLogger(__name__)

# Provider fallback order — try these if primary fails
PROVIDER_FALLBACK_ORDER = ["kiwi", "ally", "miruro", "animex"]


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
        """Get streaming URL for an episode from a specific provider."""
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
                    "subtitles": results.get("subtitles", []),
                }
            }

        return {"success": False, "message": "No M3U8 stream found"}

    async def get_stream_with_fallback(self, anilist_id: int, category: str, slug: str,
                                        preferred_provider: str = None,
                                        provider_slugs: dict = None) -> dict:
        """Get stream URL with multi-provider + per-provider slug fallback.

        Tries preferred provider first, then falls back through PROVIDER_FALLBACK_ORDER.
        If category (dub) fails, falls back to sub.
        Uses provider_slugs dict to get the correct slug for each provider.
        """
        # Build provider list: preferred first, then fallbacks
        providers_to_try = []
        if preferred_provider:
            providers_to_try.append(preferred_provider)
        for p in PROVIDER_FALLBACK_ORDER:
            if p not in providers_to_try:
                providers_to_try.append(p)

        # Try with requested category first, then fallback to sub
        categories_to_try = [category]
        if category != "sub":
            categories_to_try.append("sub")

        # Fallback slugs from original
        slugs_to_try = [slug]
        parts = slug.rsplit("-", 1)
        if len(parts) == 2 and parts[1].isdigit():
            slugs_to_try.append(parts[1])

        for cat in categories_to_try:
            for prov in providers_to_try:
                # Use provider-specific slug if available, else fallback slugs
                if provider_slugs and prov in provider_slugs:
                    try_slugs = [provider_slugs[prov]] + [s for s in slugs_to_try if s != provider_slugs[prov]]
                else:
                    try_slugs = slugs_to_try

                for try_slug in try_slugs:
                    try:
                        result = await self.get_stream(prov, anilist_id, cat, try_slug)
                        if result.get("success"):
                            result["results"]["provider_used"] = prov
                            result["results"]["category_used"] = cat
                            if cat != category:
                                logger.info("Fallback: %s → %s for provider %s", category, cat, prov)
                            if try_slug != slug:
                                logger.info("Slug fallback: %s → %s (provider %s)", slug, try_slug, prov)
                            return result
                    except Exception as e:
                        logger.warning("Provider %s category %s slug %s failed: %s", prov, cat, try_slug, e)
                        continue

        return {"success": False, "message": "All providers failed"}

    def get_episode_stream_info(self, episodes_data: dict, ep_num: int, category: str = "sub") -> dict:
        """Extract stream info for specific episode number with dub→sub fallback.

        Returns episode info including per-provider slugs, or None if not found.
        """
        if not episodes_data:
            return None

        providers = episodes_data.get("providers", {})
        if not providers:
            return None

        # Try requested category first, then sub as fallback
        categories_to_try = [category]
        if category != "sub":
            categories_to_try.append("sub")

        for cat in categories_to_try:
            # Collect slugs from ALL providers for this episode
            provider_slugs = {}
            for provider_name, provider_data in providers.items():
                eps = provider_data.get("episodes", {}).get(cat, [])
                for ep in eps:
                    if ep.get("number") == ep_num:
                        ep_id = ep.get("id", "")
                        parts = ep_id.split("/")
                        if len(parts) >= 5:
                            prov = parts[1]
                            anilist_id = int(parts[2])
                            parsed_cat = parts[3]
                            slug = parts[4]
                        else:
                            prov = provider_name
                            anilist_id = None
                            parsed_cat = cat
                            slug = ep_id
                        provider_slugs[prov] = slug

            if provider_slugs:
                # Use first found provider's info as base
                first_prov = list(provider_slugs.keys())[0]
                first_slug = provider_slugs[first_prov]
                return {
                    "provider": first_prov,
                    "anilist_id": anilist_id,
                    "category": parsed_cat,
                    "slug": first_slug,
                    "provider_slugs": provider_slugs,
                    "episode_id": ep_id,
                    "number": ep_num,
                    "title": ep.get("title", f"Episode {ep_num}"),
                    "requested_category": category,
                    "actual_category": cat,
                }

        return None

    def get_available_qualities(self, streams_data: dict) -> list:
        """Extract available quality options from stream results."""
        # This is a placeholder — actual quality list comes from the API
        # For now return common options
        return ["1080p", "720p", "480p"]

    def format_search_results(self, results: list) -> list:
        """Format search results for display with info card data."""
        formatted = []
        for item in results:
            title = item.get("title", {})
            if isinstance(title, dict):
                title_str = title.get("english") or title.get("romaji") or "Unknown"
                title_romaji = title.get("romaji", "")
                title_english = title.get("english", "")
            else:
                title_str = str(title) if title else "Unknown"
                title_romaji = ""
                title_english = title_str

            episodes = item.get("episodes", "?")
            cover = item.get("coverImage", {})
            if isinstance(cover, dict):
                cover_url = cover.get("extraLarge") or cover.get("large", "")
            else:
                cover_url = cover or ""
            anime_id = item.get("id", "")

            # Extract info card data
            description = item.get("description", "")
            if isinstance(description, str):
                # Strip HTML tags from description
                description = re.sub(r'<[^>]+>', '', description)[:300]

            rating = item.get("averageScore") or item.get("meanScore") or "?"
            genres = item.get("genres", [])
            if isinstance(genres, list):
                genres_str = ", ".join(genres[:5])
            else:
                genres_str = str(genres) if genres else ""

            status = item.get("status", "")
            total_ep = item.get("episodes", "?")
            season = item.get("season", "")
            year = item.get("year", "")

            display = f"<b>{title_str}</b>\n📺 {episodes} episodes"
            if rating and rating != "?":
                display += f" | ⭐ {rating}"
            if genres_str:
                display += f"\n🏷️ {genres_str}"

            formatted.append({
                "title": title_str,
                "title_romaji": title_romaji,
                "title_english": title_english,
                "display": display,
                "episodes": episodes,
                "total_episodes": total_ep,
                "cover": cover_url,
                "id": anime_id,
                "description": description,
                "rating": rating,
                "genres": genres_str,
                "status": status,
                "season": season,
                "year": year,
                "raw": item,
            })

        return formatted


anime_client = MiruroAPI()
