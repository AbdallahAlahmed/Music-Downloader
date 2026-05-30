
import yt_dlp
from src.archive import append_archive_title
from src.config import YDL_OPTS, ARCHIVE_FILE
from src.archive import (
    load_download_archive_ids,
    append_archive_title,
)


class MusicDownloader:
    """
    Handles YouTube Music playlist downloads
    using yt-dlp and FFmpeg.
    """

    def __init__(self):
        """
        Initialize downloader configuration.
        """
        self.options = YDL_OPTS

    def download_playlist(self, url):
        """
        Download a YouTube playlist and convert
        all tracks to MP3.

        Args:
            url (str): Playlist URL.
        """


        def progress_hook(status):

            if status.get("status") == "finished":
                append_archive_title(
                    ARCHIVE_FILE,
                    status.get("info_dict", {})
                )

        self.options["progress_hooks"] = [progress_hook]

        with yt_dlp.YoutubeDL(self.options) as ydl:
            ydl.download([url])
