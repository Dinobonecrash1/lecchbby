"""Callback query handlers package."""

# Import dispatcher submodule to register the callback router;
# dispatcher imports the other submodules automatically.
from . import dispatcher
from . import anime  # Anime download callbacks
