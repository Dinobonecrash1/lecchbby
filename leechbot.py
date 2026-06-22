#!/usr/bin/env python3
# =============================================================================
# Telegram Leech Bot - Simple Entry Point
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Simple wrapper to start LeechBot with:

    python3 leechbot.py

This delegates to the package entry point (leechbot/__main__.py) using runpy,
so you don't need to remember the `-m leechbot` syntax.
"""

import runpy

if __name__ == "__main__":
    runpy.run_module("leechbot", run_name="__main__")
