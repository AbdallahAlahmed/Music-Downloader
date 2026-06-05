
import yt_dlp

from src.config import (
    YDL_OPTS,
    LOG_FILE,
)

from src.archive import (
    append_download_log,
)
from src.config import YDL_OPTS, ARCHIVE_FILE


class MusicDownloader:
    """
    Handles YouTube Music playlist downloads
    using yt-dlp and FFmpeg.
    """

    def __init__(self, log_callback=None):
        """
        Initialize downloader configuration.
        """
        self.options = YDL_OPTS
        self.log_callback = log_callback

        self.current_title = None

    def download_playlist(self, url):
        """
        Download a YouTube playlist and convert
        all tracks to MP3.

        Args:
            url (str): Playlist URL.
        """

        
        def progress_hook(status):
            """
            Log completed downloads.
            """
            if status.get("status") == "downloading":

                title = (
                    status
                    .get("info_dict", {})
                    .get("title")
                )
                if (
                    title
                    and title != self.current_title
                ):
                    
                    self.current_title = title
                    
                    if self.log_callback:
                        self.log_callback(f"Downloading: {title}...")

            if status.get("status") == "finished":
                append_download_log(
                    LOG_FILE,
                    status.get("info_dict", {})
                )

        self.options["progress_hooks"] = [progress_hook]

        with yt_dlp.YoutubeDL(self.options) as ydl:
            ydl.download([url])
