import threading
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from src.downloader import MusicDownloader
# This class is responsible for creating the GUI for the YouTube Music Downloader application.
class DownloaderGUI:
    """GUI class for the YouTube Music Downloader application."""
    def __init__(self):
        self.downloader = MusicDownloader()

        self.root = tk.Tk()
        self.root.title("YouTube Music Downloader")
        
        self.root.geometry("700x200")
        self.url_label = tk.Label(self.root, text="Enter the YouTube playlist URL:")
        self.url_label.pack(pady=10)
        self.url_entry = tk.Entry(self.root, width=80)
        self.url_entry.pack()
        self.download_button = tk.Button(self.root, text="Download playlist", command=self.start_download)
        self.download_button.pack(pady=20)
        self.status_label = tk.Label(self.root, text="Ready to download.")
        self.status_label.pack()
                # Progressbar (toegevoegd)
        self.progress = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=400,
            mode="determinate",
            maximum=100
        )
        self.progress.pack(pady=5)

        # Track teller (toegevoegd)
        self.progress_label = tk.Label(
            self.root,
            text="0 / 0",
            font=("Consolas", 9),
            fg="#666"
        )
        self.progress_label.pack()
        self.log_text = tk.Text(self.root, height=10, width=80,state="disabled")
        self.log_text.pack(padx=10,pady=10)


    def download(self):
        """
        Download playlist.
        """

        url = self.url_entry.get().strip()

        if not url:

            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Error",
                    "Please enter a playlist URL."
                )
            )

            return

        self.root.after(
            0,
            lambda: self.status_label.config(
                text="Downloading playlist..."
            )
        )
        self.root.after(
            0,
            lambda: self.log(
                message="Downloading playlist..."
            )
        )
        self.downloader = MusicDownloader(log_callback=self.log, progress_callback=self.update_progress)

        try:

            self.downloader.download_playlist(url)

            self.root.after(
                0,
                lambda: self.log(
                    message="Download completed ✓"
                )
            )
            # Re-enable the download button after the download is complete
            self.root.after(0, lambda: self.download_button.config(state=tk.NORMAL))

            self.root.after(
                0,
                lambda: self.url_entry.delete(0, tk.END)
            )

        except Exception as error:

            self.root.after(
                0,
                lambda: self.log(
                    message="Download failed ✗"
                )
            )
            # Re-enable the download button after the download is complete or if an error occurs
            self.root.after(0, lambda: self.download_button.config(state=tk.NORMAL))

    def update_progress(self, current, total):
        """
        Update the progress bar based on the current and total number of tracks.
        """
        percentage = (current / total) * 100
        # Thread-safe update to GUI 
        self.root.after(0, lambda: self.progress.config(value=percentage))
        self.root.after(0, lambda: self.progress_label.config(text=f"{current} / {total}"))
        self.root.after(0, lambda: self.status_label.config(text=f"Downloading track {current} of {total}..."))

    def start_download(self):
        """
        Starts the download process in a separate thread to avoid blocking the GUI.
        """
        self.log("Download requested.")
        # Disable the download button to prevent multiple clicks while downloading
        self.download_button.config(state=tk.DISABLED)

        thread = threading.Thread(target=self.download, daemon=True)
        thread.start()

    def log(self, message):
        """
        Logs a message to the log text widget with a timestamp.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    def run(self):

        self.root.mainloop()