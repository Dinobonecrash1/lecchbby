# =============================================================================
# Telegram Leech Bot - Auto-Rename Command
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Auto-rename template command.

Provides /autorename command for setting filename templates
with placeholders for anime/manga downloads.
"""

import logging
from pyrogram import filters
from leechbot import app
from leechbot.utility.variables import BOT

logger = logging.getLogger(__name__)


# =============================================================================
# Auto-Rename Template State
# =============================================================================
class AutoRenameState:
    """State for autorename template setting."""
    waiting_template: dict = {}  # user_id -> True when waiting for template

    def clear(self, user_id: int):
        self.waiting_template.pop(user_id, None)


autorename_state = AutoRenameState()


# =============================================================================
# /autorename Command
# =============================================================================
@app.on_message(filters.command("autorename") & filters.private)
async def autorename_command(client, message):
    """
    Set auto-rename template for downloads.
    
    Usage:
        /autorename <template>
        /autorename clear
        
    Placeholders:
        {season}    — Season number (e.g., 1)
        {episode}   — Episode number (e.g., 05)
        {quality}   — Video quality (e.g., 1080p)
        {audio}     — Audio type (SUB/DUB)
        {title}     — Anime/Manga title
        {chapter}   — Chapter number (manga)
        
    Examples:
        /autorename [S{season} E{episode}] One Piece [{quality}] [{audio}]
        /autorename [WF] [C{chapter}] One Piece @MaximXAnime
    """
    args = message.text.split(None, 1)
    
    # Clear template
    if len(args) < 2 or args[1].strip().lower() == "clear":
        BOT.Options.custom_name = ""
        BOT.Setting.prefix = ""
        await message.reply_text(
            "<b>🗑️ Auto-Rename Template Cleared</b>\n\n"
            "Files will use their default names."
        )
        return
    
    template = args[1].strip()
    
    # Validate template has valid placeholders
    valid_placeholders = ["{season}", "{episode}", "{quality}", "{audio}", "{title}", "{chapter}"]
    has_placeholder = any(p in template for p in valid_placeholders)
    
    if not has_placeholder:
        await message.reply_text(
            "<b>⚠️ Template must contain at least one placeholder:</b>\n\n"
            "• <code>{season}</code> — Season number\n"
            "• <code>{episode}</code> — Episode number\n"
            "• <code>{quality}</code> — Video quality\n"
            "• <code>{audio}</code> — Audio type (SUB/DUB)\n"
            "• <code>{title}</code> — Anime/Manga title\n"
            "• <code>{chapter}</code> — Chapter number\n\n"
            "<b>Example:</b>\n"
            "<code>/autorename [S{season} E{episode}] One Piece [{quality}] [{audio}]</code>"
        )
        return
    
    # Store template
    BOT.Options.custom_name = template
    
    # Show preview
    preview = template
    for placeholder, example in [
        ("{season}", "1"),
        ("{episode}", "05"),
        ("{quality}", "1080p"),
        ("{audio}", "SUB"),
        ("{title}", "One Piece"),
        ("{chapter}", "100"),
    ]:
        preview = preview.replace(placeholder, example)
    
    await message.reply_text(
        f"<b>✅ Auto-Rename Template Set</b>\n\n"
        f"<b>📝 Template:</b>\n<code>{template}</code>\n\n"
        f"<b>👁️ Preview:</b>\n<code>{preview}</code>\n\n"
        f"<b>💡 Note:</b> Don't put .mkv or .mp4 at the end.\n"
        f"The bot will use this template to rename your files automatically.\n\n"
        f"<b>🗑️ To clear:</b> <code>/autorename clear</code>"
    )


# =============================================================================
# Template Parser
# =============================================================================
def parse_autorename_template(template: str, **kwargs) -> str:
    """
    Parse autorename template with placeholders.
    
    Args:
        template: Template string with {placeholder} markers
        **kwargs: Values for placeholders
        
    Returns:
        Parsed filename string
    """
    result = template
    
    # Replace known placeholders
    replacements = {
        "{season}": kwargs.get("season", "1"),
        "{episode}": kwargs.get("episode", "01"),
        "{quality}": kwargs.get("quality", "Unknown"),
        "{audio}": kwargs.get("audio", "SUB"),
        "{title}": kwargs.get("title", "Unknown"),
        "{chapter}": kwargs.get("chapter", "1"),
    }
    
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, str(value))
    
    # Clean up any remaining placeholders
    import re
    result = re.sub(r'\{[^}]+\}', '', result)
    
    # Clean up extra spaces
    result = ' '.join(result.split())
    
    return result.strip()


__all__ = ["autorename_state", "parse_autorename_template"]
