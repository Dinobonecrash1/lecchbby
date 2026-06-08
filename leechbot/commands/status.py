# =============================================================================
# Telegram Leech Bot - Status Commands
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Status command handlers — /status, /stats, /ping
"""

import logging
from datetime import datetime
from pyrogram import filters
from leechbot import app, OWNER
from leechbot.utility.variables import BOT, BotStats, BotTimes, Transfer, Messages, Queue
from leechbot.utility.helper import (
    message_deleter, format_stats, sysINFO, getTime, sizeUnit,
)
import config

logger = logging.getLogger(__name__)

# =============================================================================
# /ping
# =============================================================================
@app.on_message(filters.command("ping") & filters.private)
async def ping_command(client, message):
    """Handle the /ping command — measures Telegram round-trip latency + shows uptime."""
    start = datetime.now()
    msg = await message.reply_text("**🏓 Pinging...**", quote=True)
    latency_ms = (datetime.now() - start).total_seconds() * 1000
    uptime = getTime(int((datetime.now() - BotStats.start_time).total_seconds()))

    # ── latency quality ──
    if latency_ms < 200:
        quality = "Excellent"
    elif latency_ms < 500:
        quality = "Good"
    elif latency_ms < 1000:
        quality = "Average"
    else:
        quality = "Poor"

    pct = max(5, min(100, int((1 - latency_ms / 2000) * 100)))
    filled = pct // 5
    empty = 20 - filled
    bar = f"{'█' * filled}{'░' * empty}"

    server_status = "Online" if latency_ms < 5000 else "Slow"

    ping_text = f"""```
┌───────────────────────────────┐
        🏓  PONG
├───────────────────────────────┤
  ⚡  Latency   →  {latency_ms:.1f} ms
  📊  Quality   →  {quality}
  {bar}  {pct}%
  ⏱️  Uptime    →  {uptime}
  🤖  Version   →  v{config.VERSION}
  📡  Server    →  {server_status}
└───────────────────────────────┘
```"""
    await msg.edit(ping_text, disable_web_page_preview=True)
    await message_deleter(message, msg)

# =============================================================================
# /status
# =============================================================================
@app.on_message(filters.command("status") & filters.private)
async def status_command(client, message):
    """Handle the /status command — show active task detail + queue + transfer stats."""
    if message.chat.id != OWNER and message.chat.id not in config.ALLOWED_USERS:
        return

    # ── Active task section ──
    if BOT.State.task_going:
        task_elapsed = ""
        try:
            secs = (datetime.now() - BotTimes.task_start).total_seconds()
            task_elapsed = getTime(int(secs))
        except Exception:
            pass

        down_total = sizeUnit(sum(Transfer.down_bytes))
        up_total = sizeUnit(sum(Transfer.up_bytes))
        remaining = sizeUnit(max(Transfer.total_down_size - sum(Transfer.down_bytes), 0))

        mode = f"{BOT.Mode.type.capitalize()} {BOT.Mode.mode.capitalize()}"
        if BOT.Mode.ytdl:
            mode += " (yt-dlp)"
        elif BOT.Mode.gallery:
            mode += " (gallery-dl)"

        active_section = f"""**🎯 Active Task**

• **Mode:** `{mode}`
• **Running:** `{task_elapsed}`
• **Downloaded:** `{down_total}` ({len(Transfer.down_bytes)} chunks)
• **Uploaded:** `{up_total}` ({len(Transfer.up_bytes)} chunks)
• **Remaining:** `{remaining}`
• **Files sent:** `{len(Transfer.sent_file)}`"""
        if Messages.status_head:
            # Trim the status head for display
            head_clean = Messages.status_head.replace("**", "").replace("\n", " · ")[:120]
            active_section += f"\n• **Current:** `{head_clean}`"
    else:
        active_section = "**🎯 Active Task**\n\n• `No task running`"

    # ── Queue section ──
    pending = Queue.pending
    current = Queue.current
    if pending or current:
        queue_lines = [f"**📋 Queue** (`{pending} pending`)"]
        if current:
            link = current["links"][0][:60] + ("..." if len(current["links"][0]) > 60 else "")
            queue_lines.append(f"• 🔄 **Current:** `{link}` ({len(current['links'])} link(s))")
        for line in Queue.list_items()[:5]:
            queue_lines.append(line)
        if pending > 5:
            queue_lines.append(f"• _... and {pending - 5} more_")
        queue_section = "\n".join(queue_lines)
    else:
        queue_section = "**📋 Queue**\n\n• `Empty`"

    status_text = f"{active_section}\n\n{queue_section}"
    msg = await message.reply_text(status_text, quote=True)
    await message_deleter(message, msg)

# =============================================================================
# /stats
# =============================================================================
@app.on_message(filters.command("stats") & filters.private)
async def stats_command(client, message):
    """Handle the /stats command — shows lifetime task counts + system info."""
    stats_text = f"{format_stats()}{sysINFO()}"
    msg = await message.reply_text(stats_text, quote=True)
    await message_deleter(message, msg)