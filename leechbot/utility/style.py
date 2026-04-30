# =============================================================================
# Telegram Leech Bot - Text Styling Utilities
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Text styling for Telegram messages using Unicode small caps and formatting helpers.
Used by the welcome message and status displays.
"""

# Mapping from normal lowercase letters to small caps Unicode
SMALL_CAPS_MAP = {
    'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ',
    'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ',
    'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ',
    'p': 'ᴘ', 'q': 'ҩ', 'r': 'ʀ', 's': 's', 't': 'ᴛ',
    'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ',
    'z': 'ᴢ'
}


def to_small_caps(text: str) -> str:
    """Convert lowercase letters to small caps Unicode; leave other characters unchanged."""
    return ''.join(SMALL_CAPS_MAP.get(c, c) for c in text)


def style_text(text: str) -> str:
    """Convert lowercase letters to small caps while preserving original case."""
    return to_small_caps(text)


def style_title(text: str) -> str:
    """Convert text to Title Case with small caps for lowercase letters."""
    words = text.split(' ')
    styled_words = []
    for w in words:
        if not w:
            styled_words.append(w)
            continue
        styled = w[0].upper() + to_small_caps(w[1:].lower())
        styled_words.append(styled)
    return ' '.join(styled_words)


def style_button(text: str) -> str:
    """Style button text using Title Case with small caps."""
    return style_title(text)


def progress_text_bar(percentage: float, length: int = 12, filled_char: str = "█", empty_char: str = "░") -> str:
    """Generate a visual progress bar string."""
    filled = int(percentage / 100 * length)
    return filled_char * filled + empty_char * (length - filled)


def mini_stats_bar(label: str, value: float, max_value: float, length: int = 8) -> str:
    """Generate a mini labeled stats bar for inline display."""
    pct = min((value / max_value * 100), 100) if max_value > 0 else 0
    bar = progress_text_bar(pct, length)
    return f"`{bar}` {pct:.0f}% — {label}"
