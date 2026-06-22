# =============================================================================
# Telegram Leech Bot - User Moderation System
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
User moderation system for private group mode.

Features:
  - Warn/unwarn users (auto-ban after MAX_WARNS)
  - Ban/unban users permanently
  - Track user activity (downloads, uploads)
  - Block banned users from using bot
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import config

logger = logging.getLogger(__name__)


# =============================================================================
# Moderation Database (JSON file-based)
# =============================================================================
class ModerationDB:
    """Persistent moderation database (JSON file)."""

    _path = str(config.BASE_DIR / "moderation.json")
    _data = {}

    @classmethod
    def _load(cls):
        """Load database from file."""
        if not cls._data and os.path.exists(cls._path):
            try:
                with open(cls._path, "r") as f:
                    cls._data = json.load(f)
            except Exception:
                cls._data = {}

    @classmethod
    def _save(cls):
        """Save database to file."""
        try:
            with open(cls._path, "w") as f:
                json.dump(cls._data, f, indent=2)
        except Exception as e:
            logger.error("Failed to save moderation DB: %s", e)

    @classmethod
    def get_user(cls, user_id: int) -> dict:
        """Get user moderation data."""
        cls._load()
        uid = str(user_id)
        if uid not in cls._data:
            cls._data[uid] = {
                "warns": 0,
                "banned": False,
                "warn_reasons": [],
                "total_downloads": 0,
                "total_uploads": 0,
                "last_activity": None,
                "ban_reason": "",
                "banned_at": None,
            }
        return cls._data[uid]

    @classmethod
    def warn(cls, user_id: int, reason: str = "") -> int:
        """Warn a user. Returns total warns. Auto-bans at MAX_WARNS."""
        cls._load()
        user = cls.get_user(user_id)
        user["warns"] += 1
        if reason:
            user["warn_reasons"].append({
                "reason": reason,
                "at": datetime.now().isoformat(),
            })
        user["last_activity"] = datetime.now().isoformat()

        # Auto-ban at max warns
        if user["warns"] >= config.MAX_WARNS:
            user["banned"] = True
            user["ban_reason"] = f"Auto-banned: {user['warns']} warns reached"
            user["banned_at"] = datetime.now().isoformat()
            logger.info("User %d auto-banned after %d warns", user_id, user["warns"])

        cls._save()
        return user["warns"]

    @classmethod
    def unwarn(cls, user_id: int) -> int:
        """Remove one warn from user. Returns remaining warns."""
        cls._load()
        user = cls.get_user(user_id)
        if user["warns"] > 0:
            user["warns"] -= 1
            if user["warn_reasons"]:
                user["warn_reasons"].pop()
        cls._save()
        return user["warns"]

    @classmethod
    def ban(cls, user_id: int, reason: str = "") -> bool:
        """Ban a user permanently."""
        cls._load()
        user = cls.get_user(user_id)
        user["banned"] = True
        user["ban_reason"] = reason or "Banned by admin"
        user["banned_at"] = datetime.now().isoformat()
        cls._save()
        return True

    @classmethod
    def unban(cls, user_id: int) -> bool:
        """Unban a user."""
        cls._load()
        user = cls.get_user(user_id)
        user["banned"] = False
        user["warns"] = 0
        user["ban_reason"] = ""
        user["banned_at"] = None
        user["warn_reasons"] = []
        cls._save()
        return True

    @classmethod
    def is_banned(cls, user_id: int) -> bool:
        """Check if user is banned."""
        cls._load()
        user = cls.get_user(user_id)
        return user.get("banned", False)

    @classmethod
    def get_warns(cls, user_id: int) -> int:
        """Get user's warn count."""
        cls._load()
        user = cls.get_user(user_id)
        return user.get("warns", 0)

    @classmethod
    def track_activity(cls, user_id: int, activity_type: str = "download"):
        """Track user activity."""
        cls._load()
        user = cls.get_user(user_id)
        user["last_activity"] = datetime.now().isoformat()
        if activity_type == "download":
            user["total_downloads"] = user.get("total_downloads", 0) + 1
        elif activity_type == "upload":
            user["total_uploads"] = user.get("total_uploads", 0) + 1
        cls._save()

    @classmethod
    def get_stats(cls, user_id: int) -> dict:
        """Get user moderation stats."""
        cls._load()
        user = cls.get_user(user_id)
        return {
            "warns": user.get("warns", 0),
            "max_warns": config.MAX_WARNS,
            "banned": user.get("banned", False),
            "total_downloads": user.get("total_downloads", 0),
            "total_uploads": user.get("total_uploads", 0),
            "last_activity": user.get("last_activity"),
            "ban_reason": user.get("ban_reason", ""),
        }

    @classmethod
    def list_banned(cls) -> list:
        """List all banned users."""
        cls._load()
        banned = []
        for uid, data in cls._data.items():
            if data.get("banned"):
                banned.append({
                    "user_id": int(uid),
                    "reason": data.get("ban_reason", ""),
                    "banned_at": data.get("banned_at", ""),
                })
        return banned

    @classmethod
    def list_warned(cls) -> list:
        """List all warned users."""
        cls._load()
        warned = []
        for uid, data in cls._data.items():
            if data.get("warns", 0) > 0 and not data.get("banned"):
                warned.append({
                    "user_id": int(uid),
                    "warns": data.get("warns", 0),
                    "reasons": data.get("warn_reasons", []),
                })
        return warned


