import threading
import tkinter as tk
from tkinter import messagebox

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
                text="Downloading..."
            )
        )

        try:

            self.downloader.download_playlist(url)

            self.root.after(
                0,
                lambda: self.status_label.config(
                    text="Download completed"
                )
            )
            self.root.after(
                0,
                lambda: self.url_entry.delete(0, tk.END)
            )

        except Exception as error:

            self.root.after(
                0,
                lambda: self.status_label.config(
                    text=f"Error: {error}"
                )
            )

    def start_download(self):
        """
        Starts the download process in a separate thread to avoid blocking the GUI.
        """
        thread = threading.Thread(target=self.download, daemon=True)
        thread.start()


    def run(self):

        self.root.mainloop()