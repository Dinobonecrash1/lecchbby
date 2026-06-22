# =============================================================================
# Telegram Leech Bot - Cloudflare Bypass Proxy
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Inbuilt Cloudflare bypass proxy server.

Starts automatically with the bot on port 3000.
Routes requests through the proxy to bypass Cloudflare protection.

Usage:
    Set CF_BYPASS_PROXY=http://127.0.0.1:3000 in .env to enable.
"""

import asyncio
import logging
from aiohttp import web

logger = logging.getLogger(__name__)

PROXY_PORT = 3000
_sessions = {}


async def _get_session():
    """Get or create aiohttp session."""
    from aiohttp import ClientSession
    if _sessions.get("main") is None or _sessions["main"].closed:
        _sessions["main"] = ClientSession()
    return _sessions["main"]


async def _proxy_handler(request):
    """Proxy requests to target host with Cloudflare bypass headers."""
    hostname = request.headers.get("x-hostname") or request.query.get("host")
    if not hostname:
        # Try to extract from URL
        hostname = request.headers.get("Host", "")

    if not hostname:
        return web.json_response({"error": "x-hostname header or ?host= required"}, status=400)

    session = await _get_session()
    target_url = f"https://{hostname}{request.path_qs}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "identity",
        "Host": hostname,
    }

    # Add custom headers from request
    for key, value in request.headers.items():
        if key.lower() not in ("host", "user-agent", "accept", "accept-language", "accept-encoding"):
            headers[key] = value

    try:
        body = await request.read()
        async with session.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=body if body else None,
            timeout=30,
            ssl=False,
        ) as resp:
            response_headers = dict(resp.headers)
            response_headers["Access-Control-Allow-Origin"] = "*"

            body = await resp.read()
            return web.Response(
                status=resp.status,
                headers=response_headers,
                body=body,
            )
    except Exception as e:
        logger.error("CF proxy error: %s", e)
        return web.json_response({"error": str(e)}, status=502)


async def _health_handler(request):
    """Health check endpoint."""
    return web.json_response({"status": "ok", "service": "cf-bypass-proxy"})


async def start_cf_proxy():
    """Start the CF bypass proxy server."""
    try:
        app = web.Application()
        app.router.add_route("*", "/health", _health_handler)
        app.router.add_route("*", "/{path_info:.*}", _proxy_handler)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PROXY_PORT)
        await site.start()
        logger.info("🔒 CF bypass proxy started on port %d", PROXY_PORT)
        return True
    except Exception as e:
        logger.warning("⚠️ CF bypass proxy failed to start: %s", e)
        return False
