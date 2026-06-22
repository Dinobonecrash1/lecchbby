# =============================================================================
# Telegram Leech Bot - Downloader Modules
# =============================================================================
# Project   : LeechBot
# Developer : Shinei Nouzen
# GitHub    : https://github.com/Shineii86
# Telegram  : https://telegram.me/Shineii86
# =============================================================================

"""
LeechBot downloader modules.

This package contains all downloader implementations for various sources.
"""

from .aria2 import aria2_Download, get_Aria2c_Name
from .gdrive import build_service, g_DownLoad, get_Gfolder_size, getFileMetadata, getIDFromURL
from .mega import megadl
from .ytdl import YTDL_Status, get_YT_Name
from .terabox import terabox_download
from .gallery import gallery_download, is_gallery_link, get_gallery_name
from .gofile import gofile_download
from .catbox import catbox_download
from .streamtape import streamtape_download
from .manager import downloadManager, calDownSize, get_d_name

__all__ = [
    "aria2_Download",
    "get_Aria2c_Name",
    "build_service",
    "g_DownLoad",
    "get_Gfolder_size",
    "getFileMetadata",
    "getIDFromURL",
    "megadl",
    "YTDL_Status",
    "get_YT_Name",
    "terabox_download",
    "gallery_download",
    "is_gallery_link",
    "get_gallery_name",
    "gofile_download",
    "catbox_download",
    "streamtape_download",
    "downloadManager",
    "calDownSize",
    "get_d_name",
]
