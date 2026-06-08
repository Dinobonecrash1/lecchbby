# =============================================================================
# Telegram Leech Bot - Upload Commands
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================
# License   : MIT License
# =============================================================================

"""
Upload command handlers — /tupload, /gdupload, /drupload, /ytupload, /glupload
"""

import logging
from pyrogram import filters
from leechbot import app
from leechbot.utility.variables import BOT
from leechbot.utility.task_manager import task_starter

logger = logging.getLogger(__name__)

# =============================================================================
# /tupload
# =============================================================================
@app.on_message(filters.command("tupload") & filters.private)
async def telegram_upload_command(client, message):
    """Handle the /tupload command — leech mode."""
    BOT.Mode.mode = "leech"
    BOT.Mode.ytdl = False
    BOT.Mode.gallery = False

    text = """**⚡ Send Download Link(s)** 🔗

📋 **Follow The Pattern Below:**

<code>https://example.com/file1.mp4
https://example.com/file2.mp4
[Custom Name.mp4]
{Zip Password}
(Unzip Password)</code>

─── Tips ───
• Multiple Links Supported
• Use `[ ]` For Custom Filename
• Use `{ }` For Zip Password
• Use `( )` For Extract Password"""
    src_request_msg = await task_starter(message, text)
    BOT._src_request_msg = src_request_msg

# =============================================================================
# /gdupload
# =============================================================================
@app.on_message(filters.command("gdupload") & filters.private)
async def gdrive_upload_command(client, message):
    """Handle the /gdupload command — mirror mode."""
    BOT.Mode.mode = "mirror"
    BOT.Mode.ytdl = False
    BOT.Mode.gallery = False

    text = """**♻️ Send Download Link(s)** 🔗

📋 **Follow The Pattern Below:**

<code>https://example.com/file1.mp4
https://example.com/file2.mp4
[Custom Name.mp4]
{Zip Password}
(Unzip Password)</code>

─── Tips ───
• Multiple Links Supported
• Files Will Be Mirrored To Your GDrive
• Make Sure GDrive Is Mounted"""
    src_request_msg = await task_starter(message, text)
    BOT._src_request_msg = src_request_msg

# =============================================================================
# /drupload
# =============================================================================
@app.on_message(filters.command("drupload") & filters.private)
async def directory_upload_command(client, message):
    """Handle the /drupload command — directory leech mode."""
    BOT.Mode.mode = "dir-leech"
    BOT.Mode.ytdl = False
    BOT.Mode.gallery = False

    text = """**📁 Send Folder Path**

📋 **Example:**

<code>/home/user/Downloads/myfolder</code>

─── Note ───
• Provide Absolute Path To The Folder
• Ensure The Bot Has Read Permissions"""
    src_request_msg = await task_starter(message, text)
    BOT._src_request_msg = src_request_msg

# =============================================================================
# /ytupload
# =============================================================================
@app.on_message(filters.command("ytupload") & filters.private)
async def ytdl_upload_command(client, message):
    """Handle the /ytupload command — YT-DLP mode."""
    BOT.Mode.mode = "leech"
    BOT.Mode.ytdl = True
    BOT.Mode.gallery = False

    text = """**🏮 Send YT-DLP Link(s)** 🔗

📋 **Follow The Pattern Below:**

<code>https://youtube.com/watch?v=xxxxx
https://youtu.be/xxxxx
[Custom Name.mp4]
{Zip Password}</code>

─── Supported Sites ───
• YouTube, Facebook
• Twitter, TikTok, Vimeo, Dailymotion
• And 2000+ more sites"""
    src_request_msg = await task_starter(message, text)
    BOT._src_request_msg = src_request_msg

# =============================================================================
# /glupload
# =============================================================================
@app.on_message(filters.command("glupload") & filters.private)
async def gallery_upload_command(client, message):
    """Handle the /glupload command — gallery-dl mode for image galleries."""
    BOT.Mode.mode = "leech"
    BOT.Mode.ytdl = False
    BOT.Mode.gallery = True

    text = """**📸 Send Gallery Link(s)** 🖼️

📋 **Follow The Pattern Below:**

<code>https://twitter.com/username
https://pinterest.com/user/board
https://pixiv.net/users/123456
[Custom Name]
{Zip Password}</code>

─── Supported Sites ───
• Twitter / X, Pinterest
• Pixiv, DeviantArt, ArtStation, Flickr
• Reddit, Tumblr, Imgur, TikTok
• Bluesky, Newgrounds, Danbooru
• And 100+ more gallery sites

─── Tips ───
• Multiple Links Supported
• Use `[ ]` For Custom Folder Name
• Use `{ }` For Zip Password"""
    src_request_msg = await task_starter(message, text)
    BOT._src_request_msg = src_request_msg