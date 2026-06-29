"""Command handlers package."""

# Import submodules to register Pyrogram handlers
from . import admin
from . import downloads
from . import options
from . import rss
from . import settings
from . import start_help
from . import status
from . import anime  # Anime download commands
from . import autorename  # Auto-rename template commands

# Re-export helpers used by other packages
from .start_help import _send_welcome
