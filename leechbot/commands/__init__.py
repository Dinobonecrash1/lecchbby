# =============================================================================
# Telegram Leech Bot - Commands Package
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Commands package — imports all command modules to register handlers.

This package modularizes the commands.py file into separate modules:
- uploads.py: /tupload, /gdupload, /drupload, /ytupload, /glupload
- settings.py: /settings, /format, /speed
- help.py: /start, /help, /about
- status.py: /status, /stats, /ping
- queue.py: /queue, /cancel, /cancel_all
- admin.py: /admin, /broadcast
- cookies.py: /cookies, /setcookies, /clearcookies
- userbot.py: /userbot, /userbot_status, /userbot_logout
- system.py: /restart, /update, /logs
- utility.py: /setname, /formats, /preview, /zipaswd, /unzipaswd
"""

# Import all command modules to register handlers
from leechbot.commands.uploads import *
from leechbot.commands.settings import *
from leechbot.commands.help import *
from leechbot.commands.status import *
from leechbot.commands.queue import *
from leechbot.commands.admin import *
from leechbot.commands.cookies import *
from leechbot.commands.userbot import *
from leechbot.commands.system import *
from leechbot.commands.utility import *

__all__ = [
    "uploads",
    "settings",
    "help",
    "status",
    "queue",
    "admin",
    "cookies",
    "userbot",
    "system",
    "utility",
]