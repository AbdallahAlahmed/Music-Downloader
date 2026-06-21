import os
import tkinter as tk
from pathlib import Path
import threading
from tkinter import messagebox, ttk
import customtkinter as ctk
from datetime import datetime
from src.downloader import MusicDownloader


class DownloaderGUI:
    """GUI class for the YouTube Music Downloader application."""

    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("YouTube Music Downloader")
        self.root.geometry("700x600")

        # Icon
        icon_path = Path(__file__).parent.parent / "assets" / "icon.ico"
        if icon_path.exists():
            self.root.iconbitmap(str(icon_path))

        # URL input
        self.url_label = ctk.CTkLabel(
            self.root, text="Enter the YouTube playlist URL:"
        )
        self.url_label.pack(pady=10)

        self.url_entry = ctk.CTkEntry(
            self.root,
            width=600,
            height=35,
            placeholder_text="Paste the playlist URL here...",
        )
        self.url_entry.pack()

        # Buttons
        BUTTON_WIDTH = 250

        self.paste_button = ctk.CTkButton(
            self.root,
            width=BUTTON_WIDTH,
            text="Paste URL",
            command=self.paste_url,
        )
        self.paste_button.pack(pady=5)

        self.download_button = ctk.CTkButton(
            self.root,
            width=BUTTON_WIDTH,
            text="Download playlist",
            command=self.start_download,
        )
        self.download_button.pack(pady=10)

        # Stop button (red, disabled by default)
        self.stop_button = ctk.CTkButton(
            self.root,
            width=BUTTON_WIDTH,
            text="Stop Download",
            command=self.stop_download,
            fg_color="#CC0000",
            hover_color="#990000",
            state="disabled",
        )
        self.stop_button.pack(pady=5)

        self.open_folder_button = ctk.CTkButton(
            self.root,
            width=BUTTON_WIDTH,
            text="Open Music Folder",
            command=self.open_music_folder,
        )
        self.open_folder_button.pack(pady=5)

        self.open_log_button = ctk.CTkButton(
            self.root,
            width=BUTTON_WIDTH,
            text="Open Download Log",
            command=self.open_log,
        )
        self.open_log_button.pack()

        # Status
        self.status_label = ctk.CTkLabel(self.root, text="Ready to download.")
        self.status_label.pack(pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=400,
            mode="determinate",
            maximum=100,
        )
        self.progress.pack(pady=5)

        # Track counter
        self.progress_label = ctk.CTkLabel(
            self.root,
            text="0 / 0",
            font=("Consolas", 9),
            text_color="#666",
        )
        self.progress_label.pack()

        # Log
        self.log_text = tk.Text(
            self.root,
            height=15,
            width=80,
            font=("Consolas", 11),
            bg="#2b2b2b",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief="flat",
            state="disabled",
            wrap="word",
        )
        self.log_text.pack(padx=10, pady=10, fill="both", expand=True)

    def download(self):
        """Download playlist in a background thread."""
        url = self.url_entry.get().strip()

        if not url:
            self._safe_messagebox(
                "showerror", "Error", "Please enter a playlist URL."
            )
            return

        music_folder = "music"
        if not os.path.exists(music_folder):
            self._safe_messagebox(
                "showinfo",
                "Folder not found",
                "No music folder available yet. It will be created.",
            )

        self._safe_status("Downloading playlist...", "orange")
        self._safe_log("Downloading playlist...")
        self._safe_button(self.open_folder_button, "disabled")

        try:
            self.downloader.download_playlist(url)

            if self.downloader.stop_requested:
                self._safe_status("Download stopped by user.", "#FF6600")
                self._safe_log("Download stopped by user.")
            else:
                self._safe_status("Download completed ✓", "#00FF00")
                self._safe_log("Download completed ✓")

        except Exception as error:
            error_msg = str(error)
            if "stopped by user" in error_msg.lower():
                self._safe_status("Download stopped by user.", "#FF6600")
                self._safe_log("Download stopped by user.")
            else:
                self._safe_messagebox(
                    "showerror",
                    "Error",
                    f"An error occurred during download: {error_msg}",
                )
                self._safe_log("Download failed ✗")

        finally:
            self._safe_button(self.download_button, "normal")
            self._safe_button(self.stop_button, "disabled")
            self._safe_button(self.open_folder_button, "normal")
            self._safe_entry_clear()

    def update_progress(self, current, total):
        """Update progress bar and labels (called from downloader thread)."""
        if total == 0:
            return
        percentage = (current / total) * 100

        self.root.after(
            0, lambda: self.progress.configure(value=percentage)
        )
        self.root.after(
            0,
            lambda: self.progress_label.configure(text=f"{current} / {total}"),
        )
        self.root.after(
            0,
            lambda: self.status_label.configure(
                text=f"Downloading track {current} of {total}..."
            ),
        )

    def start_download(self):
        """Start download in a separate thread."""
        self.log("Download requested.")

        self.downloader = MusicDownloader(
            log_callback=self.log,
            progress_callback=self.update_progress,
        )

        self.download_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

        thread = threading.Thread(target=self.download, daemon=True)
        thread.start()

    def stop_download(self):
        """Stop the ongoing download."""
        self.log("Stop requested by user.")
        self.downloader.stop_download()
        self.stop_button.configure(state="disabled")
        self.status_label.configure(
            text="Stopping download...", text_color="#FF6600"
        )

    # --- Thread-safe helpers ---

    def _safe_log(self, msg):
        self.root.after(0, lambda: self.log(msg))

    def _safe_status(self, text, color):
        self.root.after(
            0,
            lambda: self.status_label.configure(text=text, text_color=color),
        )

    def _safe_button(self, button, state):
        self.root.after(0, lambda: button.configure(state=state))

    def _safe_entry_clear(self):
        self.root.after(0, lambda: self.url_entry.delete(0, "end"))

    def _safe_messagebox(self, method, title, message):
        self.root.after(
            0, lambda: getattr(messagebox, method)(title, message)
        )

    def log(self, message):
        """Thread-safe log to the text widget."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}\n"

        def _update():
            self.log_text.configure(state="normal")
            self.log_text.insert("end", line)
            self.log_text.see("end")
            self.log_text.configure(state="disabled")

        if threading.current_thread() is threading.main_thread():
            _update()
        else:
            self.root.after(0, _update)

    def paste_url(self):
        """Paste URL from clipboard into the entry field."""
        try:
            clipboard_text = self.root.clipboard_get()
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, clipboard_text)
            self.log("URL pasted from clipboard.")
        except Exception:
            self.log("Clipboard is empty.")

    def open_music_folder(self):
        """Open the music output folder."""
        music_folder = "music"
        if os.path.exists(music_folder):
            os.startfile(music_folder)
        else:
            self.log("Music folder does not exist.")

    def open_log(self):
        """Open download log file in default text editor."""
        log_file = Path(__file__).parent.parent / "logs" / "download_log.txt"

        if not log_file.exists():
            self.log("Download log not found.")
            return

        try:
            os.startfile(str(log_file))
        except Exception as e:
            self.log(f"Could not open log file: {e}")

    def run(self):
        self.root.mainloop()