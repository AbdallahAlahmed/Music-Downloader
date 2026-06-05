import threading
import tkinter as tk
from tkinter import messagebox
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
            lambda: self.log(
                message="Downloading playlist..."
            )
        )
        self.downloader = MusicDownloader(log_callback=self.log)

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