# =============================================================================
# Moderation Helper
# =============================================================================
class Moderation:
    """Moderation helper for checking and enforcing rules."""

    @staticmethod
    def check_access(user_id: int) -> tuple[bool, str]:
        """
        Check if user can use the bot.
        Returns (allowed, reason_if_not).
        """
        # Owner always allowed
        if user_id == config.OWNER_ID:
            return True, ""

        # Admins always allowed
        if user_id in config.ALLOWED_ADMINS:
            return True, ""

        # Check if banned
        if ModerationDB.is_banned(user_id):
            user = ModerationDB.get_user(user_id)
            reason = user.get("ban_reason", "Banned by admin")
            return False, f"🚫 You are banned!\n\n<b>Reason:</b> {reason}"

        # Check warn status
        warns = ModerationDB.get_warns(user_id)
        if warns >= config.MAX_WARNS:
            ModerationDB.ban(user_id, f"Auto-banned: {warns} warns")
            return False, f"🚫 You have been auto-banned after {warns} warnings!"

        # Private group mode: check if user is allowed
        if config.BOT_PRIVATE:
            if user_id not in config.ALLOWED_USERS and user_id not in config.ALLOWED_ADMINS:
                return False, "❌ You are not authorized to use this bot."

        return True, ""

    @staticmethod
    def format_user_info(user_id: int) -> str:
        """Format user info for admin display."""
        stats = ModerationDB.get_stats(user_id)
        warns = stats["warns"]
        max_w = stats["max_warns"]
        banned = stats["banned"]
        downloads = stats["total_downloads"]
        uploads = stats["total_uploads"]
        last = stats["last_activity"] or "Never"
        ban_reason = stats["ban_reason"]

        status = "🚫 BANNED" if banned else (f"⚠️ {warns}/{max_w} warns" if warns > 0 else "✅ Active")

        text = (
            f"<b>👤 User:</b> <code>{user_id}</code>\n"
            f"<b>📊 Status:</b> {status}\n"
            f"<b>📥 Downloads:</b> {downloads}\n"
            f"<b>📤 Uploads:</b> {uploads}\n"
            f"<b>🕐 Last Active:</b> {last}\n"
        )
        if banned and ban_reason:
            text += f"<b>🚫 Ban Reason:</b> {ban_reason}\n"
        if warns > 0:
            reasons = stats.get("warn_reasons", []) if isinstance(stats, dict) else []
            if reasons:
                text += "<b>⚠️ Warn Reasons:</b>\n"
                for r in reasons[-3:]:  # Show last 3
                    text += f"  • {r.get('reason', 'No reason')}\n"

        return text
