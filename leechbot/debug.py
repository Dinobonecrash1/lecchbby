# =============================================================================
# Telegram Leech Bot - Debug & Error Reporting
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================

"""
Debug logging and error reporting to Telegram.

Provides:
- TelegramLogHandler: sends ERROR/CRITICAL logs to DUMP_ID channel
- setup_error_reporting: installs asyncio + Pyrogram error hooks
- send_debug: manual debug message sender
"""

import asyncio
import logging
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)


# =============================================================================
# Telegram Log Handler — sends errors to DUMP_ID
# =============================================================================
class TelegramLogHandler(logging.Handler):
    """
    Logging handler that sends ERROR and CRITICAL level messages
    to the configured DUMP_ID channel via Telegram.
    """

    def __init__(self, client, dump_id: int, level=logging.ERROR):
        super().__init__(level=level)
        self.client = client
        self.dump_id = dump_id
        self._loop = None
        self._queue = asyncio.Queue()
        self._running = False

    def emit(self, record):
        """Queue the log record for async sending."""
        if not self._running:
            return
        try:
            msg = self.format(record)
            loop = self._loop
            if loop and loop.is_running():
                loop.call_soon_threadsafe(self._queue.put_nowait, msg)
        except Exception:
            pass

    async def _sender(self):
        """Background task that sends queued messages to Telegram."""
        while self._running:
            try:
                msg = await asyncio.wait_for(self._queue.get(), timeout=5.0)
            except asyncio.TimeoutError:
                continue
            except Exception:
                await asyncio.sleep(1)
                continue

            try:
                await self.client.send_message(
                    chat_id=self.dump_id,
                    text=msg,
                    disable_web_page_preview=True,
                )
            except Exception as e:
                # Don't recurse — just log to stderr
                print(f"[TelegramLogHandler] Failed to send log: {e}", flush=True)

    async def start(self):
        """Start the background sender task."""
        self._loop = asyncio.get_event_loop()
        self._running = True
        asyncio.create_task(self._sender())

    def stop(self):
        """Stop the background sender."""
        self._running = False

    def format(self, record):
        """Format log record as Telegram-friendly message."""
        level_emoji = {
            logging.ERROR: "🔴",
            logging.CRITICAL: "💀",
            logging.WARNING: "🟡",
        }
        emoji = level_emoji.get(record.levelno, "ℹ️")
        time_str = datetime.now().strftime("%H:%M:%S")

        msg = f"{emoji} **{record.levelname}** `{time_str}`\n"
        msg += f"**Module:** `{record.name}`\n"
        msg += f"**Message:**\n`{record.getMessage()[:1500]}`"

        # Include traceback for exceptions
        if record.exc_info and record.exc_info[1]:
            tb = "".join(traceback.format_exception(*record.exc_info))
            # Truncate long tracebacks
            if len(tb) > 1000:
                tb = tb[:500] + "\n...\n" + tb[-500:]
            msg += f"\n\n**Traceback:**\n`{tb}`"

        return msg


# =============================================================================
# Asyncio Exception Handler
# =============================================================================
class AsyncExceptionHandler:
    """
    Catches unhandled asyncio task exceptions and reports them to Telegram.
    """

    def __init__(self, client, dump_id: int):
        self.client = client
        self.dump_id = dump_id

    def handle(self, loop, context):
        """Handle unhandled asyncio exceptions."""
        exception = context.get("exception")
        message = context.get("message", "Unhandled exception in asyncio task")

        if exception:
            tb = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
            if len(tb) > 1500:
                tb = tb[:750] + "\n...\n" + tb[-750:]
        else:
            tb = "No traceback available"

        error_msg = (
            f"💀 **Unhandled Asyncio Exception**\n\n"
            f"**Message:** `{message}`\n"
            f"**Exception:** `{type(exception).__name__}: {exception}`\n\n"
            f"**Traceback:**\n`{tb}`"
        )

        # Send to Telegram (non-blocking)
        try:
            loop.create_task(self._send(error_msg))
        except Exception:
            print(f"[AsyncExceptionHandler] {error_msg}", flush=True)

        # Also log to stderr
        print(f"[Asyncio Error] {context}", flush=True)

    async def _send(self, msg: str):
        """Send error message to Telegram."""
        try:
            await self.client.send_message(
                chat_id=self.dump_id,
                text=msg[:4096],
                disable_web_page_preview=True,
            )
        except Exception as e:
            print(f"[AsyncExceptionHandler] Failed to send: {e}", flush=True)


# =============================================================================
# Setup Function
# =============================================================================
async def setup_error_reporting(client, dump_id: int, owner_id: int):
    """
    Install all error reporting hooks:
    1. TelegramLogHandler — sends ERROR/CRITICAL logs to DUMP_ID
    2. Asyncio exception handler — catches unhandled task errors
    """
    if not dump_id:
        logger.warning("DUMP_ID not set — error reporting to Telegram disabled")
        return

    # 1. Telegram log handler
    tg_handler = TelegramLogHandler(client, dump_id, level=logging.ERROR)
    tg_handler.setFormatter(logging.Formatter("%(message)s"))
    logging.getLogger().addHandler(tg_handler)
    await tg_handler.start()
    logger.info("✅ Telegram error reporting enabled → %s", dump_id)

    # 2. Asyncio exception handler
    loop = asyncio.get_event_loop()
    async_handler = AsyncExceptionHandler(client, dump_id)
    loop.set_exception_handler(async_handler.handle)
    logger.info("✅ Asyncio exception handler installed")

    return tg_handler


# =============================================================================
# Manual Debug Sender
# =============================================================================
async def send_debug(client, dump_id: int, message: str, level: str = "info"):
    """
    Send a debug message to the DUMP_ID channel.

    Args:
        client: Pyrogram client
        dump_id: target chat ID
        message: debug text
        level: "info", "warning", "error"
    """
    emoji = {"info": "ℹ️", "warning": "🟡", "error": "🔴"}.get(level, "ℹ️")
    time_str = datetime.now().strftime("%H:%M:%S")
    text = f"{emoji} **Debug** `{time_str}`\n\n`{message[:3500]}`"

    try:
        await client.send_message(
            chat_id=dump_id,
            text=text,
            disable_web_page_preview=True,
        )
    except Exception:
        pass
