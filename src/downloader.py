import yt_dlp

from src.config import (
    ARCHIVE_FILE,
    FFMPEG_PATH,
    OUTPUT_TEMPLATE,
)


def download_music_playlist(url):

    ydl_opts = {

        "format": "bestaudio/best",

        "outtmpl": OUTPUT_TEMPLATE,

        "ffmpeg_location": FFMPEG_PATH,

        "writethumbnail": True,

        "addmetadata": True,

        "concurrent_fragment_downloads": 4,

        "download_archive": ARCHIVE_FILE,

        "keepvideo": False,

        "retries": 10,
        "fragment_retries": 10,

        "ignoreerrors": True,

        "quiet": False,

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
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
