
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

    def __init__(self, log_callback=None, progress_callback=None):
        """
        Initialize downloader configuration.
        """
        self.options = YDL_OPTS
        self.log_callback = log_callback
        self.progress_callback = progress_callback
        self.current_title = None

    def _report_progress(self, current, total):
        """
        Report download progress to the GUI.
        """
        if self.progress_callback and current and total:
            self.progress_callback(current, total)

    def download_playlist(self, url):
        """
        Download a YouTube playlist and convert all tracks to MP3.
        """
        # Kopieer opts zodat we progress_hooks kunnen toevoegen
        ydl_opts = dict(self.options)

        # BELANGRIJK: progress_hook als METHOD doorgeven (zonder haakjes!)
        ydl_opts['progress_hooks'] = [self.progress_hook]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            # Fallback: als yt-dlp geen playlist info geeft, rapporteer 1/1
            entries = info.get('entries', [info])
            total = len(entries) if entries else 1

            # Handmatige progress als fallback (als hooks niet werken)
            for i, entry in enumerate(entries, start=1):
                self._report_progress(i, total)

    def progress_hook(self, status):
        """
        yt-dlp roept dit aan met één argument: status dict.
        """
        if status.get("status") == "downloading":
            info_dict = status.get("info_dict", {})

            # EERST ophalen, DAN pas gebruiken
            playlist_index = info_dict.get("playlist_index")
            playlist_count = info_dict.get("playlist_count")
            title = info_dict.get("title")

            # Progress doorgeven aan GUI
            if playlist_index and playlist_count:
                self._report_progress(playlist_index, playlist_count)

            # Titel loggen als nieuw
            if title and title != self.current_title:
                self.current_title = title
                if self.log_callback:
                    self.log_callback(
                        f"[{playlist_index:02d}/{playlist_count:02d}] {title}"
                    )

        if status.get("status") == "finished":
            append_download_log(
                LOG_FILE,
                status.get("info_dict", {})
            )