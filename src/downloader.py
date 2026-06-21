import subprocess
import sys
import threading
import yt_dlp
from src.config import YDL_OPTS, LOG_FILE
from src.archive import append_download_log


class MusicDownloader:
    """Handles YouTube Music downloads. Uses subprocess per track so Stop really works."""

    def __init__(self, log_callback=None, progress_callback=None):
        self.log_callback = log_callback
        self.progress_callback = progress_callback
        self.stop_requested = False
        self._process = None

    def stop_download(self):
        """Hard-stop the current download by killing the subprocess."""
        self.stop_requested = True
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._process.kill()

    def _log(self, msg):
        if self.log_callback:
            self.log_callback(msg)

    def _report_progress(self, current, total):
        if self.progress_callback:
            self.progress_callback(current, total)

    def _build_cmd(self, url):
        """Convert YDL_OPTS to yt-dlp CLI arguments."""
        cmd = [sys.executable, "-m", "yt_dlp"]

        # Common options from YDL_OPTS
        if "format" in YDL_OPTS:
            cmd.extend(["-f", YDL_OPTS["format"]])

        if "outtmpl" in YDL_OPTS:
            cmd.extend(["-o", YDL_OPTS["outtmpl"]])
        else:
            cmd.extend(["-o", "music/%(title)s.%(ext)s"])

        # Postprocessors -> audio extraction args
        for pp in YDL_OPTS.get("postprocessors", []):
            key = pp.get("key", "")
            if "FFmpegExtractAudio" in key or "FFmpeg" in key:
                cmd.append("-x")
                if "preferredcodec" in pp:
                    cmd.extend(["--audio-format", pp["preferredcodec"]])
                if "preferredquality" in pp:
                    cmd.extend(["--audio-quality", str(pp["preferredquality"])])

        # Add any extra args from YDL_OPTS
        if YDL_OPTS.get("quiet"):
            cmd.append("--quiet")
        if YDL_OPTS.get("noplaylist"):
            cmd.append("--no-playlist")
        if YDL_OPTS.get("cookiefile"):
            cmd.extend(["--cookies", YDL_OPTS["cookiefile"]])

        cmd.append(url)
        return cmd

    def download_playlist(self, url):
        """Download playlist track-by-track using subprocess. Truly stoppable."""
        self.stop_requested = False

        # Step 1: Fetch info quickly with library (no download)
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            entries = info.get("entries", []) or [info]
            total = len(entries)

        self._log(f"Found {total} tracks.")

        # Step 2: Download each track in a separate subprocess
        for i, entry in enumerate(entries, start=1):
            if self.stop_requested:
                self._log("Stop signal received. Aborting.")
                raise Exception("Download stopped by user")

            title = entry.get("title", "Unknown")
            self._log(f"[{i:02d}/{total:02d}] {title}")
            self._report_progress(i, total)

            track_url = entry.get("webpage_url", entry.get("url"))
            cmd = self._build_cmd(track_url)

            # Windows: hide console window
            kwargs = {}
            if sys.platform == "win32":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                **kwargs
            )

            # Stream output to log in real-time
            for line in self._process.stdout:
                line = line.strip()
                if line:
                    self._log(line)

            self._process.wait()
            exit_code = self._process.returncode
            self._process = None

            if self.stop_requested:
                break

            if exit_code != 0:
                raise Exception(f"Download failed for {title} (exit code {exit_code})")

        if not self.stop_requested:
            self._log("All downloads finished.")