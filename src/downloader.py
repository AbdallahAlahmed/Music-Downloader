import subprocess
import sys
import re
import threading
import yt_dlp
from src.config import YDL_OPTS, LOG_FILE
from src.archive import append_download_log


class MusicDownloader:
    """Download via subprocess. Echt stoppable. Skippable errors worden genegeerd."""

    def __init__(self, log_callback=None, progress_callback=None):
        self.log_callback = log_callback
        self.progress_callback = progress_callback
        self.stop_requested = False
        self._process = None

    def stop_download(self):
        """Kill het huidige download-proces onmiddellijk."""
        self.stop_requested = True
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()

    def _log(self, msg):
        if self.log_callback:
            self.log_callback(msg)

    def _report_progress(self, current, total):
        if self.progress_callback and current and total:
            self.progress_callback(current, total)

    def _strip_ansi(self, text):
        """Verwijder alle ANSI kleurcodes."""
        if not text:
            return ""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

    def _build_cmd(self, url):
        """Maak yt-dlp commando."""
        cmd = [sys.executable, "-m", "yt_dlp"]

        if "format" in YDL_OPTS:
            cmd.extend(["-f", YDL_OPTS["format"]])

        if "outtmpl" in YDL_OPTS:
            cmd.extend(["-o", YDL_OPTS["outtmpl"]])
        else:
            cmd.extend(["-o", "music/%(title)s.%(ext)s"])

        for pp in YDL_OPTS.get("postprocessors", []):
            key = pp.get("key", "")
            if "FFmpegExtractAudio" in key or "FFmpeg" in key:
                cmd.append("-x")
                if "preferredcodec" in pp:
                    cmd.extend(["--audio-format", pp["preferredcodec"]])
                if "preferredquality" in pp:
                    cmd.extend(["--audio-quality", str(pp["preferredquality"])])

        # BELANGRIJK: negeer unavailable videos, geen kleurcodes, nette output
        cmd.extend([
            "--ignore-errors",
            "--no-warnings",
            "--newline",
            "--no-color",
        ])

        if YDL_OPTS.get("quiet"):
            cmd.append("--quiet")
        if YDL_OPTS.get("noplaylist"):
            cmd.append("--no-playlist")
        if YDL_OPTS.get("cookiefile"):
            cmd.extend(["--cookies", YDL_OPTS["cookiefile"]])

        cmd.append(url)
        return cmd

    def _is_skippable(self, output_lines, exit_code):
        """Check of dit een 'mag overgeslagen' error is."""
        if exit_code == 0:
            return False
        combined = " ".join(output_lines).lower()
        skippable = [
            "private video", "unavailable", "removed", "not available",
            "members-only", "premium", "sign in", "video is private",
            "this video is not available", "content too short",
            "unable to extract", "got error: http error",
            "is not currently available", "has been removed",
        ]
        return any(s in combined for s in skippable)

    def download_playlist(self, url):
        """Download track-voor-track. Stopt écht. Skipped unavailable tracks."""
        self.stop_requested = False

        # 1. Playlist info ophalen — BELANGRIJK: ignoreerrors=True zodat private videos niet crashen
        try:
            ydl_opts_info = {
                "quiet": True,
                "no_warnings": True,
                "ignoreerrors": True,  # <--- FIX: private videos worden genegeerd
                "no_color": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as e:
            clean_error = self._strip_ansi(str(e))
            raise Exception(f"Could not fetch playlist info: {clean_error}")
        # Filter None entries ( unavailable videos ) 
        raw_entries = info.get("entries", []) or [info]
        entries = [e for e in raw_entries if e is not None]
        if not info:
            raise Exception("Could not fetch playlist info (empty response)")

        # 2. Entries filteren — unavailable videos worden soms als None teruggegeven
        raw_entries = info.get("entries", []) or [info]
        entries = [e for e in raw_entries if e is not None]

        if not entries:
            raise Exception("No available tracks found in playlist.")

        total = len(entries)
        self._log(f"Found {total} tracks.")

        downloaded = 0
        skipped = 0

        for i, entry in enumerate(entries, start=1):
            if self.stop_requested:
                self._log("Stop signal received. Aborting.")
                raise Exception("Download stopped by user")

            title = entry.get("title", "Unknown")
            self._log(f"[{i:02d}/{total:02d}] {title}")
            self._report_progress(i, total)

            track_url = entry.get("webpage_url", entry.get("url"))
            if not track_url:
                self._log("  ⚠ No URL found, skipping.")
                skipped += 1
                continue

            cmd = self._build_cmd(track_url)

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

            output_lines = []

            def _reader():
                try:
                    for raw_line in self._process.stdout:
                        line = self._strip_ansi(raw_line.strip())
                        if line:
                            output_lines.append(line)
                            self._log(line)
                except Exception:
                    pass

            reader_thread = threading.Thread(target=_reader, daemon=True)
            reader_thread.start()

            exit_code = self._process.wait()
            reader_thread.join(timeout=2)
            self._process = None

            if self.stop_requested:
                break

            if self._is_skippable(output_lines, exit_code):
                self._log(f"  ⚠ Track unavailable, skipping.")
                skipped += 1
                continue

            if exit_code != 0:
                raise Exception(f"Download failed for {title} (exit code {exit_code})")

            downloaded += 1

        if self.stop_requested:
            raise Exception("Download stopped by user")

        if skipped > 0:
            self._log(f"Finished: {downloaded} downloaded, {skipped} skipped.")
        else:
            self._log("All downloads finished.")