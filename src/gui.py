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
        self.downloader = MusicDownloader()

        self.root = ctk.CTk()
        self.root.title("YouTube Music Downloader")
        self.root.geometry("700x600")

        # Fix icon path relative to src/gui.py -> ../assets/icon.ico
        icon_path = Path(__file__).parent.parent / "assets" / "icon.ico"
        if icon_path.exists():
            self.root.iconbitmap(str(icon_path))

        # URL input
        self.url_label = ctk.CTkLabel(self.root, text="Enter the YouTube playlist URL:")
        self.url_label.pack(pady=10)

        self.url_entry = ctk.CTkEntry(
            self.root,
            width=600,
            height=35,
            placeholder_text="Paste the playlist URL here..."
        )
        self.url_entry.pack()

        # Buttons
        BUTTON_WIDTH = 250

        self.paste_button = ctk.CTkButton(
            self.root,
            width=BUTTON_WIDTH,
            text="Paste URL",
            command=self.paste_url
        )
        self.paste_button.pack(pady=5)

        self.download_button = ctk.CTkButton(
            self.root,
            width=BUTTON_WIDTH,
            text="Download playlist",
            command=self.start_download
        )
        self.download_button.pack(pady=20)

        self.open_folder_button = ctk.CTkButton(
            self.root,
            width=BUTTON_WIDTH,
            text="Open Music Folder",
            command=self.open_music_folder
        )
        self.open_folder_button.pack(pady=5)

        self.open_log_button = ctk.CTkButton(
            self.root,
            width=BUTTON_WIDTH,
            text="Open Download Log",
            command=self.open_log
        )
        self.open_log_button.pack()

        # Status
        self.status_label = ctk.CTkLabel(self.root, text="Ready to download.")
        self.status_label.pack(pady=10)

        # Progress bar (ttk is standard tkinter — .config() works, but using .configure() for consistency)
        self.progress = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=400,
            mode="determinate",
            maximum=100
        )
        self.progress.pack(pady=5)

        # Track counter
        self.progress_label = ctk.CTkLabel(
            self.root,
            text="0 / 0",
            font=("Consolas", 9),
            text_color="#666"
        )
        self.progress_label.pack()

        # FIX: Use standard tkinter.Text instead of CTkTextbox to avoid state/config bugs
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
            wrap="word"
        )
        self.log_text.pack(padx=10, pady=10, fill="both", expand=True)

    def download(self):
        """Download playlist in background thread."""
        url = self.url_entry.get().strip()

        if not url:
            self.root.after(
                0,
                lambda: messagebox.showerror("Error", "Please enter a playlist URL.")
            )
            return

        # Check music folder
        music_folder = "music"
        if not os.path.exists(music_folder):
            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Folder not found",
                    "No music folder available yet. It will be created."
                )
            )

        self.root.after(
            0,
            lambda: self.status_label.configure(
                text="Downloading playlist...",
                text_color="orange"
            )
        )
        self.root.after(
            0,
            lambda: self.log(message="Downloading playlist...")
        )
        self.root.after(
            0,
            lambda: self.open_folder_button.configure(state="disabled")
        )

        self.downloader = MusicDownloader(
            log_callback=self.log,
            progress_callback=self.update_progress
        )

        try:
            self.downloader.download_playlist(url)

            self.root.after(
                0,
                lambda: self.status_label.configure(
                    text="Download completed ✓",
                    text_color="#00FF00"
                )
            )
            self.root.after(
                0,
                lambda: self.log(message="Download completed ✓")
            )
            self.root.after(
                0,
                lambda: self.download_button.configure(state="normal")
            )
            self.root.after(
                0,
                lambda: self.open_folder_button.configure(state="normal")
            )
            self.root.after(
                0,
                lambda: self.url_entry.delete(0, "end")
            )

        except Exception as error:
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Error",
                    f"An error occurred during download: {error}", text_color="red"
                )
            )
            self.root.after(
                0,
                lambda: self.log(message="Download failed ✗")
            )
            self.root.after(
                0,
                lambda: self.download_button.configure(state="normal")
            )

    def update_progress(self, current, total):
        """Update progress bar and labels (called from downloader thread)."""
        if total == 0:
            return
        percentage = (current / total) * 100

        self.root.after(0, lambda: self.progress.configure(value=percentage))
        self.root.after(
            0,
            lambda: self.progress_label.configure(text=f"{current} / {total}")
        )
        self.root.after(
            0,
            lambda: self.status_label.configure(
                text=f"Downloading track {current} of {total}..."
            )
        )

    def start_download(self):
        """Start download in a separate thread."""
        self.log("Download requested.")
        self.download_button.configure(state="disabled")

        thread = threading.Thread(target=self.download, daemon=True)
        thread.start()

    def log(self, message):
        """Thread-safe log to the text widget."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}\n"

        # Standard tkinter.Text uses .configure() and string states — works perfectly
        self.log_text.configure(state="normal")
        self.log_text.insert("end", line)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

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

    def open_log(self) -> None:
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