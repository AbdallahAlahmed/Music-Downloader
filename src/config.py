"""
Application configuration.

Contains:
- FFmpeg settings
- yt-dlp settings
- Archive file locations
"""

FFMPEG_PATH = r"C:\ffmpeg-8.1.1-essentials_build\bin"

ARCHIVE_FILE = "logs/downloaded.txt"
LOG_FILE = "logs/download_log.txt"

YDL_OPTS = {
    "format": "bestaudio/best",

    "outtmpl": (
        "music/"
        "%(playlist_title)s/"
        "%(playlist_index)02d - %(title).50s.%(ext)s"
    ),

    "ffmpeg_location": FFMPEG_PATH,

    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        },
        {
            "key": "FFmpegMetadata",
        },
        {
            "key": "EmbedThumbnail",
        },
    ],

    "writethumbnail": True,

    "download_archive": ARCHIVE_FILE,

    "keepvideo": False,

    "ignoreerrors": True,
    "retries": 5,

    "quiet": False,
}
